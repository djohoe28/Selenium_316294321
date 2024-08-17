from typing import Optional
from selenium import webdriver
from selenium.common import NoSuchDriverException, NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from argument_types import BrowserType, Browsers, DriverType, ParserArguments, Elements


def get_driver(browser: BrowserType = Browsers[0]) -> DriverType:
    """
    Gets a new Selenium WebDriver instance by the name of the browser.

    :param BrowserType browser: The type of browser to use
    :return: The requested :class:`WebDriver`
    :rtype: DriverType
    """
    driver: Optional[DriverType] = None
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
                    driver = get_driver(browser)
                except NoSuchDriverException:
                    print(f"No driver found for \"{browser}\".")
                if driver is not None:
                    print(f"Driver found for \"{browser}\".")
                    break
        case _:
            raise NoSuchDriverException(f"Browser Type not recognized: {browser}")
    return driver


class Controller:
    """Class used to streamline interacting with the webpage via Selenium WebDriver"""
    _arguments: ParserArguments
    """Parser Arguments received upon initialization"""
    _driver: DriverType
    """The Selenium WebDriver used"""
    _elements: Elements
    """The relevant :class:`WebElement` instances used"""
    _wait: WebDriverWait
    """Used to have the WebDriver wait for something to happen"""
    _is_interacted: bool
    """Used to indicate whether an initial comment (message) has been sent to the chatbot"""
    _is_submitted: bool  # TODO: Unused?
    """Used to indicate that a password guess has been submitted; Returns to False when customAlert is closed"""

    def __init__(self, arguments: ParserArguments):
        """
        The :class:`Controller` Constructor

        :param ParserArguments arguments: Parser Arguments for initialization
        :raises NoSuchDriverException: The `browser` field for the given :param:`arguments` was not recognized
        """
        self._arguments = arguments  # TODO: address url argument
        try:
            self._driver = get_driver(self._arguments.browser)
        except NoSuchDriverException as ex:
            print(ex.msg, f"Falling back to \"{BrowserType[0]}\"", sep="; ")
            self._driver = get_driver(BrowserType[0])
        self._driver.delete_all_cookies()  # TODO: Parser Argument
        self._wait = WebDriverWait(self._driver, timeout=2, poll_frequency=.2,
                                   ignored_exceptions=[NoSuchElementException, ElementNotInteractableException])
        self._driver.get(self._arguments.url)
        self._elements = Elements()
        self._start_level()

    # def __del__(self):
    #     """
    #     :class:`Controller` Destructor - automatically closes the Selenium WebDriver instance.
    #     NOTE: Disabled because it apparently causes a race condition.
    #     """
    #     self._driver.close()

    def __str__(self):
        return f"{self._elements.level_label.text}: {self._elements.description.text}"

    def _start_level(self):
        """Refresh the stored state of the webpage"""
        self._is_interacted = False
        self._is_submitted = False
        self._get_all_elements()
        print(self)

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
        Submit a comment for the chatbot

        :param str value: The comment to submit
        :return: The answer from the chatbot
        :rtype: str
        :raises BlockingIOError: Prompt must be at least 10 characters long
        :raises NoSuchElementException: Couldn't get answer / guess elements
        """
        if len(value) < 10:
            raise BlockingIOError("Prompt must be at least 10 characters long.")
        self._elements.comment.clear()
        self._elements.comment.send_keys(value)
        self._elements.comment_submit.click()
        self._is_interacted = True
        self._wait.until(lambda _: self._get_answer_elements())
        if not self._has_answer_elements:
            raise NoSuchElementException("Couldn't get answer elements.")
        self._wait.until(lambda _: self._get_guess_elements())
        # TODO: Move?
        if not self._has_guess_elements:
            raise NoSuchElementException("Couldn't get guess elements")
        print("(Psst! You can guess the answer now!)")
        return self._elements.answer.text

    def submit_guess(self, value: str) -> str:
        """
        Submit a guess for the password

        :param str value: The guess for the password
        :return: The alert message received
        :rtype: str
        :raises NoSuchElementException: Couldn't get guess / alert elements
        """
        if not self._has_guess_elements:
            raise NoSuchElementException("You must submit a comment for the level before you can submit a guess!")
        self._elements.guess.clear()
        self._elements.guess.send_keys(value)
        self._elements.guess_submit.click()
        self._wait.until(lambda _: self._get_alert_elements())
        if not self._has_alert_elements:
            raise NoSuchElementException("Couldn't get customAlert elements.")
        answer = f"{self._elements.alert_title.text}: {self._elements.alert_text.text}"  # TODO: Check if answer correct
        self._elements.alert_submit.click()
        if answer.startswith("You guessed the password!"):
            self._start_level()
        return answer

    @property
    def _has_default_elements(self) -> bool:
        """Whether the default :class:`WebElement` instances are available"""
        return None not in [self._elements.level_label, self._elements.description,
                            self._elements.comment, self._elements.comment_submit]

    def _get_default_elements(self) -> bool:
        """Updates the default :class:`WebElement` instances"""
        self._elements.level_label = self._driver.find_element(by=By.CLASS_NAME, value="level-label")
        self._elements.description = self._driver.find_element(by=By.CLASS_NAME, value="description")
        self._elements.comment = self._driver.find_element(by=By.ID, value="comment")
        self._elements.comment_submit = self._driver.find_element(by=By.CSS_SELECTOR,
                                                                  value="button[type='submit']:nth-child(1)")
        return self._has_default_elements

    @property
    def _has_answer_elements(self) -> bool:
        """Whether the answer :class:`WebElement` instance is available"""
        return None not in [self._elements.answer]

    def _get_answer_elements(self) -> bool:
        """Update the answer :class:`WebElement` instance"""
        # TODO: Answer & Guess only appear after the first query has been sent...
        self._elements.answer = self._driver.find_element(by=By.CLASS_NAME,
                                                          value="answer") if self._is_interacted else None
        return self._has_answer_elements

    @property
    def _has_guess_elements(self) -> bool:
        """Whether the guess :class:`WebElement` instances are available"""
        return None not in [self._elements.guess, self._elements.guess_submit]

    def _get_guess_elements(self) -> bool:
        """Update the guess :class:`WebElement` instances (if available, else set to None)"""
        self._elements.guess = self._driver.find_element(by=By.ID, value="guess") if self._is_interacted else None
        self._elements.guess_submit = self._driver.find_element(by=By.CSS_SELECTOR,
                                                                value="button[type='submit']:nth-child(2)"
                                                                ) if self._is_interacted else None
        return self._has_guess_elements

    @property
    def _has_alert_elements(self) -> bool:
        """Whether the modal alert :class:`WebElement` instances are available"""
        return None not in [self._elements.alert_title, self._elements.alert_text, self._elements.alert_submit]

    def _get_alert_elements(self) -> bool:
        """Update the modal alert :class:`WebElement` instances"""
        self._elements.alert_title, self._elements.alert_text = self._driver.find_elements(
            by=By.CSS_SELECTOR, value=".customAlert div:nth-child(2)")[:2]  # 1st & 2nd matches
        self._elements.alert_submit = self._driver.find_element(by=By.CSS_SELECTOR, value=".customAlert button")
        return self._has_alert_elements


def main(arguments: Optional[ParserArguments] = None):
    instance = Controller(arguments)
    print(instance)


if __name__ == '__main__':
    main()
