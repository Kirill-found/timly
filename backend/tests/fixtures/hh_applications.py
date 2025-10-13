"""
Mock данные откликов и резюме для тестирования
Реалистичные данные кандидатов с резюме
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any
import uuid

# Mock данные откликов на вакансии
MOCK_APPLICATIONS: Dict[str, List[Dict[str, Any]]] = {
    "50001": [  # Python Backend разработчик
        {
            "id": "negotiations_001",
            "created_at": (datetime.now() - timedelta(days=2, hours=10)).isoformat() + "+03:00",
            "updated_at": (datetime.now() - timedelta(days=2, hours=10)).isoformat() + "+03:00",
            "url": "https://api.hh.ru/negotiations/negotiations_001",
            "state": {
                "id": "response",
                "name": "Отклик"
            },
            "has_updates": False,
            "viewed_by_opponent": True,
            "messages_url": "https://api.hh.ru/negotiations/negotiations_001/messages",
            "messaging_status": "ok",
            "professional_roles": [
                {
                    "id": "96",
                    "name": "Программист, разработчик"
                }
            ],
            "source": "response",
            "resume": {
                "id": "resume001",
                "title": "Python Backend разработчик",
                "url": "https://api.hh.ru/resumes/resume001",
                "first_name": "Алексей",
                "last_name": "Петров",
                "middle_name": "Игоревич",
                "age": 28,
                "alternate_url": "https://hh.ru/resume/resume001",
                "created_at": "2023-06-15T14:20:00+03:00",
                "updated_at": "2024-01-10T09:15:00+03:00",
                "area": {
                    "id": "1",
                    "name": "Москва",
                    "url": "https://api.hh.ru/areas/1"
                },
                "certificate": [],
                "education": {
                    "elementary": [],
                    "additional": [],
                    "attestation": [],
                    "primary": [
                        {
                            "year": 2018,
                            "name": "МГУ им. М.В. Ломоносова",
                            "name_id": "39420",
                            "organization": "МГУ им. М.В. Ломоnosova",
                            "organization_id": "39420",
                            "result": "Бакалавр информационных технологий",
                            "result_id": None
                        }
                    ]
                },
                "total_experience": {
                    "months": 48
                },
                "experience": [
                    {
                        "area": {
                            "id": "1",
                            "name": "Москва",
                            "url": "https://api.hh.ru/areas/1"
                        },
                        "company": "TechStart LLC",
                        "company_id": "111222",
                        "company_url": "https://api.hh.ru/employers/111222",
                        "employer": {
                            "id": "111222",
                            "name": "TechStart LLC",
                            "url": "https://api.hh.ru/employers/111222",
                            "alternate_url": "https://hh.ru/employer/111222",
                            "logo_urls": None
                        },
                        "end": "2024-01-01",
                        "industries": [
                            {
                                "id": "7.540",
                                "name": "Разработка программного обеспечения"
                            }
                        ],
                        "industry": {
                            "id": "7.540",
                            "name": "Разработка программного обеспечения"
                        },
                        "position": "Python разработчик",
                        "start": "2020-03-01",
                        "description": "Разработка backend сервисов на Django. Проектирование REST API. Работа с PostgreSQL, Redis. Интеграция с внешними API. Код ревью."
                    },
                    {
                        "area": {
                            "id": "1",
                            "name": "Москва",
                            "url": "https://api.hh.ru/areas/1"
                        },
                        "company": "StartupCorp",
                        "company_id": "222333",
                        "company_url": "https://api.hh.ru/employers/222333",
                        "end": "2020-02-01",
                        "position": "Junior Python разработчик",
                        "start": "2018-06-01",
                        "description": "Изучение Python, Django. Разработка простых веб-приложений. Работа с базами данных."
                    }
                ],
                "gender": {
                    "id": "male",
                    "name": "Мужской"
                },
                "salary": {
                    "amount": 250000,
                    "currency": "RUR"
                },
                "photo": None,
                "portfolio": [],
                "professional_roles": [
                    {
                        "id": "96",
                        "name": "Программист, разработчик"
                    }
                ],
                "recommendation": [],
                "skills": "Python, Django, FastAPI, PostgreSQL, Redis, Docker, Git, REST API, Celery, Linux",
                "skill_set": ["Python", "Django", "FastAPI", "PostgreSQL", "Redis", "Docker", "Git", "REST API"],
                "language": [
                    {
                        "id": "rus",
                        "name": "Русский",
                        "level": {
                            "id": "native",
                            "name": "Родной"
                        }
                    },
                    {
                        "id": "eng",
                        "name": "Английский",
                        "level": {
                            "id": "b2",
                            "name": "B2 — Средне-продвинутый"
                        }
                    }
                ],
                "travel_time": {
                    "id": "any",
                    "name": "Не имеет значения"
                },
                "work_ticket": [],
                "contact": [
                    {
                        "type": {
                            "id": "cell",
                            "name": "Мобильный телефон"
                        },
                        "value": {
                            "country": "7",
                            "city": "926",
                            "number": "1234567",
                            "formatted": "+7 926 123-45-67"
                        },
                        "preferred": True,
                        "comment": None
                    },
                    {
                        "type": {
                            "id": "email",
                            "name": "Эл. почта"
                        },
                        "value": "alexey.petrov@example.com",
                        "preferred": True,
                        "comment": None
                    }
                ]
            }
        },

        {
            "id": "negotiations_002",
            "created_at": (datetime.now() - timedelta(days=1, hours=15)).isoformat() + "+03:00",
            "updated_at": (datetime.now() - timedelta(days=1, hours=15)).isoformat() + "+03:00",
            "url": "https://api.hh.ru/negotiations/negotiations_002",
            "state": {
                "id": "response",
                "name": "Отклик"
            },
            "has_updates": True,
            "viewed_by_opponent": False,
            "messages_url": "https://api.hh.ru/negotiations/negotiations_002/messages",
            "messaging_status": "ok",
            "source": "response",
            "resume": {
                "id": "resume002",
                "title": "Senior Python Developer / Tech Lead",
                "url": "https://api.hh.ru/resumes/resume002",
                "first_name": "Мария",
                "last_name": "Сидорова",
                "middle_name": "Александровна",
                "age": 32,
                "alternate_url": "https://hh.ru/resume/resume002",
                "created_at": "2022-03-10T11:30:00+03:00",
                "updated_at": "2024-01-08T16:45:00+03:00",
                "area": {
                    "id": "1",
                    "name": "Москва",
                    "url": "https://api.hh.ru/areas/1"
                },
                "total_experience": {
                    "months": 96
                },
                "experience": [
                    {
                        "company": "Yandex",
                        "position": "Senior Python Developer",
                        "start": "2019-09-01",
                        "end": "2023-12-01",
                        "description": "Разработка высоконагруженных сервисов. Архитектура микросервисов. Менторинг команды разработчиков. Код ревью и техническое лидерство."
                    },
                    {
                        "company": "Mail.ru Group",
                        "position": "Python Developer",
                        "start": "2016-03-01",
                        "end": "2019-08-01",
                        "description": "Backend разработка для социальных сетей. Оптимизация производительности. Работа с большими данными."
                    }
                ],
                "salary": {
                    "amount": 400000,
                    "currency": "RUR"
                },
                "skills": "Python, Django, FastAPI, PostgreSQL, MongoDB, Redis, Kubernetes, Docker, AWS, Microservices, Team Leadership",
                "skill_set": ["Python", "Django", "FastAPI", "PostgreSQL", "MongoDB", "Redis", "Kubernetes", "Docker", "AWS"],
                "language": [
                    {
                        "id": "rus",
                        "name": "Русский",
                        "level": {
                            "id": "native",
                            "name": "Родной"
                        }
                    },
                    {
                        "id": "eng",
                        "name": "Английский",
                        "level": {
                            "id": "c1",
                            "name": "C1 — Продвинутый"
                        }
                    }
                ],
                "contact": [
                    {
                        "type": {
                            "id": "email",
                            "name": "Эл. почта"
                        },
                        "value": "maria.sidorova@example.com",
                        "preferred": True
                    }
                ]
            }
        },

        {
            "id": "negotiations_003",
            "created_at": (datetime.now() - timedelta(hours=6)).isoformat() + "+03:00",
            "updated_at": (datetime.now() - timedelta(hours=6)).isoformat() + "+03:00",
            "url": "https://api.hh.ru/negotiations/negotiations_003",
            "state": {
                "id": "response",
                "name": "Отклик"
            },
            "has_updates": True,
            "viewed_by_opponent": False,
            "source": "response",
            "resume": {
                "id": "resume003",
                "title": "Junior Python разработчик",
                "first_name": "Дмитрий",
                "last_name": "Козлов",
                "age": 24,
                "area": {
                    "id": "2",
                    "name": "Санкт-Петербург"
                },
                "total_experience": {
                    "months": 8
                },
                "experience": [
                    {
                        "company": "WebDev Studio",
                        "position": "Стажер Python разработчик",
                        "start": "2023-06-01",
                        "end": None,
                        "description": "Изучение Django, разработка простых веб-приложений, участие в проектах под руководством ментора."
                    }
                ],
                "salary": {
                    "amount": 80000,
                    "currency": "RUR"
                },
                "skills": "Python, Django, HTML, CSS, JavaScript, Git, PostgreSQL",
                "skill_set": ["Python", "Django", "HTML", "CSS", "JavaScript", "Git", "PostgreSQL"],
                "contact": [
                    {
                        "type": {
                            "id": "email",
                            "name": "Эл. почта"
                        },
                        "value": "dmitry.kozlov@example.com",
                        "preferred": True
                    }
                ]
            }
        }
    ],

    "50002": [  # Frontend React разработчик
        {
            "id": "negotiations_004",
            "created_at": (datetime.now() - timedelta(days=1, hours=8)).isoformat() + "+03:00",
            "updated_at": (datetime.now() - timedelta(days=1, hours=8)).isoformat() + "+03:00",
            "url": "https://api.hh.ru/negotiations/negotiations_004",
            "state": {
                "id": "response",
                "name": "Отклик"
            },
            "has_updates": False,
            "viewed_by_opponent": True,
            "source": "response",
            "resume": {
                "id": "resume004",
                "title": "React Frontend разработчик",
                "first_name": "Анна",
                "last_name": "Волкова",
                "age": 26,
                "area": {
                    "id": "2",
                    "name": "Санкт-Петербург"
                },
                "total_experience": {
                    "months": 30
                },
                "experience": [
                    {
                        "company": "Frontend Agency",
                        "position": "React разработчик",
                        "start": "2021-09-01",
                        "end": None,
                        "description": "Разработка SPA приложений на React. Интеграция с REST API. Оптимизация производительности. Тестирование с Jest и RTL."
                    }
                ],
                "salary": {
                    "amount": 180000,
                    "currency": "RUR"
                },
                "skills": "React, TypeScript, JavaScript, Redux, HTML5, CSS3, SCSS, Jest, Git, Webpack",
                "skill_set": ["React", "TypeScript", "JavaScript", "Redux", "HTML5", "CSS3", "Jest", "Git"],
                "contact": [
                    {
                        "type": {
                            "id": "email",
                            "name": "Эл. почта"
                        },
                        "value": "anna.volkova@example.com",
                        "preferred": True
                    }
                ]
            }
        },

        {
            "id": "negotiations_005",
            "created_at": (datetime.now() - timedelta(hours=12)).isoformat() + "+03:00",
            "updated_at": (datetime.now() - timedelta(hours=12)).isoformat() + "+03:00",
            "url": "https://api.hh.ru/negotiations/negotiations_005",
            "state": {
                "id": "response",
                "name": "Отклик"
            },
            "has_updates": True,
            "viewed_by_opponent": False,
            "source": "response",
            "resume": {
                "id": "resume005",
                "title": "Frontend разработчик (React, Vue.js)",
                "first_name": "Игорь",
                "last_name": "Морозов",
                "age": 29,
                "area": {
                    "id": "1",
                    "name": "Москва"
                },
                "total_experience": {
                    "months": 54
                },
                "experience": [
                    {
                        "company": "Digital Solutions",
                        "position": "Senior Frontend Developer",
                        "start": "2020-01-01",
                        "end": None,
                        "description": "Ведущий разработчик команды Frontend. Архитектура клиентской части. Наставничество джуниоров. Интеграция с различными API."
                    }
                ],
                "salary": {
                    "amount": 220000,
                    "currency": "RUR"
                },
                "skills": "React, Vue.js, TypeScript, Next.js, Nuxt.js, Node.js, GraphQL, Docker, AWS",
                "skill_set": ["React", "Vue.js", "TypeScript", "Next.js", "Node.js", "GraphQL", "Docker"],
                "contact": [
                    {
                        "type": {
                            "id": "email",
                            "name": "Эл. почта"
                        },
                        "value": "igor.morozov@example.com",
                        "preferred": True
                    }
                ]
            }
        }
    ],

    "50003": [  # DevOps Engineer
        {
            "id": "negotiations_006",
            "created_at": (datetime.now() - timedelta(days=3, hours=14)).isoformat() + "+03:00",
            "updated_at": (datetime.now() - timedelta(days=3, hours=14)).isoformat() + "+03:00",
            "url": "https://api.hh.ru/negotiations/negotiations_006",
            "state": {
                "id": "response",
                "name": "Отклик"
            },
            "has_updates": False,
            "viewed_by_opponent": True,
            "source": "response",
            "resume": {
                "id": "resume006",
                "title": "DevOps Engineer / Infrastructure Architect",
                "first_name": "Сергей",
                "last_name": "Кузнецов",
                "age": 35,
                "area": {
                    "id": "1",
                    "name": "Москва"
                },
                "total_experience": {
                    "months": 120
                },
                "experience": [
                    {
                        "company": "CloudTech Corp",
                        "position": "Senior DevOps Engineer",
                        "start": "2018-05-01",
                        "end": None,
                        "description": "Проектирование и поддержка облачной инфраструктуры. Kubernetes кластеры. CI/CD конвейеры. Мониторинг и алертинг. Автоматизация с Terraform."
                    }
                ],
                "salary": {
                    "amount": 350000,
                    "currency": "RUR"
                },
                "skills": "Kubernetes, Docker, AWS, GCP, Terraform, Ansible, Python, Bash, Prometheus, Grafana, Jenkins, GitLab CI",
                "skill_set": ["Kubernetes", "Docker", "AWS", "Terraform", "Ansible", "Python", "Prometheus", "Grafana"],
                "contact": [
                    {
                        "type": {
                            "id": "email",
                            "name": "Эл. почта"
                        },
                        "value": "sergey.kuznetsov@example.com",
                        "preferred": True
                    }
                ]
            }
        }
    ]
}

def get_mock_applications_by_vacancy_id(vacancy_id: str, page: int = 0, per_page: int = 20) -> Dict[str, Any]:
    """Получить mock отклики для вакансии с пагинацией"""
    applications = MOCK_APPLICATIONS.get(vacancy_id, [])

    start_idx = page * per_page
    end_idx = start_idx + per_page

    page_applications = applications[start_idx:end_idx]

    return {
        "items": page_applications,
        "page": page,
        "pages": (len(applications) + per_page - 1) // per_page if applications else 0,
        "per_page": per_page,
        "found": len(applications)
    }

def get_mock_application_by_id(application_id: str) -> Dict[str, Any] | None:
    """Получить mock отклик по ID"""
    for vacancy_id, applications in MOCK_APPLICATIONS.items():
        for application in applications:
            if application["id"] == application_id:
                return application
    return None

def get_mock_resume_by_id(resume_id: str) -> Dict[str, Any] | None:
    """Получить mock резюме по ID"""
    for vacancy_id, applications in MOCK_APPLICATIONS.items():
        for application in applications:
            if application["resume"]["id"] == resume_id:
                return application["resume"]
    return None