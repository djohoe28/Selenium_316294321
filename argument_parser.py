import argparse
from argument_types import ParserArguments, Browsers, Formats


def get_parser_arguments() -> ParserArguments:
    """Generates the argument parser using `argparse`, and parses the arguments given."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--browser",
                        choices=Browsers, default=Browsers[0],
                        help="Browser for Selenium to use.")
    # parser.add_argument("-u", "--url",
    #                     default="https://gandalf.lakera.ai/gandalf-the-white",
    #                     help="Base URL for Selenium to use")
    # NOTE: Disabled because this is generally intended for internal use only.
    parser.add_argument("-t", "--timeout",
                        default=10, type=float, help="How long should Selenium wait for responses before timing out?")
    parser.add_argument("-p", "--poll-frequency",
                        default=.2, type=float, help="How frequently should Selenium poll for responses?")
    parser.add_argument("-k", "--keep",
                        action="store_true", default=False,
                        help="Flag to disable cookie deletion when opening Selenium.")
    # Output Group
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-f", "--format", choices=Formats,  # type=Optional[FormatType], default=Formats[0],
                       help="Format of output ('stdout' = print to standard output, file extension = 'output.{ext}'")
    group.add_argument("-o", "--output",
                       help=f"Path for file output (supported extensions: {Formats}, defaults to 'txt')")
    args = parser.parse_args()
    return ParserArguments(**vars(args))


def main():
    """Main function; prints the parsed CLI arguments."""
    args = get_parser_arguments()
    print(args)


if __name__ == '__main__':
    main()
