Вариант №25 

Задание №1 

Разработать эмулятор для языка оболочки ОС. Необходимо сделать работу 
эмулятора как можно более похожей на сеанс shell в UNIX-подобной ОС. 
Эмулятор должен запускаться из реальной командной строки, а файл с 
виртуальной файловой системой не нужно распаковывать у пользователя. 
Эмулятор принимает образ виртуальной файловой системы в виде файла формата 
zip. Эмулятор должен работать в режиме GUI.

Конфигурационный файл имеет формат xml и содержит: 
• Имя пользователя для показа в приглашении к вводу. 
• Имя компьютера для показа в приглашении к вводу. 
• Путь к архиву виртуальной файловой системы. 

Необходимо поддержать в эмуляторе команды ls, cd и exit, а также 
следующие команды: 
1. mv. 
2. cat. 
3. tail.

Все функции эмулятора должны быть покрыты тестами, а для каждой из 
поддерживаемых команд необходимо написать 3 теста.


Функции

read_config(config_path):
Назначение: Читает конфигурационный файл для извлечения имени хоста, пути к виртуальной файловой системе и имени компьютера.
Параметры: config_path (str): Путь к конфигурационному файлу (например, config.ini).
Возвращает: Кортеж, содержащий имя хоста, путь к VFS и путь к журналу

ls(vfs):
Назначение: Возвращает список файлов и директорий в текущей директории.
Параметры: vfs (VirtualFileSystem): Объект виртуальной файловой системы.
Возвращает: Строку с содержимым директории.

cd(vfs, path):
Назначение: Изменяет текущую директорию.
Параметры: vfs (VirtualFileSystem): Объект виртуальной файловой системы.
path (str): Путь к новой директории.
Возвращает: Сообщение об успешном изменении директории или ошибку.

cat(vfs, file_name):
Назначение: Читает содержимое файла.
Параметры: vfs (VirtualFileSystem): Объект виртуальной файловой системы.
file_name (str): Имя файла для чтения.
Возвращает: Содержимое файла или сообщение об ошибке, если файл не найден.

tail(vfs, file_name)
Назначение: Выводит последние строки файла.
Параметры: vfs (VirtualFileSystem): Объект виртуальной файловой системы.
file_name (str): Имя файла для чтения.
Возвращает: Последние 10 строк файла или сообщение об ошибке, если файл не найден.

mv(vfs, path_A, path_B)
Назначение: Перемещает директорию или файл по указанному адресу
Параметры: vfs (VirtualFileSystem): Объект виртуальной файловой системы.
path_A (str): Путь перемещаемого файла
path_B (str): Адрес назначения
Возвращает: Сообщение об успехе или об ошибке

run_shell(hostname, vfs_path, log_path)
Назначение: Запускает основной цикл работы эмулятора оболочки с GUI на tkinter.
Параметры: hostname (str): Имя хоста.
vfs_path (str): Путь к виртуальной файловой системе.
log_path (str): Путь к журналу.
Возвращает: None



VirtualFileSystem
Класс для работы с виртуальной файловой системой.
Методы:

init(self, zip_path):
Назначение: Инициализирует VFS, извлекая содержимое ZIP-файла.
Параметры: zip_path (str): Путь к ZIP-файлу.

extract_zip(self, zip_path):
Назначение: Извлекает файлы из ZIP-архива в корневую директорию VFS.
Параметры: zip_path (str): Путь к ZIP-файлу.
Возвращает: None.

list_directory(self):
Назначение: Возвращает список содержимого текущей директории с информацией о типе (файл или директория), размере и времени последнего изменения.
Возвращает: Строку с перечислением элементов директории.

change_directory(self, path):
Назначение: Меняет текущую директорию.
Параметры:path (str): Новый путь к директории.
Возвращает: None.

get_relative_path(self):
Назначение: Возвращает относительный путь к текущей директории.
Возвращает: Строку с относительным путем.

read_file(self, file_name):
Назначение: Читает содержимое файла.
Параметры: file_name (str): Имя файла для чтения.
Возвращает: Содержимое файла или сообщение об ошибке, если файл не найден.

Пример работы консоли
![image](https://github.com/user-attachments/assets/c5bc6cac-c800-4cbf-9e39-0e35ee406c39)

Тесты
![image](https://github.com/user-attachments/assets/88e5cc75-5696-4910-ac31-3c44b85e3e16)



