from typing import Optional, Union, Any

from argument_types import ParserArguments
from selenium_driver import SeleniumDriver


class Interface:
    driver: SeleniumDriver

    def __init__(self, args_or_driver: Union[ParserArguments, SeleniumDriver]):
        if isinstance(args_or_driver, SeleniumDriver):
            self.driver = args_or_driver
        elif isinstance(args_or_driver, ParserArguments):
            self.driver = SeleniumDriver(args_or_driver)
        else:
            raise ValueError(f"Parameter must be either ParserArguments or SeleniumDriver.")

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
        """Command received via user input; Expecting string literal in ['help', 'comment', 'guess', 'quit', 'exit']"""
        query: Optional[str] = None
        """Query received via user input; Expecting any comment/guess string. Not used outside loop."""
        response: Any = None
        """The response from :class:`SeleniumDriver` to the comment/guess. Not used outside loop."""
        print("I am Gandalf, and Gandalf means me!")
        # TODO: Indicate current Level to user (on entry / level up) -> make submits return an enum?
        while command.split(sep=" ", maxsplit=1)[0].lower() not in ["quit", "exit"]:
            # Wait for user input
            command = input("All we have to decide is what to do with the time that is given us: ")
            # Separate query from command (if found)
            if " " in command:
                command, query = command.split(sep=" ", maxsplit=1)
            else:
                query = None
            # Parse command
            match command.lower():
                case "help":
                    print(self.run.__doc__)
                case "comment":
                    if query is None:
                        query = input("Please enter a comment to submit: ")
                    response = self.driver.submit_comment(query)  # TODO: response: [answer, success] ?
                    print(response)
                case "guess":
                    if query is None:
                        query = input("Please enter a guess to submit: ")
                    response = self.driver.submit_guess(query)  # TODO: response: [answer, success] ?
                    print(response)
                case "exit":
                    break
                case "quit":
                    break
                case _:
                    print("I have no memory of this place; Enter 'help' for a list of available commands.")
        print("Farewell, my brave Hobbits. My work is now finished.")


def main(arguments: Optional[ParserArguments] = None):
    instance = Interface(SeleniumDriver(arguments))
    instance.run()


if __name__ == '__main__':
    main()
