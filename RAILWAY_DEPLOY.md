# 🚂 Деплой TIMLY на Railway.app

Railway.app - отличная альтернатива Render для разработчиков из России.

## ✨ Преимущества Railway

- ✅ **$5 бесплатных кредитов** каждый месяц (без карты!)
- ✅ **Принимает российские карты** Visa/Mastercard
- ✅ **Не засыпает** (в отличие от Render Free)
- ✅ **Простая настройка** через веб-интерфейс
- ✅ **Автодеплой** из GitHub
- ✅ **PostgreSQL** включен

## 💰 Стоимость

**$5/месяц БЕСПЛАТНО** покрывает:
- ~500 часов работы backend (достаточно для тестирования)
- PostgreSQL база данных
- Неограниченный трафик

**После $5:**
- $0.000231 за GB-час (~$5-10/мес для малого проекта)
- Pay-as-you-go (платите только за использование)

---

## 📋 Пошаговая инструкция

### Шаг 1: Регистрация на Railway (2 мин)

1. Откройте: https://railway.app
2. Нажмите **Start a New Project**
3. Войдите через **GitHub** (проще всего)
4. Подтвердите email

✅ Вы получите **$5 бесплатных кредитов**!

---

### Шаг 2: Создание проекта (5 мин)

#### 2.1 Создайте новый проект

1. В Railway Dashboard нажмите **New Project**
2. Выберите **Deploy from GitHub repo**
3. Выберите репозиторий: `Kirill-found/timly`
4. Нажмите **Deploy**

Railway автоматически обнаружит backend и frontend!

#### 2.2 Добавьте PostgreSQL

1. В вашем проекте нажмите **New**
2. Выберите **Database** → **Add PostgreSQL**
3. База данных создастся автоматически

---

### Шаг 3: Настройка Backend (3 мин)

#### 3.1 Откройте Backend сервис

1. Найдите сервис с названием `backend` (или `timly`)
2. Перейдите в **Variables**

#### 3.2 Добавьте переменные окружения

Нажимайте **New Variable** и добавляйте:

```bash
# Обязательные переменные
OPENAI_API_KEY=ваш-openai-ключ
SECRET_KEY=r9g4dU8XW07FItvapivcdxz3R6GjxJNa8aZyFOIqHMc
ENCRYPTION_KEY=XLM2AFXCxysDuiLgbNKAT-wd1Nx-HJ3CYmqRDKucXSQ=
JWT_SECRET_KEY=lw3dF5hi9DkYIuQmHIpPAEQ9lA1L3M7igW0Zpef-Xy0

# Настройки приложения
APP_ENV=production
DEBUG=false

# CORS (обновите после деплоя frontend)
CORS_ORIGINS=https://timly-frontend-production.up.railway.app
```

#### 3.3 Подключите PostgreSQL

1. В **Variables** найдите кнопку **Reference Variables**
2. Выберите вашу PostgreSQL базу
3. Выберите `DATABASE_URL`
4. Нажмите **Add**

Railway автоматически подключит базу данных!

#### 3.4 Настройте Root Directory

1. Перейдите в **Settings**
2. Найдите **Root Directory**
3. Укажите: `backend`
4. Нажмите **Save**

---

### Шаг 4: Настройка Frontend (2 мин)

#### 4.1 Откройте Frontend сервис

1. Найдите сервис с названием `frontend`
2. Перейдите в **Variables**

#### 4.2 Добавьте переменные

```bash
# URL вашего backend (возьмите из Railway)
VITE_API_URL=https://timly-backend-production.up.railway.app
```

**Как узнать URL backend:**
1. Откройте backend сервис
2. Перейдите в **Settings** → **Domains**
3. Скопируйте сгенерированный URL (например: `timly-backend-production.up.railway.app`)
4. Добавьте `https://` в начале

#### 4.3 Настройте Root Directory

1. Перейдите в **Settings**
2. Найдите **Root Directory**
3. Укажите: `frontend`
4. Нажмите **Save**

---

### Шаг 5: Получите публичные URL (2 мин)

Railway генерирует случайные URL. Давайте сделаем их постоянными:

#### Backend URL:

1. Откройте backend сервис
2. Перейдите в **Settings** → **Networking**
3. Нажмите **Generate Domain**
4. Скопируйте URL (например: `timly-backend-production.up.railway.app`)

#### Frontend URL:

1. Откройте frontend сервис
2. Перейдите в **Settings** → **Networking**
3. Нажмите **Generate Domain**
4. Скопируйте URL (например: `timly-frontend-production.up.railway.app`)

#### Обновите CORS:

