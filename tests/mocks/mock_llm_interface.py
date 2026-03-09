class MockLlmInterface:
    def __init__(self):
        self.prompts = []

    def generate(self, prompt):
        self.prompts.append(prompt)
        return ""

    def get_next_page_url(self, markdown):
        # PSEUDO CODE
        pass
