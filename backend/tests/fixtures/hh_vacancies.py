"""
Mock данные вакансий для тестирования HH.ru интеграции
Реалистичные данные российского IT рынка
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any
import uuid

# Базовые тестовые вакансии
MOCK_VACANCIES: List[Dict[str, Any]] = [
    {
        "id": "50001",
        "name": "Python Backend разработчик (Middle/Senior)",
        "area": {
            "id": "1",
            "name": "Москва",
            "url": "https://api.hh.ru/areas/1"
        },
        "salary": {
            "from": 180000,
            "to": 300000,
            "currency": "RUR",
            "gross": False
        },
        "type": {
            "id": "open",
            "name": "Открытая"
        },
        "address": {
            "city": "Москва",
            "street": "Тверская улица",
            "building": "12",
            "description": "м. Тверская",
            "lat": 55.757814,
            "lng": 37.614914,
            "raw": "Москва, Тверская улица, 12",
            "metro": {
                "station_name": "Тверская",
                "line": "Сокольническая",
                "station_id": "6.41",
                "lat": 55.757814,
                "lng": 37.614914
            }
        },
        "response_letter_required": False,
        "experience": {
            "id": "between3And6",
            "name": "От 3 до 6 лет"
        },
        "schedule": {
            "id": "fullDay",
            "name": "Полный день"
        },
        "employment": {
            "id": "full",
            "name": "Полная занятость"
        },
        "department": None,
        "contacts": None,
        "description": """<p><strong>Компания:</strong> FinTech стартап в области банковских технологий</p>
<p><strong>О проекте:</strong> Разрабатываем современную платформу для корпоративного банкинга</p>

<p><strong>Что нужно делать:</strong></p>
<ul>
<li>Разработка и поддержка backend сервисов на Python/Django</li>
<li>Проектирование REST API</li>
<li>Работа с PostgreSQL, Redis</li>
<li>Интеграция с внешними API банков и платежных систем</li>
<li>Код ревью, менторинг джуниоров</li>
</ul>

<p><strong>Требования:</strong></p>
<ul>
<li>Опыт разработки на Python 3+ лет</li>
<li>Django/FastAPI, PostgreSQL</li>
<li>Знание принципов REST API</li>
<li>Опыт работы с Git, Docker</li>
<li>Понимание принципов SOLID, DRY</li>
</ul>

<p><strong>Будет плюсом:</strong></p>
<ul>
<li>Опыт в финтехе/банках</li>
<li>Kubernetes, CI/CD</li>
<li>Знание финансовых протоколов</li>
</ul>""",
        "branded_description": None,
        "vacancy_constructor_template": None,
        "key_skills": [
            {"name": "Python"},
            {"name": "Django"},
            {"name": "PostgreSQL"},
            {"name": "REST API"},
            {"name": "Docker"},
            {"name": "Git"},
            {"name": "Redis"},
            {"name": "FastAPI"}
        ],
        "accept_handicapped": False,
        "accept_kids": False,
        "archived": False,
        "premium": True,
        "response_url": None,
        "specializations": [
            {
                "profarea_id": "96",
                "profarea_name": "Информационные технологии, интернет, телеком",
                "id": "96.112",
                "name": "Разработчик"
            }
        ],
        "professional_roles": [
            {
                "id": "96",
                "name": "Программист, разработчик"
            }
        ],
        "accept_incomplete_resumes": False,
        "employer": {
            "id": "12345",
            "name": "FinTech Solutions",
            "url": "https://api.hh.ru/employers/12345",
            "alternate_url": "https://hh.ru/employer/12345",
            "logo_urls": {
                "original": "https://img.hhcdn.ru/employer-logo/1234567.png",
                "240": "https://img.hhcdn.ru/employer-logo/1234567.png",
                "90": "https://img.hhcdn.ru/employer-logo/1234567.png"
            },
            "vacancies_url": "https://api.hh.ru/vacancies?employer_id=12345",
            "trusted": True
        },
        "published_at": (datetime.now() - timedelta(days=3)).isoformat() + "+03:00",
        "created_at": (datetime.now() - timedelta(days=3)).isoformat() + "+03:00",
        "has_test": False,
        "response_notifications": False,
        "test": None,
        "alternate_url": "https://hh.ru/vacancy/50001",
        "apply_alternate_url": "https://hh.ru/applicant/vacancy_response?vacancyId=50001",
        "insider_interview": None,
        "url": "https://api.hh.ru/vacancies/50001",
        "adv_response_url": None,
        "sort_point_distance": None,
        "published_at_timestamp": int((datetime.now() - timedelta(days=3)).timestamp()),
        "counters": {
            "responses": 47,
            "unread_responses": 12,
            "invitations": 8,
            "views": 156
        },
        "allow_messages": True,
        "working_days": [],
        "working_time_intervals": [],
        "working_time_modes": [],
        "accept_temporary": False,
        "manager": {
            "id": "67890"
        }
    },

    {
        "id": "50002",
        "name": "Frontend разработчик React/TypeScript",
        "area": {
            "id": "2",
            "name": "Санкт-Петербург",
            "url": "https://api.hh.ru/areas/2"
        },
        "salary": {
            "from": 120000,
            "to": 220000,
            "currency": "RUR",
            "gross": False
        },
        "type": {
            "id": "open",
            "name": "Открытая"
        },
        "address": {
            "city": "Санкт-Петербург",
            "street": "Невский проспект",
            "building": "28",
            "description": "м. Невский проспект",
            "lat": 59.934280,
            "lng": 30.335099,
            "raw": "Санкт-Петербург, Невский проспект, 28",
            "metro": {
                "station_name": "Невский проспект",
                "line": "Сокольническая",
                "station_id": "2.17",
                "lat": 59.934280,
                "lng": 30.335099
            }
        },
        "response_letter_required": True,
        "experience": {
            "id": "between1And3",
            "name": "От 1 года до 3 лет"
        },
        "schedule": {
            "id": "remote",
            "name": "Удаленная работа"
        },
        "employment": {
            "id": "full",
            "name": "Полная занятость"
        },
        "department": None,
        "contacts": None,
        "description": """<p><strong>Компания:</strong> Продуктовая IT-компания, разработка SaaS решений</p>
