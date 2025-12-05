# Руководство по предотвращению проблем в Production

## 1. Проблемы с кодом (баги)

### Что делать:

#### Тестирование
```bash
# Создайте файл backend/tests/test_subscriptions.py
```

**Обязательные тесты:**
- ✅ Тест на безлимитные планы (`max_analyses_per_month = -1`)
- ✅ Тест на превышение лимитов
- ✅ Тест на сброс месячных счетчиков
- ✅ Тест на разные типы подписок

#### Code Review перед деплоем
- Проверяйте edge cases (граничные случаи)
- Тестируйте с разными типами подписок
- Проверяйте что `-1` корректно обрабатывается как "безлимит"

#### Мониторинг после деплоя
```bash
# Следите за ошибками в логах
docker-compose logs -f backend | grep ERROR

# Проверяйте метрики
- Количество успешных/неудачных анализов
- HTTP 500 ошибки
```

---

## 2. Проблемы с базой данных

### ⚠️ НИКОГДА не делайте в production:

1. **Множественные операции INSERT/DELETE на одной записи**
   ```sql
   -- ❌ ПЛОХО
   INSERT INTO users ...;
   DELETE FROM users WHERE email = '...';
   INSERT INTO users ... ON CONFLICT ...;
   ```

2. **Ручные операции с индексами во время работы**
   ```sql
   -- ❌ ОПАСНО без maintenance mode
   REINDEX TABLE users;
   DROP TABLE users;
   ```

3. **Операции без транзакций**
   ```sql
   -- ❌ ПЛОХО
   DELETE FROM users WHERE email = '...';
   INSERT INTO users ...;

   -- ✅ ХОРОШО
   BEGIN;
   DELETE FROM users WHERE email = '...';
   INSERT INTO users ...;
   COMMIT;
   ```

### ✅ Правильный подход:

#### 1. Используйте миграции (Alembic)
```bash
# Создайте миграцию
cd backend
alembic revision -m "fix_user_subscription"

# Примените в production
alembic upgrade head
```

#### 2. Резервное копирование перед изменениями
```bash
# Backup базы
docker exec timly_postgres_1 pg_dump -U timly_user timly_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Восстановление при необходимости
docker exec -i timly_postgres_1 psql -U timly_user timly_db < backup_20251105_120000.sql
```

#### 3. Используйте API вместо прямых SQL запросов
```bash
# ✅ Создание пользователя через API
curl -X POST http://localhost:8000/api/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email": "user@example.com", "password": "..."}'

# ❌ Вместо прямого INSERT в БД
```

---

## 3. Система бэкапов

### Автоматические бэкапы

Создайте файл `backup_db.sh`:
```bash
#!/bin/bash
BACKUP_DIR="/root/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/timly_db_$DATE.sql"

mkdir -p $BACKUP_DIR

# Создание бэкапа
docker exec timly_postgres_1 pg_dump -U timly_user timly_db > $BACKUP_FILE

# Сжатие
gzip $BACKUP_FILE

# Удаление старых бэкапов (старше 7 дней)
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete

echo "Backup created: ${BACKUP_FILE}.gz"
```

Добавьте в crontab:
```bash
# Ежедневный бэкап в 3:00 AM
0 3 * * * /root/backup_db.sh >> /var/log/backup.log 2>&1

# Еженедельный полный бэкап (воскресенье 2:00 AM)
0 2 * * 0 /root/backup_db.sh
```

---

## 4. Мониторинг здоровья БД

### Ежедневные проверки

```bash
# 1. Проверка целостности
docker exec timly_postgres_1 psql -U timly_user -d timly_db -c "
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
"

# 2. Проверка индексов
docker exec timly_postgres_1 psql -U timly_user -d timly_db -c "
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY idx_scan;
"

# 3. Проверка dead tuples (мусор после UPDATE/DELETE)
docker exec timly_postgres_1 psql -U timly_user -d timly_db -c "
SELECT
    schemaname,
    tablename,
    n_dead_tup,
    last_autovacuum
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
ORDER BY n_dead_tup DESC;
"
```

### Еженедельное обслуживание

```bash
# VACUUM ANALYZE - освобождает место и обновляет статистику
docker exec timly_postgres_1 psql -U timly_user -d timly_db -c "VACUUM ANALYZE;"

# Проверка и восстановление индексов (только если есть проблемы)
docker exec timly_postgres_1 psql -U timly_user -d timly_db -c "REINDEX DATABASE timly_db;"
```

