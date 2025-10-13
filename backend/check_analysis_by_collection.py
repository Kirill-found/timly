"""
Проверка какие коллекции анализируются
"""
from app.database import SessionLocal
from app.models.vacancy import Vacancy
from app.models.application import Application, AnalysisResult
from sqlalchemy import func

db = SessionLocal()

vacancies = db.query(Vacancy).all()

print('\n' + '='*80)
print('           ANALYSIS STATUS BY COLLECTION TYPE')
print('='*80 + '\n')

collection_names = {
    'response': 'NOVYE (new applications)',
    'consider': 'RASSMATRIVAEMYE (considering)',
    'discard': 'OTKLONENNYE (rejected/discarded)'
}

for idx, v in enumerate(vacancies, 1):
    print(f'[{idx}] Vacancy: {v.title[:50]}')
    print(f'    HH ID: {v.hh_vacancy_id}')
    print()

    result = db.query(
        Application.collection_id,
        func.count(Application.id).label('total'),
        func.count(AnalysisResult.id).label('analyzed')
    ).outerjoin(AnalysisResult).filter(
        Application.vacancy_id == v.id
    ).group_by(Application.collection_id).all()

    for c, t, a in result:
        coll_type = c.split('_')[0]
        coll_name = collection_names.get(coll_type, 'Unknown')

        if a == t:
            status = '[OK] All analyzed'
        elif a == 0:
            status = '[!!!] NONE analyzed'
        else:
            status = f'[WARN] Missing {t-a} analyses'

        print(f'    {coll_name:40} : {a:3}/{t:3} {status}')

    print()

db.close()

print('='*80)
print('\nConclusion:')
print('  - If "NONE analyzed" = this collection is NOT being analyzed')
print('  - If "All analyzed" = this collection IS being analyzed')
print('='*80 + '\n')
