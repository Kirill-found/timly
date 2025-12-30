"""
Email сервис для отправки писем через SMTP
Используется для восстановления пароля и уведомлений
"""
import smtplib
import ssl
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

from app.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Сервис отправки email через SMTP"""

    def __init__(self):
        self.host = settings.SMTP_HOST
        self.port = settings.SMTP_PORT
        self.user = settings.SMTP_USER
        self.password = settings.SMTP_PASSWORD
        self.from_email = settings.SMTP_FROM_EMAIL
        self.from_name = settings.SMTP_FROM_NAME

    def _is_configured(self) -> bool:
        """Проверка настроек SMTP"""
        return bool(self.user and self.password)

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """
        Отправка email

        Args:
            to_email: Email получателя
            subject: Тема письма
            html_content: HTML содержимое
            text_content: Текстовое содержимое (опционально)

        Returns:
            bool: Успех отправки
        """
        if not self._is_configured():
            logger.warning("SMTP not configured, email not sent")
            return False

        try:
            # Создаём сообщение
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email

            # Добавляем текстовую версию
            if text_content:
                part1 = MIMEText(text_content, "plain", "utf-8")
                message.attach(part1)

            # Добавляем HTML версию
            part2 = MIMEText(html_content, "html", "utf-8")
            message.attach(part2)

            # Отправляем через SSL
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(self.host, self.port, context=context) as server:
                server.login(self.user, self.password)
                server.sendmail(self.from_email, to_email, message.as_string())

            logger.info(f"Email sent to {to_email}: {subject}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False

    def send_password_reset_code(self, to_email: str, code: str) -> bool:
        """
        Отправка кода восстановления пароля

        Args:
            to_email: Email пользователя
            code: 6-значный код

        Returns:
            bool: Успех отправки
        """
        subject = "Восстановление пароля - Timly"

        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: #0a0a0a;
            color: #fafafa;
            margin: 0;
            padding: 40px 20px;
        }}
        .container {{
            max-width: 480px;
            margin: 0 auto;
            background-color: #111111;
            border-radius: 12px;
            padding: 40px;
            border: 1px solid #262626;
        }}
        .logo {{
            text-align: center;
            margin-bottom: 32px;
        }}
        .logo span {{
            font-size: 24px;
            font-weight: 600;
            color: #fafafa;
        }}
        h1 {{
            font-size: 20px;
            font-weight: 600;
            margin: 0 0 16px 0;
            color: #fafafa;
        }}
        p {{
            color: #a1a1a1;
            margin: 0 0 24px 0;
            line-height: 1.6;
        }}
        .code-box {{
            background-color: #1a1a1a;
            border: 1px solid #333;
            border-radius: 8px;
            padding: 24px;
            text-align: center;
            margin: 24px 0;
        }}
        .code {{
            font-size: 32px;
            font-weight: 700;
            letter-spacing: 8px;
            color: #fafafa;
            font-family: monospace;
        }}
        .timer {{
            color: #737373;
            font-size: 14px;
            margin-top: 12px;
        }}
        .footer {{
            margin-top: 32px;
            padding-top: 24px;
            border-top: 1px solid #262626;
            color: #737373;
            font-size: 12px;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">
            <span>timly.</span>
        </div>

        <h1>Восстановление пароля</h1>
        <p>Вы запросили сброс пароля для вашего аккаунта Timly. Используйте код ниже для восстановления доступа:</p>

        <div class="code-box">
            <div class="code">{code}</div>
            <div class="timer">Код действителен 15 минут</div>
        </div>

        <p>Если вы не запрашивали сброс пароля, просто проигнорируйте это письмо.</p>

        <div class="footer">
            &copy; 2024 Timly. AI-скрининг резюме.<br>
            Это автоматическое сообщение, не отвечайте на него.
        </div>
    </div>
</body>
</html>
"""

        text_content = f"""
Восстановление пароля - Timly

Вы запросили сброс пароля для вашего аккаунта Timly.

Ваш код восстановления: {code}

Код действителен 15 минут.

Если вы не запрашивали сброс пароля, просто проигнорируйте это письмо.

---
Timly - AI-скрининг резюме
"""

        return self.send_email(to_email, subject, html_content, text_content)


# Singleton instance
_email_service: Optional[EmailService] = None


def get_email_service() -> EmailService:
    """Получение singleton экземпляра EmailService"""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service


async def send_password_reset_email(email: str, code: str) -> bool:
    """Отправить email с кодом восстановления пароля"""
    service = get_email_service()
    return service.send_password_reset_code(email, code)
