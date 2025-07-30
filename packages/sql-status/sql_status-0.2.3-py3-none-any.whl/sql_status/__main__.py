import argparse
from .unpack import unpack_project

def main():
    parser = argparse.ArgumentParser(description='Распаковать шаблон проекта.')
    parser.add_argument('--to', type=str, default=None, help='Папка для распаковки (по умолчанию рядом с исполняемым файлом)')
    parser.add_argument('--template', type=str, default='gia3', choices=['gia3', 'gia4'], help='Шаблон для распаковки: gia3 или gia4')
    args = parser.parse_args()
    unpack_project(args.to, template=args.template)

if __name__ == '__main__':
    main()
