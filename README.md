# Gandalf CLI

Command Line Interface for Lakera AI's [Gandalf Challenge](https://gandalf.lakera.ai/baseline).

|   Key   |           Value           |
|:-------:|:-------------------------:|
|  Name   |    Jonathan Eddie Amir    |
|  ID #   |         316294321         |
| Course  | Operating Systems & Linux |
| Teacher |       Daniel Ohayon       |
| School  |    Tel Hai Engineering    |
|  Year   |  2023-2024, 2nd Semester  |

Also available on: https://github.com/djohoe28/Selenium_316294321

# Introduction

This CLI is intended to streamline & allow automation for Lakera AI's Gandalf Challenge.

# Installation

Same as [Selenium](https://www.selenium.dev/selenium/docs/api/py/index.html#installing), including
your [driver](https://www.selenium.dev/selenium/docs/api/py/index.html#drivers) of choice.

# Usage

For CLI instructions, please run `main.py --help` in Command Prompt or equivalent.

# Modules

- [argument_types.py](argument_types.py) - Header file used to declare types, constants, and data classes.
- [argument_parser.py](argument_parser.py) - Generates the argument parser using `argparse`, and parses the arguments given.
- [controller.py](controller.py) - Class used to streamline interacting with the webpage via the desired `WebDriver` instance.
- [interface.py](interface.py) - Class used to have the Command Line interface with `Controller`.
- [main.py](main.py) - Used to run the program.

# Libraries

- [Selenium](https://www.selenium.dev/) - Web Scraping
- [argparse](https://docs.python.org/3/library/argparse.html) - Argument Parsing for Command Line Interface
- [CSV](https://docs.python.org/3/library/csv.html) - .csv file support for output
- [JSON](https://docs.python.org/3/library/json.html) - .json file support for output

# TODO:

- Encrypt output
- Pass all levels when no arguments are given
- Better CSV & JSON integrations