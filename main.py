import selenium_driver
from argument_parser import get_parser_arguments


def main():
    args = get_parser_arguments()
    selenium_driver.main(args=args)


if __name__ == '__main__':
    main()
