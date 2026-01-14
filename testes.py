import pygame
import numpy as np

pygame.mixer.init(frequency=22050, size=-16, channels=1)

def som_slime_orgânico():
    sample_rate = 22050
    duration = 0.2
    t = np.linspace(0, duration, int(sample_rate * duration))

    base = np.sin(2 * np.pi * 70 * t)
    wobble = np.sin(2 * np.pi * 12 * t)
    noise = np.random.normal(0, 0.2, len(t))

    wave = (base * wobble) + noise
    wave *= np.exp(-8 * t)

    sound = np.int16(wave / np.max(np.abs(wave)) * 32767)
    return pygame.sndarray.make_sound(sound)

slime_sound = som_slime_orgânico()
slime_sound.play()