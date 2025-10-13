# ⚡ Быстрый старт - Деплой TIMLY за 15 минут

## Шаг 1: Генерация ключей безопасности (2 мин)

Выполните в терминале:

```bash
# SECRET_KEY
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"

# ENCRYPTION_KEY
python -c "from cryptography.fernet import Fernet; print('ENCRYPTION_KEY=' + Fernet.generate_key().decode())"

# JWT_SECRET_KEY
python -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(32))"
```

**Сохраните вывод!** Понадобится на шаге 4.

---

## Шаг 2: Создание GitHub репозитория (3 мин)

1. Откройте https://github.com/new
2. Название: `timly` (или любое другое)
3. Приватность: **Private**
4. Нажмите **Create repository**

Затем в терминале:

```bash
cd "c:\Users\wtk_x\OneDrive\Рабочий стол\TIMLY"
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/timly.git
git branch -M main
git push -u origin main
```

---

## Шаг 3: Подключение к Render.com (5 мин)

1. Откройте https://dashboard.render.com
2. Зарегистрируйтесь через GitHub
3. Нажмите **New +** → **Blueprint**
4. Выберите репозиторий `timly`
5. Нажмите **Apply**

Render создаст 3 сервиса:
- `timly-backend` (API)
- `timly-frontend` (Web)
- `timly-db` (Database)

Первый деплой займет ~5 минут и может завершиться с ошибкой - это нормально.

---

## Шаг 4: Настройка переменных окружения (3 мин)

### Backend

1. Откройте **timly-backend** → **Environment**
2. Добавьте переменные (используйте ключи из Шага 1):

```
OPENAI_API_KEY=sk-ваш-ключ-от-openai
SECRET_KEY=ваш-secret-key
ENCRYPTION_KEY=ваш-encryption-key
JWT_SECRET_KEY=ваш-jwt-secret-key
CORS_ORIGINS=https://timly-frontend.onrender.com
```

3. Нажмите **Save Changes**

### Frontend

1. Откройте **timly-frontend** → **Environment**
2. Добавьте переменную:

```
VITE_API_URL=https://timly-backend.onrender.com
```

3. Нажмите **Save Changes**

---

## Шаг 5: Проверка (2 мин)

Дождитесь когда все сервисы станут **Live** (зеленая точка).

Откройте в браузере:
```
https://timly-frontend.onrender.com
```

Должна открыться страница логина TIMLY.

---

## 🎉 Готово!

Ваш сервис работает по адресу:
- **Frontend:** https://timly-frontend.onrender.com
- **Backend API:** https://timly-backend.onrender.com
- **Database:** Автоматически подключена

---

## 🌐 Добавление кастомного домена (опционально)

### Если у вас есть домен (например, timly.ru):

1. **Добавьте домен в Render:**
   - Откройте **timly-frontend** → **Settings** → **Custom Domains**
   - Добавьте `app.timly.ru`

2. **Настройте DNS:**
   - Добавьте CNAME запись:
     ```
     Тип: CNAME
     Имя: app
     Значение: timly-frontend.onrender.com
     ```

3. **Обновите переменные:**
   - **Backend → CORS_ORIGINS:**
     ```
     https://app.timly.ru,https://timly.ru
     ```
   - **Frontend → VITE_API_URL:** (если настраиваете api.timly.ru)
     ```
     https://api.timly.ru
     ```

DNS изменения применятся через 5-30 минут.

---

## 🔄 Как обновлять сервис

После деплоя вы можете продолжать разработку локально:

```bash
# Внесите изменения в коде
# Сохраните изменения в Git
git add .
git commit -m "Описание изменений"
git push

# Render автоматически задеплоит обновления за ~3-5 минут
```

---

## 📚 Полная документация

Подробное руководство доступно в файле [DEPLOYMENT.md](DEPLOYMENT.md)

Там описаны:
- Решение проблем
- Настройка мониторинга
- Стоимость хостинга
- Резервное копирование
- И многое другое

---

## 💡 Полезные ссылки

- **Dashboard Render:** https://dashboard.render.com
- **Документация Render:** https://render.com/docs
- **OpenAI API Keys:** https://platform.openai.com/api-keys
- **Проверка DNS:** https://dnschecker.org

---

**Поздравляем! Ваш рекрутинговый сервис TIMLY запущен! 🚀**
