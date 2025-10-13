"""
Проверка синхронизации данных с HH.ru
"""
from app.database import SessionLocal
from app.models.vacancy import Vacancy
from app.models.application import Application
from sqlalchemy import func

db = SessionLocal()

vacancies = db.query(Vacancy).all()

print('\n' + '='*80)
print('                 SYNC CHECK: DATABASE vs HH.ru')
print('='*80 + '\n')

for idx, v in enumerate(vacancies, 1):
    # Подсчет откликов в БД
    apps_total = db.query(func.count(Application.id)).filter(
        Application.vacancy_id == v.id
    ).scalar()

    # Разбивка по коллекциям
    apps_by_coll = db.query(
        Application.collection_id,
        func.count(Application.id)
    ).filter(
        Application.vacancy_id == v.id
    ).group_by(Application.collection_id).all()

    print(f'[{idx}] Vacancy: {v.title[:60]}')
    print(f'    HH Vacancy ID: {v.hh_vacancy_id}')
    print(f'    ')
    print(f'    HH.ru reports: {v.applications_count} applications')
    print(f'    Our DB has:    {apps_total} applications')
    print(f'    ')

    if apps_total != v.applications_count:
        diff = v.applications_count - apps_total
        print(f'    *** MISMATCH: Missing {diff} applications! ***')
    else:
        print(f'    [OK] Counts match!')

    print(f'    ')
    print(f'    Breakdown by collection:')
    for c, cnt in apps_by_coll:
        coll_name = c.split('_')[0]
        print(f'      - {coll_name:15} : {cnt:4} applications (id: {c})')

    print()

db.close()

print('='*80)
print('\nExplanation:')
print('  - HH.ru applications_count = total applications on HH website')
print('  - Our DB = applications we downloaded and stored')
print('  - If mismatch = we are not downloading all applications!')
print('='*80 + '\n')
