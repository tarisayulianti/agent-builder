"""OpenAI client only."""
import os
from openai import OpenAI

class LLM:
    def __init__(self):
        key = os.getenv("OPENAI_API_KEY", "")
        if not key:
            raise ValueError("Set OPENAI_API_KEY dulu: export OPENAI_API_KEY=sk-...")
        self.client = OpenAI(api_key=key)
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    def chat(self, prompt, system="", temp=0.3, max_tokens=4000):
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        r = self.client.chat.completions.create(
            model=self.model, messages=messages, temperature=temp, max_tokens=max_tokens
        )
        return r.choices[0].message.content
