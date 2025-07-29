import argparse
from .unpack import unpack_project

def main():
    parser = argparse.ArgumentParser(description='Распаковать шаблон проекта.')
    parser.add_argument('--to', type=str, default=None, help='Папка для распаковки (по умолчанию рядом с исполняемым файлом)')
    args = parser.parse_args()
    unpack_project(args.to)

if __name__ == '__main__':
    main()
