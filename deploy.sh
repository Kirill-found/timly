#!/bin/bash

# TIMLY Deployment Script for Timeweb Cloud
# Автоматический деплой на сервер

set -e

echo "🚀 Starting TIMLY deployment..."

# Проверка .env.prod
if [ ! -f .env.prod ]; then
    echo "❌ Файл .env.prod не найден!"
    echo "Скопируйте .env.production в .env.prod и заполните реальными значениями"
    exit 1
fi

# Остановка старых контейнеров
echo "🛑 Stopping old containers..."
docker-compose -f docker-compose.prod.yml down || true

# Удаление старых образов
echo "🗑️  Removing old images..."
docker-compose -f docker-compose.prod.yml rm -f || true

# Скачивание последних изменений из Git
echo "📥 Pulling latest code from GitHub..."
git pull origin main

# Сборка новых образов
echo "🔨 Building new images..."
docker-compose -f docker-compose.prod.yml --env-file .env.prod build --no-cache

# Запуск контейнеров
echo "▶️  Starting containers..."
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d

# Ожидание запуска
echo "⏳ Waiting for services to start..."
sleep 10

# Применение миграций базы данных
echo "🗄️  Running database migrations..."
docker-compose -f docker-compose.prod.yml exec -T backend alembic upgrade head || echo "⚠️  Migrations failed or not needed"

# Проверка статуса
echo "✅ Checking services status..."
docker-compose -f docker-compose.prod.yml ps

echo ""
echo "🎉 Deployment complete!"
echo "Backend: http://ваш-ip:8000"
echo "Frontend: http://ваш-ip"
echo ""
echo "Проверьте логи:"
echo "  docker-compose -f docker-compose.prod.yml logs -f"
