# 🇷🇺 Деплой TIMLY на Timeweb Cloud

Пошаговая инструкция для развертывания проекта TIMLY на российском хостинге Timeweb Cloud.

---

## 📋 Что вам понадобится

- ✅ Аккаунт на Timeweb Cloud (timeweb.com)
- ✅ ~200-300₽ на балансе
- ✅ OpenAI API ключ
- ✅ 30 минут времени

---

## 🎯 ШАГ 1: Создание облачного сервера

### 1.1 Войдите в панель Timeweb

1. Откройте: https://timeweb.cloud
2. Войдите в аккаунт
3. Перейдите в **"Облачные серверы"**

### 1.2 Создайте сервер

Нажмите **"Создать сервер"** и выберите:

**Операционная система:**
- Ubuntu 22.04 LTS

**Конфигурация (для начала):**
- **1 vCPU**
- **1 GB RAM**
- **10 GB SSD**
- **Стоимость:** ~200₽/месяц

**Локация:**
- Москва (самый быстрый для России)

**SSH-ключ:**
- Можете пропустить (будет пароль для root)

**Имя сервера:**
- `timly-production`

### 1.3 Дождитесь создания

Сервер создастся за 1-2 минуты. Вы получите:
- **IP-адрес** (например: 185.123.456.78)
- **Пароль root** (придет на email или в панели)

**Сохраните IP и пароль!**

---

## 🔧 ШАГ 2: Настройка сервера

### 2.1 Подключитесь к серверу

**Через PowerShell/CMD на Windows:**

```bash
ssh root@ваш-ip-адрес
```

Введите пароль root.

**Если ssh не работает**, используйте веб-консоль в панели Timeweb:
- Откройте сервер → **"Консоль"**

### 2.2 Обновите систему

```bash
apt update && apt upgrade -y
```

### 2.3 Установите Docker

```bash
# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Установка Docker Compose
apt install docker-compose -y

# Проверка установки
docker --version
docker-compose --version
```

### 2.4 Установите Git

```bash
apt install git -y
```

---

## 📥 ШАГ 3: Загрузка проекта

### 3.1 Клонируйте репозиторий

```bash
cd /root
git clone https://github.com/Kirill-found/timly.git
cd timly
```

### 3.2 Создайте файл с переменными окружения

```bash
cp .env.production .env.prod
nano .env.prod
```

**Отредактируйте файл** (используйте стрелки для навигации, Ctrl+O для сохранения, Ctrl+X для выхода):

```env
# Database
DB_PASSWORD=создайте-сложный-пароль-123

# Security Keys (уже заполнены, можете оставить)
SECRET_KEY=r9g4dU8XW07FItvapivcdxz3R6GjxJNa8aZyFOIqHMc
ENCRYPTION_KEY=XLM2AFXCxysDuiLgbNKAT-wd1Nx-HJ3CYmqRDKucXSQ=
JWT_SECRET_KEY=lw3dF5hi9DkYIuQmHIpPAEQ9lA1L3M7igW0Zpef-Xy0

# OpenAI
OPENAI_API_KEY=sk-ваш-реальный-ключ-от-openai

# URLs (замените на IP вашего сервера)
FRONTEND_URL=http://185.123.456.78
BACKEND_URL=http://185.123.456.78:8000
```

**Важно:**
- Замените `185.123.456.78` на реальный IP вашего сервера
- Замените `sk-ваш-реальный-ключ` на ваш OpenAI ключ
- Придумайте сложный DB_PASSWORD

---

## 🚀 ШАГ 4: Запуск приложения

### 4.1 Сделайте deploy.sh исполняемым

```bash
chmod +x deploy.sh
```

### 4.2 Запустите деплой

```bash
./deploy.sh
```

**Что произойдет:**
1. Скачаются образы Docker
2. Соберутся backend и frontend
3. Запустится PostgreSQL база данных
4. Запустятся все сервисы

**Это займет 5-10 минут** (первый раз дольше).

### 4.3 Проверьте статус

```bash
docker-compose -f docker-compose.prod.yml ps
```

Должны видеть 3 контейнера в статусе **Up**:
- timly-db-1
- timly-backend-1
- timly-frontend-1

---

## ✅ ШАГ 5: Проверка работы

### 5.1 Проверьте Backend API

Откройте в браузере:
```
http://ваш-ip:8000/api/health
```

