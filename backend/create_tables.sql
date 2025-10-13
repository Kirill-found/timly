-- Создание схемы базы данных Timly
-- Основанно на SQLAlchemy моделях из /app/models/

-- Создание расширения для UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(10) DEFAULT 'user' NOT NULL CHECK (role IN ('user', 'admin')),
    company_name VARCHAR(255),
    encrypted_hh_token TEXT,
    token_verified BOOLEAN DEFAULT FALSE NOT NULL,
    token_verified_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    last_login_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_users_email ON users(email);
CREATE INDEX IF NOT EXISTS ix_users_token_verified ON users(token_verified);

-- Create vacancies table
CREATE TABLE IF NOT EXISTS vacancies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    hh_vacancy_id VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    key_skills JSONB DEFAULT '[]'::jsonb NOT NULL,
    salary_from INTEGER,
    salary_to INTEGER,
    currency VARCHAR(3) DEFAULT 'RUB',
    experience VARCHAR(50),
    employment VARCHAR(50),
    schedule VARCHAR(50),
    area VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    published_at TIMESTAMP,
    applications_count INTEGER DEFAULT 0 NOT NULL,
    new_applications_count INTEGER DEFAULT 0 NOT NULL,
    last_synced_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_vacancies_user_id ON vacancies(user_id);
CREATE INDEX IF NOT EXISTS ix_vacancies_hh_vacancy_id ON vacancies(hh_vacancy_id);
CREATE INDEX IF NOT EXISTS ix_vacancies_is_active ON vacancies(is_active);

-- Create applications table
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
    is_duplicate BOOLEAN DEFAULT FALSE NOT NULL,
    analyzed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_applications_vacancy_id ON applications(vacancy_id);
CREATE INDEX IF NOT EXISTS ix_applications_hh_application_id ON applications(hh_application_id);
CREATE INDEX IF NOT EXISTS ix_applications_hh_resume_id ON applications(hh_resume_id);
CREATE INDEX IF NOT EXISTS ix_applications_candidate_name ON applications(candidate_name);
CREATE INDEX IF NOT EXISTS ix_applications_resume_hash ON applications(resume_hash);
CREATE INDEX IF NOT EXISTS ix_applications_is_duplicate ON applications(is_duplicate);

-- Create analysis_results table
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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_analysis_results_application_id ON analysis_results(application_id);
CREATE INDEX IF NOT EXISTS ix_analysis_results_score ON analysis_results(score);
CREATE INDEX IF NOT EXISTS ix_analysis_results_recommendation ON analysis_results(recommendation);

-- Create sync_jobs table
CREATE TABLE IF NOT EXISTS sync_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'pending' NOT NULL,
    vacancies_synced INTEGER DEFAULT 0 NOT NULL,
    applications_synced INTEGER DEFAULT 0 NOT NULL,
    errors JSONB DEFAULT '[]'::jsonb NOT NULL,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_sync_jobs_user_id ON sync_jobs(user_id);
CREATE INDEX IF NOT EXISTS ix_sync_jobs_status ON sync_jobs(status);

-- Создание версии для alembic
CREATE TABLE IF NOT EXISTS alembic_version (
    version_num VARCHAR(32) NOT NULL,
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Вставляем версию миграции
INSERT INTO alembic_version (version_num) VALUES ('001') ON CONFLICT (version_num) DO NOTHING;