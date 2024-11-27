import os
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime
import tkinter as tk
from tkinter import scrolledtext
import shutil


def read_config(path):
    xml=ET.parse(path)
    return xml.find('user').text, xml.find('PC').text, xml.find('path').text

class VirtualFileSystem:
    def __init__(self, zip_path):
        self.root = "Console"
        self.current_path = self.root
        self.extract_zip(zip_path)

    def extract_zip(self, zip_path):
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(self.root)

    def list_directory(self):
        items = []
        for item in os.listdir(self.current_path):
            item_path = os.path.join(self.current_path, item)
            # Получаем информацию о файле
            stats = os.stat(item_path)
            size = stats.st_size  # Размер в байтах
            modified_time = datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')  # Время изменения
            item_type = 'Directory' if os.path.isdir(item_path) else 'File'
            items.append(f"{item_type: <10} {size: <10} {modified_time} {item}")
        return "\n".join(items)

    def change_directory(self, path):
        if path == '..':
            if self.current_path != self.root:
                self.current_path = os.path.dirname(self.current_path)
            else:
                raise FileNotFoundError("You are already at the root directory")
        else:
            new_path = os.path.join(self.current_path, path)
            if os.path.isdir(new_path):
                self.current_path = new_path
            else:
                raise FileNotFoundError("Directory not found")

    def get_relative_path(self):
        return os.path.relpath(self.current_path, self.root).replace('\\', '/')

    def read_file(self, file_name):
        file_path = os.path.join(self.current_path, file_name)
        if os.path.isfile(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    return file.readlines()
            except UnicodeDecodeError:
                return "Error reading file: unsupported characters"
        else:
            raise FileNotFoundError("File not found")
    def move(self, path_A, path_B):
        try:
            shutil.move(os.path.join(self.current_path, path_A), os.path.join(self.current_path, path_B))
        except FileNotFoundError:
            raise FileNotFoundError("File not found")


# Основные команды (ls, cd, cat, chown, date)
def ls(vfs):
    try:
        return vfs.list_directory()
    except Exception as e:
        return str(e)

def cd(vfs, path):
    # Проверка на использование более чем двух точек подряд
    if path.startswith('...') or '...' in path:
        return "Error: More than two consecutive dots are not allowed in the directory path."

    try:
        vfs.change_directory(path)
        return f"Changed directory to {vfs.current_path}"
    except Exception as e:
        return str(e)

def cat(vfs, file_name):
    exact_file = os.path.join(vfs.current_path, file_name)

    if os.path.isfile(exact_file):
        text = ''
        for line in vfs.read_file(file_name):
            text+=line
        return text

    possible_extensions = ['.txt', '.log', '.conf']
    for ext in possible_extensions:
        file_with_ext = os.path.join(vfs.current_path, file_name + ext)
        if os.path.isfile(file_with_ext):
            return vfs.read_file(file_name + ext)

    return "File not found"

def tail(vfs, file_name):
    exact_file = os.path.join(vfs.current_path, file_name)

    if os.path.isfile(exact_file):
        text = ''
        for line in vfs.read_file(file_name)[-10:]:
            text+=line
        return text

    possible_extensions = ['.txt', '.log', '.conf']
    for ext in possible_extensions:
        file_with_ext = os.path.join(vfs.current_path, file_name + ext)
        if os.path.isfile(file_with_ext):
            text = ''
            for line in vfs.read_file(file_name)[-10:]:
                text += line
            return text

    return "File not found"

def mv(vfs, path_A, path_B):
    try:
        vfs.move(path_A, path_B)
    except Exception as e:
        return str(e)



# Основной цикл работы эмулятора с GUI на tkinter
def run_shell(hostname, PC, vfs_path):
    vfs = VirtualFileSystem(vfs_path)

    def get_prompt():
        relative_path = vfs.get_relative_path()
        if relative_path == '.':
            relative_path = ''
        return f"{PC} {hostname}/{relative_path}> " if relative_path else f"{PC}> "

    def handle_command(event=None):
        # Получаем команду без приглашения
        full_text = terminal_output.get("end-1l linestart", "end-1c").strip()
        command = full_text.replace(get_prompt(), "").strip()  # Извлекаем команду без "PS MyVirtualMachine>"

        if command:

            output = ""

            if command.startswith('ls'):
                output = ls(vfs)
            elif command.startswith('cd'):
                try:
                    _, path = command.split(maxsplit=1)
                    output = cd(vfs, path)
                except ValueError:
                    output = "Please specify a directory."
            elif command.startswith('cat'):
                try:
                    _, file_name = command.split(maxsplit=1)
                    output = cat(vfs, file_name)
                except ValueError:
                    output = "Please specify a file."
            elif command == 'exit':
                window.quit()
            elif command.startswith('tail'):
                try:
                    _, file_name = command.split(maxsplit=1)
                    output=tail(vfs, file_name)
                except ValueError:
                    output = "Please specify a file"
            elif command.startswith('mv'):
                try:
                    _, path_A, path_B = command.split(maxsplit=2)
                    output=mv(vfs, path_A, path_B)
                except ValueError:
                    output = "Please specify a file"
            else:
                output = "Unknown command"

            terminal_output.insert(tk.END, f"\n{output}\n{get_prompt()}")
            terminal_output.see(tk.END)  # Прокрутка вниз

    window = tk.Tk()
    window.title(f"{hostname}")

    terminal_output = scrolledtext.ScrolledText(window, width=80, height=20, bg='black', fg='white', font=('Courier', 10), wrap=tk.WORD)
    terminal_output.grid(row=0, column=0, padx=10, pady=10)
    terminal_output.insert(tk.END, get_prompt())
    terminal_output.bind('<Return>', handle_command)  # Привязка нажатия Enter к выполнению команды
    window.mainloop()

if __name__ == "__main__":
    hostname, PC, vfs_path = read_config('config.xml')
    run_shell(hostname, PC, vfs_path)