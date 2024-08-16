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
        self._arguments = arguments  # TODO: address url argument
        self._driver = get_driver(self._arguments.browser)
        self._driver.delete_all_cookies()  # TODO: Parser Argument
        self._wait = WebDriverWait(self._driver, timeout=2, poll_frequency=.2,
                                   ignored_exceptions=[NoSuchElementException, ElementNotInteractableException])
        self._is_queried = False
        self._is_submitted = False
        self._elements = Elements(None, None, None, None, None, None, None, None, None, None)  # TODO: Make generic
        self._get_all_elements()  # TODO: Extract?
        print(self._elements.level_label.text)  # TODO: Move?

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
        self._elements.comment.clear()
        self._elements.comment.send_keys(value)
        self._elements.comment_submit.click()
        self._is_queried = True
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
        if not self._has_guess_elements:
            raise BlockingIOError("You must submit a query before you can submit an answer!")
        self._elements.guess.clear()
        self._elements.guess.send_keys(value)
        self._elements.guess_submit.click()
        self._wait.until(lambda _: self._get_alert_elements())
        if not self._has_alert_elements:
            raise NoSuchElementException("Couldn't get customAlert elements.")
        # TODO: Move?
        answer = f"{self._elements.alert_title.text}: {self._elements.alert_text.text}"  # TODO: Check if answer correct
        self._elements.alert_submit.click()
        # print(self._elements.level_label.text)
        # TODO: stale element (see bottom)
        return answer

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

# TODO:
""" 
selenium.common.exceptions.StaleElementReferenceException: Message: The element with the reference daefa989-1570-416c-9be8-cf5ebfc6bdaf is stale; either its node document is not the active document, or it is no longer connected to the DOM; For documentation on this error, please visit: https://www.selenium.dev/documentation/webdriver/troubleshooting/errors#stale-element-reference-exception
Stacktrace:
RemoteError@chrome://remote/content/shared/RemoteError.sys.mjs:8:8
WebDriverError@chrome://remote/content/shared/webdriver/Errors.sys.mjs:193:5
StaleElementReferenceError@chrome://remote/content/shared/webdriver/Errors.sys.mjs:725:5
getKnownElement@chrome://remote/content/marionette/json.sys.mjs:401:11
deserializeJSON@chrome://remote/content/marionette/json.sys.mjs:259:20
cloneObject@chrome://remote/content/marionette/json.sys.mjs:59:24
deserializeJSON@chrome://remote/content/marionette/json.sys.mjs:289:16
json.deserialize@chrome://remote/content/marionette/json.sys.mjs:293:10
receiveMessage@chrome://remote/content/marionette/actors/MarionetteCommandsChild.sys.mjs:73:30


Process finished with exit code 1
"""