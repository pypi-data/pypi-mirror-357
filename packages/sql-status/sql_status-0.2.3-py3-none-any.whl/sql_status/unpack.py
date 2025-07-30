import os
import shutil
import pkg_resources


def unpack_project(*args, **kwargs):
    """
    Распаковать содержимое выбранного шаблона (gia3 или gia4) в целевую папку.
    Можно вызывать:
        unpack_project()  # по умолчанию gia3 в текущую папку
        unpack_project('gia4')  # gia4 в текущую папку
        unpack_project(target_dir='.', template='gia4')
        unpack_project('gia4', target_dir='...')
        unpack_project('.', 'gia4')
    """
    # Разбор аргументов
    target_dir = '.'
    template = 'gia3'
    if len(args) == 1:
        if args[0] in ('gia3', 'gia4'):
            template = args[0]
        else:
            target_dir = args[0]
    elif len(args) == 2:
        target_dir, template = args
    # Переопределение через именованные параметры
    if 'target_dir' in kwargs:
        target_dir = kwargs['target_dir']
    if 'template' in kwargs:
        template = kwargs['template']
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
