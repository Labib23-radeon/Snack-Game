import wave
import math
import struct
import random
import os

def generate_sound(filename, duration, freq_start, freq_end=None, volume=0.5, wave_type="sine"):
    sample_rate = 44100
    n_frames = int(duration * sample_rate)
    
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        
        data = []
        for i in range(n_frames):
            t = i / sample_rate
            
            if freq_end:
                freq = freq_start + (freq_end - freq_start) * (i / n_frames)
            else:
                freq = freq_start
            
            if wave_type == "sine":
                value = math.sin(2 * math.pi * freq * t)
            elif wave_type == "triangle":
                value = 2 * abs(2 * (t * freq - math.floor(t * freq + 0.5))) - 1
            elif wave_type == "chime":
                # Musical chime: multiple harmonics
                value = (math.sin(2 * math.pi * freq * t) * 0.5 +
                         math.sin(2 * math.pi * freq * 2 * t) * 0.3 +
                         math.sin(2 * math.pi * freq * 3 * t) * 0.2)
            elif wave_type == "noise":
                value = random.uniform(-1, 1)
            else:
                value = 0
            
            # Smooth envelope
            attack = 500
            decay = int(n_frames * 0.7)
            if i < attack:
                value *= (i / attack)
            elif i > decay:
                value *= (n_frames - i) / (n_frames - decay)
                
            sample = int(value * volume * 32767)
            data.append(struct.pack('<h', sample))
            
        wav_file.writeframes(b''.join(data))
    print(f"Generated {filename}")

if __name__ == "__main__":
    if not os.path.exists("assets"):
        os.makedirs("assets")
        
    # Eat: Pleasant chime (C note rising)
    generate_sound("assets/eat.wav", 0.15, 523, 659, volume=0.25, wave_type="chime")
    
    # Powerup: Magical arpeggio effect (C-E-G chord progression feel)
    generate_sound("assets/powerup.wav", 0.5, 262, 784, volume=0.3, wave_type="chime")
    
    # Game Over: Sad descending tone
    generate_sound("assets/game_over.wav", 0.8, 392, 196, volume=0.35, wave_type="triangle")
    
    # Click: Soft tick
    generate_sound("assets/click.wav", 0.08, 800, 600, volume=0.15, wave_type="sine")
