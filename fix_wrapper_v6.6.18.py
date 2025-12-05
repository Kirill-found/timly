#!/usr/bin/env python3
"""
Wrapper для тестирования split функциональности v6.6.18
Обновляет Sidebar.html в Google Apps Script с проверкой operation_type
"""

import json
import os
import sys

def read_file(path):
    """Читает файл и возвращает содержимое"""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def verify_sidebar_changes():
    """Проверяет что в Sidebar.html есть проверка operation_type"""
    sidebar_path = r'C:\SheetGPT\frontend\Sidebar.html'

    if not os.path.exists(sidebar_path):
        print(f"[ERROR] File not found: {sidebar_path}")
        return False

    content = read_file(sidebar_path)

    # Проверяем наличие ключевых строк
    checks = [
        ("operation_type проверка", "const isSplitOperation = result.structured_data.operation_type === 'split'"),
        ("replaceDataInCurrentSheet вызов", ".replaceDataInCurrentSheet(result.structured_data)"),
        ("SPLIT OPERATION комментарий", "SPLIT OPERATION: заменяем данные в ТЕКУЩЕМ листе"),
        ("TABLE/CHART OPERATION комментарий", "TABLE/CHART OPERATION: создаём НОВЫЙ лист")
    ]

    all_passed = True
    for check_name, check_string in checks:
        if check_string in content:
            print(f"[OK] {check_name}: found")
        else:
            print(f"[FAIL] {check_name}: NOT found")
            all_passed = False

    return all_passed

def verify_code_gs_function():
    """Проверяет что в Code.gs есть функция replaceDataInCurrentSheet"""
    code_gs_path = r'C:\SheetGPT\frontend\Code.gs'

    if not os.path.exists(code_gs_path):
        print(f"[ERROR] File not found: {code_gs_path}")
        return False

    content = read_file(code_gs_path)

    # Проверяем наличие ключевых строк в replaceDataInCurrentSheet
    checks = [
        ("function replaceDataInCurrentSheet", "function replaceDataInCurrentSheet(structuredData)"),
        ("allData concatenation", "const allData = [headers].concat(rows)"),
        ("sheet.clear()", "sheet.clear()"),
        ("setValues(allData)", "dataRange.setValues(allData)"),
        ("header formatting", "headerRange.setFontWeight('bold')")
    ]

    all_passed = True
    for check_name, check_string in checks:
        if check_string in content:
            print(f"[OK] {check_name}: found")
        else:
            print(f"[FAIL] {check_name}: NOT found")
            all_passed = False

    return all_passed

def main():
    print("=" * 60)
    print("v6.6.18 Frontend Verification")
    print("=" * 60)

    print("\n1. Проверка Sidebar.html:")
    print("-" * 60)
    sidebar_ok = verify_sidebar_changes()

    print("\n2. Проверка Code.gs:")
    print("-" * 60)
    code_gs_ok = verify_code_gs_function()

    print("\n" + "=" * 60)
    if sidebar_ok and code_gs_ok:
        print("[SUCCESS] ALL CHECKS PASSED!")
        print("\nNext steps:")
        print("1. Open Google Apps Script (Extensions -> Apps Script)")
        print("2. Copy content from C:\\SheetGPT\\frontend\\Sidebar.html")
        print("3. Paste into Sidebar.html in Apps Script")
        print("4. Save (Ctrl+S)")
        print("5. Test query: 'razbey dannye po yacheykam'")
        print("\nExpected Console logs:")
        print("   - [UI] operation_type: split")
        print("   - [UI] SPLIT OPERATION: Replacing data in current sheet")
        print("   - [SPLIT] replaceDataInCurrentSheet called")
        print("   - [SPLIT] headers: Array(9)")
        return 0
    else:
        print("[FAILED] ERRORS FOUND!")
        return 1

if __name__ == '__main__':
    sys.exit(main())
