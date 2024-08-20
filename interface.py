from typing import Optional, Union, Any

from selenium.common import NoSuchElementException

from argument_types import ParserArguments
from controller import Controller


class Interface:
    """Command Line Interface class for :class:`Controller`."""
    _controller: Controller
    """The underlying :class:`Controller` instance."""

    def __init__(self, args_or_driver: Union[ParserArguments, Controller]):
        if isinstance(args_or_driver, Controller):
            self._controller = args_or_driver
        elif isinstance(args_or_driver, ParserArguments):
            self._controller = Controller(args_or_driver)
        else:
            raise ValueError(f"Parameter must be either ParserArguments or Controller.")

    def run(self):
        """
        Run the CLI (REPL).

        help
            Prints this text.

        comment [text]
            Ask Gandalf question.

        guess [text]
            Submit password attempt.

        exit | quit
            Terminate the program.
        """
        command: str = ""
        """Command received via user input; Expecting string literal in ['help', 'comment', 'guess', 'quit', 'exit']."""
        query: Optional[str] = None
        """Query received via user input; Expecting any comment/guess string. Not used outside loop."""
        response: Any = None
        """The response from :class:`Controller` to the comment/guess. Not used outside loop."""
        self._controller.print("I am Gandalf, and Gandalf means me! (If you don't know what to do, enter 'help'!)")
        while command.split(sep=" ", maxsplit=1)[0].lower() not in ["quit", "exit"]:
            # Wait for user input ("All we have to decide is what to do with the time that is given us: ")
            command = input("> ")
            # Separate query from command (if found)
            if " " in command:
                command, query = command.split(sep=" ", maxsplit=1)
            else:
                query = None
            # Parse command
            match command.lower():
                case "help":
                    self._controller.print(self.run.__doc__)
                case "comment":
                    if query is None:
                        query = input("Please enter a comment to submit: ")
                    try:
                        response = self._controller.submit_comment(query)
                    except ValueError as ex:
                        response = ex.args
                    self._controller.print(response)
                case "guess":
                    if query is None:
                        query = input("Please enter a guess to submit: ")
                    try:
                        response = self._controller.submit_guess(query)
                    except NoSuchElementException as ex:
                        # ERROR: Can't submit a guess before submitting a comment for the level.
                        response = ex.msg
                    self._controller.print(response)
                case "exit":
                    break
                case "quit":
                    break
                case _:
                    self._controller.print("I have no memory of this place; (Enter 'help' for a list of commands!)")
        self._controller.print("Farewell, my brave Hobbits. My work is now finished.")
        self._controller.close()


def main(arguments: Optional[ParserArguments] = None):
    instance = Interface(Controller(arguments))
    instance.run()


if __name__ == '__main__':
    main()
