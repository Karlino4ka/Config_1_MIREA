import os
import zipfile
import xml.etree.ElementTree as ET
import tkinter as tk
from tempfile import TemporaryDirectory
from tkinter import scrolledtext
import shutil


def read_config(path):
    xml=ET.parse(path)
    return xml.find('user').text, xml.find('PC').text, xml.find('path').text

class Shell:
    def __init__(self, zip_path):
        self.temp_dir = TemporaryDirectory()
        self.zip_path = zip_path
        self.cwd = "/"  # Корень виртуальной файловой системы
        self.archive = zipfile.ZipFile(zip_path, 'a')  # Открытие ZIP-архива

    def get_relative_path(self):
        return self.cwd


    def __del__(self):
        self.archive.close()
        self.temp_dir.cleanup()


    def run_command(self, command):
        parts = command.split()  # Разделение строки на части
        cmd = parts[0]  # Первая часть — это команда
        args = parts[1:]  # Остальные части — аргументы

        if cmd == "ls":
            return self.ls(args)
        elif cmd == "cd":
            return self.cd(args[0] if args else "/")
        elif cmd == "cat":
            return self.cat(args)
        elif cmd == "mv":
            return self.mv(args)
        elif cmd == "exit":
            return self.exit()
        elif cmd == "tail":
            return self.tail(args)  # Передача всех аргументов
        else:
            return "Command not found"

    def ls(self, args):
        detailed = "-l" in args
        entries = self.archive.namelist()

        dirs = set()  # Уникальные директории
        files = set()

        # Разделяем директории и файлы
        for entry in entries:
            if entry.startswith(self.cwd.strip("/")):
                rel_path = entry[len(self.cwd.strip("/")):].strip("/")
                if "/" in rel_path:  # Это директория
                    dirs.add(rel_path.split("/")[0])
                elif rel_path:  # Это файл
                    files.add(rel_path)

        if detailed:
            result = []
            for entry in sorted(dirs | files):  # Перебираем директории и файлы
                if entry in dirs:
                    result.append(f"drwxr-xr-x 0 {entry}")
                else:
                    # Получаем информацию о файле
                    info = next((i for i in self.archive.infolist() if i.filename == f"{self.cwd.strip('/')}/{entry}"),
                                None)
                    size = info.file_size if info else 0
                    result.append(f"-rw-r--r-- {size} {entry}")
            return "\n".join(result)
        else:
            return "\n".join(sorted(dirs | files))

    def cd(self, path):
        if not path:
            path = "/"  # Если путь пустой, возвращаемся в корень

        # Обрабатываем команду 'cd ..'
        if path == "..":
            # Если мы уже в корне, не можем подняться выше
            if self.cwd == "/":
                return "Already at root directory"

            # Разделяем текущий путь по слешам и убираем последний элемент (переходим на уровень выше)
            new_path = '/'.join(self.cwd.strip('/').split('/')[:-1])
            if new_path == "":
                new_path = "/"  # Если путь пустой, значит, мы вернулись в корень
            self.cwd = "/" + new_path.lstrip("/")  # Обновляем текущий путь
            return ""

        # Нормализуем путь относительно текущего каталога
        new_path = os.path.normpath(os.path.join(self.cwd.strip("/"), path)).replace("\\", "/")

        # Проверяем, существует ли каталог в архиве
        entries = self.archive.namelist()
        matched_dirs = [entry for entry in entries if entry.startswith(new_path + "/")]

        if matched_dirs:
            # Убедимся, что путь всегда начинается с одного слэша
            self.cwd = "/" + new_path.lstrip("/")  # Обновляем текущий путь
            return ""
        else:
            return f"No such directory: {path}"


    def mv(self, args):
        pathA=args[0]
        pathB=args[1]
        obj2 = os.path.normpath(os.path.join(self.cwd.strip("/"), pathB)).strip("/")
        obj1 = obj2+'/'+os.path.normpath(os.path.join(self.cwd.strip("/"), pathA)).strip("/")
        self.archive.writestr(obj1, "rvrvrvvrvr")
        #self.archive.remove(os.path.normpath(os.path.join(self.cwd.strip("/"), pathA)).strip("/"))
        print (obj1, obj2)

        if any(entry == obj1 or entry.startswith(obj1) for entry in self.archive.namelist()):
            return f"'{obj1}' already exists"


    def tail(self, args):

        if not args:
            return "Error: tail command requires a file path"

        path = args[0]

        if path is None:
            return "Error: no file specified"

        file_path = os.path.normpath(os.path.join(self.cwd.strip("/"), path)).strip("/")

        if file_path not in self.archive.namelist():
            return f"No such file: {path}"

        try:
            with self.archive.open(file_path) as f:
                lines_content = f.readlines()[-10:]
            return ''.join(line.decode('utf-8') for line in lines_content)
        except Exception as e:
            return f"Error: {str(e)}"

    def cat(self, args):
        if not args:
            return "Error: cat command requires a file path"

        path = args[0]

        if path is None:
            return "Error: no file specified"

        file_path = os.path.normpath(os.path.join(self.cwd.strip("/"), path)).strip("/")

        if file_path not in self.archive.namelist():
            return f"No such file: {path}"

        try:
            with self.archive.open(file_path) as f:
                lines_content = f.readlines()
            return ''.join(line.decode('utf-8') for line in lines_content)
        except Exception as e:
            return f"Error: {str(e)}"




    def exit(self):
        return "Exiting shell..."

    def get_current_path(self):
        return self.cwd


# Основной цикл работы эмулятора с GUI на tkinter
def run_shell(hostname, PC, vfs_path):
    vfs = Shell(vfs_path)
    window = tk.Tk()
    window.title(f"{hostname}")

    def get_prompt():
        relative_path = vfs.get_relative_path()
        if relative_path == '.':
            relative_path = ''
        return f"{PC} {hostname}/{relative_path}> " if relative_path else f"{PC} {hostname}> "

    def handle_command(event=None):
        # Получаем команду без приглашения
        full_text = terminal_output.get("end-1l linestart", "end-1c").strip()
        command = full_text.replace(get_prompt(), "").strip()  # Извлекаем команду без "PS MyVirtualMachine>"
        if command=="exit":
            window.quit()
        output = vfs.run_command(command)
        terminal_output.insert(tk.END, f"\n{output}\n{get_prompt()}")
        # terminal_output.insert(tk.END, '\b ')
        terminal_output.see(tk.END)  # Прокрутка вниз

    terminal_output = scrolledtext.ScrolledText(window, width=80, height=20, bg='black', fg='white', font=('Courier', 10), wrap=tk.WORD)
    terminal_output.grid(row=0, column=0, padx=10, pady=10)
    terminal_output.insert(tk.END, get_prompt())
    terminal_output.bind('<Return>', handle_command)  # Привязка нажатия Enter к выполнению команды
    window.mainloop()

if __name__ == "__main__":
    hostname, PC, vfs_path = read_config('config.xml')
    run_shell(hostname, PC, vfs_path)