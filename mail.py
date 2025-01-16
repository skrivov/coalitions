"""
mail.py

Handles sending and reading messages between agents, as well as public statements.
"""

from __future__ import annotations
from message import Message


class Mail:
    """
    A mailbox system for managing private messages and public statements.
    """

    def __init__(self) -> None:
        """
        Initializes empty mailboxes for private and public messages.
        """
        self.private_mailbox: dict[str, list[Message]] = {}
        self.public_statements: list[Message] = []
        self.temp_private_mailbox: dict[str, list[Message]] = {}
        self.temp_public_statements: list[Message] = []

    def send(self, message: Message) -> None:
        """
        Sends a message, either to a specific recipient (private mailbox) or
        to the public statements list.

        Args:
            message (Message): The message to be sent.
        """
        if message.recipient == "PUBLIC":
            self.temp_public_statements.append(message)
        else:
            if message.recipient not in self.temp_private_mailbox:
                self.temp_private_mailbox[message.recipient] = []
            self.temp_private_mailbox[message.recipient].append(message)

    def read(self, alias: str) -> list[Message]:
        """
        Reads and returns all private messages for a specific alias.

        Args:
            alias (str): The alias of the agent to retrieve messages for.

        Returns:
            list[Message]: A list of messages in the private mailbox for this alias.
        """
        return self.private_mailbox.get(alias, [])

    def read_public_statements(self) -> list[Message]:
        """
        Returns all public statements.

        Returns:
            list[Message]: A list of public messages.
        """
        return self.public_statements

    def finalize(self) -> None:
        """
        Moves all temporary messages to the main mailboxes and clears the temporary storage.
        """
        # Move temp messages to main mailbox
        for alias, messages in self.temp_private_mailbox.items():
            if alias not in self.private_mailbox:
                self.private_mailbox[alias] = []
            self.private_mailbox[alias].extend(messages)

        # Move temp public statements to main public statements list
        self.public_statements.extend(self.temp_public_statements)

        # Clear temporary storage
        self.temp_private_mailbox.clear()
        self.temp_public_statements.clear()
