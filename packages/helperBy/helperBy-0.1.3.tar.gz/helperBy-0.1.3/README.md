HelperBy - Python Utilities Collection
HelperBy - это набор полезных утилит для работы с файлами, системной информацией, консольным интерфейсом и простым GUI.

Установка
bash
pip install helperBy
Основные модули
File Utilities - работа с файлами

System Info - получение системной информации

Console Utilities - инструменты для консольных приложений

Примеры использования
1. Работа с файлами
python
from helperBy import RawFileReader, simple_write

# Чтение файлов
reader = RawFileReader()
content = reader.read_file('example.txt')  # Автоопределение типа
csv_data = reader.read_csv('data.csv')  # Чтение CSV

# Запись в файл
simple_write('output.txt', 'Hello, World!')
2. Системная информация
python
from helperBy import get_system_info, get_cpu_info, get_processes

# Основная информация о системе
print(get_system_info())

# Информация о процессоре
print(get_cpu_info())

# Топ-5 процессов по использованию CPU
top_processes = get_processes(sort_by='cpu_percent', limit=5)
for proc in top_processes:
    print(f"{proc['name']}: {proc['cpu_percent']}%")
3. Консольные утилиты
python
from helperBy import (
    easy_input, print_list, ask_yes_no,
    progress_bar, custom_print, color_print,
    calculate, print_menu, plot_bar
)

# Ввод с проверкой типа
age = easy_input("Введите ваш возраст: ", int)

# Красивый вывод списка
print_list(['Яблоки', 'Бананы', 'Апельсины'], numbered=True)

# Прогресс-бар
progress_bar(100, desc="Processing", color="BLUE")

# ASCII-арт
custom_print("Hello")

# Цветной текст
color_print("Важное сообщение", "RED")

# Меню
print_menu(3, "Опция 1", "Опция 2", "Опция 3")

# Графики в консоли
data = {"A": 25, "B": 40, "C": 35}
plot_bar(data)
4. Графический интерфейс
python
from helperBy import New, Color, Text, Button

def on_click():
    print("Кнопка нажата!")


# Полный список функций
File Utilities
mmap_read(file_path) - чтение больших файлов через memory-mapping

RawFileReader - класс для чтения файлов разных форматов

read_txt() - чтение текстовых файлов

read_csv() - чтение CSV

read_xls() - чтение XLS как CSV

read_file() - автоопределение формата

simple_write() - простая запись в файл

# System Info
get_system_info() - информация о системе

get_cpu_info() - информация о процессоре

get_memory_info() - информация о памяти

get_disk_info() - информация о дисках

get_processes() - список процессов

kill_process() - завершение процесса

get_network_info() - сетевая статистика

get_uptime() - время работы системы

get_users() - активные пользователи

# Console Utilities
easy_input() - ввод с проверкой типа

print_list() - красивый вывод списка

ask_yes_no() - вопрос Да/Нет

tqdm_use() - прогресс-бар с tqdm

progress_bar() - кастомный прогресс-бар

custom_print() - ASCII-арт текст

color_print() - цветной текст

calculate() - простые вычисления

print_menu() - вывод меню

plot_bar() - гистограмма в консоли

plot_pie() - круговая диаграмма в консоли

UI Utilities
New - главный класс приложения

Color - работа с цветами

Text - текстовый элемент

Image - изображение

Button - кнопка

Лицензия
MIT License. Свободно для использования и модификации.

