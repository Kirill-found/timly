# 📊 Система тарификации Timly

## Обзор

Реализована полноценная система подписок и тарификации для контроля доступа пользователей к функциям платформы.

---

## 🏗️ Архитектура

### 1. Модели данных

#### `SubscriptionPlan` - Тарифный план
Определяет лимиты и возможности тарифа.

**Поля:**
- `plan_type` - Тип плана (free, starter, professional, enterprise)
- `name` - Название тарифа
- `price_monthly` / `price_yearly` - Цены
- `max_active_vacancies` - Лимит активных вакансий
- `max_analyses_per_month` - Лимит анализов в месяц
- `max_export_per_month` - Лимит экспортов в месяц
- `features` - JSON с дополнительными возможностями

**Методы:**
- `has_feature(feature_name)` - Проверка наличия функции
- `to_dict()` - Сериализация для API

#### `Subscription` - Подписка пользователя
Связь пользователя с тарифным планом + отслеживание использования.

**Поля:**
- `user_id` - Владелец подписки
- `plan_id` - Связь с тарифным планом
- `status` - active, trial, expired, cancelled
- `started_at` / `expires_at` - Период действия
- `analyses_used_this_month` - Использовано анализов
- `exports_used_this_month` - Использовано экспортов
- `last_reset_at` - Дата последнего сброса счётчиков

**Свойства:**
- `is_active` - Активна ли подписка
- `days_remaining` - Дней до окончания
- `usage_percentage` - Процент использования лимитов

**Методы:**
- `can_analyze()` - Можно ли выполнить анализ
- `can_export()` - Можно ли экспортировать
- `reset_monthly_usage()` - Сброс месячных счётчиков

#### `UsageLog` - Лог использования
Аудит всех действий пользователя для аналитики.

**Поля:**
- `user_id` - Пользователь
- `action_type` - Тип действия (analysis, export, sync)
- `vacancy_id` / `application_id` - Связанные ресурсы
- `metadata` - JSON с дополнительной информацией

---

## 📋 Тарифные планы

### Free (Бесплатный)
- **Цена:** 0 ₽
- **Вакансии:** 1 активная
- **Анализы:** 20/месяц
- **Экспорты:** 5/месяц
- **Функции:**
  - ✅ Базовый анализ
  - ✅ Email поддержка
  - ✅ Экспорт в Excel
  - ❌ API доступ
  - ❌ Приоритетная поддержка

### Starter
- **Цена:** 2990 ₽/мес или 29900 ₽/год (~16% скидка)
- **Вакансии:** 5 активных
- **Анализы:** 200/месяц
- **Экспорты:** 50/месяц
- **Функции:**
  - ✅ Всё из Free
  - ✅ Расширенные фильтры

### Professional
- **Цена:** 5990 ₽/мес или 59900 ₽/год (~16% скидка)
- **Вакансии:** 20 активных
- **Анализы:** 1000/месяц
- **Экспорты:** 200/месяц
- **Функции:**
  - ✅ Всё из Starter
  - ✅ API доступ
  - ✅ Приоритетная поддержка
  - ✅ Кастомные отчёты
  - ✅ Bulk операции
  - ✅ Webhook уведомления

### Enterprise
- **Цена:** По запросу
- **Вакансии:** Без ограничений
- **Анализы:** Без ограничений
- **Экспорты:** Без ограничений
- **Функции:**
  - ✅ Всё из Professional
  - ✅ Командная работа
  - ✅ Персональный менеджер
  - ✅ Кастомные интеграции
  - ✅ SLA гарантии
  - ✅ Помощь с внедрением

---

## 🔧 API Endpoints

### `GET /api/subscription/plans`
Получить список всех тарифных планов.

**Ответ:**
```json
{
  "success": true,
  "data": {
    "plans": [
      {
        "id": "...",
        "plan_type": "free",
        "name": "Free",
        "description": "...",
        "pricing": {
          "monthly": 0,
          "yearly": 0,
          "currency": "RUB",
          "yearly_discount": 0
        },
        "limits": {
          "active_vacancies": 1,
          "analyses_per_month": 20,
          "exports_per_month": 5
        },
        "features": {
          "basic_analysis": true,
          "api_access": false,
          ...
        }
      },
      ...
    ]
  }
}
```

### `GET /api/subscription/current`
Получить текущую подписку пользователя.

**Требуется:** Авторизация

