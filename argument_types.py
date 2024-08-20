from typing import Optional, Literal, List, get_args, AnyStr
from dataclasses import dataclass
from selenium.webdriver.remote.webelement import WebElement

BrowserType = Literal["auto", "firefox", "chrome", "edge", "safari"]
"""String-Literal Type of supported browsers (and their respective drivers)."""
FormatType = Literal["stdout", "txt", "csv", "json"]
"""String-Literal Type of supported output formats."""
Browsers: List[BrowserType] = list(get_args(BrowserType))
"""List of supported browsers' names."""
Formats: List[FormatType] = list(get_args(FormatType))
"""List of supported output formats' extensions."""


@dataclass
class ParserArguments:
    """Data Class container for all available :class:`argparse.ArgumentParser` arguments"""
    browser: BrowserType
    """Browser for Selenium to use."""
    url: AnyStr
    """Base URL for Selenium to use. (NOTE: Generally shouldn't be changed!)"""
    keep: bool
    """Flag to disable cookie deletion when opening Selenium."""
    timeout: float
    """How long should Selenium wait for responses before timing out?"""
    poll_frequency: float
    """How frequently should Selenium poll for responses?"""
    format: Optional[FormatType]
    """Format of output; Cannot be used with Output (`stdout` = print to standard output, extension = `output.{ext}`)"""
    output: Optional[str]
    """Output file path; Cannot be used with Format."""


@dataclass
class Elements:
    """Data Class container for all relevant :class:`WebElement` instances."""
    level_label: Optional[WebElement] = None
    """The label displaying the current level."""
    description: Optional[WebElement] = None
    """The description for the current level."""
    comment: Optional[WebElement] = None
    """The textbox used to enter a comment (message) to the chatbot."""
    comment_submit: Optional[WebElement] = None
    """The submit button used to submit the entered comment (message) to the chatbot."""
    answer: Optional[WebElement] = None
    """The reply to the latest comment (message) to the chatbot (first appears after submitting a comment)."""
    guess: Optional[WebElement] = None
    """The textbox used to enter a guess for the password answer (first appears after submitting a comment)."""
    guess_submit: Optional[WebElement] = None
    """The textbox used to submit the entered password attempt (first appears after submitting a comment)."""
    alert_title: Optional[WebElement] = None
    """The header of the alert messagebox (appears after each password attempt submission)."""
    alert_text: Optional[WebElement] = None
    """The text content of the alert messagebox (appears after each password attempt submission)."""
    alert_submit: Optional[WebElement] = None
    """The button used to submit & close the alert messagebox (appears after each password attempt submission)."""
