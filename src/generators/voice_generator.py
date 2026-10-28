import asyncio
import edge_tts
from pathlib import Path
from ..config import VOICE_NAME, VOICE_RATE


class VoiceGenerator:
    def __init__(self):
        self.voice = VOICE_NAME
        self.rate = VOICE_RATE
        self.max_retries = 5
        self.retry_delay = 5

    def _clean_text(self, text: str) -> str:
        """Очистка текста от проблемных символов"""
        # Убираем лишние пробелы и переносы
        text = ' '.join(text.split())
        # Убираем специальные символы, которые могут вызывать проблемы
        text = text.replace('\n', ' ').replace('\r', ' ')
        # Убираем множественные пробелы
        while '  ' in text:
            text = text.replace('  ', ' ')
        return text.strip()

    def _split_text_into_chunks(self, text: str, max_length: int = 4000) -> list:
        """Разбиение длинного текста на части по предложениям"""
        if len(text) <= max_length:
            return [text]
        
        chunks = []
        sentences = text.replace('!', '.').replace('?', '.').split('.')
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip() + '.'
            if len(current_chunk) + len(sentence) > max_length:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                current_chunk += " " + sentence
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks

    async def _generate_chunk(self, text: str, output_path: str) -> None:
        """Генерация одной части текста"""
        for attempt in range(self.max_retries):
            try:
                communicate = edge_tts.Communicate(text, self.voice, rate=self.rate)
                await communicate.save(str(output_path))
                
                if not Path(output_path).exists() or Path(output_path).stat().st_size == 0:
                    raise ValueError("Файл озвучки не создан или пуст")
                
                return
            except edge_tts.exceptions.NoAudioReceived as e:
                if attempt < self.max_retries - 1:
                    print(f"   Попытка {attempt + 1} не удалась, жду {self.retry_delay} сек...")
                    await asyncio.sleep(self.retry_delay)
                    continue
                raise
            except Exception as e:
                if attempt < self.max_retries - 1:
                    print(f"   Попытка {attempt + 1} не удалась, жду {self.retry_delay} сек...")
                    await asyncio.sleep(self.retry_delay)
                    continue
                raise

    async def generate(self, text: str, output_path: str) -> str:
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Текст должен быть непустой строкой")
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Очищаем текст
        clean_text = self._clean_text(text)
        print(f"   Текст: {len(clean_text)} символов")
        
        # Разбиваем на части если нужно
        chunks = self._split_text_into_chunks(clean_text)
        
        if len(chunks) == 1:
            # Один кусок - генерируем напрямую
            await self._generate_chunk(clean_text, output_path)
        else:
            # Несколько кусков - генерируем каждый и объединяем
            print(f"   Разбит на {len(chunks)} частей")
            temp_files = []
            
            for i, chunk in enumerate(chunks, 1):
                temp_path = output_path.with_suffix(f'.part{i}.mp3')
                print(f"   Генерация части {i}/{len(chunks)}...")
                await self._generate_chunk(chunk, temp_path)
                temp_files.append(temp_path)
            
            # Объединяем файлы
            with open(output_path, 'wb') as outfile:
                for temp_file in temp_files:
                    with open(temp_file, 'rb') as infile:
                        outfile.write(infile.read())
            
            # Удаляем временные файлы
            for temp_file in temp_files:
                temp_file.unlink()
        
        return str(output_path)

    def generate_sync(self, text: str, output_path: str) -> str:
        return asyncio.run(self.generate(text, output_path))