<p><strong>О проекте:</strong> CRM система для малого и среднего бизнеса</p>

<p><strong>Задачи:</strong></p>
<ul>
<li>Разработка пользовательских интерфейсов на React/TypeScript</li>
<li>Интеграция с REST API</li>
<li>Оптимизация производительности приложений</li>
<li>Покрытие кода тестами (Jest, RTL)</li>
<li>Code review, работа в команде</li>
</ul>

<p><strong>Требования:</strong></p>
<ul>
<li>Опыт разработки на React 2+ года</li>
<li>TypeScript, HTML5, CSS3/SCSS</li>
<li>Опыт с Redux/Zustand</li>
<li>Знание принципов REST API</li>
<li>Git, npm/yarn</li>
</ul>

<p><strong>Плюсом будет:</strong></p>
<ul>
<li>Next.js</li>
<li>Опыт тестирования (Jest, Cypress)</li>
<li>Material-UI, Ant Design</li>
</ul>""",
        "key_skills": [
            {"name": "React"},
            {"name": "TypeScript"},
            {"name": "JavaScript"},
            {"name": "HTML5"},
            {"name": "CSS3"},
            {"name": "Redux"},
            {"name": "Git"},
            {"name": "REST API"}
        ],
        "accept_handicapped": True,
        "accept_kids": True,
        "archived": False,
        "premium": False,
        "employer": {
            "id": "23456",
            "name": "CRM Systems LLC",
            "url": "https://api.hh.ru/employers/23456",
            "alternate_url": "https://hh.ru/employer/23456",
            "logo_urls": None,
            "vacancies_url": "https://api.hh.ru/vacancies?employer_id=23456",
            "trusted": True
        },
        "published_at": (datetime.now() - timedelta(days=1)).isoformat() + "+03:00",
        "created_at": (datetime.now() - timedelta(days=1)).isoformat() + "+03:00",
        "alternate_url": "https://hh.ru/vacancy/50002",
        "apply_alternate_url": "https://hh.ru/applicant/vacancy_response?vacancyId=50002",
        "url": "https://api.hh.ru/vacancies/50002",
        "published_at_timestamp": int((datetime.now() - timedelta(days=1)).timestamp()),
        "counters": {
            "responses": 23,
            "unread_responses": 6,
            "invitations": 3,
            "views": 89
        },
        "allow_messages": True,
        "manager": {
            "id": "67891"
        }
    },

    {
        "id": "50003",
        "name": "DevOps Engineer / SRE",
        "area": {
            "id": "1",
            "name": "Москва",
            "url": "https://api.hh.ru/areas/1"
        },
        "salary": {
            "from": 200000,
            "to": 350000,
            "currency": "RUR",
            "gross": False
        },
        "type": {
            "id": "open",
            "name": "Открытая"
        },
        "address": {
            "city": "Москва",
            "street": "Садовая-Кудринская улица",
            "building": "3",
            "description": "м. Маяковская",
            "lat": 55.769717,
            "lng": 37.595463,
            "raw": "Москва, Садовая-Кудринская улица, 3",
            "metro": {
                "station_name": "Маяковская",
                "line": "Замоскворецкая",
                "station_id": "6.8",
                "lat": 55.769717,
                "lng": 37.595463
            }
        },
        "response_letter_required": True,
        "experience": {
            "id": "moreThan6",
            "name": "Более 6 лет"
        },
        "schedule": {
            "id": "flexible",
            "name": "Гибкий график"
        },
        "employment": {
            "id": "full",
            "name": "Полная занятость"
        },
        "description": """<p><strong>Компания:</strong> Международная e-commerce платформа</p>
