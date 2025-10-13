-- Инициализация базы данных Timly
-- Создание расширений и начальных данных

-- Включение необходимых расширений PostgreSQL
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; -- для полнотекстового поиска

-- Создание enum типов
CREATE TYPE user_role AS ENUM ('user', 'admin');
CREATE TYPE recommendation_type AS ENUM ('hire', 'interview', 'maybe', 'reject');
CREATE TYPE job_status AS ENUM ('pending', 'processing', 'completed', 'failed');

-- Создание функции для автоматического обновления updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Таблица пользователей
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role user_role DEFAULT 'user',
    company_name VARCHAR(255),
    encrypted_hh_token TEXT,
    token_verified BOOLEAN DEFAULT FALSE,
    token_verified_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    last_login_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица вакансий
CREATE TABLE IF NOT EXISTS vacancies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    hh_vacancy_id VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    key_skills JSONB DEFAULT '[]'::jsonb,
    salary_from INTEGER,
    salary_to INTEGER,
    currency VARCHAR(3),
    experience VARCHAR(50),
    employment VARCHAR(50),
    schedule VARCHAR(50),
    area VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    published_at TIMESTAMP,
    applications_count INTEGER DEFAULT 0,
    new_applications_count INTEGER DEFAULT 0,
    last_synced_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, hh_vacancy_id)
);

-- Таблица откликов
CREATE TABLE IF NOT EXISTS applications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vacancy_id UUID NOT NULL REFERENCES vacancies(id) ON DELETE CASCADE,
    hh_application_id VARCHAR(50) UNIQUE NOT NULL,
    hh_resume_id VARCHAR(50),
    hh_negotiation_id VARCHAR(50),
    candidate_name VARCHAR(255),
    candidate_email VARCHAR(255),
    candidate_phone VARCHAR(50),
    resume_url VARCHAR(500),
    resume_data JSONB,
    resume_hash VARCHAR(64),
    is_duplicate BOOLEAN DEFAULT FALSE,
    analyzed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица результатов анализа
CREATE TABLE IF NOT EXISTS analysis_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    application_id UUID UNIQUE NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    score INTEGER CHECK (score >= 0 AND score <= 100),
    skills_match INTEGER CHECK (skills_match >= 0 AND skills_match <= 100),
    experience_match INTEGER CHECK (experience_match >= 0 AND experience_match <= 100),
    salary_match VARCHAR(20),
    strengths TEXT[],
    weaknesses TEXT[],
    red_flags TEXT[],
    recommendation VARCHAR(20),
    reasoning TEXT,
    ai_model VARCHAR(50),
    ai_tokens_used INTEGER,
    ai_cost_cents INTEGER,
    processing_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица задач синхронизации
CREATE TABLE IF NOT EXISTS sync_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'pending',
    vacancies_synced INTEGER DEFAULT 0,
    applications_synced INTEGER DEFAULT 0,
    errors JSONB DEFAULT '[]'::jsonb,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создание индексов для производительности
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_token_verified ON users(token_verified) WHERE token_verified = TRUE;

CREATE INDEX IF NOT EXISTS idx_vacancies_user_id ON vacancies(user_id);
CREATE INDEX IF NOT EXISTS idx_vacancies_hh_id ON vacancies(hh_vacancy_id);
CREATE INDEX IF NOT EXISTS idx_vacancies_active ON vacancies(is_active) WHERE is_active = TRUE;

CREATE INDEX IF NOT EXISTS idx_applications_vacancy_id ON applications(vacancy_id);
CREATE INDEX IF NOT EXISTS idx_applications_hash ON applications(resume_hash);
CREATE INDEX IF NOT EXISTS idx_applications_duplicate ON applications(is_duplicate) WHERE is_duplicate = FALSE;

CREATE INDEX IF NOT EXISTS idx_analysis_score ON analysis_results(score DESC);
CREATE INDEX IF NOT EXISTS idx_analysis_recommendation ON analysis_results(recommendation);

CREATE INDEX IF NOT EXISTS idx_sync_jobs_user_id ON sync_jobs(user_id);
CREATE INDEX IF NOT EXISTS idx_sync_jobs_status ON sync_jobs(status);

-- Индекс для полнотекстового поиска по именам кандидатов
CREATE INDEX IF NOT EXISTS idx_applications_name_trgm ON applications USING gin (candidate_name gin_trgm_ops);

-- Создание триггеров для автоматического обновления updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_vacancies_updated_at BEFORE UPDATE ON vacancies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Демонстрационные данные (опционально для development)
-- INSERT INTO users (email, password_hash, role, company_name) VALUES
-- ('demo@timly.ru', '$2b$12$demo_password_hash', 'user', 'Демо Компания')
-- ON CONFLICT (email) DO NOTHING;

-- Сообщение об успешной инициализации
DO $$
BEGIN
    RAISE NOTICE 'Timly database initialized successfully!';
END $$;