Должны увидеть: `{"status":"ok"}`

### 5.2 Проверьте Frontend

Откройте в браузере:
```
http://ваш-ip
```

Должна открыться страница TIMLY с формой входа! 🎉

---

## 🔥 Настройка Firewall (ВАЖНО!)

По умолчанию порты могут быть закрыты. Откройте их:

### В панели Timeweb:

1. Откройте ваш сервер
2. Перейдите в **"Firewall"** или **"Сеть"**
3. Добавьте правила:
   - **Порт 80** (HTTP) - для frontend
   - **Порт 8000** (HTTP) - для backend API
   - **Порт 22** (SSH) - для подключения

### Или через команду на сервере:

```bash
ufw allow 80/tcp
ufw allow 8000/tcp
ufw allow 22/tcp
ufw enable
```

---

## 📊 Мониторинг и логи

### Просмотр логов:

```bash
# Все сервисы
docker-compose -f docker-compose.prod.yml logs -f

# Только backend
docker-compose -f docker-compose.prod.yml logs -f backend

# Только frontend
docker-compose -f docker-compose.prod.yml logs -f frontend
```

### Перезапуск сервисов:

```bash
docker-compose -f docker-compose.prod.yml restart
```

### Остановка:

```bash
docker-compose -f docker-compose.prod.yml down
```

---

## 🔄 Обновление приложения

Когда вы внесете изменения в код и отправите на GitHub:

```bash
cd /root/timly
./deploy.sh
```

Скрипт автоматически:
1. Скачает новый код
2. Пересоберет образы
3. Перезапустит сервисы

---

## 🌐 Подключение домена (опционально)

### Если хотите красивый домен вместо IP:

1. **Купите домен** (например, на reg.ru или timeweb.com)
2. **Добавьте A-записи в DNS:**
   ```
   @ → ваш-ip (для timly.ru)
   www → ваш-ip (для www.timly.ru)
   api → ваш-ip (для api.timly.ru)
   ```

3. **Настройте Nginx на сервере:**

```bash
apt install nginx -y
nano /etc/nginx/sites-available/timly
```

Добавьте конфигурацию:
```nginx
server {
    listen 80;
    server_name timly.ru www.timly.ru;

    location / {
        proxy_pass http://localhost:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

server {
    listen 80;
    server_name api.timly.ru;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Активируйте:
```bash
ln -s /etc/nginx/sites-available/timly /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

4. **Обновите .env.prod:**
```env
FRONTEND_URL=https://timly.ru
BACKEND_URL=https://api.timly.ru
```

5. **Установите SSL (бесплатный Let's Encrypt):**
```bash
apt install certbot python3-certbot-nginx -y
certbot --nginx -d timly.ru -d www.timly.ru -d api.timly.ru
```

---

## 💰 Стоимость

**Минимальная конфигурация:**
- Timeweb Cloud Server (1 vCPU, 1GB): ~200₽/мес
- Домен .ru: ~200₽/год
- OpenAI API: ~$5-10/мес (по факту)

**Итого: ~500₽/месяц**

**При росте трафика:**
- Можете увеличить мощность сервера
- Или разделить на несколько серверов

---

## 🐛 Решение проблем

### Backend не запускается

```bash
docker-compose -f docker-compose.prod.yml logs backend
```

Проверьте:
- Правильно ли заполнен .env.prod
- Есть ли OpenAI API ключ

### База данных не работает

```bash
docker-compose -f docker-compose.prod.yml logs db
```

Проверьте что DB_PASSWORD установлен.

### Не открывается сайт

Проверьте firewall:
```bash
ufw status
```

Откройте порты 80 и 8000.

---

## 📞 Поддержка Timeweb

- **Документация:** https://timeweb.cloud/docs
- **Поддержка:** https://timeweb.cloud/support
- **Telegram:** @timewebcloud

---

## 🎉 Готово!

Ваш TIMLY теперь работает на российском хостинге!

**Адреса:**
- Frontend: `http://ваш-ip`
- Backend API: `http://ваш-ip:8000`
- Документация API: `http://ваш-ip:8000/docs`

**Следующие шаги:**
1. Зарегистрируйте первого пользователя
2. Протестируйте все функции
3. Подключите домен
4. Настройте мониторинг

---

**Удачи с проектом! 🚀**
