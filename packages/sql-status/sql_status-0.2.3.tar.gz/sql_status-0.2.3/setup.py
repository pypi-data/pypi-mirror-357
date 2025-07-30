from setuptools import setup, find_packages

setup(
    name='sql_status',
    version='0.2.3',
    description='Утилита для распаковки шаблона проекта',
    author='sin2t',
    author_email='my@email.com',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'sql_status': ['gia3/**/*', 'gia4/**/*'],
    },
    entry_points={
        'console_scripts': [
            'project-unpack=sql_status.__main__:main',
        ],
    },
    install_requires=[],
    python_requires='>=3.7',
)
