import requests
import transformers
from config import *


def check_promt_len(message):
    tokenizer = transformers.AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.1")
    return len(tokenizer.encode(message)) < MAX_TOKENS


def get_answer(request, assistant_content):
    response = requests.post(
      "http://localhost:1234/v1/chat/completions",
      headers={"Content-Type": "application/json"},
      json={
            "messages": [
                {"role": "user", "content": request},
                {"role": "system", "content": "Пиши на русском"},
                {"role": "assistant", "content": assistant_content},
            ],
            "temperature": 1.2,
            "max_tokens": MAX_TOKENS,
        }
      )

    if response.status_code == 200 and "choices" in response.json():
        answer = response.json()["choices"][0]["message"]["content"]
        return answer
    else:
        return response.json()
