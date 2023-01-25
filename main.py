# -------- Setup
import pygame, sys, random, pygame.font, os, subprocess
pygame.init()

# ------- Constant variables
INFO = pygame.display.Info()
GAME_WIDTH, GAME_HEIGHT = 1280, 720
SCREEN_WIDTH, SCREEN_HEIGHT = INFO.current_w, INFO.current_h
#SCREEN_WIDTH, SCREEN_HEIGHT = (960, 40)
FPS = 80

WIDTH_MULTI = SCREEN_WIDTH/GAME_WIDTH
HEIGHT_MULTI = SCREEN_HEIGHT/GAME_HEIGHT

class Font:
    fps = pygame.font.Font(None, 25)
    death = pygame.font.Font(None, 50)

# Colors
class Color:
    red = (255, 0, 0)
    green = (0, 255, 0)
    blue = (0, 0, 255)
    white = (255, 255, 255)
    black = (0, 0, 0)
    grey = (150, 150, 150)

# Sprites
class Sprite:
    player = pygame.image.load(os.path.join(os.getcwd(), 'images', 'Player.png'))
    rock = pygame.image.load(os.path.join(os.getcwd(), 'images', 'Rock.png'))

# -------- Variables
display = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
clock = pygame.time.Clock()

background_color = Color.blue

# -------- Functions

# --------- Class's
class RelativeHandler:
    @staticmethod
    def relative_image(image):
        return pygame.transform.smoothscale(image, (image.get_width() * WIDTH_MULTI, image.get_height() * HEIGHT_MULTI))

    @staticmethod
    def relative_rect(rect):
        rect[0] *= WIDTH_MULTI
        rect[1] *= HEIGHT_MULTI
        rect[2] *= WIDTH_MULTI
        rect[3] *= HEIGHT_MULTI
        return rect

    @staticmethod
    def absolute_rect(rect):
        rect[0] /= WIDTH_MULTI
        rect[1] /= HEIGHT_MULTI
        rect[2] /= WIDTH_MULTI
        rect[3] /= HEIGHT_MULTI
        return rect

    @staticmethod
    def absolute_pos(pos):
        pos = list(pos)
        pos[0] /= WIDTH_MULTI
        pos[1] /= HEIGHT_MULTI
        return pos


class Object:
    def __init__(self, start_pos, image_path, size):
        self.pos = start_pos
        self.image = RelativeHandler.relative_image(pygame.transform.smoothscale(pygame.image.load(image_path), size))
        self.size = size

    def set_pos(self, pos):
        self.pos[0] = pos[0] - (self.size[0] / 2)
        self.pos[1] = pos[1] - (self.size[1] / 2)

    def update(self):
        pass

    def display(self, screen):
        screen.blit(self.image, (self.pos[0] * WIDTH_MULTI, self.pos[1] * HEIGHT_MULTI))


class Player:
    def __init__(self, start_pos, image, size = None, relative_size = False):
        self.start_pos = list(start_pos)
        self.pos = list(start_pos)
        if size and not relative_size:
            self.image = RelativeHandler.relative_image(pygame.transform.smoothscale(image, size))
            self.size = size
        elif type(size) in [tuple, list]:
            self.size = (image.get_width()*size[0], image.get_height()*size[1])
            self.image = RelativeHandler.relative_image(pygame.transform.smoothscale(image, self.size))
        else:
            self.size = image.get_size()
            self.image = RelativeHandler.relative_image(image)

        self.velocity = [0, 0]

        self.jump_power = 25
        self.gravity_strength = 0.98

        self.dead = False
    
    def ground(self):
        if self.pos[1] > self.start_pos[1]:
            self.pos[1] = self.start_pos[1]
            self.velocity[1] = 0

    def collide_check(self, rocks_rect):
        if pygame.Rect(*self.pos, *self.size).colliderect(rocks_rect):
            self.dead = True

    def move(self, delta):
        self.pos[0] += self.velocity[0] * delta
        self.pos[1] += self.velocity[1] * delta

    def gravity(self, delta):
        if self.pos[1] < self.start_pos[1]:
            self.velocity[1] += self.gravity_strength * delta

    def update(self, pressed, delta):
        if pressed and self.pos == self.start_pos:
            self.velocity[1] -= self.jump_power

        self.gravity(delta)
        self.move(delta)
        self.ground()

    def display(self, screen):
        screen.blit(self.image, (self.pos[0] * WIDTH_MULTI, self.pos[1] * HEIGHT_MULTI))


class Rock:
    def __init__(self, start_pos, image, size = None, relative_size = False):
        self.start_pos = list(start_pos)
        self.pos = list(start_pos)
        if size and not relative_size:
            self.image = RelativeHandler.relative_image(pygame.transform.smoothscale(image, size))
            self.size = size
        elif type(size) in [tuple, list]:
            self.size = (image.get_width()*size[0], image.get_height()*size[1])
            self.image = RelativeHandler.relative_image(pygame.transform.smoothscale(image, self.size))
        else:
            self.size = image.get_size()
            self.image = RelativeHandler.relative_image(image)

        self.speed = -5

    def move(self, delta):
        self.pos[0] += self.speed * delta

    def update(self, delta):
        self.move(delta)

        if self.pos[0] < -20 - self.image.get_width():
            self.pos[0] = SCREEN_WIDTH
            self.speed -= 1

    def get_rect(self):
        return (*self.pos, *self.size)

    def display(self, screen):
        screen.blit(self.image, (self.pos[0] * WIDTH_MULTI, self.pos[1] * HEIGHT_MULTI))

player = Player((50, GAME_HEIGHT - Sprite.player.get_height()*0.3 - 50), Sprite.player, (0.3, 0.3), True)
rock = Rock((SCREEN_WIDTH + 50, GAME_HEIGHT - Sprite.player.get_height()*0.3 - 15), Sprite.rock, (0.3, 0.3), True)

# --------- Main
def main():
    global player, rock
    pressed = False
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
        
        # Time
        if clock.get_fps() != 0:
            delta = 80 / clock.get_fps()
        else:
            delta = 1

        # Update
        prev_pressed = pressed
        pressed = pygame.mouse.get_pressed()[0]
        clicked = (not prev_pressed and pressed)

        player.collide_check(rock.get_rect())

        player.update(pressed, delta)
        rock.update(delta)

        # Render
        display.fill(background_color)

        rock.display(display)
        player.display(display)

        if player.dead:
            display.fill(Color.red)
            dead_text = RelativeHandler.relative_image(Font.death.render("You died! Click to restart!", True, Color.black))
            display.blit(dead_text, ((SCREEN_WIDTH / 2 - dead_text.get_width() / 2), (SCREEN_HEIGHT / 2 - dead_text.get_height() / 2)))

            if clicked:
                player = Player((50, GAME_HEIGHT - Sprite.player.get_height()*0.3 - 50), Sprite.player, (0.3, 0.3), True)
                rock = Rock((SCREEN_WIDTH + 50, GAME_HEIGHT - Sprite.player.get_height()*0.3 - 15), Sprite.rock, (0.3, 0.3), True)

        fps_text = Font.fps.render("FPS: " + str(round(clock.get_fps(), 2)), True, Color.black)
        display.blit(fps_text, (5, 5))

        pygame.display.flip()
        clock.tick(FPS)

# -------- Start
if __name__ == "__main__":
    main()
