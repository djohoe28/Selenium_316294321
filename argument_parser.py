import argparse
from typing import Optional

from argument_types import ParserArguments, Browsers, Formats


def get_parser_arguments() -> ParserArguments:
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--browser",
                        choices=Browsers, default=Browsers[0],
                        help="Browser for Selenium to use")
    parser.add_argument("-u", "--url",
                        default="https://gandalf.lakera.ai/gandalf-the-white",
                        help="Base URL for Selenium to use")
    parser.add_argument("-f", "--format",
                        choices=Formats, default=Formats[0],
                        help="Format of output file")
    # TODO: Add level argument? Keep cookie cache?
    parser.add_argument("-o", "--output", type=Optional[str], help="Path to output file")
    args = parser.parse_args()
    return ParserArguments(**vars(args))


def main():
    args = get_parser_arguments()
    print(args)


if __name__ == '__main__':
    main()
