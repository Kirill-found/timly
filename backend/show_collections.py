"""
Показать коллекции откликов и их статус анализа
"""
from app.database import SessionLocal
from app.models.application import Application, AnalysisResult
from sqlalchemy import func

db = SessionLocal()
vacancy_id = 'e18cde91-5afc-4a9c-a837-113f476957fc'

result = db.query(
    Application.collection_id,
    func.count(Application.id).label('total'),
    func.count(AnalysisResult.id).label('analyzed')
).outerjoin(AnalysisResult).filter(
    Application.vacancy_id == vacancy_id
).group_by(Application.collection_id).all()

print('\n' + '='*70)
print('             КОЛЛЕКЦИИ ОТКЛИКОВ HH.RU')
print('='*70 + '\n')

collections_map = {
    'response': 'НОВЫЕ ОТКЛИКИ (еще не просмотренные работодателем)',
    'consider': 'РАССМАТРИВАЕМЫЕ (интересные кандидаты)',
    'discard': 'ОТКЛОНЕННЫЕ (не подошли работодателю)'
}

total_all = 0
analyzed_all = 0

for c, t, a in result:
    total_all += t
    analyzed_all += a

    coll_type = c.split('_')[0] if '_' in c else c
    coll_name = collections_map.get(coll_type, 'Неизвестная категория')

    print(f'[*] {coll_name}')
    print(f'    Vsego resume: {t}')
    print(f'    [+] Proanalizirovano: {a}')
    print(f'    [-] Ne proanalizirovano: {t-a}')
    print(f'   (ID коллекции: {c})')
    print()

print('-'*70)
print(f'ИТОГО: {analyzed_all} из {total_all} проанализировано ({analyzed_all*100//total_all if total_all > 0 else 0}%)')
print('='*70 + '\n')

db.close()
