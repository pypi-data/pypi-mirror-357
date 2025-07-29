from setuptools import setup, find_packages
import os

# Собираем все файлы из текущей папки (кроме project_template и setup.py)
def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            full_path = os.path.join(path, filename)
            rel_path = os.path.relpath(full_path, directory)
            paths.append(os.path.join('template_files', rel_path))
    return paths

extra_files = package_files('.')

setup(
    name='sql_status',
    version='0.1.5',
    description='Утилита для распаковки шаблона проекта',
    author='sin2t',
    author_email='my@email.com',
    packages=find_packages(),
    package_data={'sql_status': extra_files},
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'project-unpack=sql_status.__main__:main',
        ],
    },
    install_requires=[],
    python_requires='>=3.7',
)
