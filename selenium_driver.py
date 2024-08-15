from typing import Optional
from selenium import webdriver
from selenium.common import NoSuchDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

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
    _arguments: ParserArguments
    _driver: DriverType
    _elements: Elements
    _is_queried: bool
    _is_submitted: bool

    def __init__(self, arguments: ParserArguments):
        self._arguments = arguments
        self._driver = get_driver(self._arguments.browser)
        self._is_queried = False
        self._is_submitted = False
        self._elements = Elements(None, None, None, None, None, None, None)  # TODO: Make generic
        self._get_all_elements()  # TODO: Extract?

    def __del__(self):
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
        self._is_queried = True  # Wait?
        # TODO: Handle answer
        return self._elements.answer.text  # TODO: response: [answer, success] ?

    def submit_guess(self, value: str):
        if self._elements.answer is None:
            raise BlockingIOError("You must submit a query before you can submit an answer!")
        self._elements.guess.send_keys(value)
        self._elements.guess_submit.click()
        # TODO: Handle customAlert
        return self._elements.answer.text  # TODO: response: [answer, success] ?

    def _get_default_elements(self):
        self._elements.level_label = self._driver.find_element(by=By.CLASS_NAME, value="level-label")
        self._elements.description = self._driver.find_element(by=By.CLASS_NAME, value="description"),
        self._elements.comment = self._driver.find_element(by=By.ID, value="comment"),
        self._elements.comment_submit = self._driver.find_element(by=By.CSS_SELECTOR,
                                                                  value="button[type='submit']:nth-child(1)"),

    def _get_answer_elements(self):
        # TODO: Answer & Guess only appear after the first query has been sent...
        self._elements.answer = self._driver.find_element(by=By.CLASS_NAME,
                                                          value="answer") if self._is_queried else None

    def _get_guess_elements(self):
        self._elements.guess = self._driver.find_element(by=By.ID, value="guess") if self._is_queried else None
        self._elements.guess_submit = self._driver.find_element(by=By.CSS_SELECTOR,
                                                                value="button[type='submit']:nth-child(2)"
                                                                ) if self._is_queried else None


def main(arguments: Optional[ParserArguments] = None):
    instance = SeleniumDriver(arguments)


if __name__ == '__main__':
    main()
