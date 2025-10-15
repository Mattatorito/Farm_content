#!/bin/bash
# Скрипт для активации виртуального окружения
# Использование: source activate_env.sh

echo "Активируем виртуальное окружение для проекта Farm Content..."
source venv/bin/activate
echo "✅ Виртуальное окружение активировано!"
echo "Python путь: $(which python)"
echo "Python версия: $(python --version)"
echo ""
echo "Для деактивации используйте команду: deactivate"
