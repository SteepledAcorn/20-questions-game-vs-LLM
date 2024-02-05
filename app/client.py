import requests
import time

class LLMApiClient:
    def __init__(self, api_key):
        self.url = "https://api.openai.com/v1/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "x-api-key": api_key,
        }

    def chat_completion(self, model, messages, temperature):
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }

        try:
            response = requests.post(self.url, headers=self.headers, json=payload)
            response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)

            # Check specific status codes
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                # Throttle request
                time.sleep(1)
                response = requests.post(self.url, headers=self.headers, json=payload)
                response.raise_for_status()  

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
