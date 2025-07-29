import os
import shutil
import pkg_resources


def unpack_project(target_dir=None):
    """
    Распаковать все содержимое sql_status в целевую папку (по умолчанию рядом с исполняемым файлом).
    """
    if target_dir is None:
        target_dir = os.path.dirname(os.path.abspath(__file__))
    # Получаем путь к папке sql_status внутри установленного пакета
    source_dir = pkg_resources.resource_filename('sql_status', '')
    exclude_files = {'__init__.py', '__main__.py', 'unpack.py'}
    for root, dirs, files in os.walk(source_dir):
        rel_path = os.path.relpath(root, source_dir)
        dest_dir = os.path.join(target_dir, rel_path) if rel_path != '.' else target_dir
        os.makedirs(dest_dir, exist_ok=True)
        for file in files:
            if file in exclude_files:
                continue
            shutil.copy2(os.path.join(root, file), os.path.join(dest_dir, file))
    print(f'Проект успешно распакован в {target_dir}')