1. Вернитесь в **Backend** → **Variables**
2. Обновите `CORS_ORIGINS`:
```
CORS_ORIGINS=https://timly-frontend-production.up.railway.app
```

---

### Шаг 6: Проверка (1 мин)

#### Проверьте Backend:

Откройте: `https://ваш-backend-url.up.railway.app/api/health`

Должно вернуться:
```json
{"status": "ok"}
```

#### Проверьте Frontend:

Откройте: `https://ваш-frontend-url.up.railway.app`

Должна открыться страница логина TIMLY!

---

## 🎉 Готово!

Ваш сервис TIMLY теперь работает на Railway!

### 📍 Ваши URL:

- **Frontend:** https://timly-frontend-production.up.railway.app
- **Backend API:** https://timly-backend-production.up.railway.app
- **Database:** Подключена автоматически

---

## 🔄 Автоматические обновления

Railway автоматически деплоит при каждом `git push`:

```bash
# Внесите изменения локально
git add .
git commit -m "Обновление функционала"
git push

# Railway автоматически:
# ✅ Заметит изменения
# ✅ Пересоберет сервисы
# ✅ Задеплоит за ~2-3 минуты
```

---

## 🌐 Добавление кастомного домена

### Для Frontend:

1. Откройте frontend сервис → **Settings** → **Networking**
2. В разделе **Custom Domains** нажмите **Add Custom Domain**
3. Введите ваш домен (например: `app.timly.ru`)
4. Добавьте CNAME запись в DNS:
```
Тип: CNAME
Имя: app
Значение: timly-frontend-production.up.railway.app
```

### Для Backend:

1. Откройте backend сервис → **Settings** → **Networking**
2. Добавьте поддомен (например: `api.timly.ru`)
3. Добавьте CNAME запись:
```
Тип: CNAME
Имя: api
Значение: timly-backend-production.up.railway.app
```

### Обновите переменные:

**Backend → CORS_ORIGINS:**
```
CORS_ORIGINS=https://app.timly.ru,https://timly.ru
```

**Frontend → VITE_API_URL:**
```
VITE_API_URL=https://api.timly.ru
```

SSL сертификаты настроятся автоматически за ~5 минут!

---

## 💳 Когда понадобится карта

**Бесплатные $5/месяц** обычно достаточно для:
- Разработки и тестирования
- Небольшого MVP
- Демо для инвесторов

**Карта понадобится когда:**
- Исчерпаете $5 кредитов (Railway пришлет уведомление)
- Захотите больше ресурсов
- Проект станет популярным

**Railway принимает:**
- ✅ Visa/Mastercard из России
- ✅ Виртуальные карты (Tinkoff, Сбер)
- ✅ Карты других стран

---

## 📊 Мониторинг использования

### Проверить расход кредитов:

1. Откройте Railway Dashboard
2. Нажмите на ваш аватар (правый верхний угол)
3. Выберите **Usage**
4. Увидите:
   - Использовано кредитов
   - Оставшиеся кредиты
   - Прогноз расхода

### Оптимизация расходов:

- Frontend почти не тратит ресурсы (статика)
- Backend тратит больше (Python процесс)
- Database ~$1-2/месяц

**Совет:** На начальном этапе $5 должно хватить на месяц!

---

## 🐛 Решение проблем

### Backend не запускается

**Проблема:** Deploy failed

**Решение:**
1. Проверьте логи: Backend сервис → **Deployments** → последний деплой → **View Logs**
2. Убедитесь что `ROOT_DIRECTORY = backend`
3. Проверьте что все переменные окружения установлены

### Frontend показывает ошибки API

**Проблема:** Network Error или CORS

**Решение:**
1. Убедитесь что `VITE_API_URL` правильный (с https://)
2. Проверьте `CORS_ORIGINS` в backend содержит frontend URL
3. Проверьте что backend в статусе Active

### База данных не подключается

**Проблема:** Connection refused

**Решение:**
1. Убедитесь что PostgreSQL создана
2. Проверьте что `DATABASE_URL` добавлена в backend через **Reference Variables**
3. Перезапустите backend: **Settings** → **Redeploy**

---

## 💡 Полезные ссылки

- **Railway Dashboard:** https://railway.app/dashboard
- **Документация:** https://docs.railway.app
- **Discord поддержка:** https://discord.gg/railway
- **Статус Railway:** https://status.railway.app

---

## 🎯 Следующие шаги

После успешного деплоя:

1. ✅ Зарегистрируйте первого пользователя
2. ✅ Протестируйте все функции
3. ✅ Настройте кастомный домен
4. ✅ Настройте мониторинг (опционально)
5. ✅ Добавьте аналитику (опционально)

---

**Поздравляем! Ваш TIMLY запущен на Railway! 🚀**
