# Timly - AI-анализ откликов с HH.ru

Сервис для автоматического анализа откликов на вакансии с HH.ru с использованием искусственного интеллекта (GPT-4o-mini).

## Основные возможности

- Интеграция с HH.ru через API токен работодателя
- Автоматическая синхронизация вакансий и откликов
- AI-анализ резюме кандидатов с оценкой соответствия вакансии
- Безопасное шифрование токенов HH.ru
- Удобный веб-интерфейс для управления

## Технологический стек

### Backend
- **FastAPI** - современный асинхронный веб-фреймворк
- **PostgreSQL** - надёжная база данных
- **SQLAlchemy** - ORM для работы с БД
- **OpenAI GPT-4o-mini** - AI модель для анализа
- **JWT** - аутентификация пользователей

### Frontend
- **React** с TypeScript
- **Material-UI** - компоненты интерфейса
- **Vite** - сборщик
- **Axios** - HTTP клиент

## Требования

- Docker и Docker Compose
- OpenAI API ключ
- HH.ru API токен работодателя

## Быстрый старт

### 1. Клонирование проекта

```bash
cd timly
```

### 2. Настройка переменных окружения

Создайте файл `.env` на основе примера:

```bash
cp .env.example .env
```

Откройте `.env` и добавьте:
- `OPENAI_API_KEY` - ваш ключ OpenAI API
- `ENCRYPTION_KEY` - ключ для шифрования (опционально, генерируется автоматически)

### 3. Запуск через Docker Compose

```bash
docker-compose up -d
```

Это запустит:
- PostgreSQL на порту 5432
- Backend API на http://localhost:8000
- Frontend на http://localhost:3000

### 4. Альтернативный запуск (без Docker)

#### Backend:

```bash
cd backend

# Создание виртуального окружения
python -m venv venv

# Активация (Windows)
venv\Scripts\activate

# Активация (Linux/Mac)
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt

# Запуск PostgreSQL (должен быть установлен отдельно)
# Создайте БД timly и обновите DATABASE_URL в .env

# Запуск сервера
uvicorn app.main:app --reload
```

#### Frontend:

```bash
cd frontend

# Установка зависимостей
npm install

# Запуск в режиме разработки
npm run dev
```

## Использование

### 1. Регистрация и вход

1. Откройте http://localhost:3000
2. Зарегистрируйте новый аккаунт
3. Войдите в систему

### 2. Настройка токена HH.ru

1. Перейдите в раздел "Настройки"
2. Получите токен в личном кабинете работодателя на HH.ru:
   - Войдите на HH.ru как работодатель
   - Перейдите в "Настройки" → "Интеграция и API"
   - Создайте приложение и скопируйте токен
3. Вставьте токен в поле и сохраните

### 3. Работа с вакансиями

1. На главной странице нажмите "Синхронизировать"
2. Система загрузит ваши активные вакансии с HH.ru
3. Нажмите на вакансию для просмотра откликов
4. Используйте кнопку "Анализировать" для AI-анализа резюме

## Структура проекта

```
timly/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Конфигурация и безопасность
│   │   ├── models/       # Модели БД
│   │   ├── schemas/      # Pydantic схемы
│   │   ├── services/     # Бизнес-логика
│   │   └── main.py       # Точка входа
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/   # React компоненты
│   │   ├── pages/        # Страницы приложения
│   │   ├── services/     # API сервисы
│   │   ├── hooks/        # React хуки
│   │   └── App.tsx       # Главный компонент
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## API Документация

После запуска backend доступна интерактивная документация:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## Безопасность

- Все пароли хешируются с использованием bcrypt
- Токены HH.ru шифруются перед сохранением (Fernet)
- JWT токены для аутентификации
- CORS настроен для защиты от внешних запросов

## Разработка

### Генерация ключа шифрования

```python
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```

### Миграции БД (Alembic)

```bash
cd backend
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## Возможные проблемы

1. **Ошибка подключения к БД**: Убедитесь, что PostgreSQL запущен и DATABASE_URL корректный
2. **Ошибка токена HH.ru**: Проверьте, что токен актуальный и имеет необходимые права
3. **Ошибка OpenAI**: Проверьте баланс и лимиты вашего OpenAI аккаунта

## Лицензия

MIT

## Поддержка

При возникновении вопросов создайте issue в репозитории проекта.