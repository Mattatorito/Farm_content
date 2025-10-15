# 🎵 ГЕНЕРАТОР ЗВУКОВЫХ ЭФФЕКТОВ ДЛЯ ВИРУСНЫХ ВИДЕО

import numpy as np
import wave
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def generate_audio_effects():
    """
    Генерирует простые звуковые эффекты для видео
    """
    audio_dir = Path("viral_assets/audio")
    audio_dir.mkdir(parents=True, exist_ok=True)
    
    sample_rate = 44100
    
    # Эффект 1: Драматичный удар/бум
    def create_impact_sound():
        duration = 1.5  # 1.5 секунды
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # Низкочастотный удар с затуханием
        frequency = 60  # Низкая частота для драматизма
        impact = np.sin(2 * np.pi * frequency * t) * np.exp(-t * 3)
        
        # Добавляем шум для реализма
        noise = np.random.normal(0, 0.1, len(t)) * np.exp(-t * 5)
        
        audio = impact + noise
        audio = np.clip(audio, -1, 1)  # Ограничиваем амплитуду
        
        return (audio * 32767).astype(np.int16)
    
    # Эффект 2: Свуш (переход)
    def create_swoosh_sound():
        duration = 0.8
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # Частота поднимается со временем
        frequency = 200 + 800 * t / duration
        swoosh = np.sin(2 * np.pi * frequency * t) * np.exp(-t * 2)
        
        # Добавляем высокочастотный шум
        noise = np.random.normal(0, 0.05, len(t)) * (1 - t / duration)
        
        audio = swoosh + noise
        audio = np.clip(audio, -1, 1)
        
        return (audio * 32767).astype(np.int16)
    
    # Эффект 3: Цифровой глитч
    def create_glitch_sound():
        duration = 0.3
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # Случайные частоты с резкими изменениями
        glitch = np.zeros_like(t)
        for i in range(len(t)):
            if i % 100 == 0:  # Изменяем частоту каждые 100 сэмплов
                freq = np.random.randint(200, 2000)
            glitch[i] = np.sin(2 * np.pi * freq * t[i])
        
        # Случайное отключение сигнала
        mask = np.random.random(len(t)) > 0.3
        glitch = glitch * mask
        
        audio = np.clip(glitch, -1, 1)
        return (audio * 32767 * 0.7).astype(np.int16)
    
    # Создаем звуковые файлы
    effects = {
        "impact.wav": create_impact_sound(),
        "swoosh.wav": create_swoosh_sound(), 
        "glitch.wav": create_glitch_sound()
    }
    
    created_files = []
    
    for filename, audio_data in effects.items():
        file_path = audio_dir / filename
        
        with wave.open(str(file_path), 'wb') as wav_file:
            wav_file.setnchannels(1)  # Моно
            wav_file.setsampwidth(2)  # 16-бит
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_data.tobytes())
        
        logger.info(f"✅ Создан звуковой эффект: {filename}")
        created_files.append(str(file_path))
    
    return created_files

def create_background_music():
    """
    Создает простую фоновую музыку
    """
    audio_dir = Path("viral_assets/audio")
    audio_dir.mkdir(parents=True, exist_ok=True)
    
    sample_rate = 44100
    duration = 30  # 30 секунд
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # Создаем простую электронную мелодию
    def create_electronic_beat():
        # Основной бас на 120 BPM
        beat_freq = 2  # 2 удара в секунду (120 BPM)
        bass = np.sin(2 * np.pi * 80 * t) * (np.sin(2 * np.pi * beat_freq * t) > 0)
        
        # Мелодия с изменяющимися нотами
        melody_notes = [440, 523, 659, 784, 659, 523]  # A, C, E, G, E, C
        melody = np.zeros_like(t)
        
        note_duration = duration / len(melody_notes)
        for i, note in enumerate(melody_notes):
            start_idx = int(i * note_duration * sample_rate)
            end_idx = int((i + 1) * note_duration * sample_rate)
            if end_idx > len(melody):
                end_idx = len(melody)
            
            t_note = t[start_idx:end_idx] - t[start_idx]
            note_sound = np.sin(2 * np.pi * note * t_note) * 0.3
            melody[start_idx:end_idx] = note_sound
        
        # Объединяем бас и мелодию
        music = bass * 0.6 + melody * 0.4
        
        # Добавляем эффект затухания в конце
        fade_samples = int(2 * sample_rate)  # 2 секунды затухания
        fade = np.ones_like(music)
        fade[-fade_samples:] = np.linspace(1, 0, fade_samples)
        music = music * fade
        
        return np.clip(music, -1, 1)
    
    # Создаем музыку
    music = create_electronic_beat()
    audio_data = (music * 32767 * 0.7).astype(np.int16)
    
    # Сохраняем файл
    file_path = audio_dir / "background_electronic.wav"
    
    with wave.open(str(file_path), 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data.tobytes())
    
    logger.info(f"✅ Создана фоновая музыка: background_electronic.wav")
    return str(file_path)

if __name__ == "__main__":
    print("🎵 Создание звуковых эффектов...")
    
    # Создаем эффекты
    effects = generate_audio_effects()
    print(f"✅ Созданы эффекты: {len(effects)}")
    
    # Создаем музыку
    music = create_background_music()
    print(f"✅ Создана музыка: {music}")
    
    print("🎉 Все звуковые файлы готовы!")