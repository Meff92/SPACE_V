import pygame
import os

pygame.init()

# Screen
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('SPACE-V')

# Time
clock = pygame.time.Clock()
FPS = 60
ANIMATION_COOLDOWN = 150

# Game variables
GRAVITY = 0.8

# Player's actions
is_moving_left = False
is_moving_right = False
is_shooting = False
is_using_grenade = False
is_grenade_thrown = False

# Images
bullet_image = pygame.image.load('project-VAK/img/shoot/player-shoot-hit1.png').convert_alpha()
grenade_image = pygame.image.load('project-VAK/img/items/grenade.png').convert_alpha()

# Colors
BACKGROUND_COLOR = (144, 201, 120)
RED_COLOR = (255, 0, 0)

# Fonts
font = pygame.font.Font("project-VAK/img/gui/ThaleahFat.ttf", 48)


def draw_text(text, font, text_col, x, y):
    text_image = font.render(text, True, text_col)
    screen.blit(text_image, (x, y))


def draw_background():
    screen.fill(BACKGROUND_COLOR)
    pygame.draw.line(screen, RED_COLOR, (0, 300), (SCREEN_WIDTH, 300))

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, scale, speed, ammo, grenades):
        pygame.sprite.Sprite.__init__(self)
        self.is_alive = True
        self.speed = speed
        self.ammo = ammo
        self.start_ammo = ammo
        self.shoot_cooldown = 0
        self.direction = 1
        self.grenades = grenades
        self.health = 100
        self.max_health = self.health
        self.v_vel = 0
        self.is_jumping = False
        self.in_air = True
        self.is_flipped = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()

        animation_types = ['Player-idle', 'player-run', 'Player-Jump', 'Player-Death']
        for animation in animation_types:
            temp_list = []
            num_of_frames = len(os.listdir(f'project-VAK/img/sprites/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'project-VAK/img/sprites/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20
            bullet = Bullet(self.rect.centerx + (0.9 * self.rect.size[0] * self.direction), self.rect.centery,
                            self.direction)
            bullet_group.add(bullet)
            self.ammo -= 1

    def update(self):
        self.update_animation()
        self.check_alive()
        if self.shoot_cooldown != 0:
            self.shoot_cooldown -= 1

    def move(self, moving_left, moving_right):
        if moving_left and moving_right:
            dx = 0
        else:
            dx = -self.speed if moving_left else self.speed if moving_right else 0

        self.is_flipped = moving_left
        self.direction = -1 if moving_left else 1 if moving_right else self.direction

        if self.is_jumping and not self.in_air:
            self.v_vel, self.is_jumping, self.in_air = -11, False, True

        self.v_vel = min(self.v_vel + GRAVITY, 10)
        dy = self.v_vel
        if self.rect.bottom + dy > 300:
            dy, self.in_air = 300 - self.rect.bottom, False

        self.rect.x += dx
        self.rect.y += dy

    def update_animation(self):
        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.is_alive = False
            self.update_action(3)

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.is_flipped, False), self.rect)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = bullet_image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        self.rect.x += (self.direction * self.speed)
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.is_alive:
                player.health -= 20
                self.kill()
        for enemy in enemies_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.is_alive:
                    enemy.health -= 25
                    self.kill()


class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 38
        self.v_vel = -11
        self.speed = 7
        self.image = grenade_image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        self.v_vel += GRAVITY
        dx = self.direction * self.speed
        dy = self.v_vel

        if self.rect.bottom + dy > 300:
            dy = 300 - self.rect.bottom
            self.speed = 0

        if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
            self.direction *= -1
            dx = self.direction * self.speed

        self.rect.x += dx
        self.rect.y += dy

        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            explosion = Explosion(self.rect.x, self.rect.y, 6)
            explosion_group.add(explosion)

            if abs(self.rect.centerx - player.rect.centerx) < 90 and abs(
                    self.rect.centery - player.rect.centery) < 90:
                player.health -= 100
            for enemy in enemies_group:
                if abs(self.rect.centerx - enemy.rect.centerx) < 90 and abs(
                        self.rect.centery - enemy.rect.centery) < 90:
                    enemy.health -= 100


class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        self.images = list()
        for i in range(1, 9):
            img = pygame.image.load(f'project-VAK/img/exp/explosion{i}.png').convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.images.append(img)
        self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0

    def update(self):
        speed_of_explosion = 5
        self.counter += 1

        if self.counter >= speed_of_explosion:
            self.counter = 0
            self.frame_index += 1
            if self.frame_index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_index]


enemies_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()

player = Player(200, 200, 3, 5, 20, 5)
enemy = Player(400, 200, 3, 5, 20, 0)
enemy1 = Player(400, 400, 3, 5, 20, 0)
enemies_group.add(enemy)
enemies_group.add(enemy1)
run = True


def draw_status_bar(player_value, bars, pos_x, pos_y):
    for limit, img in sorted(bars.items(), reverse=True):
        if player_value > limit:
            img_bar = pygame.image.load(f"project-VAK/img/gui/{img}").convert_alpha()
            img_bar = pygame.transform.scale(img_bar, (int(img_bar.get_width() * 4), int(img_bar.get_height() * 4)))
            screen.blit(img_bar, (pos_x, pos_y))
            break


while run:

    clock.tick(FPS)

    draw_background()
    health_bars = {75: "health_bar4.png", 40: "health_bar3.png", 10: "health_bar2.png", 0: "health_bar1.png",
                   -1: "health_bar0.png"}
    ammo_bars = {15: "ammo5.png", 10: "ammo4.png", 5: "ammo3.png", 1: "ammo2.png", 0: "ammo1.png", -1: "ammo0.png"}

    draw_text(f'HEALTH', font, (0, 0, 0), 843, 15)
    draw_status_bar(player.health, health_bars, 670, 23)

    draw_text(f'AMMO', font, (0, 0, 0), 523, 15)
    draw_status_bar(player.ammo, ammo_bars, 440, 25)

    player.update()
    player.draw()

    for enemy in enemies_group:
        enemy.update()
        enemy.draw()

    bullet_group.update()
    grenade_group.update()
    explosion_group.update()
    bullet_group.draw(screen)
    grenade_group.draw(screen)
    explosion_group.draw(screen)
    if player.is_alive:
        if is_shooting:
            player.shoot()
            is_shooting = False
        elif is_using_grenade and not is_grenade_thrown and player.grenades > 0:
            is_using_grenade = Grenade(player.rect.centerx + (0.5 * player.rect.size[0] * player.direction),
                                       player.rect.top,
                                       player.direction)
            grenade_group.add(is_using_grenade)
            player.grenades -= 1
            is_grenade_thrown = True
        if player.in_air:
            player.update_action(2)
        elif is_moving_left or is_moving_right:
            player.update_action(1)
        else:
            player.update_action(0)
        player.move(is_moving_left, is_moving_right)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                is_moving_left = True
            if event.key == pygame.K_d:
                is_moving_right = True
            if event.key == pygame.K_w and player.is_alive:
                player.is_jumping = True
            if event.key == pygame.K_ESCAPE:
                run = False
            if event.key == pygame.K_q:
                is_using_grenade = True
            if event.key == pygame.K_SPACE:
                is_shooting = True

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                is_moving_left = False
            if event.key == pygame.K_d:
                is_moving_right = False
            if event.key == pygame.K_q:
                is_using_grenade = False
                is_grenade_thrown = False

    pygame.display.update()

pygame.quit()