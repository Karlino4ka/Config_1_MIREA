import unittest
import os
import tempfile
import zipfile
from datetime import datetime
from main import VirtualFileSystem, ls, cd, cat, tail, mv

class TestVirtualFileSystem(unittest.TestCase):

    def setUp(self):
        # Создание временной директории для тестирования
        self.test_dir = tempfile.mkdtemp()
        # Создание временного ZIP-файла с тестовыми файлами
        self.zip_file = os.path.join(self.test_dir, 'test.zip')
        with zipfile.ZipFile(self.zip_file, 'w') as zipf:
            zipf.writestr('file1.txt', 'Hello, World!')
            zipf.writestr('file2.txt', 'Goodbye, World!')
            zipf.writestr('file3.txt', 'Hello, World!')
            zipf.writestr('file4.txt', 'Goodbye, World!')
            zipf.writestr('subdir/file3.txt', 'Hello, World!')

        # Инициализация виртуальной файловой системы
        self.vfs = VirtualFileSystem(self.zip_file)

    def tearDown(self):
        # Удаление временной директории после тестов
        for root, dirs, files in os.walk(self.test_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(self.test_dir)

    def test_ls(self):
        # Проверяем вывод команды ls
        expected_output = "File      13        " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " file1.txt\n" \
                          "File      15        " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " file2.txt\n" \
                          "Directory 0        " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " subdir"
        actual_output = ls(self.vfs)
        self.assertIn('file1.txt', actual_output)
        self.assertIn('file2.txt', actual_output)
        self.assertIn('subdir', actual_output)

    def test_cd(self):
        # Переход в подкаталог
        output = cd(self.vfs, 'subdir')
        self.assertIn("Changed directory to", output)
        self.assertEqual(self.vfs.current_path, os.path.join(self.vfs.root, 'subdir'))

    def test_cd_invalid(self):
        # Проверка перехода в несуществующий каталог
        output = cd(self.vfs, 'nonexistent')
        self.assertEqual(output, "Directory not found")

    def test_cat(self):
        # Чтение содержимого файла
        output = cat(self.vfs, 'file1')
        self.assertEqual(output[0], 'Hello, World!')

    def test_cat_invalid(self):
        # Проверка чтения несуществующего файла
        output = cat(self.vfs, 'tvvbyovohuvouvo')
        self.assertEqual(output, 'File not found')

    def test_cat_invalid_extension(self):
        # Проверка чтения файла без расширения
        output = cat(self.vfs, 'file2')
        self.assertEqual(output[0], 'Goodbye, World!')

    def test_tail(self):
        # Чтение содержимого файла
        output = tail(self.vfs, 'file3')
        self.assertEqual(output[0], 'Hello, World!')

    def test_tail_invalid(self):
        # Проверка чтения несуществующего файла
        output = tail(self.vfs, 'tycitvugbuovgit')
        self.assertEqual(output, 'File not found')

    def test_tail_invalid_extension(self):
        # Проверка чтения файла без расширения
        output = tail(self.vfs, 'file4')
        self.assertEqual(output[0], 'Goodbye, World!')

    def test_mv(self):


if __name__ == '__main__':
    unittest.main()