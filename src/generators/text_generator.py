import requests
from typing import Optional
from ..config import QWEN_API_KEY, QWEN_MODEL, QWEN_ENDPOINT
from ..prompts import TOPIC_PROMPT, TITLE_PROMPT, HASHTAGS_PROMPT, STORY_PROMPT, IMAGE_PROMPT_TEMPLATE


class TextGenerator:
    def __init__(self):
        if not QWEN_API_KEY:
            raise ValueError("QWEN_API_KEY не установлен в .env файле")
        self.api_key = QWEN_API_KEY
        self.model = QWEN_MODEL
        self.endpoint = QWEN_ENDPOINT

    def _api_request(self, prompt: str, max_tokens: int = 400, temperature: float = 0.85, enable_thinking: bool = False) -> str:
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("Промпт должен быть непустой строкой")
        if not isinstance(max_tokens, int) or max_tokens <= 0:
            raise ValueError("max_tokens должен быть положительным целым числом")
        if not isinstance(temperature, (int, float)) or not (0 <= temperature <= 2):
            raise ValueError("temperature должен быть числом от 0 до 2")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "enable_thinking": enable_thinking
        }
        
        response = requests.post(self.endpoint, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        
        if "choices" in result and len(result["choices"]) > 0:
            choice = result["choices"][0]
            message = choice.get("message", {})
            content = message.get("content", "")
            reasoning = message.get("reasoning_content", "")
            
            if not content and reasoning:
                content = reasoning
            
            if not content:
                raise ValueError("Пустой ответ от API")
            
            return content.strip()
        else:
            raise ValueError(f"Ошибка API: {result}")

    def generate_topic(self) -> str:
        result = self._api_request(TOPIC_PROMPT, max_tokens=100, temperature=0.95)
        result = result.replace("Тема:", "").replace("тема:", "").strip()
        return result

    def generate_title(self, topic: str) -> str:
        if not isinstance(topic, str) or not topic.strip():
            raise ValueError("Тема должна быть непустой строкой")
        
        prompt = TITLE_PROMPT.format(topic=topic)
        result = self._api_request(prompt, max_tokens=20, temperature=0.9)
        
        result = result.replace('"', '').replace("'", '').replace('«', '').replace('»', '').strip()
        result = result.replace('Название:', '').replace('название:', '').strip()
        
        if not result:
            result = topic[:30]
        
        return result

    def generate_hashtags(self, topic: str) -> str:
        if not isinstance(topic, str) or not topic.strip():
            raise ValueError("Тема должна быть непустой строкой")
        
        prompt = HASHTAGS_PROMPT.format(topic=topic)
        return self._api_request(prompt, max_tokens=200, temperature=0.7)

    def generate_story(self, topic: str) -> str:
        if not isinstance(topic, str) or not topic.strip():
            raise ValueError("Тема должна быть непустой строкой")
        
        prompt = STORY_PROMPT.format(topic=topic)
        return self._api_request(prompt, max_tokens=2400, temperature=0.85)

    def generate_image_prompt(self, story: str, topic: str) -> str:
        if not isinstance(story, str) or not story.strip():
            raise ValueError("Рассказ должен быть непустой строкой")
        if not isinstance(topic, str) or not topic.strip():
            raise ValueError("Тема должна быть непустой строкой")
        
        prompt = IMAGE_PROMPT_TEMPLATE.format(story=story)
        return self._api_request(prompt, max_tokens=300, temperature=0.7)