<p><strong>О роли:</strong> Поддержка и развитие облачной инфраструктуры</p>

<p><strong>Обязанности:</strong></p>
<ul>
<li>Администрирование Kubernetes кластеров</li>
<li>CI/CD pipeline (GitLab CI, Jenkins)</li>
<li>Мониторинг (Prometheus, Grafana, ELK)</li>
<li>Автоматизация инфраструктуры (Terraform, Ansible)</li>
<li>Обеспечение High Availability сервисов</li>
</ul>

<p><strong>Требования:</strong></p>
<ul>
<li>Опыт работы с Kubernetes 3+ года</li>
<li>Docker, Linux администрирование</li>
<li>AWS/GCP/Azure (любой из облачных провайдеров)</li>
<li>Python/Bash для автоматизации</li>
<li>Опыт с мониторингом и алертингом</li>
</ul>""",
        "key_skills": [
            {"name": "Kubernetes"},
            {"name": "Docker"},
            {"name": "Linux"},
            {"name": "AWS"},
            {"name": "Terraform"},
            {"name": "Ansible"},
            {"name": "Python"},
            {"name": "Prometheus"},
            {"name": "Grafana"}
        ],
        "accept_handicapped": False,
        "accept_kids": False,
        "archived": False,
        "premium": True,
        "employer": {
            "id": "34567",
            "name": "E-Commerce Giant",
            "url": "https://api.hh.ru/employers/34567",
            "alternate_url": "https://hh.ru/employer/34567",
            "logo_urls": {
                "original": "https://img.hhcdn.ru/employer-logo/3456789.png",
                "240": "https://img.hhcdn.ru/employer-logo/3456789.png",
                "90": "https://img.hhcdn.ru/employer-logo/3456789.png"
            },
            "vacancies_url": "https://api.hh.ru/vacancies?employer_id=34567",
            "trusted": True
        },
        "published_at": (datetime.now() - timedelta(days=7)).isoformat() + "+03:00",
        "created_at": (datetime.now() - timedelta(days=7)).isoformat() + "+03:00",
        "alternate_url": "https://hh.ru/vacancy/50003",
        "apply_alternate_url": "https://hh.ru/applicant/vacancy_response?vacancyId=50003",
        "url": "https://api.hh.ru/vacancies/50003",
        "published_at_timestamp": int((datetime.now() - timedelta(days=7)).timestamp()),
        "counters": {
            "responses": 68,
            "unread_responses": 19,
            "invitations": 12,
            "views": 234
        },
        "allow_messages": True,
        "manager": {
            "id": "67892"
        }
    }
]

def get_mock_vacancy_by_id(vacancy_id: str) -> Dict[str, Any] | None:
    """Получить mock вакансию по ID"""
    for vacancy in MOCK_VACANCIES:
        if vacancy["id"] == vacancy_id:
            return vacancy
    return None

def get_mock_vacancies_page(page: int = 0, per_page: int = 20) -> Dict[str, Any]:
    """Получить страницу mock вакансий с пагинацией"""
    start_idx = page * per_page
    end_idx = start_idx + per_page

    page_vacancies = MOCK_VACANCIES[start_idx:end_idx]

    return {
        "items": page_vacancies,
        "page": page,
        "pages": (len(MOCK_VACANCIES) + per_page - 1) // per_page,
        "per_page": per_page,
        "found": len(MOCK_VACANCIES)
    }