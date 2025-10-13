# Timly - Product Specification

**Version:** 2.0
**Last Updated:** December 2024
**Status:** Active Development

---

## What We're Building

AI-powered resume screening platform for Russian HR market. Automatically analyzes job applications from HH.ru, reducing screening time from 10 hours to 10 minutes.

### Core Value Proposition
"Turn 100 resumes into 10 best candidates in 5 minutes"

---

## Target Users

### Primary: HR Managers (SMB)
- Companies: 50-500 employees
- Vacancies: 10-50 per month
- Applications: 100-500 per vacancy
- Pain: 60-70% time wasted on manual screening

### Secondary: Startups without HR
- <50 employees
- CEO/CTO hire themselves
- 1-5 vacancies per month
- Pain: No expertise in resume evaluation

---

## MVP Features (Month 1)

**Must Have (P0):**
1. User registration & authentication (JWT, 24h tokens)
2. HH.ru token integration (save encrypted, validate)
3. Vacancy synchronization (manual trigger)
4. AI resume analysis (0-100 scoring, GPT-4o-mini)
5. Results table (sortable, filterable)
6. Excel export

**Success Criteria:**
- Time to first value: <5 minutes
- Analysis time: <2 seconds per resume
- Cost per analysis: <5₽
- User can complete full flow without help

---

## User Flow
Register → Email + Password
Add HH.ru Token → Paste API token from HH.ru account
Sync Vacancies → Click "Sync", see list of active vacancies
Analyze → Click "Analyze" on vacancy, wait 30-60 seconds
Review Results → See candidates sorted by score (0-100)
Export → Download Excel with top candidates

---

## Business Metrics

### Targets
- Month 1: 10 beta users, 1,000 analyses
- Month 3: 100 paying customers, 400K₽ MRR
- Month 6: 500 customers, 2M₽ MRR

### KPIs
- Trial → Paid conversion: >30%
- Customer Acquisition Cost: <2,000₽
- Monthly churn: <5%
- Net Promoter Score: >50

---

## Pricing

| Tier | Price | Analyses | Users |
|------|-------|----------|-------|
| Starter | 2,000₽/mo | 100 | 1 |
| Professional | 5,000₽/mo | 500 | 3 |
| Enterprise | 15,000₽/mo | 2,000 | Unlimited |

---

## Out of Scope (Not MVP)

- Automatic sync (every 30 min) - Version 1.1
- Team accounts - Version 1.1
- API access - Version 1.2
- Telegram bot - Version 1.2
- Custom scoring templates - Version 2.0
- Mobile apps - Future

---

## User Stories

**US-001: HH.ru Integration**
As an HR manager
I want to connect my HH.ru account with one click
So that I don't have to manually enter vacancy data
Acceptance:
- Can paste API token
- System validates token
- See list of my vacancies within 30 seconds

**US-002: Automatic Analysis**
As an HR manager
I want AI to analyze all applications automatically
So that I see best candidates first
Acceptance:
- Click one button to start analysis
- See progress indicator
- Results appear sorted by score (highest first)
- Analysis completes in <2 minutes for 100 resumes

**US-003: Export Results**
As an HR manager
I want to export results to Excel
So that I can share with colleagues
Acceptance:
- Click "Export" button
- Download Excel file immediately
- File contains: Name, Score, Skills, Recommendation
- Russian characters display correctly

---

## Success Definition

MVP is successful if:
- 10 beta users complete full flow without breaking
- Average analysis cost <5₽ per resume
- Users save >8 hours per week (self-reported)
- NPS >50 after 2 weeks of use