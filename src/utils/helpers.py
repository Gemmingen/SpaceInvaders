import pygame
import os

def load_image(path):
    """Load an image from the project assets folder.

    The function resolves ``path`` relative to the repository root (two levels up
    from this helper module). If the file cannot be found, a small transparent
    placeholder surface is returned so the game does not crash.

    Additionally, pygame requires an initialized video mode for ``convert_alpha``
    to work. In head‑less or test environments the display may not yet be set, so
    we lazily initialise a minimal dummy display (1×1) when necessary.
    """
    # Ensure a video mode exists – required for ``convert_alpha``.
    if pygame.display.get_surface() is None:
        # ``pygame.display.set_mode`` will create a hidden window when the
        # ``SDL_VIDEODRIVER`` is set to ``dummy`` (as tests do).
        pygame.display.set_mode((1, 1))

    # Repository root: <project_root>/ (two directories up from utils/helpers.py)
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    full_path = os.path.normpath(os.path.join(base_dir, path))
    if not os.path.isfile(full_path):
        # Return a minimal transparent surface as a fallback (32×32)
        placeholder = pygame.Surface((32, 32), pygame.SRCALPHA)
        placeholder.fill((0, 0, 0, 0))
        return placeholder
    return pygame.image.load(full_path).convert_alpha()

def load_sound(path):
    return pygame.mixer.Sound(path)