**Ответ:**
```json
{
  "success": true,
  "data": {
    "subscription": {
      "id": "...",
      "user_id": "...",
      "plan": { /* SubscriptionPlan */ },
      "status": "active",
      "is_active": true,
      "period": {
        "started_at": "2025-10-13T10:00:00",
        "expires_at": "2025-11-13T10:00:00",
        "days_remaining": 30
      },
      "usage": {
        "analyses": {
          "used": 5,
          "limit": 20,
          "percentage": 25.0
        },
        "exports": {
          "used": 2,
          "limit": 5,
          "percentage": 40.0
        }
      }
    }
  }
}
```

### `POST /api/subscription/upgrade`
Обновить тарифный план.

**Требуется:** Авторизация

**Тело запроса:**
```json
{
  "plan_type": "professional",
  "duration_months": 12
}
```

**Параметры:**
- `plan_type` - Тип плана (free, starter, professional, enterprise)
- `duration_months` - Длительность (1 или 12 месяцев)

**Ответ:**
```json
{
  "success": true,
  "data": {
    "subscription": { /* новая подписка */ },
    "message": "Подписка успешно обновлена на тариф Professional"
  }
}
```

### `GET /api/subscription/usage?days=30`
Получить статистику использования.

**Требуется:** Авторизация

**Параметры:**
- `days` - Количество дней для анализа (1-365)

**Ответ:**
```json
{
  "success": true,
  "data": {
    "period_days": 30,
    "subscription": { /* текущая подписка */ },
    "total_usage": {
      "analysis": 45,
      "export": 12,
      "sync": 8
    },
    "daily_usage": {
      "2025-10-01": {
        "analysis": 3,
        "export": 1
      },
      "2025-10-02": {
        "analysis": 5,
        "export": 2
      },
      ...
    }
  }
}
```

### `GET /api/subscription/limits/check`
Проверить доступность операций.

**Требуется:** Авторизация

**Ответ:**
```json
{
  "success": true,
  "data": {
    "can_analyze": true,
    "can_export": false,
    "can_add_vacancy": true,
    "messages": {
      "analyze": null,
      "export": "Достигнут лимит экспортов (5 в месяц)",
      "vacancy": null
    }
  }
}
```

### `POST /api/subscription/cancel`
Отменить подписку.

**Требуется:** Авторизация

**Ответ:**
```json
{
  "success": true,
  "data": {
    "subscription": { /* обновлённая подписка */ },
    "message": "Подписка отменена. Доступ сохранится до 13.11.2025"
  }
}
```

---

## 💡 Использование в коде

### Проверка лимитов перед операцией

```python
from app.services.subscription_service import SubscriptionService

# В вашем endpoint
@router.post("/analyze")
async def analyze_application(
    application_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Проверка лимита
    service = SubscriptionService(db)
    can_analyze, error_msg = await service.check_can_analyze(current_user.id)

    if not can_analyze:
        return bad_request(
            error="LIMIT_EXCEEDED",
            message=error_msg
        )

    # Выполняем анализ
    result = await perform_analysis(application_id)

    # Увеличиваем счётчик использования
    await service.increment_analysis_usage(
        user_id=current_user.id,
        application_id=application_id,
        metadata={"score": result.score}
    )

    return success(data=result.to_dict())
```

### Проверка доступа к функции

```python
# Проверка наличия функции в тарифе
service = SubscriptionService(db)
has_access, error_msg = await service.check_feature_access(
    user_id=current_user.id,
    feature_name="api_access"
)

if not has_access:
    return bad_request(
        error="FEATURE_NOT_AVAILABLE",
        message="API доступ недоступен в вашем тарифе"
    )
```

---

## 🚀 Инициализация

### Шаг 1: Запустить скрипт создания тарифов

```bash
cd backend
python app/scripts/init_subscription_plans.py
```

Скрипт создаст 4 тарифных плана в базе данных.

### Шаг 2: Автоматическое создание подписок

При первом обращении к системе каждому пользователю автоматически создаётся бесплатная подписка через:

```python
subscription = await service.get_or_create_subscription(user_id)
```

---

## 🔄 Логика работы

### Автоматический сброс месячных лимитов

Система автоматически сбрасывает счётчики использования каждые 30 дней:

```python
if subscription.should_reset_monthly_usage():
    subscription.reset_monthly_usage()
    db.commit()
```

### Истечение подписки

При истечении оплаченного периода:
1. Подписка переводится в статус `expired`
2. Автоматически создаётся новая бесплатная подписка
3. Пользователь получает доступ к функциям Free плана

### Отмена подписки

При отмене:
1. Подписка переводится в статус `cancelled`
2. Доступ сохраняется до конца оплаченного периода
3. После окончания создаётся бесплатная подписка

---

## 📊 Мониторинг и аналитика

### Таблица `usage_logs`

