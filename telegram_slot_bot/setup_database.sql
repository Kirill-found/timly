-- Скрипт для создания базы данных и пользователя
-- Запустите этот файл в pgAdmin или через psql

-- Создание базы данных
CREATE DATABASE slot_bot_db;

-- Создание пользователя
CREATE USER slot_bot_user WITH PASSWORD 'myslotbot123';

-- Выдача всех прав на базу данных
GRANT ALL PRIVILEGES ON DATABASE slot_bot_db TO slot_bot_user;

-- Подключение к новой базе данных (выполните отдельно после создания базы)
\c slot_bot_db

-- Выдача прав на схему public
GRANT ALL ON SCHEMA public TO slot_bot_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO slot_bot_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO slot_bot_user;

-- Готово!
SELECT 'Database setup completed successfully!' as result;
