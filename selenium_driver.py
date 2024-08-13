from typing import Optional
from selenium import webdriver
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
                driver = get_driver(browser)
                if driver is not None:
                    break
        case _:
            # TODO: Fallback or Error?
            # raise TypeError(f"Browser Type not supported: {arg}")
            return get_driver("auto")
    return driver


class SeleniumDriver:
    arguments: ParserArguments
    driver: DriverType
    elements: Elements

    def __init__(self, arguments: ParserArguments):
        self.arguments = arguments
        self.driver = get_driver(self.arguments.browser)
        self.get_elements()

    def __del__(self):
        self.driver.close()

    def get_elements(self, is_queried: bool = False):
        """
        Updates the DOM :class:`WebElement` :py:attr:`elements`.

        If the site hasn't been queried yet, the Answer & Guess elements will not be available, and thus skipped.

        :param bool is_queried: Whether the site has been previously queried
        """
        self.driver.get(self.arguments.url)
        # TODO: Refine CSS Selector - "#guess ~ button[type='submit']:first-of-type" ?
        # comment_submit = driver.find_element(by=By.CSS_SELECTOR, value="button.h-7")
        # guess_submit = driver.find_element(by=By.SELECT, value="button.button-white-to-gray-animation:nth-child(2)")
        # comment_submit, guess_submit = driver.find_elements(by=By.CSS_SELECTOR, value="button[type='submit']")[:2]
        self.elements = Elements(level_label=self.driver.find_element(by=By.CLASS_NAME, value="level-label"),
                                 description=self.driver.find_element(by=By.CLASS_NAME, value="description"),
                                 # TODO: Answer & Guess only appear after the first query has been sent...
                                 comment=self.driver.find_element(by=By.ID, value="comment"),
                                 comment_submit=self.driver.find_element(by=By.CSS_SELECTOR,
                                                                         value="button[type='submit']:nth-child(1)"),
                                 answer=self.driver.find_element(by=By.CLASS_NAME,
                                                                 value="answer") if is_queried else None,
                                 guess=self.driver.find_element(by=By.ID, value="guess") if is_queried else None,
                                 guess_submit=self.driver.find_element(by=By.CSS_SELECTOR,
                                                                       value="button[type='submit']:nth-child(2)"
                                                                       ) if not is_queried else None
                                 )

    def submit_comment(self, value: str):
        if len(value) < 10:
            raise ValueError("Prompt must be at least 10 characters long.")
        self.elements.comment.send_keys(value)
        self.elements.comment_submit.click()
        # TODO: Handle answer

    def submit_guess(self, value: str):
        if self.elements.answer is None:
            raise BlockingIOError("You must submit a query before you can submit an answer!")
        self.elements.guess.send_keys(value)
        self.elements.guess_submit.click()
        # TODO: Handle customAlert


def main(arguments: Optional[ParserArguments] = None):
    instance = SeleniumDriver(arguments)


if __name__ == '__main__':
    main()
