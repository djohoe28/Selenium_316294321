from typing import Optional, Literal, List, Union, get_args
from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement

BrowserType = Literal["auto", "firefox", "chrome", "edge", "safari"]
FormatType = Literal["txt", "csv", "json"]
Browsers: List[BrowserType] = list(get_args(BrowserType))
Formats: List[FormatType] = list(get_args(FormatType))
DriverType = Union[webdriver.Chrome, webdriver.Edge, webdriver.Firefox, webdriver.Safari]


@dataclass
class ParserArguments:
    browser: BrowserType
    url: str
    format: FormatType
    output: str


@dataclass
class Elements:
    level_label: Optional[WebElement]
    description: Optional[WebElement]
    comment: Optional[WebElement]
    comment_submit: Optional[WebElement]
    answer: Optional[WebElement]
    guess: Optional[WebElement]
    guess_submit: Optional[WebElement]