---

## 5. Места на диске

### Текущая ситуация
```
Диск: 30GB
Использовано: 25GB (83%)
Свободно: 5GB
```

⚠️ **Критично!** При 90%+ заполнения PostgreSQL может работать некорректно.

### Что делать:

#### 1. Очистка логов Docker
```bash
# Проверить размер логов
docker ps -q | xargs docker inspect --format='{{.LogPath}}' | xargs ls -lh

# Очистить логи
truncate -s 0 $(docker inspect --format='{{.LogPath}}' timly_backend_1)
truncate -s 0 $(docker inspect --format='{{.LogPath}}' timly_postgres_1)

# Настроить лимит логов в docker-compose.prod.yml
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

#### 2. Очистка Docker
```bash
# Удалить неиспользуемые образы
docker image prune -a

# Удалить неиспользуемые volumes (ОСТОРОЖНО!)
docker volume prune

# Очистить build cache
docker builder prune
```

#### 3. Мониторинг места
```bash
# Скрипт мониторинга
cat > /root/check_disk.sh << 'EOF'
#!/bin/bash
USED=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $USED -gt 85 ]; then
    echo "WARNING: Disk usage is ${USED}%"
    # Можно добавить отправку уведомления
fi
EOF

chmod +x /root/check_disk.sh

# Добавить в crontab (каждый час)
0 * * * * /root/check_disk.sh
```

---

## 6. Правила работы с Production

### ✅ МОЖНО:

1. **Чтение данных**
   ```sql
   SELECT * FROM users WHERE email = '...';
   ```

2. **Обновление через API**
   ```bash
   curl -X PATCH /api/admin/users/...
   ```

3. **Миграции через Alembic**
   ```bash
   alembic upgrade head
   ```

4. **Мониторинг**
   ```bash
   docker-compose logs -f
   docker stats
   ```

### ❌ НЕЛЬЗЯ:

1. **Прямое изменение данных в БД без бэкапа**
2. **DROP TABLE/TRUNCATE без maintenance mode**
3. **Множественные перезапуски подряд (> 3 раз в час)**
4. **Изменение структуры БД без миграций**
5. **Эксперименты с SQL в production**

---

## 7. Процедура экстренного восстановления

### Если база повреждена:

```bash
# 1. Остановить приложение
docker-compose stop backend

# 2. Создать бэкап текущего состояния (даже если повреждена)
docker exec timly_postgres_1 pg_dumpall -U timly_user > emergency_backup.sql

# 3. Проверить целостность
docker exec timly_postgres_1 psql -U timly_user -d timly_db -c "
SELECT pg_database.datname, pg_size_pretty(pg_database_size(pg_database.datname))
FROM pg_database;
"

# 4. VACUUM FULL (может занять время)
docker exec timly_postgres_1 psql -U timly_user -d timly_db -c "VACUUM FULL;"

# 5. REINDEX
docker exec timly_postgres_1 psql -U timly_user -d timly_db -c "REINDEX DATABASE timly_db;"

# 6. Перезапустить всё
docker-compose restart postgres backend

# 7. Проверить работоспособность
curl http://localhost:8000/health
```

### Если восстановление не помогло:

```bash
# Восстановить из последнего бэкапа
docker-compose down
docker volume rm timly_postgres_data
docker-compose up -d postgres

# Подождать запуска PostgreSQL
sleep 10

# Восстановить данные
docker exec -i timly_postgres_1 psql -U timly_user timly_db < /root/backups/timly_db_YYYYMMDD_HHMMSS.sql

docker-compose up -d
```

---

## 8. Checklist перед деплоем

- [ ] Все тесты проходят локально
- [ ] Создан бэкап production базы
- [ ] Есть план отката (rollback)
- [ ] Проверена миграция на staging
- [ ] Свободно > 15% места на диске
- [ ] Нет критичных ошибок в логах
- [ ] Подготовлено сообщение для пользователей (если будет downtime)

---

## 9. Контакты при проблемах

1. **Проверить логи**
   ```bash
   docker-compose logs --tail=100 backend
   docker-compose logs --tail=100 postgres
   ```

2. **Проверить здоровье сервисов**
   ```bash
   docker-compose ps
   curl http://localhost:8000/health
   ```

3. **Откатить изменения**
   ```bash
   git log --oneline -10
   git revert <commit-hash>
   docker-compose up -d --build
   ```
