# Timly - Technical Specification

**Version:** 2.0
**Stack:** Python/FastAPI + React/TypeScript
**Last Updated:** December 2024

---

## Architecture

**Pattern:** Modular Monolith (microservices-ready)
```
┌─────────────────────────────────────┐
│         React Frontend              │
│   TypeScript + Tailwind + shadcn   │
└─────────────┬───────────────────────┘
              │ HTTPS/REST
              ↓
┌─────────────────────────────────────┐
│         FastAPI Backend             │
│   Python 3.11 + SQLAlchemy         │
├─────────────────────────────────────┤
│  Auth │ HH.ru │ AI │ Export        │
└──────┬──────────────┬───────────────┘
       │              │
       ↓              ↓
┌──────────┐   ┌──────────┐
│PostgreSQL│   │  Redis   │
└──────────┘   └──────────┘
       ↓              ↓
┌─────────────────────────────────────┐
│      External Services              │
│   HH.ru API  │  OpenAI API         │
└─────────────────────────────────────┘
```

---

## Tech Stack (STRICT - No Changes)

### Backend
```python
Python: 3.11+
Framework: FastAPI 0.104+
Database: PostgreSQL 15
ORM: SQLAlchemy 2.0.23 (async)
Cache/Queue: Redis 7.2+ with RQ
Auth: JWT (python-jose)
Encryption: Fernet (cryptography)
HTTP Client: httpx (async)
```

### Frontend
```javascript
Framework: React 18.2 + TypeScript 5.0 (strict mode)
Styling: Tailwind CSS 3.4.0
Components: shadcn/ui (Radix primitives)
State: Context API only (NO Redux)
HTTP: Axios 1.6.2
Build: Vite 5.0
```

### AI
```
Provider: OpenAI
Model: GPT-4o-mini
Cost: $0.15/$0.60 per 1M tokens
Target: <5₽ per analysis
```

### Infrastructure
```
Development: Docker + Docker Compose
Production: Railway.app
Database: Railway PostgreSQL
Frontend: Vercel
Monitoring: Sentry (free tier)
```

## Project Structure

```
timly/
├── backend/
│   ├── app/
│   │   ├── models/          # SQLAlchemy models ONLY
│   │   ├── schemas/         # Pydantic schemas ONLY
│   │   ├── api/             # FastAPI routes ONLY
│   │   ├── services/        # Business logic ONLY
│   │   └── workers/         # Background jobs ONLY
│   ├── tests/
│   ├── alembic/             # Database migrations
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── hooks/           # Custom hooks
│   │   ├── lib/             # Utils
│   │   └── pages/           # Page components
│   ├── package.json
│   └── Dockerfile
│
└── docs/
    ├── PRODUCT.md           # This is WHAT to build
    ├── TECHNICAL.md         # This is HOW to build
    └── AGENTS.md            # AI agent prompts
```

## Database Schema

```sql
-- Users with encrypted HH.ru tokens
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    company_name VARCHAR(255),
    encrypted_hh_token TEXT,              -- MUST use Fernet
    token_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Vacancies from HH.ru
CREATE TABLE vacancies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    hh_vacancy_id VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    key_skills JSONB DEFAULT '[]'::jsonb,
    salary_from INTEGER,
    salary_to INTEGER,
    applications_count INTEGER DEFAULT 0,
    last_synced_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, hh_vacancy_id)
);

-- Applications with deduplication
CREATE TABLE applications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vacancy_id UUID NOT NULL REFERENCES vacancies(id) ON DELETE CASCADE,
    hh_application_id VARCHAR(50) UNIQUE NOT NULL,
    hh_resume_id VARCHAR(50),
    candidate_name VARCHAR(255),
    resume_data JSONB,
    resume_hash VARCHAR(64),              -- MD5 for deduplication
    created_at TIMESTAMP DEFAULT NOW()
);

-- AI analysis results (separate for performance)
CREATE TABLE analysis_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id UUID UNIQUE NOT NULL REFERENCES applications(id),
    score INTEGER CHECK (score >= 0 AND score <= 100),
    skills_match INTEGER CHECK (skills_match >= 0 AND skills_match <= 100),
    experience_match INTEGER CHECK (experience_match >= 0 AND experience_match <= 100),
    recommendation VARCHAR(20),           -- hire|interview|maybe|reject
    reasoning TEXT,
    ai_cost_rub DECIMAL(6,2),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_vacancies_user ON vacancies(user_id);
CREATE INDEX idx_applications_vacancy ON applications(vacancy_id);
CREATE INDEX idx_applications_hash ON applications(resume_hash);
CREATE INDEX idx_analysis_score ON analysis_results(score DESC);
```

## API Endpoints