Содержит детальную информацию о всех действиях:
- Кто и когда выполнил операцию
- Тип операции (analysis, export, sync)
- Связанные ресурсы (vacancy_id, application_id)
- Дополнительные метаданные

### Использование для аналитики

```sql
-- Топ пользователей по количеству анализов
SELECT user_id, COUNT(*) as analyses_count
FROM usage_logs
WHERE action_type = 'analysis'
  AND created_at >= DATE('now', '-30 days')
GROUP BY user_id
ORDER BY analyses_count DESC
LIMIT 10;

-- Статистика использования по тарифам
SELECT sp.name, COUNT(DISTINCT u.id) as users_count,
       AVG(s.analyses_used_this_month) as avg_analyses
FROM subscriptions s
JOIN subscription_plans sp ON s.plan_id = sp.id
JOIN users u ON s.user_id = u.id
WHERE s.status = 'active'
GROUP BY sp.name;
```

---

## 🔐 Интеграция с платёжными системами

### Подготовлено для интеграции

Endpoint `/api/subscription/upgrade` готов для интеграции с:
- YooKassa (Яндекс.Касса)
- CloudPayments
- Robokassa
- Stripe (для международных платежей)

### Алгоритм интеграции

1. Пользователь выбирает тариф на фронтенде
2. Создаётся платёж через платёжную систему
3. После успешной оплаты вызывается webhook
4. Webhook вызывает `/api/subscription/upgrade`
5. Подписка обновляется, пользователь получает доступ

---

## ✅ Чек-лист интеграции

- [x] Модели данных (SubscriptionPlan, Subscription, UsageLog)
- [x] Сервис управления подписками (SubscriptionService)
- [x] API endpoints для работы с подписками
- [x] Скрипт инициализации тарифов
- [x] Автоматическое создание бесплатной подписки
- [x] Проверка лимитов перед операциями
- [x] Логирование использования
- [x] Автосброс месячных счётчиков
- [ ] Интеграция с платёжной системой
- [ ] Frontend для отображения тарифов
- [ ] Frontend для управления подпиской
- [ ] Email уведомления об истечении подписки
- [ ] Админ-панель для управления подписками

---

## 📝 Примеры использования

### Пример 1: Ограничение анализа

```python
# В analysis.py
@router.post("/analyze/{application_id}")
async def analyze_application(
    application_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = SubscriptionService(db)

    # Проверяем лимит
    can_analyze, msg = await service.check_can_analyze(current_user.id)
    if not can_analyze:
        raise HTTPException(status_code=429, detail=msg)

    # Анализируем
    result = analyze(application_id)

    # Увеличиваем счётчик
    await service.increment_analysis_usage(
        user_id=current_user.id,
        application_id=application_id
    )

    return result
```

### Пример 2: Ограничение экспорта

```python
# В analysis.py
@router.get("/export/excel")
async def export_to_excel(
    vacancy_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = SubscriptionService(db)

    # Проверяем лимит экспорта
    can_export, msg = await service.check_can_export(current_user.id)
    if not can_export:
        raise HTTPException(status_code=429, detail=msg)

    # Экспортируем
    file = create_excel_report(vacancy_id)

    # Увеличиваем счётчик
    await service.increment_export_usage(
        user_id=current_user.id,
        vacancy_id=vacancy_id
    )

    return FileResponse(file)
```

### Пример 3: Ограничение вакансий

```python
# В vacancies.py
@router.post("/")
async def create_vacancy(
    vacancy_data: VacancyCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = SubscriptionService(db)

    # Проверяем лимит вакансий
    can_create, msg = await service.check_vacancy_limit(current_user.id)
    if not can_create:
        raise HTTPException(status_code=429, detail=msg)

    # Создаём вакансию
    vacancy = Vacancy(**vacancy_data.dict(), user_id=current_user.id)
    db.add(vacancy)
    db.commit()

    return vacancy
```

---

## 🎯 Дальнейшее развитие

### Планируется добавить:

1. **Email уведомления**
   - За 7 дней до окончания подписки
   - При достижении 80% лимита
   - При блокировке функций

2. **Промокоды и скидки**
   - Таблица promo_codes
   - Скидки для новых пользователей
   - Реферальная программа

3. **Командные подписки**
   - Несколько пользователей на одной подписке
   - Управление правами доступа
   - Распределение лимитов

4. **Детальная аналитика**
   - Dashboard использования ресурсов
   - Прогнозирование расхода лимитов
   - Рекомендации по оптимизации

5. **A/B тестирование тарифов**
   - Экспериментальные цены
   - Анализ конверсии
   - Оптимизация предложений

---

**Документация обновлена:** 13 октября 2025
**Версия:** 1.0
