from typing import Optional, Literal, List, Union, get_args
from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement

BrowserType = Literal["auto", "firefox", "chrome", "edge", "safari"]
FormatType = Literal["stdout", "txt", "csv", "json"]
Browsers: List[BrowserType] = list(get_args(BrowserType))
Formats: List[FormatType] = list(get_args(FormatType))
DriverType = Union[webdriver.Chrome, webdriver.Edge, webdriver.Firefox, webdriver.Safari]


@dataclass
class ParserArguments:
    """Data Class container for all available :class:`argparse.ArgumentParser` arguments"""
    browser: BrowserType
    """Browser for Selenium to use"""
    url: str
    """Base URL for Selenium to use"""
    format: FormatType
    """Format of output file (stdout = print to standard output)"""
    output: str
    """Path to output file"""


@dataclass
class Elements:
    """Data Class container for all relevant :class:`WebElement` instances"""
    level_label: Optional[WebElement] = None
    """The label displaying the current level"""
    description: Optional[WebElement] = None
    """The description for the current level"""
    comment: Optional[WebElement] = None
    """The textbox used to enter a comment (message) to the chatbot"""
    comment_submit: Optional[WebElement] = None
    """The submit button used to submit the entered comment (message) to the chatbot"""
    answer: Optional[WebElement] = None
    """The reply to the latest comment (message) to the chatbot (first appears after submitting a comment)"""
    guess: Optional[WebElement] = None
    """The textbox used to enter a guess for the password answer (first appears after submitting a comment)"""
    guess_submit: Optional[WebElement] = None
    """The textbox used to submit the entered password attempt (first appears after submitting a comment)"""
    alert_title: Optional[WebElement] = None
    """The header of the alert messagebox (appears after each password attempt submission)"""
    alert_text: Optional[WebElement] = None
    """The text content of the alert messagebox (appears after each password attempt submission)"""
    alert_submit: Optional[WebElement] = None
    """The button used to submit & close the alert messagebox (appears after each password attempt submission)"""
