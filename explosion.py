import pygame
from pygame.sprite import Sprite

class Explosion(Sprite):
    """Класс для создания анимации взрыва."""
    def __init__(self, ai_settings, screen, x, y):
        """Инициализация взрыва в заданной позиции."""
        super().__init__()
        self.screen = screen
        self.ai_settings = ai_settings
        self.images = []
        self.load_images()
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50  # Время между кадрами в миллисекундах

    def load_images(self):
        """Загрузка изображений для анимации взрыва."""
        for i in range(1, 10):
            img = pygame.image.load(f'images/explosion{i}.png')
            self.images.append(img)

    def update(self):
        """Обновление анимации взрыва."""
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(self.images):
                self.kill()  # Удалить спрайт после завершения анимации
            else:
                self.image = self.images[self.frame]

    def blitme(self):
        """Рисует взрыв в текущей позиции."""
        self.screen.blit(self.image, self.rect)
