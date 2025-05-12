@echo off
REM Скрипт для запуска тестов

echo Запуск всех тестов с отчетом о покрытии кода
pytest --cov=insurance_app --cov-report=html

echo.
echo Отчет о покрытии кода сохранен в директории htmlcov
echo.
echo Для просмотра отчета откройте файл htmlcov\index.html
