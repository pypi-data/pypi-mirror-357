import os
import shutil
import pkg_resources


def unpack_project(target_dir=None, template='gia3'):
    """
    Распаковать содержимое выбранного шаблона (gia3 или gia4) в целевую папку.
    :param target_dir: Куда распаковать (по умолчанию — текущая рабочая директория)
    :param template: 'gia3' или 'gia4'
    """
    if target_dir is None:
        target_dir = os.getcwd()
    # Проверяем корректность шаблона
    if template not in ('gia3', 'gia4'):
        raise ValueError("template должен быть 'gia3' или 'gia4'")
    # Получаем путь к папке шаблона внутри установленного пакета
    source_dir = pkg_resources.resource_filename('sql_status', template)
    if not os.path.exists(source_dir):
        raise FileNotFoundError(f"Шаблон {template} не найден в пакете.")
    for root, dirs, files in os.walk(source_dir):
        rel_path = os.path.relpath(root, source_dir)
        dest_dir = os.path.join(target_dir, rel_path) if rel_path != '.' else target_dir
        os.makedirs(dest_dir, exist_ok=True)
        for file in files:
            shutil.copy2(os.path.join(root, file), os.path.join(dest_dir, file))
    print(f'Шаблон {template} успешно распакован в {target_dir}')
