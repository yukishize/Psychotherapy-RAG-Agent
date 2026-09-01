from typing import Iterator, List, Union

from openai import OpenAI


class LLMClient:
    def __init__(self, base_url: str, api_key: str, model: str, temperature: float = 0.8):
        self.model = model
        self.temperature = temperature
        self._client = OpenAI(base_url=base_url or None, api_key=api_key)

    def chat(self, messages: List[dict], stream: bool = True) -> Union[Iterator[str], str]:
        if stream:#流式
            resp = self._client.chat.completions.create(
                model=self.model, messages=messages, stream=True, temperature=self.temperature
            )
            for chunk in resp:
                if chunk.choices:
                    delta = chunk.choices[0].delta.content
                    if delta:
                        yield delta
        else:#非流式
            resp = self._client.chat.completions.create(
                model=self.model, messages=messages, stream=False, temperature=self.temperature
            )
            return resp.choices[0].message.content
