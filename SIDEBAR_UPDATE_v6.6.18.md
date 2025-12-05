# ИСПРАВЛЕНИЕ v6.6.18 - Split функциональность

## Проблема
В Sidebar.html **отсутствовала проверка operation_type**, из-за чего код всегда вызывал `createTableAndChart()` вместо `replaceDataInCurrentSheet()`. Это приводило к тому что заголовки не добавлялись в текущий лист.

## Что исправлено

### Sidebar.html (строки 1008-1102)
Добавлена проверка `operation_type`:

```javascript
if (result.structured_data) {
  const isSplitOperation = result.structured_data.operation_type === 'split';

  if (isSplitOperation) {
    // SPLIT OPERATION: заменяем данные в ТЕКУЩЕМ листе
    google.script.run.replaceDataInCurrentSheet(result.structured_data);
  } else {
    // TABLE/CHART OPERATION: создаём НОВЫЙ лист
    google.script.run.createTableAndChart(result.structured_data);
  }
}
```

## Инструкция по обновлению

### 1. Откройте Google Apps Script
- В Google Sheets: Extensions → Apps Script

### 2. Обновите Sidebar.html
- Откройте файл Sidebar.html в редакторе Apps Script
- Полностью замените содержимое на файл из: `C:\SheetGPT\frontend\Sidebar.html`
- Сохраните (Ctrl+S)

### 3. Проверьте Code.gs (должен быть уже обновлен)
- Убедитесь что функция `replaceDataInCurrentSheet()` присутствует (строка 1020)
- Если её нет, скопируйте из: `C:\SheetGPT\frontend\Code.gs`

### 4. Тестирование

Введите в чат: **"разбей данные по ячейкам"**

#### Ожидаемое поведение:
1. Backend вернет `structured_data` с `operation_type: "split"`
2. В Console появятся логи:
   ```
   [UI] operation_type: split
   [UI] SPLIT OPERATION: Replacing data in current sheet
   [SPLIT] replaceDataInCurrentSheet called
   [SPLIT] headers: Array(9)
   [SPLIT] rows count: 4
   [SPLIT] Inserted data: 5 rows x 9 cols
   ```
3. В ТЕКУЩЕМ листе появятся:
   - Строка 1: **Канал, Показы, Клики, CTR, Лиды, CPL, Клиенты, CAC, Выручка** (жирный шрифт, серый фон)
   - Строка 2-5: данные из исходных строк

## Backend Status
✅ Backend v6.6.17 уже задеплоен на Railway
✅ API возвращает правильный `structured_data` с 9 заголовками
✅ `operation_type: "split"` добавлен в ответ

## Верификация
Запустите скрипт для проверки:
```bash
python fix_wrapper_v6.6.18.py
```

Все проверки должны пройти успешно: `[SUCCESS] ALL CHECKS PASSED!`
