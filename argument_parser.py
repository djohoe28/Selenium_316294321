import argparse
from typing import Optional

from argument_types import ParserArguments, Browsers, Formats, FormatType


def get_parser_arguments() -> ParserArguments:
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--browser",
                        choices=Browsers, default=Browsers[0],
                        help="Browser for Selenium to use")
    parser.add_argument("-u", "--url",
                        default="https://gandalf.lakera.ai/gandalf-the-white",
                        help="Base URL for Selenium to use")
    parser.add_argument("-k", "--keep",
                        action="store_true", default=False,
                        help="Flag to disable cookie deletion when opening Selenium")
    # Output Group
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-f", "--format", choices=Formats,  # type=Optional[FormatType], default=Formats[0],
                       help="Format of output ('stdout' = print to standard output, file extension = 'output.{ext}'")
    group.add_argument("-o", "--output",
                       help=f"Path for file output (supported extensions: {Formats}, defaults to 'txt')")
    args = parser.parse_args()
    return ParserArguments(**vars(args))


def main():
    args = get_parser_arguments()
    print(args)


if __name__ == '__main__':
    main()
