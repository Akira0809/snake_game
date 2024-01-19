import pygame
import pygame.mixer
from pygame.locals import *

import spotipy
from spotipy.oauth2 import SpotifyOAuth

import random

from PIL import Image

SIZE = 40
name = []

class Spotify:
    def __init__(self):
        self.my_id = "3b3edf74b13b4a909411a3fddebd9fad"
        self.my_secret = "2c575faf6a9b419083dd24e675386ac5"
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=self.my_id,
                                                            client_secret=self.my_secret,
                                                            redirect_uri="http://localhost:3000",
                                                            scope="user-read-recently-played"))
        self.playlist_items = self.sp.playlist_items("6BKEQZYYimjnjvEUgQyWIF")
        self.blocks = []

        for item in self.playlist_items['items']:
            music_name = item['track']['name']
            self.blocks.append(music_name)

        random.shuffle(self.blocks)

        self.index = -1

    def get_random_block(self):
        self.index += 1
        if self.index >= len(self.blocks):
            self.index = 0
            random.shuffle(self.blocks)
        name.append(self.blocks[self.index])
        return self.blocks[self.index]


class Apple:
    def __init__(self, parent_screen):
        music_name = Spotify().get_random_block()
        self.apple = pygame.image.load(f'resources/spotify/images/{music_name}_image.jpg').convert()
        pygame.mixer.music.load(f'resources/spotify/musics/{music_name}_music.mp3')
        pygame.mixer.music.set_volume(0.1)
        pygame.mixer.music.play()
        self.parent_screen = parent_screen
        self.x = random.randint(0, 24)*SIZE
        self.y = random.randint(0, 19)*SIZE

    def average_color(image_path):
        img = Image.open(image_path)

        total_red = 0
        total_green = 0
        total_blue = 0

        for x in range(SIZE):
            for y in range(SIZE):
                red, green, blue = img.getpixel((x, y))
                total_red += red
                total_green += green
                total_blue += blue

        num_pixels = SIZE * SIZE
        avg_red = int(total_red / num_pixels)
        avg_green = int(total_green / num_pixels)
        avg_blue = int(total_blue / num_pixels)

        return (avg_red, avg_green, avg_blue)

    def draw(self):
        self.parent_screen.blit(self.apple, (self.x, self.y))
        pygame.display.flip()

    def move(self):
        pygame.mixer.music.stop()
        self.x = random.randint(0, 24)*SIZE
        self.y = random.randint(0, 19)*SIZE
        music_name = Spotify().get_random_block()
        self.apple = pygame.image.load(f'resources/spotify/images/{music_name}_image.jpg').convert()
        pygame.mixer.music.load(f'resources/spotify/musics/{music_name}_music.mp3')
        pygame.mixer.music.set_volume(0.1)
        pygame.mixer.music.play()


class Snake:
    def __init__(self, parent_screen, length):
        self.length = length
        self.parent_screen = parent_screen
        self.block = pygame.image.load('resources/block.jpg').convert()
        self.x = [SIZE]*length
        self.y = [SIZE]*length
        self.direction = 'right'

    def increase_length(self):
        self.length += 1
        self.x.append(-1)
        self.y.append(-1)

    def draw(self):
        self.parent_screen.fill((Apple.average_color(f'resources/spotify/images/{name[-1]}_image.jpg')))
        self.parent_screen.blit(self.block, (self.x[0], self.y[0]))
        for i in range(1, self.length):
            torso = pygame.image.load(f'resources/spotify/images/{name[i-1]}_image.jpg').convert()
            self.parent_screen.blit(torso, (self.x[i], self.y[i]))
        pygame.display.flip()

    def walk(self):

        for i in range(self.length-1, 0, -1):
            self.x[i] = self.x[i-1]
            self.y[i] = self.y[i-1]

        if self.direction == 'up':
            self.y[0] -= SIZE
            self.draw()
        elif self.direction == 'down':
            self.y[0] += SIZE
            self.draw()
        elif self.direction == 'left':
            self.x[0] -= SIZE
            self.draw()
        elif self.direction == 'right':
            self.x[0] += SIZE
            self.draw()


class Game:
    def __init__(self):
        pygame.init()
        self.surface = pygame.display.set_mode((1000, 800))
        self.apple = Apple(self.surface)
        self.apple.draw()
        self.snake = Snake(self.surface, 1)
        self.snake.draw()
        self.clock = pygame.time.Clock()

    def is_collision(self, x1, y1, x2, y2):
        if x1 >= x2 and x1 < x2+SIZE:
            if y1 >= y2 and y1 < y2+SIZE:
                return True

        return False

    def wall_collision(self, x1, y1):
        if x1 < 0 or x1 > 1000:
            return True
        if y1 < 0 or y1 > 800:
            return True

        return False

    def play(self):
        self.snake.walk()
        self.apple.draw()
        self.display_score()
        pygame.display.flip()

        if self.is_collision(self.snake.x[0], self.snake.y[0], self.apple.x, self.apple.y):
            self.apple.move()
            self.snake.increase_length()

        for i in range(3, self.snake.length):
            if self.is_collision(self.snake.x[0], self.snake.y[0], self.snake.x[i], self.snake.y[i]):
                raise "Game over"

        if self.wall_collision(self.snake.x[0], self.snake.y[0]):
            raise "Game over"



    def show_game_over(self):
        self.surface.fill((Apple.average_color(f'resources/spotify/images/{name[-1]}_image.jpg')))
        font = pygame.font.SysFont('arial', 30)
        line1 = font.render(f"Game is over! Your score is {self.snake.length}", True, (200, 200, 200))
        self.surface.blit(line1, (200, 300))
        line2 = font.render("To play again press Enter. To exit press Escape!", True, (200, 200, 200))
        self.surface.blit(line2, (200, 350))
        pygame.display.flip()

    def display_score(self):
        font = pygame.font.SysFont('arial', 30)
        score = font.render(f"Score: {self.snake.length}", True, (200, 200, 200))
        self.surface.blit(score, (850, 10))

    def run(self):
        running = True
        pause = False

        while running:
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False

                    if event.key == K_UP:
                        if self.snake.direction != 'down':
                            self.snake.direction = 'up'

                    if event.key == K_DOWN:
                        if self.snake.direction != 'up':
                            self.snake.direction = 'down'

                    if event.key == K_LEFT:
                        if self.snake.direction != 'right':
                            self.snake.direction = 'left'

                    if event.key == K_RIGHT:
                        if self.snake.direction != 'left':
                            self.snake.direction = 'right'

                    if event.key == K_RETURN:
                        pause = False
                        self.snake = Snake(self.surface, 1)
                        self.apple = Apple(self.surface)

                elif event.type == QUIT:
                    running = False

            try:
                if not pause:
                    self.play()
            except Exception as e:
                self.show_game_over()
                pause = True

            self.clock.tick(5)


if __name__ == '__main__':
    game = Game()
    game.run()