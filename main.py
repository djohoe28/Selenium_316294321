import interface
from argument_parser import get_parser_arguments


def main():
    """Main function; Runs the program."""
    interface.main(get_parser_arguments())


if __name__ == '__main__':
    main()
