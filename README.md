# Timly - AI-powered Resume Screening Platform

AI-платформа для автоматического скрининга резюме, интегрированная с HH.ru API для российского рынка труда.

## 🚀 Быстрый старт

### Предварительные требования

- Docker и Docker Compose
- OpenAI API ключ (для AI анализа)
- HH.ru API токен работодателя (получить на hh.ru)

### Запуск проекта

1. **Клонирование репозитория**
   ```bash
   git clone <repository-url>
   cd TIMLY
   ```

2. **Настройка переменных окружения**
   ```bash
   cp .env.example .env
   # Отредактируйте .env файл и добавьте ваш OpenAI API ключ
   ```

3. **Запуск всех сервисов**
   ```bash
   docker-compose up -d
   ```

4. **Проверка работоспособности**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## 🏗 Архитектура проекта

```
TIMLY/
├── backend/                 # FastAPI сервер
│   ├── app/
│   │   ├── api/            # REST API endpoints
│   │   ├── models/         # SQLAlchemy модели
│   │   ├── schemas/        # Pydantic схемы
│   │   ├── services/       # Бизнес логика
│   │   ├── workers/        # Фоновые задачи (RQ)
│   │   └── utils/          # Утилиты
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/               # React + TypeScript приложение
│   ├── src/
│   │   ├── components/     # React компоненты
│   │   ├── pages/          # Страницы приложения
│   │   ├── services/       # API клиенты
│   │   ├── store/          # Context API состояние
│   │   └── types/          # TypeScript типы
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml      # Оркестрация всех сервисов
├── init-db.sql            # Инициализация PostgreSQL
└── README.md              # Этот файл
```

## 🛠 Технологический стек

### Backend
- **Python 3.11** - Основной язык
- **FastAPI** - Web framework
- **PostgreSQL 15** - База данных
- **Redis 7.2** - Кеш и очереди
- **RQ** - Фоновые задачи
- **SQLAlchemy 2.0** - ORM
- **Pydantic 2.5** - Валидация данных

### Frontend
- **React 18** - UI библиотека
- **TypeScript 5.0** - Типизация
- **Vite 5** - Сборщик
- **Ant Design 5.12** - UI компоненты
- **Axios** - HTTP клиент

### Infrastructure
- **Docker** - Контейнеризация
- **Docker Compose** - Локальная оркестрация
- **Nginx** - Reverse proxy (production)

### Внешние API
- **HH.ru API** - Получение вакансий и откликов
- **OpenAI GPT-4o-mini** - AI анализ резюме

## 📋 Основные функции

### ✅ Реализовано в каркасе
- 🔐 **Аутентификация** - JWT токены, регистрация/вход
- 🏢 **Интеграция HH.ru** - Подключение API токена работодателя
- 🤖 **AI анализ** - Оценка резюме через OpenAI GPT-4o-mini
- 📊 **Dashboard** - Статистика и быстрые действия
- 🔄 **Синхронизация** - Автоматическое получение данных с HH.ru
- 📈 **Аналитика** - Результаты анализа кандидатов
- 📤 **Экспорт** - Выгрузка в Excel

### 🚧 TODO (заглушки созданы)
- Полная реализация всех API endpoints
- UI для всех страниц приложения
- Система уведомлений
- Расширенная аналитика
- Настройки пользователя

## 🔧 Разработка

### Запуск в режиме разработки

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Базы данных:**
```bash
# Только PostgreSQL и Redis
docker-compose up postgres redis -d
```

### Структура API

Все API endpoints документированы автоматически через FastAPI:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

**Основные группы endpoints:**
- `/api/auth/*` - Аутентификация и профиль
- `/api/hh/*` - Интеграция с HH.ru
- `/api/analysis/*` - AI анализ резюме
- `/api/settings/*` - Настройки пользователя

## 🔒 Безопасность

### Критичные меры безопасности
- ✅ **HH.ru токены** - Шифрование Fernet перед сохранением в БД
- ✅ **JWT токены** - 24-часовой срок действия
- ✅ **Пароли** - Хеширование bcrypt
- ✅ **CORS** - Настройка разрешенных доменов
- ✅ **Headers** - Безопасные HTTP заголовки

### Переменные окружения
Обязательно измените значения по умолчанию в production:
```env
SECRET_KEY=your-super-secret-key-min-32-chars
ENCRYPTION_KEY=your-fernet-encryption-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
OPENAI_API_KEY=sk-your-openai-api-key-here
```

## 💾 База данных

### Миграции
Для изменения схемы БД используйте Alembic:
```bash
cd backend
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

### Основные таблицы
- `users` - Пользователи и зашифрованные HH.ru токены
- `vacancies` - Синхронизированные вакансии
- `applications` - Отклики кандидатов с данными резюме
- `analysis_results` - Результаты AI анализа
- `sync_jobs` - История задач синхронизации

## 🤖 AI анализ

### Стоимость и оптимизация
- **Модель:** GPT-4o-mini (~$0.15 за 1M токенов)
- **Батчинг:** Максимум 5 резюме за запрос
- **Кеширование:** 24 часа для повторных анализов
- **Fallback:** Правила-основанный анализ при недоступности AI

### Критерии оценки
- Соответствие навыков (0-100)
- Соответствие опыта (0-100)
- Общая оценка (0-100)
- Рекомендация: hire/interview/maybe/reject
- Детальное обоснование на русском языке

## 📦 Deployment

### Production окружение
```bash
# С Nginx reverse proxy
docker-compose --profile production up -d

# Или без Nginx
docker-compose up -d
```

### Railway deployment
Проект готов к деплою на Railway:
1. Backend автоматически деплоится как web сервис
2. Frontend хостится на Vercel/Netlify
3. PostgreSQL и Redis - Railway аддоны

## 🐛 Troubleshooting

### Частые проблемы

**Backend не запускается:**
- Проверьте OPENAI_API_KEY в .env
- Убедитесь что PostgreSQL доступен
- Проверьте логи: `docker-compose logs backend`

**Frontend не загружается:**
- Проверьте что backend отвечает на /health
- Очистите кеш браузера
- Проверьте CORS настройки

**AI анализ не работает:**
- Проверьте валидность OpenAI API ключа
- Убедитесь что Redis доступен для кеширования
- Проверьте логи worker'а: `docker-compose logs worker`

## 📞 Поддержка

Для вопросов по разработке и деплою:
- Создайте issue в репозитории
- Проверьте логи сервисов: `docker-compose logs [service-name]`
- Используйте health check endpoints для диагностики

---

**Создано специально для российского рынка труда и HH.ru экосистемы** 🇷🇺