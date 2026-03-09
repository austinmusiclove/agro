import requests


class OllamaLlm:
    def __init__(self, model="phi3"):
        self.model = model
        self.url = "http://localhost:11434/api/generate"

    def get_next_page_url(self, markdown):
        prompt = f"""Find the next page link in this markdown.
Return only the URL if found, or return nothing if there is no next page.
Markdown:
{markdown}"""

        response = requests.post(self.url, json={
            "model": self.model,
            "prompt": prompt,
            "stream": False
        })

        return response.json().get("response", "").strip()
