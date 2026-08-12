import pygame
import os
import sys

def lilLoad(relative_path: str) -> pygame.Surface:
    """Does pygame.image.load but smaller and also
       returns correct path for dev and PyInstaller builds."""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    path =  os.path.join(base_path, relative_path)
    return pygame.image.load(path)

def timeout(timer : float) -> bool:
    return (timer == 0.0)