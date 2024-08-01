import unittest
import pygame
from alien_invasion import AlienInvasion

class TestAlienInvasion(unittest.TestCase):

    def setUp(self):
        # Инициализируем игру
        self.game = AlienInvasion()
        self.game._create_fleet()
        self.game.ship.center_ship()

    def tearDown(self):
        # Завершение работы pygame
        pygame.quit()

    def test_game_initialization(self):
        """Тест инициализации игры"""
        self.assertIsInstance(self.game, AlienInvasion)
        self.assertTrue(self.game.stats.game_active)

    def test_ship_initial_position(self):
        """Тест начальной позиции корабля"""
        self.assertEqual(self.game.ship.rect.midbottom, self.game.ship.screen_rect.midbottom)

    def test_ship_movement_right(self):
        """Тест движения корабля вправо"""
        initial_position = self.game.ship.rect.x
        self.game.ship.moving_right = True
        self.game.ship.update()
        self.assertGreater(self.game.ship.rect.x, initial_position)
        self.game.ship.moving_right = False

    def test_ship_movement_left(self):
        """Тест движения корабля влево"""
        initial_position = self.game.ship.rect.x
        self.game.ship.moving_left = True
        self.game.ship.update()
        self.assertLess(self.game.ship.rect.x, initial_position)
        self.game.ship.moving_left = False

    def test_bullet_firing(self):
        """Тест стрельбы пулями"""
        initial_bullet_count = len(self.game.bullets)
        self.game._fire_bullet()
        self.assertEqual(len(self.game.bullets), initial_bullet_count + 1)

    def test_bullet_removal(self):
        """Тест удаления пуль, вышедших за экран"""
        self.game._fire_bullet()
        bullet = self.game.bullets.sprites()[0]
        bullet.rect.y = -10  # Пуля выходит за экран
        self.game._update_bullets()
        self.assertEqual(len(self.game.bullets), 0)

    def test_alien_creation(self):
        """Тест создания пришельцев"""
        self.assertGreater(len(self.game.aliens), 0)

    def test_alien_movement(self):
        """Тест движения пришельцев"""
        initial_positions = [alien.rect.x for alien in self.game.aliens.sprites()]
        self.game._update_aliens()
        new_positions = [alien.rect.x for alien in self.game.aliens.sprites()]
        self.assertNotEqual(initial_positions, new_positions)

    def test_ship_hit(self):
        """Тест столкновения с пришельцем"""
        self.game.stats.ships_left = 1
        self.game._ship_hit()
        self.assertEqual(self.game.stats.ships_left, 0)
        self.assertFalse(self.game.stats.game_active)

if __name__ == '__main__':
    unittest.main()
