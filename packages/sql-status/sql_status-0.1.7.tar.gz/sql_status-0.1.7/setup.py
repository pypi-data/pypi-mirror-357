from setuptools import setup, find_packages

setup(
    name='sql_status',
    version='0.1.7',
    description='Утилита для распаковки шаблона проекта',
    author='sin2t',
    author_email='my@email.com',
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'project-unpack=sql_status.__main__:main',
        ],
    },
    install_requires=[],
    python_requires='>=3.7',
)
