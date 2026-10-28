import random
import subprocess
from pathlib import Path
from ..config import FFMPEG, MUSIC_DIR, EFFECTS


class VideoGenerator:
    def __init__(self):
        self.ffmpeg = FFMPEG
        self.effects = EFFECTS
        self.music_dir = MUSIC_DIR

    def _get_effect_filters(self, effect: str) -> str:
        effect_filters = {
            "vhs_glitch": (
                "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
                "noise=alls=28:allf=t+u,"
                "eq=contrast=1.14:brightness=-0.06:saturation=1.34,"
                "hue=h=1.2*t:enable='between(mod(t\\,0.3)\\,0\\,0.03)'"
            ),
            "film_grain": (
                "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
                "noise=alls=38:allf=t,"
                "eq=contrast=1.19:brightness=-0.04:saturation=0.88"
            ),
            "static_noise": (
                "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
                "noise=alls=58:allf=t+u,"
                "eq=contrast=1.24:brightness=-0.09:saturation=0.66"
            ),
            "scan_lines": (
                "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
                "eq=contrast=1.14:brightness=-0.06,"
                "noise=alls=10:allf=t"
            ),
            "datamosh": (
                "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
                "noise=alls=23:allf=t,"
                "eq=contrast=1.14:brightness=-0.05:saturation=1.24"
            ),
        }
        return effect_filters.get(effect, effect_filters["film_grain"])

    def create(self, image_path: str, audio_path: str, output_path: str, effect: str = None) -> str:
        image_path = Path(image_path)
        audio_path = Path(audio_path)
        output_path = Path(output_path)
        
        if not image_path.exists():
            raise ValueError(f"Изображение не найдено: {image_path}")
        if not audio_path.exists():
            raise ValueError(f"Аудио не найдено: {audio_path}")
        
        if effect is None:
            effect = random.choice(self.effects)
        if effect not in self.effects:
            raise ValueError(f"Неизвестный эффект: {effect}. Доступные: {self.effects}")

        output_path.parent.mkdir(parents=True, exist_ok=True)

        music_file = None
        if self.music_dir.exists():
            music_files = list(self.music_dir.glob("*.mp3"))
            if music_files:
                music_file = str(random.choice(music_files))

        vf_base = self._get_effect_filters(effect)
        zoompan = "zoompan=z='min(zoom+0.0015,1.5)':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920"
        vf = f"{zoompan},{vf_base}"

        cmd = [
            self.ffmpeg, "-y",
            "-loop", "1", "-i", str(image_path),
            "-i", str(audio_path),
        ]

        if music_file:
            cmd.extend(["-stream_loop", "-1", "-i", music_file])
            cmd.extend([
                "-filter_complex",
                f"[1:a]volume=1.0[voice];[2:a]volume=0.4[music];[voice][music]amix=inputs=2:duration=first[aout]",
                "-map", "0:v",
                "-map", "[aout]",
            ])
        else:
            cmd.extend(["-map", "0:v", "-map", "1:a"])

        cmd.extend([
            "-vf", vf,
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "28",
            "-b:v", "1000k",
            "-maxrate", "1500k",
            "-bufsize", "2000k",
            "-c:a", "aac",
            "-b:a", "128k",
            "-pix_fmt", "yuv420p",
            "-shortest",
            "-r", "24",
            "-movflags", "+faststart",
            str(output_path)
        ])

        subprocess.run(cmd, capture_output=True, check=True)
        return str(output_path)
