import asyncio
import edge_tts
from pathlib import Path
from ..config import VOICE_NAME, VOICE_RATE


class VoiceGenerator:
    def __init__(self):
        self.voice = VOICE_NAME
        self.rate = VOICE_RATE
        self.max_retries = 3

    async def generate(self, text: str, output_path: str) -> str:
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Текст должен быть непустой строкой")
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        for attempt in range(self.max_retries):
            try:
                communicate = edge_tts.Communicate(text, self.voice, rate=self.rate)
                await communicate.save(str(output_path))
                
                if not output_path.exists() or output_path.stat().st_size == 0:
                    raise ValueError("Файл озвучки не создан или пуст")
                
                return str(output_path)
            except edge_tts.exceptions.NoAudioReceived as e:
                if attempt < self.max_retries - 1:
                    print(f"   Попытка {attempt + 1} не удалась, повторяю...")
                    await asyncio.sleep(2)
                    continue
                raise ValueError(f"Edge TTS не вернул аудио после {self.max_retries} попыток. Проверьте голос '{self.voice}' и текст. Ошибка: {e}")
            except Exception as e:
                if attempt < self.max_retries - 1:
                    print(f"   Попытка {attempt + 1} не удалась, повторяю...")
                    await asyncio.sleep(2)
                    continue
                raise ValueError(f"Ошибка генерации голоса: {e}")

    def generate_sync(self, text: str, output_path: str) -> str:
        return asyncio.run(self.generate(text, output_path))
