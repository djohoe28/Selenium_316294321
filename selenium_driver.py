from typing import Optional
from selenium import webdriver
from selenium.common import NoSuchDriverException, NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from argument_types import BrowserType, Browsers, DriverType, ParserArguments, Elements


def get_driver(browser: BrowserType = Browsers[0]) -> DriverType:
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
            # TODO: Surround with try-catch ?
            # Iterate through other drivers and find the first one that works.
            for browser in Browsers:
                if browser == "auto":
                    continue
                try:
                    driver = get_driver(browser)
                except NoSuchDriverException:
                    print(f"No driver found for {browser.capitalize()}.")
                if driver is not None:
                    print(f"Driver found for {browser}.")
                    break
        case _:
            # TODO: raise TypeError(f"Browser Type not supported: {arg}")
            print(f"Browser {browser} not recognized - falling back to auto.")
            return get_driver("auto")
    return driver


class SeleniumDriver:
    """Class used to streamline handling the Selenium Driver"""
    _arguments: ParserArguments
    """Parser Arguments received upon initialization"""
    _driver: DriverType
    """The Selenium WebDriver used"""
    _elements: Elements
    """The relevant :class:`WebElement` instances used"""
    _wait: WebDriverWait
    """Used to have the WebDriver wait for something to happen"""
    _is_queried: bool
    """Used to indicate whether an initial comment (message) has been sent to the chatbot"""
    _is_submitted: bool  # TODO: Unused?
    """Used to indicate that a password guess has been submitted; Returns to False when customAlert is closed"""

    def __init__(self, arguments: ParserArguments):
        """:class:`SeleniumDriver` Constructor - initializes all :py:attr:`_elements`"""
        self._arguments = arguments
        self._driver = get_driver(self._arguments.browser)
        self._wait = WebDriverWait(self._driver, timeout=2, poll_frequency=.2,
                                   ignored_exceptions=[NoSuchElementException, ElementNotInteractableException])
        self._is_queried = False
        self._is_submitted = False
        self._elements = Elements(None, None, None, None, None, None, None, None, None, None)  # TODO: Make generic
        self._get_all_elements()  # TODO: Extract?

    def __del__(self):
        """:class:`SeleniumDriver` Destructor - automatically closes the Selenium WebDriver instance."""
        self._driver.close()

    def _get_all_elements(self):
        """
        Updates the DOM :class:`WebElement` :py:attr:`elements`.

        If the site hasn't been queried yet, the Answer & Guess elements will not be available, and thus skipped.
        """
        self._driver.get(self._arguments.url)
        # TODO: Refine CSS Selector - "#guess ~ button[type='submit']:first-of-type" ?
        # comment_submit = driver.find_element(by=By.CSS_SELECTOR, value="button.h-7")
        # guess_submit = driver.find_element(by=By.SELECT, value="button.button-white-to-gray-animation:nth-child(2)")
        # comment_submit, guess_submit = driver.find_elements(by=By.CSS_SELECTOR, value="button[type='submit']")[:2]
        self._get_default_elements()
        if self._is_queried:
            self._get_answer_elements()
            self._get_guess_elements()

    def submit_comment(self, value: str) -> str:
        if len(value) < 10:
            raise ValueError("Prompt must be at least 10 characters long.")
        self._elements.comment.send_keys(value)
        self._elements.comment_submit.click()
        self._is_queried = True
        self._wait.until(lambda _: self._get_answer_elements())
        if not self._has_answer_elements:
            raise NoSuchElementException("Couldn't get answer elements.")
        return self._elements.answer.text

    def submit_guess(self, value: str) -> str:
        if not self._has_guess_elements:
            raise BlockingIOError("You must submit a query before you can submit an answer!")
        self._elements.guess.send_keys(value)
        self._elements.guess_submit.click()
        self._wait.until(lambda _: self._get_alert_elements())
        if not self._has_alert_elements:
            raise NoSuchElementException("Couldn't get customAlert elements.")
        return f"{self._elements.alert_title.text}: {self._elements.alert_text.text}"  # TODO: Check if answer's correct

    @property
    def _has_default_elements(self) -> bool:
        return None not in [self._elements.level_label, self._elements.description,
                            self._elements.comment, self._elements.comment_submit]

    def _get_default_elements(self) -> bool:
        self._elements.level_label = self._driver.find_element(by=By.CLASS_NAME, value="level-label")
        self._elements.description = self._driver.find_element(by=By.CLASS_NAME, value="description")
        self._elements.comment = self._driver.find_element(by=By.ID, value="comment")
        self._elements.comment_submit = self._driver.find_element(by=By.CSS_SELECTOR,
                                                                  value="button[type='submit']:nth-child(1)")
        return self._has_default_elements

    @property
    def _has_answer_elements(self) -> bool:
        return None not in [self._elements.answer]

    def _get_answer_elements(self) -> bool:
        # TODO: Answer & Guess only appear after the first query has been sent...
        self._elements.answer = self._driver.find_element(by=By.CLASS_NAME,
                                                          value="answer") if self._is_queried else None
        return self._has_answer_elements

    @property
    def _has_guess_elements(self) -> bool:
        return None not in [self._elements.guess, self._elements.guess_submit]

    def _get_guess_elements(self) -> bool:
        self._elements.guess = self._driver.find_element(by=By.ID, value="guess") if self._is_queried else None
        self._elements.guess_submit = self._driver.find_element(by=By.CSS_SELECTOR,
                                                                value="button[type='submit']:nth-child(2)"
                                                                ) if self._is_queried else None
        return self._has_guess_elements

    @property
    def _has_alert_elements(self) -> bool:
        return None not in [self._elements.alert_title, self._elements.alert_text, self._elements.alert_submit]

    def _get_alert_elements(self) -> bool:
        self._elements.alert_title, self._elements.alert_text = self._driver.find_elements(
            by=By.CSS_SELECTOR, value=".customAlert div:nth-child(2)")[:2]  # 1st & 2nd matches
        self._elements.alert_submit = self._driver.find_element(by=By.CSS_SELECTOR, value=".customAlert button")
        return self._has_alert_elements


def main(arguments: Optional[ParserArguments] = None):
    instance = SeleniumDriver(arguments)


if __name__ == '__main__':
    main()
