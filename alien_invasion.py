import sys
import pygame
from time import sleep
from settings import Settings
from game_stats import GameStats
from scoreboard import Scoreboard
from button import Button
from ship import Ship
from bullet import Bullet
from alien import Alien
from explosion import Explosion  # Добавляем класс для анимации взрывов

class AlienInvasion:
    """Класс для управления ресурсами и поведением игры."""

    def __init__(self):
        """Инициализация игры и создание игровых ресурсов."""
        pygame.init()
        self.ai_settings = Settings()
        self.screen = pygame.display.set_mode(
            (self.ai_settings.screen_width, self.ai_settings.screen_height))
        pygame.display.set_caption("Alien Invasion")

        # Создание экземпляров для хранения статистики и табло
        self.stats = GameStats(self.ai_settings)
        self.sb = Scoreboard(self.ai_settings, self.screen, self.stats)
        
        self.ship = Ship(self.ai_settings, self.screen)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self.explosions = pygame.sprite.Group()  # Группа для хранения анимаций взрывов

        self._create_fleet()

        # Создание кнопки Play
        self.play_button = Button(self.ai_settings, self.screen, "Play")

        # Инициализация звуков
        pygame.mixer.init()
        self.alien_hit_sound = pygame.mixer.Sound('sounds/alien_hit.wav')
        self.ship_hit_sound = pygame.mixer.Sound('sounds/ship_hit.wav')

    def run_game(self):
        """Запуск основного цикла игры."""
        while True:
            self._check_events()

            if self.stats.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()

            self._update_screen()

    def _check_events(self):
        """Обработка нажатий клавиш и событий мыши."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                self._check_play_button(mouse_x, mouse_y)

    def _check_keydown_events(self, event):
        """Реагирование на нажатие клавиш."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()
        elif event.key == pygame.K_q:
            sys.exit()

    def _check_keyup_events(self, event):
        """Реагирование на отпускание клавиш."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        if event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _check_play_button(self, mouse_x, mouse_y):
        """Запуск новой игры при нажатии кнопки Play мышью."""
        button_clicked = self.play_button.rect.collidepoint(mouse_x, mouse_y)
        if button_clicked and not self.stats.game_active:
            self.ai_settings.initialize_dynamic_settings()
            pygame.mouse.set_visible(False)
            self.stats.reset_stats()
            self.stats.game_active = True
            self.sb.prep_score()
            self.sb.prep_high_score()
            self.sb.prep_level()
            self.sb.prep_ships()

            self.aliens.empty()
            self.bullets.empty()

            self._create_fleet()
            self.ship.center_ship()

    def _update_bullets(self):
        """Обновление позиции пуль и удаление старых пуль."""
        self.bullets.update()
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)

        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        """Обработка коллизий пуль с пришельцами."""
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)
        if collisions:
            for aliens in collisions.values():
                for alien in aliens:
                    explosion = Explosion(self.ai_settings, self.screen, alien.rect.x, alien.rect.y)
                    self.explosions.add(explosion)
                self.stats.score += self.ai_settings.alien_points * len(aliens)
                self.sb.prep_score()
                self.alien_hit_sound.play()
            self._check_high_score()

        if not self.aliens:
            self.bullets.empty()
            self.ai_settings.increase_speed()
            self.stats.level += 1
            self.sb.prep_level()
            self._create_fleet()

    def _check_high_score(self):
        """Проверка, появился ли новый рекорд."""
        if self.stats.score > self.stats.high_score:
            self.stats.high_score = self.stats.score
            self.sb.prep_high_score()

    def _update_aliens(self):
        """Проверка, достиг ли флот края экрана, и обновление позиций всех пришельцев."""
        self._check_fleet_edges()
        self.aliens.update()

        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()

        self._check_aliens_bottom()

    def _check_fleet_edges(self):
        """Реагирует на достижение пришельцем края экрана."""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        """Опускает весь флот и меняет его направление."""
        for alien in self.aliens.sprites():
            alien.rect.y += self.ai_settings.fleet_drop_speed
        self.ai_settings.fleet_direction *= -1

    def _check_aliens_bottom(self):
        """Проверяет, достигли ли пришельцы нижнего края экрана."""
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                self._ship_hit()
                break

    def _ship_hit(self):
        """Обрабатывает столкновение корабля с пришельцем."""
        if self.stats.ships_left > 0:
            self.stats.ships_left -= 1
            self.sb.prep_ships()

            self.aliens.empty()
            self.bullets.empty()

            self._create_fleet()
            self.ship.center_ship()

            explosion = Explosion(self.ai_settings, self.screen, self.ship.rect.x, self.ship.rect.y)
            self.explosions.add(explosion)

            self.ship_hit_sound.play()

            sleep(0.5)
        else:
            self.stats.game_active = False
            pygame.mouse.set_visible(True)
            self._game_over()  # Вызов метода отображения GAME OVER

    def _game_over(self):
        """Отображение сообщения GAME OVER на экране."""
        font = pygame.font.SysFont(None, 74)
        game_over_surface = font.render('GAME OVER', True, (255, 0, 0))
        game_over_rect = game_over_surface.get_rect()
        game_over_rect.center = self.screen.get_rect().center
        self.screen.blit(game_over_surface, game_over_rect)
        pygame.display.flip()
        sleep(2)  # Даем пользователю 2 секунды, чтобы увидеть сообщение

    def _create_fleet(self):
        """Создание флота пришельцев."""
        alien = Alien(self.ai_settings, self.screen)
        number_aliens_x = self._get_number_aliens_x(alien.rect.width)
        number_rows = self._get_number_rows(self.ship.rect.height, alien.rect.height)

        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number, row_number)

    def _get_number_aliens_x(self, alien_width):
        """Вычисляет количество пришельцев в ряду."""
        available_space_x = self.ai_settings.screen_width - 2 * alien_width
        number_aliens_x = int(available_space_x / (2 * alien_width))
        return number_aliens_x

    def _get_number_rows(self, ship_height, alien_height):
        """Определяет количество рядов, помещающихся на экране."""
        available_space_y = (self.ai_settings.screen_height -
                             (3 * alien_height) - ship_height)
        number_rows = int(available_space_y / (2 * alien_height))
        return number_rows

    def _create_alien(self, alien_number, row_number):
        """Создание пришельца и размещение его в ряду."""
        alien = Alien(self.ai_settings, self.screen)
        alien_width = alien.rect.width
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
        self.aliens.add(alien)

    def _fire_bullet(self):
        """Выпуск новой пули, если максимум еще не достигнут."""
        if len(self.bullets) < self.ai_settings.bullets_allowed:
            new_bullet = Bullet(self.ai_settings, self.screen, self.ship)
            self.bullets.add(new_bullet)

    def _update_screen(self):
        """Обновляет изображения на экране и отображает новый экран."""
        self.screen.fill(self.ai_settings.bg_color)
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.ship.blitme()
        self.aliens.draw(self.screen)

        # Отображение взрывов
        self.explosions.update()
        for explosion in self.explosions.sprites():
            explosion.blitme()

        self.sb.show_score()

        if not self.stats.game_active:
            self.play_button.draw_button()

        pygame.display.flip()

if __name__ == '__main__':
    ai = AlienInvasion()
    ai.run_game()
