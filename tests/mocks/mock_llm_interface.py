from lib.llm_interface.llm_interface import LlmInterface


class MockLlmInterface(LlmInterface):
    def __init__(self):
        self.prompts = []

    def _prompt_llm(self, prompt):
        self.prompts.append(prompt)
        return ""

    def get_next_page_url(self, markdown):
        # PSEUDO CODE
        pass
