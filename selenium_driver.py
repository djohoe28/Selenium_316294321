from typing import Optional
from selenium import webdriver
from selenium.webdriver.common.by import By

from argument_types import BrowserType, Browsers, DriverType, ParserArguments, Elements


def get_driver(arg: BrowserType = Browsers[0]) -> DriverType:
    driver: Optional[DriverType] = None
    match arg:
        case "chrome":
            driver = webdriver.Chrome()
        case "edge":
            driver = webdriver.Edge()
        case "firefox":
            driver = webdriver.Firefox()
        case "safari":
            driver = webdriver.Safari()
        case "auto":
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


def main(args: Optional[ParserArguments] = None):
    print("Selenium Driver - Main")
    driver = get_driver(args.browser)
    driver.get(args.url)
    # TODO: Refine CSS Selector - "#guess ~ button[type='submit']:first-of-type" ?
    # comment_submit = driver.find_element(by=By.CSS_SELECTOR, value="button.h-7")
    # guess_submit = driver.find_element(by=By.CSS_SELECTOR, value="button.button-white-to-gray-animation:nth-child(2)")
    # comment_submit, guess_submit = driver.find_elements(by=By.CSS_SELECTOR, value="button[type='submit']")[:2]
    elements = Elements(level_label=driver.find_element(by=By.CLASS_NAME, value="level-label"),
                        description=driver.find_element(by=By.CLASS_NAME, value="description"),
                        # TODO: Answer & Guess only appear after the first query has been sent...
                        comment=driver.find_element(by=By.ID, value="comment"),
                        comment_submit=driver.find_element(by=By.CSS_SELECTOR,
                                                           value="button[type='submit']:nth-child(1)"),
                        answer=None,  # driver.find_element(by=By.CLASS_NAME, value="answer"),
                        guess=None,  # driver.find_element(by=By.ID, value="guess"),
                        guess_submit=None  # driver.find_element(CSS_SELECT, value="button[type='submit']:nth-child(2)")
                        )
    print(elements.description)
    driver.quit()


if __name__ == '__main__':
    main()
