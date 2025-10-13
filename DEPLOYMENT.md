# 🚀 Руководство по деплою TIMLY на Render.com

Это пошаговое руководство поможет вам развернуть сервис TIMLY на Render.com с поддержкой кастомного домена.

## 📋 Содержание

1. [Предварительные требования](#предварительные-требования)
2. [Подготовка к деплою](#подготовка-к-деплою)
3. [Создание репозитория GitHub](#создание-репозитория-github)
4. [Настройка Render.com](#настройка-rendercom)
5. [Настройка переменных окружения](#настройка-переменных-окружения)
6. [Настройка кастомного домена](#настройка-кастомного-домена)
7. [Проверка и тестирование](#проверка-и-тестирование)
8. [Обновление приложения](#обновление-приложения)
9. [Решение проблем](#решение-проблем)

---

## 🔧 Предварительные требования

- ✅ Аккаунт на [GitHub](https://github.com)
- ✅ Аккаунт на [Render.com](https://render.com) (бесплатная регистрация)
- ✅ OpenAI API ключ ([получить здесь](https://platform.openai.com/api-keys))
- ✅ Кастомный домен (опционально, но рекомендуется)
- ✅ Git установлен локально

---

## 📦 Подготовка к деплою

### 1. Генерация секретных ключей

Выполните эти команды в терминале для генерации безопасных ключей:

```bash
# SECRET_KEY (32+ символов)
python -c "import secrets; print(secrets.token_urlsafe(32))"

# ENCRYPTION_KEY (Fernet ключ)
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# JWT_SECRET_KEY (32+ символов)
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Сохраните эти ключи!** Они понадобятся на следующих шагах.

---

## 🐙 Создание репозитория GitHub

### 1. Создайте новый репозиторий на GitHub

1. Откройте https://github.com/new
2. Назовите репозиторий (например, `timly`)
3. Выберите **Private** (рекомендуется) или Public
4. НЕ добавляйте README, .gitignore или лицензию (они уже есть)
5. Нажмите **Create repository**

### 2. Отправьте код в GitHub

```bash
# Перейдите в папку проекта
cd "c:\Users\wtk_x\OneDrive\Рабочий стол\TIMLY"

# Инициализируйте Git (если еще не инициализирован)
git init

# Добавьте все файлы
git add .

# Создайте первый коммит
git commit -m "Initial commit: TIMLY recruitment platform"

# Подключите удаленный репозиторий (замените YOUR_USERNAME на ваш GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/timly.git

# Отправьте код
git branch -M main
git push -u origin main
```

---

## 🌐 Настройка Render.com

### 1. Подключите GitHub к Render

1. Откройте https://dashboard.render.com
2. Нажмите **New +** → **Blueprint**
3. Подключите ваш GitHub аккаунт (если еще не подключен)
4. Выберите репозиторий `timly`
5. Render автоматически обнаружит файл `render.yaml`
6. Нажмите **Apply**

Render создаст:
- ✅ **timly-backend** - FastAPI сервис
- ✅ **timly-frontend** - React приложение
- ✅ **timly-db** - PostgreSQL база данных

### 2. Дождитесь первого деплоя

Первый деплой может занять 5-10 минут. Render будет:
- Устанавливать зависимости
- Создавать базу данных
- Запускать сервисы

**Важно:** Первый деплой может завершиться с ошибкой - это нормально! Нам нужно настроить переменные окружения.

---

## ⚙️ Настройка переменных окружения

### Backend (timly-backend)

1. Откройте **Dashboard** → **timly-backend**
2. Перейдите в **Environment**
3. Добавьте следующие переменные:

```env
# ОБЯЗАТЕЛЬНЫЕ
OPENAI_API_KEY=sk-ваш-openai-ключ
SECRET_KEY=ваш-сгенерированный-secret-key
ENCRYPTION_KEY=ваш-сгенерированный-encryption-key
JWT_SECRET_KEY=ваш-сгенерированный-jwt-secret-key

# DATABASE_URL создается автоматически из timly-db

# CORS (замените на ваш фронтенд URL после деплоя)
CORS_ORIGINS=https://timly-frontend.onrender.com,https://yourdomain.com
```

4. Нажмите **Save Changes**
5. Backend автоматически перезапустится

### Frontend (timly-frontend)

1. Откройте **Dashboard** → **timly-frontend**
2. Перейдите в **Environment**
3. Добавьте переменную:

```env
# Замените на URL вашего бэкенда
VITE_API_URL=https://timly-backend.onrender.com
```

4. Нажмите **Save Changes**
5. Frontend автоматически пересоберется

---

## 🌍 Настройка кастомного домена

### 1. Добавление домена к Frontend

1. Откройте **Dashboard** → **timly-frontend**
2. Перейдите в **Settings** → **Custom Domains**
3. Нажмите **Add Custom Domain**
4. Введите ваш домен (например, `app.timly.ru` или `timly.ru`)
5. Render покажет DNS записи, которые нужно добавить

### 2. Настройка DNS

В панели управления вашего регистратора доменов добавьте:

**Для поддомена (app.timly.ru):**
```
Тип: CNAME
Имя: app
Значение: timly-frontend.onrender.com
```

**Для основного домена (timly.ru):**
```
Тип: A
Имя: @
Значение: IP адрес из Render (показан в панели)

Тип: A
Имя: www
Значение: тот же IP адрес
```

### 3. Добавление поддомена для Backend (опционально)

Для красивого API URL (api.timly.ru вместо timly-backend.onrender.com):

1. Откройте **Dashboard** → **timly-backend**
2. Перейдите в **Settings** → **Custom Domains**
3. Добавьте `api.timly.ru`
4. Добавьте CNAME запись в DNS:

```
Тип: CNAME
Имя: api
Значение: timly-backend.onrender.com
```

### 4. Обновите CORS и API URL

После настройки доменов обновите переменные:

**Backend → Environment:**
```env
CORS_ORIGINS=https://app.timly.ru,https://timly.ru,https://www.timly.ru
```

**Frontend → Environment:**
```env
VITE_API_URL=https://api.timly.ru
```

**Важно:** SSL сертификаты настраиваются автоматически и занимают ~5 минут.

---

## ✅ Проверка и тестирование

### 1. Проверьте статус сервисов

В Dashboard Render все сервисы должны быть в статусе **Live** (зеленая точка).

### 2. Проверьте Backend API

Откройте в браузере:
```
https://timly-backend.onrender.com/api/health
```

Должен вернуться JSON:
```json
{"status": "ok"}
```

### 3. Проверьте Frontend

Откройте ваш домен (например, `https://app.timly.ru`)

Должна открыться страница логина TIMLY.

### 4. Проверьте базу данных

1. Откройте **Dashboard** → **timly-db**
2. Перейдите в **Shell**
3. Выполните:
```sql
\dt
```

Должны отобразиться таблицы: users, vacancies, resumes, analyses, subscriptions и т.д.

---

## 🔄 Обновление приложения

### Автоматический деплой (рекомендуется)

Render автоматически деплоит при push в main:

```bash
# Внесите изменения локально
# Например, отредактируйте файл

# Сохраните изменения
git add .
git commit -m "Описание изменений"
git push

# Render автоматически:
# 1. Заметит изменения в GitHub
# 2. Пересоберет и задеплоит сервисы
# 3. Процесс займет ~3-5 минут
```

### Ручной деплой

Если автодеплой отключен:

1. Откройте **Dashboard** → выберите сервис
2. Нажмите **Manual Deploy** → **Deploy latest commit**

---

## 🐛 Решение проблем

### Backend не запускается

**Проблема:** Build failed или Health check failed

**Решение:**
1. Проверьте логи: Dashboard → timly-backend → Logs
2. Убедитесь, что все переменные окружения установлены
3. Проверьте DATABASE_URL подключен к timly-db

### Frontend показывает ошибки API

**Проблема:** "Network Error" или CORS ошибки

**Решение:**
1. Убедитесь, что `VITE_API_URL` правильный
2. Проверьте `CORS_ORIGINS` в backend включает ваш frontend URL
3. Проверьте, что backend в статусе Live

### База данных недоступна

**Проблема:** "Connection refused" в логах backend

**Решение:**
1. Откройте Dashboard → timly-db
2. Проверьте статус (должен быть Available)
3. Убедитесь, что backend использует правильный DATABASE_URL

### Домен не работает после настройки

**Проблема:** Сайт недоступен по кастомному домену

**Решение:**
1. DNS изменения могут занять до 48 часов (обычно ~30 мин)
2. Проверьте DNS записи: https://dnschecker.org
3. Убедитесь, что SSL сертификат выпущен (Render → Custom Domain → Status: Active)

---

## 💰 Стоимость хостинга

### Бесплатный план (Free)
- Backend: Free Web Service (спит после 15 мин неактивности)
- Frontend: Free Static Site
- Database: Free PostgreSQL (256 MB)
- **Итого: $0/месяц**

**Ограничения:**
- Services засыпают после 15 мин без запросов
- Первый запрос после сна может занять ~30 сек

### Платный план (Рекомендуется для продакшена)
- Backend: Starter ($7/месяц)
- Frontend: Free Static Site
- Database: Starter ($7/месяц)
- **Итого: ~$14/месяц**

**Преимущества:**
- ✅ Сервисы всегда активны (без засыпания)
- ✅ Больше ресурсов (512 MB RAM → 1 GB)
- ✅ Больше места в БД (256 MB → 1 GB)

---

## 📞 Поддержка

**Документация Render:** https://render.com/docs

**Мониторинг статуса:** https://status.render.com

**Команда для быстрой проверки логов:**
```bash
# Установите Render CLI (опционально)
# https://render.com/docs/cli

render logs -s timly-backend
render logs -s timly-frontend
```

---

## ✨ Следующие шаги

После успешного деплоя:

1. ✅ Создайте первого пользователя-администратора
2. ✅ Настройте мониторинг (Sentry, Prometheus)
3. ✅ Настройте резервное копирование БД
4. ✅ Настройте уведомления об ошибках
5. ✅ Добавьте аналитику (Google Analytics, Яндекс.Метрика)

---

## 🎉 Готово!

Ваш сервис TIMLY теперь доступен онлайн!

Вы можете продолжать разработку локально, а все изменения будут автоматически деплоиться при `git push`.

**Удачи с проектом! 🚀**