### Authentication
```
POST   /api/auth/register
POST   /api/auth/login
POST   /api/auth/refresh
```

### Settings
```
POST   /api/settings/hh-token
GET    /api/settings/profile
```

### HH.ru Integration
```
GET    /api/hh/vacancies
POST   /api/hh/sync
GET    /api/hh/vacancies/{id}/applications
```

### Analysis
```
POST   /api/analysis/vacancy/{id}
GET    /api/analysis/status/{job_id}
GET    /api/analysis/results/{vacancy_id}
POST   /api/analysis/export/excel
```

### Response Format (ALL endpoints)
```json
{
  "data": {...},
  "error": null,
  "meta": {
    "timestamp": "2024-12-01T00:00:00Z"
  }
}
```

## AI Analysis Specification

### Input
```json
{
  "vacancy": {
    "title": str,
    "key_skills": List[str],
    "experience": str,
    "salary_from": int,
    "salary_to": int
  },
  "resume": {
    "title": str,
    "skills": List[str],
    "total_experience_months": int,
    "salary_expectation": int,
    "last_positions": List[dict]
  }
}
```

### Processing
```
Model: gpt-4o-mini
Temperature: 0.3 (consistency)
Max tokens: 500
Format: json_object
```

### Output Schema
```json
{
  "score": 85,
  "skills_match": 90,
  "experience_match": 80,
  "education_match": 85,
  "salary_match": "within_range",
  "strengths": ["5 years Python", "FastAPI expert", "Team lead"],
  "weaknesses": ["No PostgreSQL", "Remote only"],
  "red_flags": [],
  "recommendation": "hire",
  "reasoning": "Excellent technical match, 5+ years experience"
}
```

### Constraints
```
Cost: <5₽ per analysis (with caching)
Cache: 24 hours (Redis)
Fallback: Rule-based if AI fails
Batch: Maximum 5 resumes per API call
```

## Security Requirements

### CRITICAL - Never Compromise:

**Token Encryption**
- ALL HH.ru tokens → Fernet encryption before DB storage
- Generate key: `Fernet.generate_key()`
- Store in .env as `ENCRYPTION_KEY`

**Authentication**
- JWT tokens with 24-hour expiration
- Password hashing with bcrypt
- No session storage (Context API only)

**Data Protection**
- HTTPS only in production
- CORS restricted to frontend domain
- Rate limiting: 100 requests/minute
- SQL injection prevention (parameterized queries)

**GDPR/152-ФЗ Compliance**
- User consent for data processing
- Right to delete all user data
- Data retention: 90 days max

## Error Handling

### HTTP Status Codes
```
200 - Success
201 - Created
400 - Bad Request (validation error)
401 - Unauthorized (invalid/expired token)
403 - Forbidden (insufficient permissions)
404 - Not Found
429 - Rate Limit Exceeded
500 - Internal Server Error
503 - Service Unavailable
```

### Error Response Format
```json
{
  "error": {
    "code": "INVALID_HH_TOKEN",
    "message": "HH.ru token is invalid or expired",
    "details": {
      "field": "hh_token",
      "reason": "Token validation failed"
    }
  }
}
```

## Environment Variables

```bash
# Application
APP_ENV=production
DEBUG=false
SECRET_KEY=<32+ character random string>
ENCRYPTION_KEY=<Fernet key>

# Database
DATABASE_URL=postgresql://user:pass@host:5432/timly

# Redis
REDIS_URL=redis://localhost:6379/0

# External APIs
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

# Monitoring
SENTRY_DSN=https://...@sentry.io/...

# CORS
CORS_ORIGINS=https://timly.ru
```

## Testing Requirements

### Minimum Coverage: 80%

**Unit Tests**
- All service layer functions
- Token encryption/decryption
- AI response validation
- Deduplication logic

**Integration Tests**
- API endpoints (all)
- HH.ru API integration
- OpenAI API integration
- Database operations

**E2E Tests**
- Complete user flow: Register → Token → Sync → Analyze → Export
- Mobile responsiveness
- Error scenarios

## Deployment

### Local Development
```bash
docker-compose up -d
cd backend && alembic upgrade head
cd frontend && npm run dev
```

### Production (Railway)
```bash
git push origin main
# Auto-deploys via GitHub Actions
# Check: https://timly.ru
```

## Critical Constraints

### NEVER:
- Use localStorage/sessionStorage (not supported in Claude.ai artifacts)
- Store unencrypted tokens
- Process >5 resumes in single AI batch
- Deviate from specified tech stack
- Skip database migrations
- Commit secrets to Git

### ALWAYS:
- Encrypt HH.ru tokens with Fernet
- Use async/await for I/O operations
- Add database indexes for queries
- Cache AI results for 24 hours
- Log errors with Sentry
- Test before deploying