import json
import csv
from datetime import datetime
from json import JSONDecodeError
from typing import Optional, Literal
from selenium import webdriver
from selenium.common import NoSuchDriverException, NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.remote.webdriver import WebDriver
from argument_types import BrowserType, Browsers, ParserArguments, Elements


class Controller:
    """Class used to streamline interacting with the webpage via the desired :class:`WebDriver` instance."""
    _arguments: ParserArguments
    """Parser Arguments received upon initialization."""
    _output_path: Optional[str]
    """The output file path to print to (None = standard output)."""
    _output_encoding: str = "utf"  # Used instead of hard-coding 'utf' everywhere.
    """Encoding for output file."""
    _driver: WebDriver
    """The Selenium :class:`WebDriver` instance used."""
    _elements: Elements
    """The relevant :class:`WebElement` instances used."""
    _wait: WebDriverWait
    """Used to have the :class:`WebDriver` wait for something to happen."""
    _is_interacted: bool
    """Used to indicate whether an initial comment (message) has been sent to the chatbot."""
    _last_comment: Optional[str]

    def __init__(self, arguments: ParserArguments):
        """
        The :class:`Controller` Constructor.

        :param ParserArguments arguments: Parser Arguments for initialization.
        :raises NoSuchDriverException: The `browser` field for the given :param:`arguments` was not recognized.
        """
        self._arguments = arguments
        try:
            if self._arguments.output is not None:  # Print to designated file
                self._output_path = self._arguments.output
            elif self._arguments.format is not None:
                if self._arguments.format == "stdout":  # Print to standard output
                    self._output_path = None
                else:  # Print to file 'output.{format}'
                    self._output_path = f"output.{self._arguments.format}"
            else:
                raise ValueError("No output or format found")
        except ValueError as ex:
            print(*ex.args, "Falling back to 'stdout' (standard output)", sep="; ")
            self._output_path = None
        try:
            self._driver = self.create_driver(self._arguments.browser)
        except NoSuchDriverException as ex:
            self.print(ex.msg, f"Falling back to '{BrowserType[0]}'", sep="; ")
            self._driver = self.create_driver(BrowserType[0])
        if not self._arguments.keep:
            self._driver.delete_all_cookies()
        self._wait = WebDriverWait(self._driver, timeout=10, poll_frequency=.2,  # TODO: timeout & poll_frequency CLI
                                   ignored_exceptions=[NoSuchElementException, ElementNotInteractableException])
        self._driver.get(self._arguments.url)
        self._elements = Elements()
        self._start_level()
        self._last_comment = None

    # def __del__(self):
    #     """
    #     :class:`Controller` Destructor - automatically closes the :class:`WebDriver` instance.
    #     NOTE: Disabled because it apparently causes a race condition.
    #     """
    #     self._driver.close()

    def __str__(self):
        return f"{self._elements.level_label.text}: {self._elements.description.text}"

    def close(self):
        """Closes the underlying :class:`WebDriver` instance."""
        self._driver.close()

    def print(self, *values: object,
              sep: Optional[str] = " ",
              end: Optional[str] = "\n",
              flush: Literal[False] = False) -> None:
        """
        Prints the values to a file-like object (stream), or to `sys.stdout` by default.
        Custom facade for :py:func:`print` to support `stdout` or [TXT, CSV, JSON] files.

        :param *object values: Values to print.
        :param Optional[str] sep: string inserted between values, default a space.
        :param Optional[str] end: string appended after the last value, default a newline.
        :param Literal[False] flush: whether to forcibly flush the stream.
        :return: None
        :rtype: NoneType
        """
        if self._output_path is None:  # Print to standard output
            print(*values, sep=sep, end=end, file=None, flush=flush)
        else:
            if self._output_path.endswith(".json"):  # Print to JSON file
                try:
                    with open(self._output_path, "r", encoding=self._output_encoding) as file:
                        obj = json.loads(file.read())
                except (FileNotFoundError, JSONDecodeError):  # Failed to read from file
                    obj = []
                with open(self._output_path, "w+", encoding=self._output_encoding) as file:
                    for value in values:
                        obj.append(value)
                    json.dump(obj, file)  # TODO: Clear JSON in __init__
            elif self._output_path.endswith(".csv"):  # Print to CSV file
                with open(self._output_path, "a+", encoding=self._output_encoding, newline="") as file:
                    reader = csv.reader(file)
                    line_num = reader.line_num
                    del reader
                    writer = csv.writer(file)  # TODO: Add CSV header in __init__ ?
                    for value in values:
                        writer.writerow([line_num, datetime.now(), str(value)])  # TODO: Better row definition
            else:  # Print to file as regular text ('txt')
                with open(self._output_path, "a+", encoding=self._output_encoding) as file:
                    print(*values, sep=sep, end=end, file=file, flush=flush)

    def create_driver(self, browser: BrowserType = Browsers[0]) -> WebDriver:
        """
        Creates a new :class:`WebDriver` instance, type determined by the name of the browser.

        :param BrowserType browser: The type of browser to use.
        :return: The requested :class:`WebDriver` instance.
        :rtype: DriverType
        """
        driver: Optional[WebDriver] = None
        match browser.lower():
            case "chrome":
                driver = webdriver.Chrome()
            case "edge":
                driver = webdriver.Edge()
            case "firefox":
                driver = webdriver.Firefox()
            case "safari":
                driver = webdriver.Safari()
            case "auto":
                # Iterate through other drivers and find the first one that works.
                for browser in Browsers:
                    if browser == "auto":
                        # Skips "auto" to prevent infinite recursion
                        continue
                    try:
                        driver = self.create_driver(browser)
                    except NoSuchDriverException:
                        self.print(f"No driver found for '{browser}'.")
                    if driver is not None:
                        self.print(f"Driver found for '{browser}'.")
                        break
            case _:
                raise NoSuchDriverException(f"Browser Type not recognized: {browser}")
        return driver

    def _start_level(self):
        """Refresh the stored state of the webpage."""
        self._is_interacted = False
        self._get_all_elements()
        self.print(str(self))  # Happens before

    def _get_all_elements(self):
        """
        Updates the DOM :class:`WebElement` :py:attr:`elements`.

        If the site hasn't been queried yet, the Answer & Guess elements will not be available, and thus skipped.
        """
        # TODO: Refine CSS Selector - "#guess ~ button[type='submit']:first-of-type" ?
        # comment_submit = driver.find_element(by=By.CSS_SELECTOR, value="button.h-7")
        # guess_submit = driver.find_element(by=By.SELECT, value="button.button-white-to-gray-animation:nth-child(2)")
        # comment_submit, guess_submit = driver.find_elements(by=By.CSS_SELECTOR, value="button[type='submit']")[:2]
        self._get_default_elements()
        self._get_answer_elements()
        self._get_guess_elements()

    def submit_comment(self, value: str) -> str:
        """
        Submit a comment for the chatbot.

        :param str value: The comment to submit.
        :return: The answer from the chatbot.
        :rtype: str
        :raises ValueError: Prompt must be at least 10 characters long.
        :raises NoSuchElementException: Couldn't get answer / guess elements.
        """
        if len(value) < 10:
            raise ValueError(f"Prompt must be at least 10 characters long ({value})")
        if value == self._last_comment:
            raise ValueError(f"Prompt cannot be the same as the previous prompt ({value})")
        self._elements.comment.clear()
        self._elements.comment.send_keys(value)
        self._elements.comment_submit.click()
        self._is_interacted = True
        self._last_comment = value  # TODO: Move?
        self._wait.until(lambda _: self._get_answer_elements())
        if not self._has_answer_elements:
            raise NoSuchElementException("Couldn't get answer elements.")
        self._wait.until(lambda _: self._get_guess_elements())
        # TODO: Move?
        if not self._has_guess_elements:
            raise NoSuchElementException("Couldn't get guess elements")
        self.print("(Psst! You can guess the answer now!)")
        return self._elements.answer.text

    def submit_guess(self, value: str) -> str:
        """
        Submit a guess for the password.

        :param str value: The guess for the password.
        :return: The alert message received.
        :rtype: str
        :raises NoSuchElementException: Couldn't get guess / alert elements.
        """
        if not self._has_guess_elements:
            raise NoSuchElementException("You must submit a comment for the level before you can submit a guess!")
        self._elements.guess.clear()
        self._elements.guess.send_keys(value)
        self._elements.guess_submit.click()
        # Handle the alert modal
        self._wait.until(lambda _: self._get_alert_elements())
        if not self._has_alert_elements:
            raise NoSuchElementException("Couldn't get customAlert elements.")
        answer = f"{self._elements.alert_title.text}: {self._elements.alert_text.text}"
        self._elements.alert_submit.click()
        if answer.startswith("You guessed the password!"):
            self._start_level()  # TODO: This prints level details before returning the answer for printing...
        return answer

    @property
    def _has_default_elements(self) -> bool:
        """Whether the default :class:`WebElement` instances are available."""
        return None not in [self._elements.level_label, self._elements.description,
                            self._elements.comment, self._elements.comment_submit]

    def _get_default_elements(self) -> bool:
        """Updates the default :class:`WebElement` instances."""
        self._elements.level_label = self._driver.find_element(by=By.CLASS_NAME, value="level-label")
        self._elements.description = self._driver.find_element(by=By.CLASS_NAME, value="description")
        self._elements.comment = self._driver.find_element(by=By.ID, value="comment")
        self._elements.comment_submit = self._driver.find_element(by=By.CSS_SELECTOR,
                                                                  value="button[type='submit']:nth-child(1)")
        return self._has_default_elements

    @property
    def _has_answer_elements(self) -> bool:
        """Whether the answer :class:`WebElement` instance is available."""
        return None not in [self._elements.answer]

    def _get_answer_elements(self) -> bool:
        """Update the answer :class:`WebElement` instance."""
        # TODO: Answer & Guess only appear after the first query has been sent...
        self._elements.answer = self._driver.find_element(by=By.CLASS_NAME,
                                                          value="answer") if self._is_interacted else None
        return self._has_answer_elements

    @property
    def _has_guess_elements(self) -> bool:
        """Whether the guess :class:`WebElement` instances are available."""
        return None not in [self._elements.guess, self._elements.guess_submit]

    def _get_guess_elements(self) -> bool:
        """Update the guess :class:`WebElement` instances (if available, else set to None)."""
        self._elements.guess = self._driver.find_element(by=By.ID, value="guess") if self._is_interacted else None
        self._elements.guess_submit = self._driver.find_element(by=By.CSS_SELECTOR,
                                                                value="button[type='submit']:nth-child(2)"
                                                                ) if self._is_interacted else None
        return self._has_guess_elements

    @property
    def _has_alert_elements(self) -> bool:
        """Whether the modal alert :class:`WebElement` instances are available."""
        return None not in [self._elements.alert_title, self._elements.alert_text, self._elements.alert_submit]

    def _get_alert_elements(self) -> bool:
        """Update the modal alert :class:`WebElement` instances."""
        self._elements.alert_title, self._elements.alert_text = self._driver.find_elements(
            by=By.CSS_SELECTOR, value=".customAlert div:nth-child(2)")[:2]  # 1st & 2nd matches
        self._elements.alert_submit = self._driver.find_element(by=By.CSS_SELECTOR, value=".customAlert button")
        return self._has_alert_elements


def main(arguments: Optional[ParserArguments] = None):
    """Main function; Instantiates & prints a :class:`Controller` instance with the given CLI arguments."""
    instance = Controller(arguments)
    print(instance)


if __name__ == '__main__':
    main()
