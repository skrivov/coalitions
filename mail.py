class Mail:
    def __init__(self):
        self.private_mailbox = {}
        self.public_statements = []
        self.temp_private_mailbox = {}
        self.temp_public_statements = []

    def send(self, message):
        if message.recipient == "PUBLIC":
            self.temp_public_statements.append(message)
        else:
            if message.recipient not in self.temp_private_mailbox:
                self.temp_private_mailbox[message.recipient] = []
            self.temp_private_mailbox[message.recipient].append(message)

    def read(self, alias):
        messages = self.private_mailbox.get(alias, [])
        # print(messages)
        return messages

    def read_public_statements(self):
        return self.public_statements

    def finalize(self):
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
