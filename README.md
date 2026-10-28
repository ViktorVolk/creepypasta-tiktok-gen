# Creepypasta TikTok Pipeline

Автоматизированная система создания хоррор-контента для TikTok с помощью ИИ.

## Возможности

- **Текст**: Qwen Studio API (генерация концепции, рассказа, названия, хештегов)
- **Голос**: Edge TTS (бесплатно, локально)
- **Изображения**: ComfyUI + SDXL (локально, RTX 5070)
- **Видео**: ffmpeg с эффектами помех и фоновой музыкой
- **Обложки**: Pillow + шрифт Creepster

## Установка

### 1. Клонировать репозиторий
```bash
git clone <repository-url>
cd creepypasta-pipeline
```

### 2. Установить зависимости Python
```bash
pip install -r requirements.txt
```

### 3. Установить ffmpeg
**Windows:**
```bash
winget install Gyan.FFmpeg
```

**Или скачать вручную:** https://ffmpeg.org/download.html

### 4. Установить ComfyUI
```bash
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI
pip install -r requirements.txt
```

Скачать модель SDXL в `ComfyUI/models/checkpoints/`:
- [JuggernautXL v8](https://huggingface.co/RunDiffusion/Juggernaut-XL-v8)

### 5. Настроить .env
Скопировать `.env.example` в `.env` и заполнить:
```bash
cp .env.example .env
```

```env
QWEN_API_KEY=your-api-key-here
QWEN_MODEL=qwen3.8-flash
FFMPEG_PATH=C:\path\to\ffmpeg.exe
TITLE_FONT_PATH=C:/Windows/Fonts/arialbd.ttf
```

**Получить Qwen API ключ:** https://dashscope.console.aliyun.com/

### 6. Установить шрифт
Скачать [Creepster](https://fonts.google.com/specimen/Creepster) в папку `fonts/`

## Использование

### Запуск ComfyUI (в отдельном окне)
```bash
python ComfyUI\main.py --listen
```

### Проверка компонентов
```bash
python scripts/check_components.py
```

### Генерация контента

**Вариант 1: Автоматическая тема**
```bash
python main.py
```

**Вариант 2: С указанием темы**
```bash
python main.py "заброшенная больница"
```

**Вариант 3: С детальными пожеланиями**
```bash
python main.py "история про подростка 15 лет, деревня у бабушки, старый радиоприемник"
```

### Тестирование отдельных этапов

Каждый этап можно тестировать отдельно:

```bash
# Этап 1: Генерация текста
python scripts/test_stage1_text.py "заброшенная больница"

# Этап 2: Генерация голоса
python scripts/test_stage2_voice.py "Текст для озвучки"

# Этап 3: Генерация изображения (требует запущенный ComfyUI)
python scripts/test_stage3_image.py "dark horror house, fog, night"

# Этап 4: Генерация видео
python scripts/test_stage4_video.py image.png audio.mp3 output.mp4 vhs_glitch

# Этап 5: Создание обложек
python scripts/test_stage5_cover.py image.png "Название" 1 cover.png
```

## Что генерируется

Для каждой истории создается папка в `stories/NNN_тема/`:

| Файл | Описание |
|------|----------|
| `title.txt` | Название (1-2 слова) |
| `hashtags_part1.txt` | Хештеги для части 1 |
| `hashtags_part2.txt` | Хештеги для части 2 |
| `hashtags_part3.txt` | Хештеги для части 3 |
| `story.txt` | Полный рассказ (800-850 слов, ~6 мин) |
| `story_part1.txt` | Часть 1 (~2 мин) |
| `story_part2.txt` | Часть 2 (~2 мин) |
| `story_part3.txt` | Часть 3 (~2 мин) |
| `image.png` | Изображение 768x1344 |
| `image_prompt.txt` | Промпт для изображения |
| `voice_part1.mp3` | Озвучка части 1 |
| `voice_part2.mp3` | Озвучка части 2 |
| `voice_part3.mp3` | Озвучка части 3 |
| `cover_part1.png` | Обложка часть 1 |
| `cover_part2.png` | Обложка часть 2 |
| `cover_part3.png` | Обложка часть 3 |
| `video_part1.mp4` | Видео часть 1 (1080x1920) |
| `video_part2.mp4` | Видео часть 2 (1080x1920) |
| `video_part3.mp4` | Видео часть 3 (1080x1920) |

## Эффекты видео

Случайно выбирается для каждого видео:
- **vhs_glitch** - VHS полосы + искажение цвета
- **film_grain** - зернистость плёнки
- **static_noise** - белый шум
- **scan_lines** - линии развёртки
- **datamosh** - цифровое растекание

## Фоновая музыка

Добавьте MP3 файлы в папку `music/`. Случайный трек будет добавлен к видео с громкостью 40%.

## Структура проекта

```
.
├── main.py                      # Точка входа (запуск пайплайна)
├── requirements.txt             # Python зависимости
├── .env                         # Секреты (не в git)
├── .env.example                 # Шаблон .env
├── .gitignore                   # Игнор для git
├── README.md                    # Документация
├── src/                         # Исходный код
│   ├── config.py                # Конфигурация (env vars, constants)
│   ├── prompts.py               # Промпты для Qwen API
│   ├── pipeline.py              # Главный класс CreepypastaPipeline
│   ├── generators/              # Генераторы контента
│   │   ├── text_generator.py    # Qwen API (текст)
│   │   ├── voice_generator.py   # Edge TTS (голос)
│   │   ├── image_generator.py   # ComfyUI (изображения)
│   │   ├── video_generator.py   # ffmpeg (видео)
│   │   └── cover_generator.py   # Pillow (обложки)
│   └── utils/                   # Утилиты
│       ├── story_splitter.py    # Разделение рассказа на части
│       └── file_manager.py      # Управление файлами
├── scripts/                     # Тестовые скрипты
│   ├── check_components.py      # Проверка живучести компонентов
│   ├── test_stage1_text.py      # Тест генерации текста
│   ├── test_stage2_voice.py     # Тест генерации голоса
│   ├── test_stage3_image.py     # Тест генерации изображения
│   ├── test_stage4_video.py     # Тест генерации видео
│   └── test_stage5_cover.py     # Тест создания обложек
├── fonts/                       # Шрифты
│   └── Creepster-Regular.ttf
├── music/                       # Фоновая музыка (MP3)
└── stories/                     # Сгенерированный контент (не в git)
    └── 001_название/
        ├── title.txt
        ├── hashtags_part1.txt
        ├── hashtags_part2.txt
        ├── hashtags_part3.txt
        ├── story.txt
        ├── story_part1.txt
        ├── story_part2.txt
        ├── story_part3.txt
        ├── image.png
        ├── image_prompt.txt
        ├── voice_part1.mp3
        ├── voice_part2.mp3
        ├── voice_part3.mp3
        ├── cover_part1.png
        ├── cover_part2.png
        ├── cover_part3.png
        ├── video_part1.mp4
        ├── video_part2.mp4
        └── video_part3.mp4
```

## Требования

- Python 3.10+
- PyTorch 2.15.0+ (для RTX 5070 нужна версия с CUDA 13.0+)
- ComfyUI
- ffmpeg
- Qwen Studio API ключ

## Стоимость

- **Текст**: ~$0.02-0.10 за видео (Qwen Studio)
- **Голос**: Бесплатно (Edge TTS)
- **Изображения**: Бесплатно (локально)

**Итого: ~$2-10/мес** за 100+ видео

## Лицензия

MIT
