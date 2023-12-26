import pygame
import os
import random
import math

pygame.init()


# Screen
info = pygame.display.Info()
SCREEN_WIDTH = 1536
SCREEN_HEIGHT = 864
SCREEN_WIDTH_19 = 1980
SCREEN_HEIGHT_19 = 864

print(SCREEN_WIDTH, SCREEN_HEIGHT)

screen = pygame.display.set_mode((1536,864),pygame.FULLSCREEN)
pygame.display.set_caption('SPACE-V')

# Time
clock = pygame.time.Clock()
FPS = 60
ANIMATION_COOLDOWN = 150

# Game variables

# Player's actions
is_moving_left = False
is_moving_right = False
is_moving_down = False
is_moving_up = False
is_shooting = False
is_using_grenade = False
is_grenade_thrown = False

# Images
bullet_image = pygame.image.load('project-VAK/img/shoot/player-shoot-hit1.png').convert_alpha()
grenade_image = pygame.image.load('project-VAK/img/gui/Robert_junk/big_demon_idle_anim_f1.png').convert_alpha()

# Colors
BACKGROUND_COLOR = (144, 201, 120)
RED_COLOR = (255, 0, 0)

# Fonts
font = pygame.font.Font("project-VAK/img/gui/ThaleahFat.ttf", 48)
font_2 = pygame.font.Font("project-VAK/img/gui/Stacked pixel.ttf", 320)
font_3 = pygame.font.Font("project-VAK/img/gui/Stacked pixel.ttf", 58)
font_4 =  pygame.font.Font("project-VAK/img/gui/Stacked pixel.ttf", 38)
def draw_text(text, font, text_col, x, y):
    text_image = font.render(text, True, text_col)
    screen.blit(text_image, (x, y))


def draw_background():
    screen.fill((255,255,255))


def get_angle_to_cursor(player_rect):
    mouseX, mouseY = pygame.mouse.get_pos()
    delta_x, delta_y = mouseX - player_rect.centerx, mouseY - player_rect.centery
    angle_rad = math.atan2(delta_y, delta_x)

    # Переводим радианы в градусы
    angle_deg = math.degrees(angle_rad)
    print(angle_deg)
    # Отрицательные углы преобразуем в положительные
    if angle_deg < 0:
        angle_deg += 360

    return angle_deg

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

        animation_types = ['Player-idle', 'player-run', 'Player-Death']
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
            # Get the angle to the cursor
            angle = get_angle_to_cursor(self.rect)
            bullet = Bullet(self.rect.centerx, self.rect.centery, angle, "player")
            bullet_group.add(bullet)
            self.ammo -= 1

    def update(self):
        self.update_animation()
        self.check_alive()
        if self.shoot_cooldown != 0:
            self.shoot_cooldown -= 1

    def move(self, moving_left, moving_right, moving_down, moving_up):
        if moving_left and moving_right:
            dx = 0
        else:
            dx = -self.speed if moving_left else self.speed if moving_right else 0
        
        self.direction = -1 if moving_left else 1 if moving_right else self.direction

        if moving_up and moving_down:
            dy = 0
        else:
            dy = self.speed if moving_down else -self.speed if moving_up else 0


        self.rect.x += dx
        self.rect.y += dy

    def update_animation(self):
        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 2:
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
            self.update_action(2)

    def draw(self):
        if self.direction == -1:
            screen.blit(pygame.transform.flip(self.image, True, False), self.rect)
        else:
            screen.blit(pygame.transform.flip(self.image, False, False), self.rect)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, sender):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = bullet_image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.angle = angle
        self.sender = sender

    def update(self):
        # Update bullet position based on angle
        self.rect.x += self.speed * math.cos(math.radians(self.angle))
        self.rect.y += self.speed * math.sin(math.radians(self.angle))

        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH or \
           self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()

        if pygame.sprite.spritecollide(player, bullet_group, False):
            if self.sender != "player":
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
        self.v_vel += 0.8
        dx = self.direction * self.speed
        dy = self.v_vel

        if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
            self.direction *= -1
            dx = self.direction * self.speed

        self.rect.x += dx
        self.rect.y += dy

        self.timer -= 1.15
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

class Animate_smt(pygame.sprite.Sprite):
    def __init__(self, update, num_of_i, path_to, need_to_scale, scale_w=0, scale_h=0):
        pygame.sprite.Sprite.__init__(self)
        self.images = list()
        self.num_of_i = num_of_i
        for i in range(self.num_of_i):
            img_sd = pygame.image.load(f'project-VAK/img/{path_to}{i+1}.png').convert_alpha()
            if need_to_scale:
                img_sd = pygame.transform.scale(img_sd, (int(SCREEN_WIDTH * scale_w), int(SCREEN_HEIGHT * scale_h)))
            else:
                img_sd = pygame.transform.scale(img_sd, (int(img_sd.get_width() * scale_w), int(img_sd.get_height() * scale_h)))
            self.images.append(img_sd)
        self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.counter = 0
        self.update_ = update

    def update(self):
        self.counter += 1

        if self.counter >= self.update_:
            self.frame_index += 1
            self.counter = 0
            if self.frame_index >= self.num_of_i:
                self.frame_index = 0
                self.image = self.images[self.frame_index]
            else:
                self.image = self.images[self.frame_index]
    
    def draw(self, surface, x, y):
        surface.blit(self.image, (x, y))

enemies_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
sounds_group = list()

player = Player(200, 200, 3, 5, 20, 5)
player_for_menu = Player(500, 760, 2.7, 5, 20, 5)
enemy = Player(400, 200, 3, 5, 20, 0)
enemy1 = Player(400, 400, 3, 5, 20, 0)
enemies_group.add(enemy)
enemies_group.add(enemy1)
run = True

stars = Animate_smt(random.randint(250, 280), 4, "gui/bg_men/menu_", True, 0.5, 0.5)
stars1 = Animate_smt(random.randint(250, 280), 4, "gui/bg_men/menu_", True, 0.5, 0.5)
stars2 = Animate_smt(random.randint(250, 280), 4, "gui/bg_men/menu_", True, 0.5, 0.5)
stars3 = Animate_smt(random.randint(250, 280), 4, "gui/bg_men/menu_", True, 0.5, 0.5)
white_cat = Animate_smt(100, 15, "gui/white_cat/white_grey", False, 5, 5)
brown_cat = Animate_smt(50, 5, "gui/brown_cat/brown", False, 5, 5)

Jack = Animate_smt(10, 4, "gui/Jack_guns/Idle", False, 12, 12)
Jenifer = Animate_smt(10, 4, "gui/Jenifer_skills/Idle-", False, 8, 8)
Robert = Animate_smt(10, 4, "gui/Robert_junk/big_demon_idle_anim_f", False, 8, 8)
Alla = Animate_smt(15, 8, "gui/Alla_food/balancing", False, 15, 15)

def color_menu():
    stars.update()
    stars1.update()
    stars2.update()
    stars3.update()
    stars.draw(screen, 0, 0)
    stars.draw(screen, 900, 190)
    stars.draw(screen, 900, 360)
    stars.draw(screen, 900, 480)
    stars1.draw(screen, 50, 0)
    stars1.draw(screen, 0, 500)
    stars.draw(screen, 500, 500)
    stars.draw(screen, 800, 500)
    stars2.draw(screen, 800, 200)
    stars2.draw(screen, 900, 0)
    stars.draw(screen, 600, 0)
    stars3.draw(screen, 300, 70)
    stars3.draw(screen, 0, 70)


click_sound = pygame.mixer.Sound("project-VAK/img/sfx/main_menu/click.mp3")
select_but = pygame.mixer.Sound("project-VAK/img/sfx/main_menu/select_but.mp3")
city_noise = pygame.mixer.Sound("project-VAK/img/sfx/main_menu/home_noise.mp3")
sounds_group.append(click_sound)
sounds_group.append(select_but)
sounds_group.append(city_noise)
random_track = [1,2,3,4,5]
random.shuffle(random_track)
for i in random_track:
    main_music = pygame.mixer.music.load(f"project-VAK/img/sfx/main_menu/main_music{i}.mp3")
pygame.mixer.music.play(-1)

def draw_status_bar(player_value, bars, pos_x, pos_y):
    for limit, img in sorted(bars.items(), reverse=True):
        if player_value > limit:
            img_bar = pygame.image.load(f"project-VAK/img/gui/{img}").convert_alpha()
            img_bar = pygame.transform.scale(img_bar, (int(img_bar.get_width() * 4), int(img_bar.get_height() * 4)))
            screen.blit(img_bar, (pos_x, pos_y))
            break

class Button:
    def __init__(self, x, y, image, scale, image_sel, image_press=None, sound_make=True):
        self.width = image.get_width()
        self.height = image.get_height()
        self.scale = scale
        self.image = pygame.transform.scale(
            image, (int(self.width * self.scale), int(self.height * self.scale))
        )
        self.image_press = image_press
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False
        self.image_sel = image_sel
        self.sound_make = sound_make



    def draw(self, surface):
        self.clicked = False
        action = False
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            self.image = pygame.transform.scale(
                self.image_sel, (int(self.width * self.scale), int(self.height * self.scale))
            )
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                if self.image_press != None:
                    self.image = pygame.transform.scale(
                        self.image_press, (int(self.width * self.scale), int(self.height * self.scale))
                    )
                if self.sound_make == True:
                    click_sound.stop()
                    click_sound.play()
                    
                self.clicked = True
        surface.blit(self.image, (self.rect.x, self.rect.y))
        return action

class ScreenFade():
    def __init__(self, direction, clr, speed):
        self.direc = direction
        self.clr = clr
        self.speed = speed
        self.fade_counter = 0

    def fade(self):
        fade_complete = False
        self.fade_counter += self.speed
        if self.direc == 1:
            pygame.draw.rect(screen, self.clr, (0 - self.fade_counter, 0, SCREEN_WIDTH//2, SCREEN_HEIGHT + 300))
            pygame.draw.rect(screen, self.clr, (768 + self.fade_counter, 0, SCREEN_WIDTH, SCREEN_HEIGHT + 300))
        if self.direc == 2:
            pygame.draw.rect(screen, self.clr, (0,0, SCREEN_WIDTH, 0 + self.fade_counter))
        if self.direc == 3:
            pygame.draw.rect(screen, self.clr, (0 - self.fade_counter * 7, 0, SCREEN_WIDTH//2, SCREEN_HEIGHT + 300))
            pygame.draw.rect(screen, self.clr, (768 + self.fade_counter * 7, 0, SCREEN_WIDTH, SCREEN_HEIGHT + 300))
        if self.fade_counter > SCREEN_WIDTH - 500:
            fade_complete = True
        
        return fade_complete

intro_fade = ScreenFade(1, (0,0,0), 4)
death_fade = ScreenFade(2, (0,0,0), 4)
shop_fade = ScreenFade(3, (0,0,0), 4)

money = 5000
money_diamond = 500
ship_level = 6
bar_of_volume_game_music = 0
bar_of_volume_game_sounds = 5
volume_game_music = 0
volume_game_sound = 1
guns_player_have = [2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
small_fruit = 0
fresh_fruit = 0
big_fruit = 0

floating_ship_speed = 0.1
floating_arrow_speed = 0.2
y_for_ship_pos = 300
y_for_ship_pos_for_menu = 525
arrow_pos = 824
pygame.mixer.music.set_volume(volume_game_music)
for sound in sounds_group:
    sound.set_volume(volume_game_sound)
make_action = 0
current_window_selected = "main_menu"
flag_shop = 2
gun_which = 1

while run:
    if current_window_selected == "main_menu":
        color_menu()
        button_images = {
            "start": {
                "default": pygame.image.load("project-VAK/img/gui/button_start.png").convert_alpha(),
                "selected": pygame.image.load("project-VAK/img/gui/button_start_select.png").convert_alpha()
            },
            "option": {
                "default": pygame.image.load("project-VAK/img/gui/button_options.png").convert_alpha(),
                "selected": pygame.image.load("project-VAK/img/gui/button_options_select.png").convert_alpha()
            },
            "credit": {
                "default": pygame.image.load("project-VAK/img/gui/button_credits.png").convert_alpha(),
                "selected": pygame.image.load("project-VAK/img/gui/button_credits_select.png").convert_alpha()
            },
            "exit": {
                "default": pygame.image.load("project-VAK/img/gui/button_exit.png").convert_alpha(),
                "selected": pygame.image.load("project-VAK/img/gui/button_exit_select.png").convert_alpha()
            }
        }

        ship_images = {
            1: "project-VAK/img/gui/ships/ship1.png",
            2: "project-VAK/img/gui/ships/ship2.png",
            3: "project-VAK/img/gui/ships/ship3.png",
            4: "project-VAK/img/gui/ships/ship4.png",
            5: "project-VAK/img/gui/ships/ship5.png",
            6: "project-VAK/img/gui/ships/ship6.png"
        }

        ship_im = pygame.image.load(ship_images[ship_level]).convert_alpha()
        ship_im = pygame.transform.scale(ship_im, (int(ship_im.get_width() * 5), int(ship_im.get_height() * 5)))
        screen.blit(ship_im, (680 if ship_level == 1 else 580, y_for_ship_pos + 180 if ship_level == 1 else y_for_ship_pos))

        draw_text("SPACE V", font_2, (255, 255, 255), 10, 90)
        draw_text("ver 0.6", font, (155, 55, 95), 1440, 860)
        draw_text("ver 0.6", font, (90, 90, 90), 1440, 858)

        y_for_ship_pos += floating_ship_speed
        if y_for_ship_pos >= 320 or y_for_ship_pos <= 290:
            floating_ship_speed = -floating_ship_speed

        buttons = {
            "credit": Button(SCREEN_WIDTH // 45, SCREEN_HEIGHT // 2 + 210, button_images["credit"]["default"], 7, button_images["credit"]["selected"]),
            "start": Button(SCREEN_WIDTH // 45, SCREEN_HEIGHT // 2 - 10, button_images["start"]["default"], 7, button_images["start"]["selected"]),
            "option": Button(SCREEN_WIDTH // 45, SCREEN_HEIGHT // 2 + 100, button_images["option"]["default"], 7, button_images["option"]["selected"]),
            "exit": Button(SCREEN_WIDTH // 45, SCREEN_HEIGHT // 2 + 320, button_images["exit"]["default"], 7, button_images["exit"]["selected"])
        }

        if buttons["credit"].draw(screen):
            current_window_selected = "credits"
        if buttons["start"].draw(screen):
            city_noise.play(-1)
            start_intro = True
            current_window_selected = "home"
        if buttons["option"].draw(screen):
            current_window_selected = "options"
        if buttons["exit"].draw(screen):
            run = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                run = False

    if current_window_selected == "home":
        page = 1
        enter_shop = None
        clock.tick(FPS)
        back_ground_for_home = pygame.image.load("project-VAK/img/gui/menu_in_play.png").convert_alpha()
        back_ground_for_home = pygame.transform.scale(back_ground_for_home, (int(back_ground_for_home.get_width() * 4), int(back_ground_for_home.get_height() * 5.1)))
        screen.blit(back_ground_for_home, (0,12))
        screen.blit(back_ground_for_home, (0,-80))
    
        ship_images = {
            1: ("project-VAK/img/gui/ships/ship1.png", 4),
            2: ("project-VAK/img/gui/ships/ship2.png", 4.2),
            3: ("project-VAK/img/gui/ships/ship3.png", 4.4),
            4: ("project-VAK/img/gui/ships/ship4.png", 4.4),
            5: ("project-VAK/img/gui/ships/ship5.png", 4.6),
            6: ("project-VAK/img/gui/ships/ship6.png", 4.5)
        }
    
        if ship_level in ship_images:
            ship_im = pygame.image.load(ship_images[ship_level][0]).convert_alpha()
            ship_im = pygame.transform.scale(ship_im, (int(ship_im.get_width() * ship_images[ship_level][1]), int(ship_im.get_height() * ship_images[ship_level][1])))
            screen.blit(ship_im, (310, y_for_ship_pos_for_menu - 170))
    
        player_for_menu.update()
        player_for_menu.draw()
        
        y_for_ship_pos_for_menu += floating_ship_speed
        if y_for_ship_pos_for_menu >= 525:
            floating_ship_speed = -floating_ship_speed
        if y_for_ship_pos_for_menu <= 535:
            floating_ship_speed = -floating_ship_speed

        if player_for_menu.rect.x >= 500 and player_for_menu.rect.x <= 590:
            draw_text("PRESS SPACE TO FLY INTO THE SPACE", font_4, (255,255,255), 20, 12)
        if player_for_menu.rect.x >= 5 and player_for_menu.rect.x <= 95:
            draw_text("PRESS SPACE TO ENTER THE WEAPONS STORE", font_4, (255,255,255), 20, 12)
            enter_shop = "weapons"
        if player_for_menu.rect.x >= 850 and player_for_menu.rect.x <= 1170:
            draw_text("PRESS SPACE TO ENTER THE FOOD SHOP", font_4, (255,255,255), 20, 12)
            enter_shop = "food"
        if player_for_menu.rect.x >= 1233 and player_for_menu.rect.x <= 1310:
            draw_text("PRESS SPACE TO ENTER THE 'JUNK' STORE", font_4, (255,255,255), 20, 12)
            enter_shop = "junk"
        if player_for_menu.rect.x >= 1400 and player_for_menu.rect.x <= 1493:
            draw_text("PRESS SPACE TO ENTER THE SKILL STORE", font_4, (255,255,255), 20, 12)
            enter_shop = "skill"
        arrow = pygame.image.load("project-VAK/img/gui/strelka.png").convert_alpha()
        arrow = pygame.transform.scale(arrow, (int(arrow .get_width() * 6), int(arrow .get_height() * 6)))
        screen.blit(arrow , (70, arrow_pos))
        screen.blit(arrow , (580, arrow_pos))
        screen.blit(arrow , (1050, arrow_pos))
        screen.blit(arrow , (1287, arrow_pos))
        screen.blit(arrow , (1485, arrow_pos))
        arrow_pos += floating_arrow_speed
        if arrow_pos >= 824:
            floating_arrow_speed = -floating_arrow_speed
        if arrow_pos <= 832:
            floating_arrow_speed = -floating_arrow_speed
        if start_intro == True:
                if flag_shop != 1:
                    if intro_fade.fade():
                        start_intro = False
                        intro_fade.fade_counter = 0
                else:
                    if shop_fade.fade():
                        start_intro = False
                        shop_fade.fade_counter = 0
        
        if player_for_menu.is_alive:
            if is_moving_left or is_moving_right or is_moving_down or is_moving_up:
                if (is_moving_left and is_moving_right) and not is_moving_up and not is_moving_down:
                    player_for_menu.update_action(0)
                elif (is_moving_down and is_moving_up) and not is_moving_right and not is_moving_left:
                    player_for_menu.update_action(0)
                else:
                    player_for_menu.update_action(1)
            else:
                player_for_menu.update_action(0)
            player_for_menu.move(is_moving_left, is_moving_right, is_moving_down, is_moving_up)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    is_moving_left = True
                if event.key == pygame.K_d:
                    is_moving_right = True
                if event.key == pygame.K_ESCAPE:
                    run = False
                if event.key == pygame.K_SPACE:
                    if enter_shop != None:
                        start_intro = True
                        intro_fade.fade_counter = 0
                        shop_fade.fade_counter = 0
                        current_window_selected = enter_shop
                        city_noise.stop()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    is_moving_left = False
                if event.key == pygame.K_d:
                    is_moving_right = False

    if current_window_selected == "weapons":
        clock.tick(FPS)
        is_moving_left = False
        is_moving_right = False
        back_shop = pygame.image.load("project-VAK/img/gui/shops_back/guns.png").convert_alpha()
        back_shop = pygame.transform.scale(back_shop, (int(back_shop.get_width() * 3), int(back_shop.get_height() * 3)))
        screen.blit(back_shop, (820,0))
        screen.blit(back_shop, (0,0))
        Jack.update()
        Jack.draw(screen, 950, -60)
        back_im = pygame.image.load("project-VAK/img/gui/button_back.png").convert_alpha()
        back_im_s = pygame.image.load("project-VAK/img/gui/button_back_select.png").convert_alpha()
        back_button = Button(1430, 20, back_im, 5, back_im_s)
        table_im = pygame.image.load("project-VAK/img/gui/shops_back/guns_table.png").convert_alpha()
        table_im = pygame.transform.scale(table_im, (int(table_im.get_width() * 9), int(table_im.get_height() * 8.35)))
        sml_button_empty = pygame.image.load("project-VAK/img/gui/empty_small.png").convert_alpha()
        sml_button_empty = pygame.transform.scale(sml_button_empty, (int(sml_button_empty.get_width() * 1), int(sml_button_empty.get_height() * 1)))
        sml_button_clossed = pygame.image.load("project-VAK/img/gui/closed_small.png").convert_alpha()
        sml_button_clossed = pygame.transform.scale(sml_button_clossed, (int(sml_button_clossed.get_width() * 1), int(sml_button_clossed.get_height() * 1)))
        sml_button_yes = pygame.image.load("project-VAK/img/gui/yes_small.png").convert_alpha()
        sml_button_yes = pygame.transform.scale(sml_button_yes, (int(sml_button_yes.get_width() * 1), int(sml_button_yes.get_height() * 1)))
        sml_button_no = pygame.image.load("project-VAK/img/gui/no_small.png").convert_alpha()
        sml_button_no = pygame.transform.scale(sml_button_no, (int(sml_button_no.get_width() * 1), int(sml_button_no.get_height() * 1)))
        screen.blit(table_im, (-120,-15))
        move_for_guns = 170
        # кнопки для покупки тут как много ща будет
        if page == 1:
            button_positions = [
    (14, 110), (164, 110), (334, 110), (494, 110), (655, 110), (865, 110),
    (14, 320), (184, 320), (344, 320), (564, 320), (744, 320), (914, 320),
    (14, 540), (174, 540), (344, 540), (534, 540), (684, 540), (884, 540),
    (10, 740), (170, 740), (344, 740), (514, 740), (684, 740), (864, 740)
]

            for i, (x, y) in enumerate(button_positions):
                index = i % len(guns_player_have)
                if guns_player_have[index] == 2:
                    button = Button(x, y, sml_button_yes, 7, sml_button_yes, sml_button_yes)
                elif guns_player_have[index] == 1:
                    button = Button(x, y, sml_button_empty, 7, sml_button_empty, sml_button_empty)
                else:
                    button = Button(x, y, sml_button_clossed, 7, sml_button_clossed, sml_button_clossed)

                locals()[f'b{i + 1}'] = button

                
            for i in range(24):
                if globals()[f"b{i+1}"].draw(screen):
                    if guns_player_have[i] == 0 or guns_player_have[i] == 2:
                        page = 3
                        gun_which = i + 1
                    elif guns_player_have[i] == 1:
                        guns_player_have[guns_player_have.index(2)] = 1
                        guns_player_have[i] = 2
                        page = 3
                        gun_which = i + 1


            button_right_im = pygame.image.load("project-VAK/img/gui/button_right.png").convert_alpha()
            button_right_im_press = pygame.image.load("project-VAK/img/gui/button_right_press.png").convert_alpha()
            button_right = Button(1020, 700, button_right_im, 7, button_right_im, button_right_im_press)

            if button_right.draw(screen):
                page = 2

            for i in range(6):
                gun = pygame.image.load(f"project-VAK/img/gui/guns/{i + 1}.png").convert_alpha()
                gun = pygame.transform.scale(gun, (int(gun.get_width() * 5), int(gun.get_height() * 5)))
                if i > 0:
                    screen.blit(gun, (10 + move_for_guns * i - 25, 30))
                else:
                    screen.blit(gun, (10 + move_for_guns * i , 30))
            for i in range(6):
                gun = pygame.image.load(f"project-VAK/img/gui/guns/{6 + i + 1}.png").convert_alpha()
                gun = pygame.transform.scale(gun, (int(gun.get_width() * 5), int(gun.get_height() * 5)))
                if i > 1 and i != 2 and i != 4:
                    screen.blit(gun, (10 + move_for_guns * i + 50, 245))
                elif i == 2:
                    screen.blit(gun, (10 + move_for_guns * i, 245))
                elif i == 4:
                    screen.blit(gun, (10 + move_for_guns * i + 70, 265))
                else:
                    screen.blit(gun, (10 + move_for_guns * i, 230))
            for i in range(6):
                gun = pygame.image.load(f"project-VAK/img/gui/guns/{12 + i + 1}.png").convert_alpha()
                gun = pygame.transform.scale(gun, (int(gun.get_width() * 5), int(gun.get_height() * 5)))
                screen.blit(gun, (10 + move_for_guns * i, 445))
            for i in range(6):
                gun = pygame.image.load(f"project-VAK/img/gui/guns/{18 + i + 1}.png").convert_alpha()
                gun = pygame.transform.scale(gun, (int(gun.get_width() * 5), int(gun.get_height() * 5)))
                if i == 0:
                    screen.blit(gun, (10 + move_for_guns * i, 685))
                elif i == 4:
                    screen.blit(gun, (10 + move_for_guns * i, 685))
                elif i == 1:
                    screen.blit(gun, (10 + move_for_guns * i, 675))
                else:
                    screen.blit(gun, (10 + move_for_guns * i, 655))

        if page == 2:
            for i in range(len(guns_player_have)):
                if i == 24:
                    if guns_player_have[i] == 2:
                        b25 = Button(14, 110, sml_button_yes, 7, sml_button_yes, sml_button_yes)
                    if guns_player_have[i] == 1:
                        b25 = Button(14, 110, sml_button_empty, 7, sml_button_empty, sml_button_empty)
                    if guns_player_have[i] == 0:
                        b25 = Button(14, 110, sml_button_clossed, 7, sml_button_clossed, sml_button_clossed)
                if i == 25:
                    if guns_player_have[i] == 2:
                        b26 = Button(204, 110, sml_button_yes, 7, sml_button_yes, sml_button_yes)
                    if guns_player_have[i] == 1:
                        b26 = Button(204, 110, sml_button_empty, 7, sml_button_empty, sml_button_empty)
                    if guns_player_have[i] == 0:
                        b26 = Button(204, 110, sml_button_clossed, 7, sml_button_clossed, sml_button_clossed)
                if i == 26:
                    if guns_player_have[i] == 2:
                        b27 = Button(384,110, sml_button_yes, 7, sml_button_yes, sml_button_yes)
                    if guns_player_have[i] == 1:
                        b27 = Button(384, 110, sml_button_empty, 7, sml_button_empty, sml_button_empty)
                    if guns_player_have[i] == 0:
                        b27 = Button(384, 110, sml_button_clossed, 7, sml_button_clossed, sml_button_clossed)
                if i == 27:
                    if guns_player_have[i] == 2:
                        b28 = Button(574, 110, sml_button_yes, 7, sml_button_yes, sml_button_yes)
                    if guns_player_have[i] == 1:
                        b28 = Button(574, 110, sml_button_empty, 7, sml_button_empty, sml_button_empty)
                    if guns_player_have[i] == 0:
                        b28 = Button(574, 110, sml_button_clossed, 7, sml_button_clossed, sml_button_clossed)
                if i == 28:
                    if guns_player_have[i] == 2:
                        b29 = Button(785, 110, sml_button_yes, 7, sml_button_yes, sml_button_yes)
                    if guns_player_have[i] == 1:
                        b29 = Button(785, 110, sml_button_empty, 7, sml_button_empty, sml_button_empty)
                    if guns_player_have[i] == 0:
                        b29 = Button(785, 110, sml_button_clossed, 7, sml_button_clossed, sml_button_clossed)
                if i == 29:
                    if guns_player_have[i] == 2:
                        b30 = Button(985, 110, sml_button_yes, 7, sml_button_yes, sml_button_yes)
                    if guns_player_have[i] == 1:
                        b30 = Button(985, 110, sml_button_empty, 7, sml_button_empty, sml_button_empty)
                    if guns_player_have[i] == 0:
                        b30 = Button(985, 110, sml_button_clossed, 7, sml_button_clossed, sml_button_clossed)

                if i == 30:
                    if guns_player_have[i] == 2:
                        b31 = Button(14, 280, sml_button_yes, 7, sml_button_yes, sml_button_yes)
                    if guns_player_have[i] == 1:
                        b31 = Button(14, 280, sml_button_empty, 7, sml_button_empty, sml_button_empty)
                    if guns_player_have[i] == 0:
                        b31 = Button(14, 320, sml_button_clossed, 7, sml_button_clossed, sml_button_clossed)
                if i == 31:
                    if guns_player_have[i] == 2:
                        b32 = Button(234, 320, sml_button_yes, 7, sml_button_yes, sml_button_yes)
                    if guns_player_have[i] == 1:
                        b32 = Button(234, 320, sml_button_empty, 7, sml_button_empty, sml_button_empty)
                    if guns_player_have[i] == 0:
                        b32 = Button(234, 320, sml_button_clossed, 7, sml_button_clossed, sml_button_clossed)
                if i == 32:
                    if guns_player_have[i] == 2:
                        b33 = Button(494, 320, sml_button_yes, 7, sml_button_yes, sml_button_yes)
                    if guns_player_have[i] == 1:
                        b33 = Button(494, 320, sml_button_empty, 7, sml_button_empty, sml_button_empty)
                    if guns_player_have[i] == 0:
                        b33 = Button(494, 320, sml_button_clossed, 7, sml_button_clossed, sml_button_clossed)
                if i == 33:
                    if guns_player_have[i] == 2:
                        b34 = Button(704, 320, sml_button_yes, 7, sml_button_yes, sml_button_yes)
                    if guns_player_have[i] == 1:
                        b34 = Button(704, 320, sml_button_empty, 7, sml_button_empty, sml_button_empty)
                    if guns_player_have[i] == 0:
                        b34 = Button(704, 320, sml_button_clossed, 7, sml_button_clossed, sml_button_clossed)
                if i == 34:
                    if guns_player_have[i] == 2:
                        b35 = Button(904, 320, sml_button_yes, 7, sml_button_yes, sml_button_yes)
                    if guns_player_have[i] == 1:
                        b35 = Button(904, 320, sml_button_empty, 7, sml_button_empty, sml_button_empty)
                    if guns_player_have[i] == 0:
                        b35 = Button(904, 320, sml_button_clossed, 7, sml_button_clossed, sml_button_clossed) 

            if b25.draw(screen):
                if guns_player_have[24] == 0:
                    page = 3
                    gun_which = 25
                if guns_player_have[24] == 1 or guns_player_have[24] == 2:
                    guns_player_have[guns_player_have.index(2)] = 1
                    guns_player_have[24] = 2
                    page = 3
                    gun_which = 25
            if b26.draw(screen):
                if guns_player_have[25] == 0:
                    page = 3
                    gun_which = 26
                if guns_player_have[25] == 1 or guns_player_have[25] == 2:
                    guns_player_have[guns_player_have.index(2)] = 1
                    guns_player_have[25] = 2
                    page = 3
                    gun_which = 26
            if b27.draw(screen):
                if guns_player_have[26] == 0 or guns_player_have[26] == 2:
                    gun_which = 27
                    page = 3
                if guns_player_have[26] == 1 or guns_player_have[26] == 2:
                    guns_player_have[guns_player_have.index(2)] = 1
                    guns_player_have[26] = 2
                    gun_which = 27
                    page = 3
            if b28.draw(screen):
                if guns_player_have[27] == 0 or guns_player_have[27] == 2:
                    gun_which = 28
                    page = 3
                if guns_player_have[27] == 1 or guns_player_have[27] == 2:
                    guns_player_have[guns_player_have.index(2)] = 1
                    guns_player_have[27] = 2
                    gun_which = 28
                    page = 3
            if b29.draw(screen):
                if guns_player_have[28] == 0:
                    gun_which = 29
                    page = 3
                if guns_player_have[28] == 1 or guns_player_have[28] == 2:
                    guns_player_have[guns_player_have.index(2)] = 1
                    guns_player_have[28] = 2
                    gun_which = 29
                    page = 3
            if b30.draw(screen):
                if guns_player_have[29] == 0:
                    gun_which = 30
                    page = 3
                if guns_player_have[29] == 1 or guns_player_have[29] == 2:
                    guns_player_have[guns_player_have.index(2)] = 1
                    guns_player_have[29] = 2
                    gun_which = 30
                    page = 3
            if b31.draw(screen):
                if guns_player_have[30] == 0:
                    gun_which = 31
                    page = 3
                if guns_player_have[30] == 1 or guns_player_have[30] == 2:
                    guns_player_have[guns_player_have.index(2)] = 1
                    guns_player_have[30] = 2
                    gun_which = 31
                    page = 3
            if b32.draw(screen):
                if guns_player_have[31] == 0:
                    gun_which = 32
                    page = 3
                if guns_player_have[31] == 1 or guns_player_have[31] == 2:
                    guns_player_have[guns_player_have.index(2)] = 1
                    guns_player_have[31] = 2
                    gun_which = 32
                    page = 3
            if b33.draw(screen):
                if guns_player_have[32] == 0:
                    gun_which = 33
                    page = 3
                if guns_player_have[32] == 1 or guns_player_have[32] == 2:
                    guns_player_have[guns_player_have.index(2)] = 1
                    guns_player_have[32] = 2
                    gun_which = 33
                    page = 3
            if b34.draw(screen):
                if guns_player_have[33] == 0:
                    gun_which = 34
                    page = 3
                if guns_player_have[33] == 1 or guns_player_have[33] == 2:
                    guns_player_have[guns_player_have.index(2)] = 1
                    guns_player_have[33] = 2
                    gun_which = 34
                    page = 3
            if b35.draw(screen):
                if guns_player_have[34] == 0:
                    gun_which = 35
                    page = 3
                if guns_player_have[34] == 1 or guns_player_have[34] == 2:
                    guns_player_have[guns_player_have.index(2)] = 1
                    guns_player_have[34] = 2
                    gun_which = 35
                    page = 3
            button_left_im = pygame.image.load("project-VAK/img/gui/button_left.png").convert_alpha()
            button_left_im_press = pygame.image.load("project-VAK/img/gui/button_left_press.png").convert_alpha()
            button_left = Button(20, 450, button_left_im, 7, button_left_im, button_left_im_press)
            if button_left.draw(screen):
                page = 1
            for i in range(6):
                gun = pygame.image.load(f"project-VAK/img/gui/guns/{24 + i + 1}.png").convert_alpha()
                gun = pygame.transform.scale(gun, (int(gun.get_width() * 5), int(gun.get_height() * 5)))
                if i == 0:
                    screen.blit(gun, (10 + move_for_guns * i * 1.15 , 20))
                elif i == 2 or i == 3:
                    screen.blit(gun, (10 + move_for_guns * i * 1.15 - 30, 30))
                else:
                    screen.blit(gun, (10 + move_for_guns * i * 1.15 , 30))
            for i in range(5):
                gun = pygame.image.load(f"project-VAK/img/gui/guns/{30 + i + 1}.png").convert_alpha()
                gun = pygame.transform.scale(gun, (int(gun.get_width() * 5), int(gun.get_height() * 5)))
                screen.blit(gun, (30 + move_for_guns * i * 1.3 , 240))


        if page == 3:
            money_im = pygame.image.load(f"project-VAK/img/gui/money/money.png").convert_alpha()
            money_im = pygame.transform.scale(money_im, (int(money_im.get_width() * 5), int(money_im.get_height() * 5)))
            screen.blit(money_im,(10, 30))
            
            button_left_im = pygame.image.load("project-VAK/img/gui/button_left.png").convert_alpha()
            button_left_im_press = pygame.image.load("project-VAK/img/gui/button_left_press.png").convert_alpha()
            button_left = Button(20, 660, button_left_im, 7, button_left_im, button_left_im_press)
            

            draw_text("----------------------------------------------------------------------------------", font_4, (255,255,255), 0, 800)

            if button_left.draw(screen):
                page = 1

            diamond_im = pygame.image.load(f"project-VAK/img/gui/money/diamond.png").convert_alpha()
            diamond_im = pygame.transform.scale(diamond_im, (int(diamond_im.get_width() * 3), int(diamond_im.get_height() * 3)))
            screen.blit(diamond_im,(350, 60))
            draw_text(f"{money_diamond}", font_3, (255,255,255), 470, 100)
            button_buy_im = pygame.image.load("project-VAK/img/gui/button_buy.png").convert_alpha()
            button_buy_im_select = pygame.image.load("project-VAK/img/gui/button_buy_select.png").convert_alpha()
            button_buy = Button(690, 645, button_buy_im, 9, button_buy_im_select, button_buy_im)
            draw_text(f"{money}", font_3, (255,255,255), 190, 100)
            money_im_sml = pygame.image.load(f"project-VAK/img/gui/money/money_sml.png").convert_alpha()
            money_im_sml = pygame.transform.scale(money_im_sml, (int(money_im_sml.get_width() * 5), int(money_im_sml.get_height() * 5)))

            diamond_im_sml = pygame.image.load(f"project-VAK/img/gui/money/diamond_sml.png").convert_alpha()
            diamond_im_sml = pygame.transform.scale(diamond_im_sml, (int(diamond_im_sml.get_width() * 5), int(diamond_im_sml.get_height() * 5)))   

            if gun_which == 1:
                if guns_player_have[0] == 2 or guns_player_have[0] == 1:
                    pass
                elif money >= 50 and money_diamond >= 1:
                    if button_buy.draw(screen):
                        money -= 50
                        money_diamond -= 1
                        guns_player_have[guns_player_have.index(2)] = 1
                        guns_player_have[0] = 2
                else:
                    draw_text("You can't buy it!", font_3, (255,255,255), 600, 690)
                gun = pygame.image.load(f"project-VAK/img/gui/guns/1.png").convert_alpha()
                gun = pygame.transform.scale(gun, (int(gun.get_width() * 13), int(gun.get_height() * 13)))
                screen.blit(gun,(0, 250))
                draw_text("Celestial Blaster", font_3, (255,205,205), 450, 228)
                draw_text("Celestial Blaster", font_3, (255,255,255), 450, 230)
                draw_text("common", font_3, (255,205,205), 450, 280)
                draw_text("----------------------------------------------------------------------------------", font_4, (255,205,205), 0, 802)
                draw_text("- 10 charges", font_3, (255,255,255), 450, 350)
                draw_text("- 1 bullet per shot", font_3, (255,255,255), 450, 400)
                draw_text("- 10 damage", font_3, (255,255,255), 450, 450)
                draw_text("- 1 Speed", font_3, (255,255,255), 450, 500)

            if gun_which == 2:
                if guns_player_have[1] == 2 or guns_player_have[1] == 1:
                    pass
                elif money >= 20 and money_diamond >= 0:
                    if button_buy.draw(screen):
                        money -= 20
                        money_diamond -= 0
                        guns_player_have[guns_player_have.index(2)] = 1
                        guns_player_have[1] = 2
                else:
                    draw_text("You can't buy it!", font_3, (255,255,255), 670, 680)
                gun = pygame.image.load(f"project-VAK/img/gui/guns/2.png").convert_alpha()
                gun = pygame.transform.scale(gun, (int(gun.get_width() * 13), int(gun.get_height() * 13)))
                screen.blit(gun,(0, 250))
                draw_text("Starstrike Cannon", font_3, (255,205,205), 450, 228)
                draw_text("Starstrike Cannon", font_3, (255,255,255), 450, 230)
                draw_text("common", font_3, (255,205,205), 450, 280)
                draw_text("----------------------------------------------------------------------------------", font_4, (255,205,205), 0, 802)
                draw_text("- 15 charges", font_3, (255,255,255), 450, 350)
                draw_text("- 1 bullet per shot", font_3, (255,255,255), 450, 400)
                draw_text("- 15 damage", font_3, (255,255,255), 450, 450)
                draw_text("- 1.2 Speed", font_3, (255,255,255), 450, 500)
                draw_text("Cost: 20", font_3, (255,255,255), 150, 680)
                draw_text("0", font_3, (255,255,255), 520, 680)
                screen.blit(money_im_sml,(390, 660))
                screen.blit(diamond_im_sml,(560, 660))

            if gun_which == 3:
                if guns_player_have[2] == 2 or guns_player_have[2] == 1:
                    pass
                elif money >= 50 and money_diamond >= 0:
                    if button_buy.draw(screen):
                        money -= 50
                        money_diamond -= 0
                        guns_player_have[guns_player_have.index(2)] = 1
                        guns_player_have[2] = 2
                else:
                    draw_text("You can't buy it!", font_3, (255,255,255), 670, 680)
                gun = pygame.image.load(f"project-VAK/img/gui/guns/3.png").convert_alpha()
                gun = pygame.transform.scale(gun, (int(gun.get_width() * 13), int(gun.get_height() * 13)))
                screen.blit(gun,(0, 250))
                draw_text("Nebula Ray", font_3, (255,205,205), 450, 228)
                draw_text("Nebula Ray", font_3, (255,255,255), 450, 230)
                draw_text("common", font_3, (255,205,205), 450, 280)
                draw_text("----------------------------------------------------------------------------------", font_4, (255,205,205), 0, 802)
                draw_text("- 20 charges", font_3, (255,255,255), 450, 350)
                draw_text("- 2 bullet per shot", font_3, (255,255,255), 450, 400)
                draw_text("- 10 damage", font_3, (255,255,255), 450, 450)
                draw_text("- 0.8 Speed", font_3, (255,255,255), 450, 500)
                draw_text("Cost: 50", font_3, (255,255,255), 150, 680)
                draw_text("0", font_3, (255,255,255), 520, 680)
                screen.blit(money_im_sml,(390, 660))
                screen.blit(diamond_im_sml,(560, 660))

            if gun_which == 4:
                if guns_player_have[3] == 2 or guns_player_have[3] == 1:
                    pass
                elif money >= 90 and money_diamond >= 1:
                    if button_buy.draw(screen):
                        money -= 90
                        money_diamond -= 1
                        guns_player_have[guns_player_have.index(2)] = 1
                        guns_player_have[3] = 2
                else:
                    draw_text("You can't buy it!", font_3, (255,255,255), 670, 680)

                gun = pygame.image.load(f"project-VAK/img/gui/guns/4.png").convert_alpha()
                gun = pygame.transform.scale(gun, (int(gun.get_width() * 13), int(gun.get_height() * 13)))
                screen.blit(gun,(0, 250))
                draw_text("Lunar Phaser", font_3, (255,205,205), 450, 228)
                draw_text("Lunar Phaser", font_3, (255,255,255), 450, 230)
                draw_text("common", font_3, (255,205,205), 450, 280)
                draw_text("----------------------------------------------------------------------------------", font_4, (255,205,205), 0, 802)
                draw_text("- 30 charges", font_3, (255,255,255), 450, 350)
                draw_text("- 1 bullet per shot", font_3, (255,255,255), 450, 400)
                draw_text("- 30 damage", font_3, (255,255,255), 450, 450)
                draw_text("- 0.6 Speed", font_3, (255,255,255), 450, 500)
                draw_text("Cost: 90", font_3, (255,255,255), 150, 680)
                draw_text("1", font_3, (255,255,255), 520, 680)
                screen.blit(money_im_sml,(390, 660))
                screen.blit(diamond_im_sml,(560, 660))

            if gun_which == 5:
                if guns_player_have[4] == 2 or guns_player_have[4] == 1:
                    pass
                elif money >= 130 and money_diamond >= 0:
                    if button_buy.draw(screen):
                        money -= 130
                        money_diamond -= 0
                        guns_player_have[guns_player_have.index(2)] = 1
                        guns_player_have[4] = 2
                else:
                    draw_text("You can't buy it!", font_3, (255,255,255), 670, 680)

                gun = pygame.image.load(f"project-VAK/img/gui/guns/5.png").convert_alpha()
                gun = pygame.transform.scale(gun, (int(gun.get_width() * 13), int(gun.get_height() * 13)))
                screen.blit(gun,(0, 250))
                draw_text("Plasma Cannon", font_3, (255,205,205), 450, 228)
                draw_text("Plasma Cannon", font_3, (255,255,255), 450, 230)
                draw_text("common", font_3, (255,205,205), 450, 280)
                draw_text("----------------------------------------------------------------------------------", font_4, (255,205,205), 0, 802)
                draw_text("- 25 charges", font_3, (255,255,255), 450, 350)
                draw_text("- 1 bullet per shot", font_3, (255,255,255), 450, 400)
                draw_text("- 50 damage", font_3, (255,255,255), 450, 450)
                draw_text("- 0.8 Speed", font_3, (255,255,255), 450, 500)
                draw_text("Cost: 130", font_3, (255,255,255), 150, 680)
                draw_text("0", font_3, (255,255,255), 520, 680)
                screen.blit(money_im_sml,(390, 660))
                screen.blit(diamond_im_sml,(560, 660))

            if gun_which == 6:
                if guns_player_have[5] == 2 or guns_player_have[5] == 1:
                    pass
                elif money >= 145 and money_diamond >= 2:
                    if button_buy.draw(screen):
                        money -= 145
                        money_diamond -= 2
                        guns_player_have[guns_player_have.index(2)] = 1
                        guns_player_have[5] = 2
                else:
                    draw_text("You can't buy it!", font_3, (255,255,255), 670, 680)

                gun = pygame.image.load(f"project-VAK/img/gui/guns/6.png").convert_alpha()
                gun = pygame.transform.scale(gun, (int(gun.get_width() * 13), int(gun.get_height() * 13)))
                screen.blit(gun,(0, 250))
                draw_text("Venusian Vortex", font_3, (255,205,205), 450, 228)
                draw_text("Venusian Vortex", font_3, (255,255,255), 450, 230)
                draw_text("common", font_3, (255,205,205), 450, 280)
                draw_text("----------------------------------------------------------------------------------", font_4, (255,205,205), 0, 802)
                draw_text("- 30 charges", font_3, (255,255,255), 450, 350)
                draw_text("- 1 bullet per shot", font_3, (255,255,255), 450, 400)
                draw_text("- 25 damage", font_3, (255,255,255), 450, 450)
                draw_text("- 1.3 Speed", font_3, (255,255,255), 450, 500)
                draw_text("Cost: 145", font_3, (255,255,255), 150, 680)
                draw_text("2", font_3, (255,255,255), 520, 680)
                screen.blit(money_im_sml,(390, 660))
                screen.blit(diamond_im_sml,(560, 660))



            if gun_which == 7:
                if guns_player_have[6] == 2 or guns_player_have[6] == 1:
                    pass
                elif money >= 200 and money_diamond >= 1:
                    if button_buy.draw(screen):
                        money -= 200
                        money_diamond -= 1
                        guns_player_have[guns_player_have.index(2)] = 1
                        guns_player_have[6] = 2
                else:
                    draw_text("You can't buy it!", font_3, (255,255,255), 670, 680)

                gun = pygame.image.load(f"project-VAK/img/gui/guns/7.png").convert_alpha()
                gun = pygame.transform.scale(gun, (int(gun.get_width() * 13), int(gun.get_height() * 13)))
                screen.blit(gun,(0, 250))
                draw_text("Draco Destructor", font_3, (60,255,60), 450, 228)
                draw_text("Draco Destructor", font_3, (255,255,255), 450, 230)
                draw_text("Rare", font_3, (60,255,60), 450, 280)
                draw_text("----------------------------------------------------------------------------------", font_4, (60,205,60), 0, 802)
                draw_text("- 40 charges", font_3, (255,255,255), 450, 350)
                draw_text("- 1 bullet per shot", font_3, (255,255,255), 450, 400)
                draw_text("- 30 damage", font_3, (255,255,255), 450, 450)
                draw_text("- 1 Speed", font_3, (255,255,255), 450, 500)
                draw_text("Cost: 200", font_3, (255,255,255), 150, 680)
                draw_text("1", font_3, (255,255,255), 520, 680)
                screen.blit(money_im_sml,(390, 660))
                screen.blit(diamond_im_sml,(560, 660))

            if gun_which == 8:
                if guns_player_have[7] == 2 or guns_player_have[7] == 1:
                    pass
                elif money >= 245 and money_diamond >= 4:
                    if button_buy.draw(screen):
                        money -= 245
                        money_diamond -= 4
                        guns_player_have[guns_player_have.index(2)] = 1
                        guns_player_have[7] = 2
                else:
                    draw_text("You can't buy it!", font_3, (255,255,255), 670, 680)

                gun = pygame.image.load(f"project-VAK/img/gui/guns/8.png").convert_alpha()
                gun = pygame.transform.scale(gun, (int(gun.get_width() * 13), int(gun.get_height() * 13)))
                screen.blit(gun,(0, 250))
                draw_text("Infinity Laser", font_3, (60,255,60), 450, 228)
                draw_text("Infinity Laser", font_3, (255,255,255), 450, 230)
                draw_text("rare", font_3, (60,255,60), 450, 280)
                draw_text("----------------------------------------------------------------------------------", font_4, (60,205,60), 0, 802)
                draw_text("- 40 charges", font_3, (255,255,255), 450, 350)
                draw_text("- lazer", font_3, (255,255,255), 450, 400)
                draw_text("- 30 damage", font_3, (255,255,255), 450, 450)
                draw_text("- 1 Speed", font_3, (255,255,255), 450, 500)
                draw_text("Cost: 245", font_3, (255,255,255), 150, 680)
                draw_text("4", font_3, (255,255,255), 520, 680)
                screen.blit(money_im_sml,(390, 660))
                screen.blit(diamond_im_sml,(560, 660))

            if gun_which == 9:
                if guns_player_have[8] == 2 or guns_player_have[8] == 1:
                    pass
                elif money >= 240 and money_diamond >= 0:
                    if button_buy.draw(screen):
                        money -= 240
                        money_diamond -= 0
                        guns_player_have[guns_player_have.index(2)] = 1
                        guns_player_have[8] = 2
                else:
                    draw_text("You can't buy it!", font_3, (255,255,255), 670, 680)

                gun = pygame.image.load(f"project-VAK/img/gui/guns/9.png").convert_alpha()
                gun = pygame.transform.scale(gun, (int(gun.get_width() * 13), int(gun.get_height() * 13)))
                screen.blit(gun,(0, 250))
                draw_text("Automatic Hydra Homeing", font_3, (60,255,60), 450, 228)
                draw_text("Automatic Hydra Homeing", font_3, (255,255,255), 450, 230)
                draw_text("rare", font_3, (60,255,60), 450, 280)
                draw_text("----------------------------------------------------------------------------------", font_4, (60,205,60), 0, 802)
                draw_text("- 25 charges", font_3, (255,255,255), 450, 350)
                draw_text("- burst shooting", font_3, (255,255,255), 450, 400)
                draw_text("- 30 damage", font_3, (255,255,255), 450, 450)
                draw_text("- 1 Speed", font_3, (255,255,255), 450, 500)
                draw_text("Cost: 240", font_3, (255,255,255), 150, 680)
                draw_text("0", font_3, (255,255,255), 520, 680)
                screen.blit(money_im_sml,(390, 660))
                screen.blit(diamond_im_sml,(560, 660))         

            if gun_which == 10:
                if guns_player_have[9] == 2 or guns_player_have[9] == 1:
                    pass
                elif money >= 240 and money_diamond >= 0:
                    if button_buy.draw(screen):
                        money -= 240
                        money_diamond -= 0
                        guns_player_have[guns_player_have.index(2)] = 1
                        guns_player_have[9] = 2
                else:
                    draw_text("You can't buy it!", font_3, (255,255,255), 670, 680)

                gun = pygame.image.load(f"project-VAK/img/gui/guns/10.png").convert_alpha()
                gun = pygame.transform.scale(gun, (int(gun.get_width() * 13), int(gun.get_height() * 13)))
                screen.blit(gun,(0, 250))
                draw_text("Quantum Torpedo", font_3, (60,255,60), 450, 228)
                draw_text("Quantum Torpedo", font_3, (255,255,255), 450, 230)
                draw_text("rare", font_3, (60,255,60), 450, 280)
                draw_text("----------------------------------------------------------------------------------", font_4, (60,205,60), 0, 802)
                draw_text("- 10 charges", font_3, (255,255,255), 450, 350)
                draw_text("- 1 per shoot", font_3, (255,255,255), 450, 400)
                draw_text("- 50 damage", font_3, (255,255,255), 450, 450)
                draw_text("- 0.5 Speed", font_3, (255,255,255), 450, 500)
                draw_text("Cost: 240", font_3, (255,255,255), 150, 680)
                draw_text("0", font_3, (255,255,255), 520, 680)
                screen.blit(money_im_sml,(390, 660))
                screen.blit(diamond_im_sml,(560, 660))   

            if gun_which == 11:
                if guns_player_have[10] == 2 or guns_player_have[10] == 1:
                    pass
                elif money >= 225 and money_diamond >= 2:
                    if button_buy.draw(screen):
                        money -= 225
                        money_diamond -= 2
                        guns_player_have[guns_player_have.index(2)] = 1
                        guns_player_have[10] = 2
                else:
                    draw_text("You can't buy it!", font_3, (255,255,255), 670, 680)

                gun = pygame.image.load(f"project-VAK/img/gui/guns/11.png").convert_alpha()
                gun = pygame.transform.scale(gun, (int(gun.get_width() * 13), int(gun.get_height() * 13)))
                screen.blit(gun,(50, 350))
                draw_text("Plasma Lance", font_3, (60,255,60), 450, 228)
                draw_text("Plasma Lance", font_3, (255,255,255), 450, 230)
                draw_text("rare", font_3, (60,255,60), 450, 280)
                draw_text("----------------------------------------------------------------------------------", font_4, (60,205,60), 0, 802)
                draw_text("- 3 charges", font_3, (255,255,255), 450, 350)
                draw_text("- 3 pre shot", font_3, (255,255,255), 450, 400)
                draw_text("- 60 damage", font_3, (255,255,255), 450, 450)
                draw_text("- 1.2 Speed", font_3, (255,255,255), 450, 500)
                draw_text("Cost: 225", font_3, (255,255,255), 150, 680)
                draw_text("2", font_3, (255,255,255), 520, 680)
                screen.blit(money_im_sml,(390, 660))
                screen.blit(diamond_im_sml,(560, 660))

            if gun_which == 12:
                if guns_player_have[11] == 2 or guns_player_have[11] == 1:
                    pass
                elif money >= 310 and money_diamond >= 1:
                    if button_buy.draw(screen):
                        money -= 310
                        money_diamond -= 1
                        guns_player_have[guns_player_have.index(2)] = 1
                        guns_player_have[11] = 2
                else:
                    draw_text("You can't buy it!", font_3, (255,255,255), 670, 680)

                gun = pygame.image.load(f"project-VAK/img/gui/guns/12.png").convert_alpha()
                gun = pygame.transform.scale(gun, (int(gun.get_width() * 13), int(gun.get_height() * 13)))
                screen.blit(gun,(0, 250))
                draw_text("Supernova Staff", font_3, (60,255,60), 450, 228)
                draw_text("Supernova Staff", font_3, (255,255,255), 450, 230)
                draw_text("rare", font_3, (60,255,60), 450, 280)
                draw_text("----------------------------------------------------------------------------------", font_4, (60,205,60), 0, 802)
                draw_text("- 30 charges", font_3, (255,255,255), 450, 350)
                draw_text("- 2 pre shot", font_3, (255,255,255), 450, 400)
                draw_text("- 75 damage", font_3, (255,255,255), 450, 450)
                draw_text("- 1 Speed", font_3, (255,255,255), 450, 500)
                draw_text("Cost: 310", font_3, (255,255,255), 150, 680)
                draw_text("1", font_3, (255,255,255), 520, 680)
                screen.blit(money_im_sml,(390, 660))
                screen.blit(diamond_im_sml,(560, 660))

            if gun_which == 13:
                if guns_player_have[12] == 2 or guns_player_have[12] == 1:
                    pass
                elif money >= 470 and money_diamond >= 2:
                    if button_buy.draw(screen):
                        money -= 470
                        money_diamond -= 2
                        guns_player_have[guns_player_have.index(2)] = 1
                        guns_player_have[12] = 2
                else:
                    draw_text("You can't buy it!", font_3, (255,255,255), 670, 680)

                gun = pygame.image.load(f"project-VAK/img/gui/guns/13.png").convert_alpha()
                gun = pygame.transform.scale(gun, (int(gun.get_width() * 13), int(gun.get_height() * 13)))
                screen.blit(gun,(0, 250))
                draw_text("Quantum Accelerator", font_3, (255,255,10), 450, 228)
                draw_text("Quantum Accelerator", font_3, (255,255,255), 450, 230)
                draw_text("New", font_3, (255,255,10), 450, 280)
                draw_text("----------------------------------------------------------------------------------", font_4, (255,255,10), 0, 802)
                draw_text("- 40 charges", font_3, (255,255,255), 450, 350)
                draw_text("- Lazer", font_3, (255,255,255), 450, 400)
                draw_text("- 100 damage", font_3, (255,255,255), 450, 450)
                draw_text("- 1.2 Speed", font_3, (255,255,255), 450, 500)
                draw_text("Cost: 470", font_3, (255,255,255), 150, 680)
                draw_text("2", font_3, (255,255,255), 520, 680)
                screen.blit(money_im_sml,(390, 660))
                screen.blit(diamond_im_sml,(560, 660))

            if gun_which == 14:
                if guns_player_have[13] == 2 or guns_player_have[13] == 1:
                    pass
                elif money >= 400 and money_diamond >= 3:
                    if button_buy.draw(screen):
                        money -= 400
                        money_diamond -= 3
                        guns_player_have[guns_player_have.index(2)] = 1
                        guns_player_have[13] = 2
                else:
                    draw_text("You can't buy it!", font_3, (255,255,255), 670, 680)

                gun = pygame.image.load(f"project-VAK/img/gui/guns/14.png").convert_alpha()
                gun = pygame.transform.scale(gun, (int(gun.get_width() * 13), int(gun.get_height() * 13)))
                screen.blit(gun,(0, 250))
                draw_text("Solar Wind Whip", font_3, (255,255,10), 450, 228)
                draw_text("Solar Wind Whip", font_3, (255,255,255), 450, 230)
                draw_text("New", font_3, (255,255,10), 450, 280)
                draw_text("----------------------------------------------------------------------------------", font_4, (255,255,10), 0, 802)
                draw_text("- 50 charges", font_3, (255,255,255), 450, 350)
                draw_text("- 3 per shot", font_3, (255,255,255), 450, 400)
                draw_text("- 120 damage", font_3, (255,255,255), 450, 450)
                draw_text("- 1.5 Speed", font_3, (255,255,255), 450, 500)
                draw_text("Cost: 400", font_3, (255,255,255), 150, 680)
                draw_text("3", font_3, (255,255,255), 520, 680)
                screen.blit(money_im_sml,(390, 660))
                screen.blit(diamond_im_sml,(560, 660))

            if gun_which == 15:
                if guns_player_have[14] == 2 or guns_player_have[14] == 1:
                    pass
                elif money >= 430 and money_diamond >= 1:
                    if button_buy.draw(screen):
                        money -= 430
                        money_diamond -= 1
                        guns_player_have[guns_player_have.index(2)] = 1
                        guns_player_have[14] = 2
                else:
                    draw_text("You can't buy it!", font_3, (255,255,255), 670, 680)

                gun = pygame.image.load(f"project-VAK/img/gui/guns/15.png").convert_alpha()
                gun = pygame.transform.scale(gun, (int(gun.get_width() * 13), int(gun.get_height() * 13)))
                screen.blit(gun,(0, 250))
                draw_text("Starfire Bow", font_3, (255,255,10), 450, 228)
                draw_text("Starfire Bow", font_3, (255,255,255), 450, 230)
                draw_text("New", font_3, (255,255,10), 450, 280)
                draw_text("----------------------------------------------------------------------------------", font_4, (255,255,10), 0, 802)
                draw_text("- 10 charges", font_3, (255,255,255), 450, 350)
                draw_text("- 1 per shot", font_3, (255,255,255), 450, 400)
                draw_text("- 150 damage", font_3, (255,255,255), 450, 450)
                draw_text("- 1.5 Speed", font_3, (255,255,255), 450, 500)
                draw_text("Cost: 430", font_3, (255,255,255), 150, 680)
                draw_text("1", font_3, (255,255,255), 520, 680)
                screen.blit(money_im_sml,(390, 660))
                screen.blit(diamond_im_sml,(560, 660))

            if gun_which == 16:
                if guns_player_have[15] == 2 or guns_player_have[15] == 1:
                    pass
                elif money >= 470 and money_diamond >= 0:
                    if button_buy.draw(screen):
                        money -= 470
                        money_diamond -= 0
                        guns_player_have[guns_player_have.index(2)] = 1
                        guns_player_have[15] = 2
                else:
                    draw_text("You can't buy it!", font_3, (255,255,255), 670, 680)

                gun = pygame.image.load(f"project-VAK/img/gui/guns/16.png").convert_alpha()
                gun = pygame.transform.scale(gun, (int(gun.get_width() * 13), int(gun.get_height() * 13)))
                screen.blit(gun,(0, 250))
                draw_text("Meteoric Assault Cannon", font_3, (255,255,10), 450, 228)
                draw_text("Meteoric Assault Cannon", font_3, (255,255,255), 450, 230)
                draw_text("New", font_3, (255,255,10), 450, 280)
                draw_text("----------------------------------------------------------------------------------", font_4, (255,255,10), 0, 802)
                draw_text("- 30 charges", font_3, (255,255,255), 450, 350)
                draw_text("- 1 per shot", font_3, (255,255,255), 450, 400)
                draw_text("- 170 damage", font_3, (255,255,255), 450, 450)
                draw_text("- 1 Speed", font_3, (255,255,255), 450, 500)
                draw_text("Cost: 470", font_3, (255,255,255), 150, 680)
                draw_text("0", font_3, (255,255,255), 520, 680)
                screen.blit(money_im_sml,(390, 660))
                screen.blit(diamond_im_sml,(560, 660))

            if gun_which == 17:
                if guns_player_have[16] == 2 or guns_player_have[16] == 1:
                    pass
                elif money >= 440 and money_diamond >= 4:
                    if button_buy.draw(screen):
                        money -= 440
                        money_diamond -= 4
                        guns_player_have[guns_player_have.index(2)] = 1
                        guns_player_have[16] = 2
                else:
                    draw_text("You can't buy it!", font_3, (255,255,255), 670, 680)

                gun = pygame.image.load(f"project-VAK/img/gui/guns/17.png").convert_alpha()
                gun = pygame.transform.scale(gun, (int(gun.get_width() * 13), int(gun.get_height() * 13)))
                screen.blit(gun,(0, 250))
                draw_text("Comet Slice Dagger", font_3, (255,255,10), 450, 228)
                draw_text("Comet Slice Dagger", font_3, (255,255,255), 450, 230)
                draw_text("New", font_3, (255,255,10), 450, 280)
                draw_text("----------------------------------------------------------------------------------", font_4, (255,255,10), 0, 802)
                draw_text("- 20 charges", font_3, (255,255,255), 450, 350)
                draw_text("- 1 per shot", font_3, (255,255,255), 450, 400)
                draw_text("- 190 damage", font_3, (255,255,255), 450, 450)
                draw_text("- 1 Speed", font_3, (255,255,255), 450, 500)
                draw_text("Cost: 440", font_3, (255,255,255), 150, 680)
                draw_text("4", font_3, (255,255,255), 520, 680)
                screen.blit(money_im_sml,(390, 660))
                screen.blit(diamond_im_sml,(560, 660))

            if gun_which == 18:
                if guns_player_have[17] == 2 or guns_player_have[17] == 1:
                    pass
                elif money >= 560 and money_diamond >= 5:
                    if button_buy.draw(screen):
                        money -= 560
                        money_diamond -= 5
                        guns_player_have[guns_player_have.index(2)] = 1
                        guns_player_have[17] = 2
                else:
                    draw_text("You can't buy it!", font_3, (255,255,255), 670, 680)

                gun = pygame.image.load(f"project-VAK/img/gui/guns/18.png").convert_alpha()
                gun = pygame.transform.scale(gun, (int(gun.get_width() * 13), int(gun.get_height() * 13)))
                screen.blit(gun,(0, 250))
                draw_text("Ion Resonator Rifle", font_3, (255,255,10), 450, 228)
                draw_text("Ion Resonator Rifle", font_3, (255,255,255), 450, 230)
                draw_text("New", font_3, (255,255,10), 450, 280)
                draw_text("----------------------------------------------------------------------------------", font_4, (255,255,10), 0, 802)
                draw_text("- 30 charges", font_3, (255,255,255), 450, 350)
                draw_text("- burst shooting", font_3, (255,255,255), 450, 400)
                draw_text("- 185 damage", font_3, (255,255,255), 450, 450)
                draw_text("- 1.5 Speed", font_3, (255,255,255), 450, 500)
                draw_text("Cost: 560", font_3, (255,255,255), 150, 680)
                draw_text("5", font_3, (255,255,255), 520, 680)
                screen.blit(money_im_sml,(390, 660))
                screen.blit(diamond_im_sml,(560, 660))



            if gun_which == 19:
                if guns_player_have[18] == 2 or guns_player_have[18] == 1:
                    pass
                elif money >= 600 and money_diamond >= 3:
                    if button_buy.draw(screen):
                        money -= 600
                        money_diamond -= 3
                        guns_player_have[guns_player_have.index(2)] = 1
                        guns_player_have[18] = 2
                else:
                    draw_text("You can't buy it!", font_3, (255,255,255), 670, 680)

                gun = pygame.image.load(f"project-VAK/img/gui/guns/19.png").convert_alpha()
                gun = pygame.transform.scale(gun, (int(gun.get_width() * 13), int(gun.get_height() * 13)))
                screen.blit(gun,(50, 350))
                draw_text("Interstellar Hunter", font_3, (255,55,200), 450, 228)
                draw_text("Interstellar Hunter", font_3, (255,255,255), 450, 230)
                draw_text("Epic", font_3, (255,55,200), 450, 280)
                draw_text("----------------------------------------------------------------------------------", font_4, (255,55,200), 0, 802)
                draw_text("- 1 charges", font_3, (255,255,255), 450, 350)
                draw_text("- 1 per shoot", font_3, (255,255,255), 450, 400)
                draw_text("- 250 damage", font_3, (255,255,255), 450, 450)
                draw_text("- 1 Speed", font_3, (255,255,255), 450, 500)
                draw_text("Cost: 600", font_3, (255,255,255), 150, 680)
                draw_text("3", font_3, (255,255,255), 520, 680)
                screen.blit(money_im_sml,(390, 660))
                screen.blit(diamond_im_sml,(560, 660))


            if gun_which == 20:
                if guns_player_have[19] == 2 or guns_player_have[19] == 1:
                    pass
                elif money >= 750 and money_diamond >= 4:
                    if button_buy.draw(screen):
                        money -= 750
                        money_diamond -= 4
                        guns_player_have[guns_player_have.index(2)] = 1
                        guns_player_have[19] = 2
                else:
                    draw_text("You can't buy it!", font_3, (255,255,255), 670, 680)

                gun = pygame.image.load(f"project-VAK/img/gui/guns/20.png").convert_alpha()
                gun = pygame.transform.scale(gun, (int(gun.get_width() * 13), int(gun.get_height() * 13)))
                screen.blit(gun,(0, 250))
                draw_text("Gravity Particle Rifle", font_3, (255,55,200), 450, 228)
                draw_text("Gravity Particle Rifle", font_3, (255,255,255), 450, 230)
                draw_text("Epic", font_3, (255,55,200), 450, 280)
                draw_text("----------------------------------------------------------------------------------", font_4, (255,55,200), 0, 802)
                draw_text("- 10 charges", font_3, (255,255,255), 450, 350)
                draw_text("- burst shooting", font_3, (255,255,255), 450, 400)
                draw_text("- 120 damage", font_3, (255,255,255), 450, 450)
                draw_text("- 0.5 Speed", font_3, (255,255,255), 450, 500)
                draw_text("Cost: 750", font_3, (255,255,255), 150, 680)
                draw_text("4", font_3, (255,255,255), 520, 680)
                screen.blit(money_im_sml,(390, 660))
                screen.blit(diamond_im_sml,(560, 660))

            if gun_which == 21:
                if guns_player_have[20] == 2 or guns_player_have[20] == 1:
                    pass
                elif money >= 800 and money_diamond >= 6:
                    if button_buy.draw(screen):
                        money -= 800
                        money_diamond -= 6
                        guns_player_have[guns_player_have.index(2)] = 1
                        guns_player_have[20] = 2
                else:
                    draw_text("You can't buy it!", font_3, (255,255,255), 670, 680)

                gun = pygame.image.load(f"project-VAK/img/gui/guns/21.png").convert_alpha()
                gun = pygame.transform.scale(gun, (int(gun.get_width() * 13), int(gun.get_height() * 13)))
                screen.blit(gun,(0, 250))
                draw_text("Electr. Pulse Whip", font_3, (255,55,200), 450, 228)
                draw_text("Electr. Pulse Whip", font_3, (255,255,255), 450, 230)
                draw_text("Epic", font_3, (255,55,200), 450, 280)
                draw_text("----------------------------------------------------------------------------------", font_4, (255,55,200), 0, 802)
                draw_text("- 4 charges", font_3, (255,255,255), 450, 350)
                draw_text("- 2 per shoot", font_3, (255,255,255), 450, 400)
                draw_text("- 200 damage", font_3, (255,255,255), 450, 450)
                draw_text("- 1.3 Speed", font_3, (255,255,255), 450, 500)
                draw_text("Cost: 800", font_3, (255,255,255), 150, 680)
                draw_text("6", font_3, (255,255,255), 520, 680)
                screen.blit(money_im_sml,(390, 660))
                screen.blit(diamond_im_sml,(560, 660))

            if gun_which == 22:
                if guns_player_have[21] == 2 or guns_player_have[21] == 1:
                    pass
                elif money >= 840 and money_diamond >= 9:
                    if button_buy.draw(screen):
                        money -= 840
                        money_diamond -= 9
                        guns_player_have[guns_player_have.index(2)] = 1
                        guns_player_have[21] = 2
                else:
                    draw_text("You can't buy it!", font_3, (255,255,255), 670, 680)

                gun = pygame.image.load(f"project-VAK/img/gui/guns/22.png").convert_alpha()
                gun = pygame.transform.scale(gun, (int(gun.get_width() * 13), int(gun.get_height() * 13)))
                screen.blit(gun,(0, 250))
                draw_text("Orion's Odyssey", font_3, (255,55,200), 450, 228)
                draw_text("Orion's Odyssey", font_3, (255,255,255), 450, 230)
                draw_text("Epic", font_3, (255,55,200), 450, 280)
                draw_text("----------------------------------------------------------------------------------", font_4, (255,55,200), 0, 802)
                draw_text("- 10 charges", font_3, (255,255,255), 450, 350)
                draw_text("- burst shooting", font_3, (255,255,255), 450, 400)
                draw_text("- 200 damage", font_3, (255,255,255), 450, 450)
                draw_text("- 1 Speed", font_3, (255,255,255), 450, 500)
                draw_text("Cost: 840", font_3, (255,255,255), 150, 680)
                draw_text("9", font_3, (255,255,255), 520, 680)
                screen.blit(money_im_sml,(390, 660))
                screen.blit(diamond_im_sml,(560, 660))
            

            if gun_which == 23:
                if guns_player_have[22] == 2 or guns_player_have[22] == 1:
                    pass
                elif money >= 900 and money_diamond >= 3:
                    if button_buy.draw(screen):
                        money -= 900
                        money_diamond -= 3
                        guns_player_have[guns_player_have.index(2)] = 1
                        guns_player_have[22] = 2
                else:
                    draw_text("You can't buy it!", font_3, (255,255,255), 670, 680)

                gun = pygame.image.load(f"project-VAK/img/gui/guns/23.png").convert_alpha()
                gun = pygame.transform.scale(gun, (int(gun.get_width() * 13), int(gun.get_height() * 13)))
                screen.blit(gun,(50, 350))
                draw_text("Interstellar Hunter", font_3, (255,55,200), 450, 228)
                draw_text("Interstellar Hunter", font_3, (255,255,255), 450, 230)
                draw_text("Epic", font_3, (255,55,200), 450, 280)
                draw_text("----------------------------------------------------------------------------------", font_4, (255,55,200), 0, 802)
                draw_text("- 1 charges", font_3, (255,255,255), 450, 350)
                draw_text("- 1 per shoot", font_3, (255,255,255), 450, 400)
                draw_text("- 320 damage", font_3, (255,255,255), 450, 450)
                draw_text("- 1 Speed", font_3, (255,255,255), 450, 500)
                draw_text("Cost: 900", font_3, (255,255,255), 150, 680)
                draw_text("3", font_3, (255,255,255), 520, 680)
                screen.blit(money_im_sml,(390, 660))
                screen.blit(diamond_im_sml,(560, 660))

            if gun_which == 24:
                if guns_player_have[23] == 2 or guns_player_have[23] == 1:
                    pass
                elif money >= 700 and money_diamond >= 3:
                    if button_buy.draw(screen):
                        money -= 700
                        money_diamond -= 3
                        guns_player_have[guns_player_have.index(2)] = 1
                        guns_player_have[23] = 2
                else:
                    draw_text("You can't buy it!", font_3, (255,255,255), 670, 680)

                gun = pygame.image.load(f"project-VAK/img/gui/guns/24.png").convert_alpha()
                gun = pygame.transform.scale(gun, (int(gun.get_width() * 13), int(gun.get_height() * 13)))
                screen.blit(gun,(0, 250))
                draw_text("Each round, the weapon's stats", font_4, (255,0,90), 580, 88)
                draw_text("change to the stats shown below", font_4, (255,0,90), 573, 128)
                draw_text("Galactic Gauss Random Gun", font_3, (255,0,90), 450, 228)
                draw_text("Galactic Gauss Random Gun", font_3, (255,255,255), 450, 230)
                draw_text("unique", font_3, (255,0,90), 450, 280)
                draw_text("----------------------------------------------------------------------------------", font_4, (255,0,90), 0, 802)
                draw_text("- 20/30/40 charges", font_3, (255,255,255), 450, 350)
                draw_text("- 1/2/5 per shoot", font_3, (255,255,255), 450, 400)
                draw_text("- 100/200/400 damage", font_3, (255,255,255), 450, 450)
                draw_text("- 0.5/1/1.5 Speed", font_3, (255,255,255), 450, 500)
                draw_text("Cost: 700", font_3, (255,255,255), 150, 680)
                draw_text("3", font_3, (255,255,255), 520, 680)
                screen.blit(money_im_sml,(390, 660))
                screen.blit(diamond_im_sml,(560, 660))



            if gun_which == 25:
                if guns_player_have[24] == 2 or guns_player_have[24] == 1:
                    pass
                elif money >= 1200 and money_diamond >= 6:
                    if button_buy.draw(screen):
                        money -= 1200
                        money_diamond -= 6
                        guns_player_have[guns_player_have.index(2)] = 1
                        guns_player_have[24] = 2
                else:
                    draw_text("You can't buy it!", font_3, (255,255,255), 670, 680)

                gun = pygame.image.load(f"project-VAK/img/gui/guns/25.png").convert_alpha()
                gun = pygame.transform.scale(gun, (int(gun.get_width() * 13), int(gun.get_height() * 13)))
                screen.blit(gun,(0, 250))
                draw_text("Supernova Sights", font_3, (235, 186, 52), 450, 228)
                draw_text("Supernova Sights", font_3, (255,255,255), 450, 230)
                draw_text("Legendary", font_3, (235, 186, 52), 450, 280)
                draw_text("----------------------------------------------------------------------------------", font_4, (235,186,52), 0, 802)
                draw_text("- 40 charges", font_3, (255,255,255), 450, 350)
                draw_text("- 2 per shoot", font_3, (255,255,255), 450, 400)
                draw_text("- 280 damage", font_3, (255,255,255), 450, 450)
                draw_text("- 1.4 Speed", font_3, (255,255,255), 450, 500)
                draw_text("Cost: 1200", font_3, (255,255,255), 135, 680)
                draw_text("6", font_3, (255,255,255), 520, 680)
                screen.blit(money_im_sml,(415, 660))
                screen.blit(diamond_im_sml,(560, 660))

            if gun_which == 26:
                if guns_player_have[25] == 2 or guns_player_have[25] == 1:
                    pass
                elif money >= 1010 and money_diamond >= 4:
                    if button_buy.draw(screen):
                        money -= 1010
                        money_diamond -= 4
                        guns_player_have[guns_player_have.index(2)] = 1
                        guns_player_have[25] = 2
                else:
                    draw_text("You can't buy it!", font_3, (255,255,255), 670, 680)

                gun = pygame.image.load(f"project-VAK/img/gui/guns/26.png").convert_alpha()
                gun = pygame.transform.scale(gun, (int(gun.get_width() * 13), int(gun.get_height() * 13)))
                screen.blit(gun,(0, 250))
                draw_text("Comet Carver", font_3, (235, 186, 52), 450, 228)
                draw_text("Comet Carver", font_3, (255,255,255), 450, 230)
                draw_text("Legendary", font_3, (235, 186, 52), 450, 280)
                draw_text("----------------------------------------------------------------------------------", font_4, (235,186,52), 0, 802)
                draw_text("- 5 charges", font_3, (255,255,255), 450, 350)
                draw_text("- 1 per shoot", font_3, (255,255,255), 450, 400)
                draw_text("- 300 damage", font_3, (255,255,255), 450, 450)
                draw_text("- 3 Speed", font_3, (255,255,255), 450, 500)
                draw_text("Cost: 1010", font_3, (255,255,255), 135, 680)
                draw_text("4", font_3, (255,255,255), 520, 680)
                screen.blit(money_im_sml,(415, 660))
                screen.blit(diamond_im_sml,(560, 660))


            if gun_which == 27:
                if guns_player_have[26] == 2 or guns_player_have[26] == 1:
                    pass
                elif money >= 1400 and money_diamond >= 1:
                    if button_buy.draw(screen):
                        money -= 1400
                        money_diamond -= 1
                        guns_player_have[guns_player_have.index(2)] = 1
                        guns_player_have[26] = 2
                else:
                    draw_text("You can't buy it!", font_3, (255,255,255), 670, 680)

                gun = pygame.image.load(f"project-VAK/img/gui/guns/27.png").convert_alpha()
                gun = pygame.transform.scale(gun, (int(gun.get_width() * 13), int(gun.get_height() * 13)))
                screen.blit(gun,(0, 250))
                draw_text("Starry Siege", font_3, (235, 186, 52), 450, 228)
                draw_text("Starry Siege", font_3, (255,255,255), 450, 230)
                draw_text("Legendary", font_3, (235, 186, 52), 450, 280)
                draw_text("----------------------------------------------------------------------------------", font_4, (235,186,52), 0, 802)
                draw_text("- 10 charges", font_3, (255,255,255), 450, 350)
                draw_text("- 1 per shoot", font_3, (255,255,255), 450, 400)
                draw_text("- 320 damage", font_3, (255,255,255), 450, 450)
                draw_text("- 2 Speed", font_3, (255,255,255), 450, 500)
                draw_text("Cost: 1400", font_3, (255,255,255), 135, 680)
                draw_text("1", font_3, (255,255,255), 520, 680)
                screen.blit(money_im_sml,(415, 660))
                screen.blit(diamond_im_sml,(560, 660))


            if gun_which == 28:
                if guns_player_have[27] == 2 or guns_player_have[27] == 1:
                    pass
                elif money >= 1620 and money_diamond >= 4:
                    if button_buy.draw(screen):
                        money -= 1620
                        money_diamond -= 4
                        guns_player_have[guns_player_have.index(2)] = 1
                        guns_player_have[27] = 2
                else:
                    draw_text("You can't buy it!", font_3, (255,255,255), 670, 680)

                gun = pygame.image.load(f"project-VAK/img/gui/guns/28.png").convert_alpha()
                gun = pygame.transform.scale(gun, (int(gun.get_width() * 13), int(gun.get_height() * 13)))
                screen.blit(gun,(0, 250))
                draw_text("Interstellar Interceptor", font_3, (235, 186, 52), 450, 228)
                draw_text("Interstellar Interceptor", font_3, (255,255,255), 450, 230)
                draw_text("Legendary", font_3, (235, 186, 52), 450, 280)
                draw_text("----------------------------------------------------------------------------------", font_4, (235,186,52), 0, 802)
                draw_text("- 16 charges", font_3, (255,255,255), 450, 350)
                draw_text("- 4 per shoot", font_3, (255,255,255), 450, 400)
                draw_text("- 350 damage", font_3, (255,255,255), 450, 450)
                draw_text("- 1 Speed", font_3, (255,255,255), 450, 500)
                draw_text("Cost: 1620", font_3, (255,255,255), 135, 680)
                draw_text("4", font_3, (255,255,255), 520, 680)
                screen.blit(money_im_sml,(415, 660))
                screen.blit(diamond_im_sml,(560, 660))

            if gun_which == 29:
                if guns_player_have[28] == 2 or guns_player_have[28] == 1:
                    pass
                elif money >= 1720 and money_diamond >= 8:
                    if button_buy.draw(screen):
                        money -= 1720
                        money_diamond -= 8
                        guns_player_have[guns_player_have.index(2)] = 1
                        guns_player_have[28] = 2
                else:
                    draw_text("You can't buy it!", font_3, (255,255,255), 670, 680)

                gun = pygame.image.load(f"project-VAK/img/gui/guns/29.png").convert_alpha()
                gun = pygame.transform.scale(gun, (int(gun.get_width() * 13), int(gun.get_height() * 13)))
                screen.blit(gun,(0, 250))
                draw_text("Asteroid Artillery", font_3, (235, 186, 52), 450, 228)
                draw_text("Asteroid Artillery", font_3, (255,255,255), 450, 230)
                draw_text("Legendary", font_3, (235, 186, 52), 450, 280)
                draw_text("----------------------------------------------------------------------------------", font_4, (235,186,52), 0, 802)
                draw_text("- 20 charges", font_3, (255,255,255), 450, 350)
                draw_text("- burst shooting", font_3, (255,255,255), 450, 400)
                draw_text("- 300 damage", font_3, (255,255,255), 450, 450)
                draw_text("- 1.5 Speed", font_3, (255,255,255), 450, 500)
                draw_text("Cost: 1720", font_3, (255,255,255), 135, 680)
                draw_text("8", font_3, (255,255,255), 520, 680)
                screen.blit(money_im_sml,(415, 660))
                screen.blit(diamond_im_sml,(560, 660))

            if gun_which == 30:
                if guns_player_have[29] == 2 or guns_player_have[29] == 1:
                    pass
                elif money >= 2320 and money_diamond >= 5:
                    if button_buy.draw(screen):
                        money -= 2320
                        money_diamond -= 5
                        guns_player_have[guns_player_have.index(2)] = 1
                        guns_player_have[29] = 2
                else:
                    draw_text("You can't buy it!", font_3, (255,255,255), 670, 680)

                gun = pygame.image.load(f"project-VAK/img/gui/guns/30.png").convert_alpha()
                gun = pygame.transform.scale(gun, (int(gun.get_width() * 13), int(gun.get_height() * 13)))
                screen.blit(gun,(0, 250))
                draw_text("Nebula Nuke", font_3, (235, 186, 52), 450, 228)
                draw_text("Nebula Nuke", font_3, (255,255,255), 450, 230)
                draw_text("Legendary", font_3, (235, 186, 52), 450, 280)
                draw_text("----------------------------------------------------------------------------------", font_4, (235,186,52), 0, 802)
                draw_text("- 25 charges", font_3, (255,255,255), 450, 350)
                draw_text("- 5 per shoot", font_3, (255,255,255), 450, 400)
                draw_text("- 360 damage", font_3, (255,255,255), 450, 450)
                draw_text("- 1 Speed", font_3, (255,255,255), 450, 500)
                draw_text("Cost: 2320", font_3, (255,255,255), 135, 680)
                draw_text("5", font_3, (255,255,255), 520, 680)
                screen.blit(money_im_sml,(415, 660))
                screen.blit(diamond_im_sml,(560, 660))



            if gun_which == 31:
                if guns_player_have[30] == 2 or guns_player_have[30] == 1:
                    pass
                elif money >= 3640 and money_diamond >= 8:
                    if button_buy.draw(screen):
                        money -= 3640
                        money_diamond -= 8
                        guns_player_have[guns_player_have.index(2)] = 1
                        guns_player_have[30] = 2
                else:
                    draw_text("You can't buy it!", font_3, (255,255,255), 670, 680)

                gun = pygame.image.load(f"project-VAK/img/gui/guns/31.png").convert_alpha()
                gun = pygame.transform.scale(gun, (int(gun.get_width() * 13), int(gun.get_height() * 13)))
                screen.blit(gun,(0, 250))
                draw_text("Sagittarius Seeker", font_3, (52, 235, 222), 450, 228)
                draw_text("Sagittarius Seeker", font_3, (255,255,255), 450, 230)
                draw_text("absolute", font_3, (52, 235, 222), 450, 280)
                draw_text("----------------------------------------------------------------------------------", font_4, (52,235,222), 0, 802)
                draw_text("- 1 charges", font_3, (255,255,255), 450, 350)
                draw_text("- 1 per shoot", font_3, (255,255,255), 450, 400)
                draw_text("- 490 damage", font_3, (255,255,255), 450, 450)
                draw_text("- 0.8 Speed", font_3, (255,255,255), 450, 500)
                draw_text("Cost: 3640", font_3, (255,255,255), 135, 680)
                draw_text("8", font_3, (255,255,255), 520, 680)
                screen.blit(money_im_sml,(415, 660))
                screen.blit(diamond_im_sml,(560, 660))

            if gun_which == 32:
                if guns_player_have[31] == 2 or guns_player_have[31] == 1:
                    pass
                elif money >= 5220 and money_diamond >= 9:
                    if button_buy.draw(screen):
                        money -= 5220
                        money_diamond -= 9
                        guns_player_have[guns_player_have.index(2)] = 1
                        guns_player_have[31] = 2
                else:
                    draw_text("You can't buy it!", font_3, (255,255,255), 670, 680)

                gun = pygame.image.load(f"project-VAK/img/gui/guns/32.png").convert_alpha()
                gun = pygame.transform.scale(gun, (int(gun.get_width() * 13), int(gun.get_height() * 13)))
                screen.blit(gun,(0, 250))
                draw_text("Polaris Missiles", font_3, (52, 235, 222), 450, 228)
                draw_text("Polaris Missiles", font_3, (255,255,255), 450, 230)
                draw_text("absolute", font_3, (52, 235, 222), 450, 280)
                draw_text("----------------------------------------------------------------------------------", font_4, (52,235,222), 0, 802)
                draw_text("- 45 charges", font_3, (255,255,255), 450, 350)
                draw_text("- 1 per shoot", font_3, (255,255,255), 450, 400)
                draw_text("- 430 damage", font_3, (255,255,255), 450, 450)
                draw_text("- 1 Speed", font_3, (255,255,255), 450, 500)
                draw_text("Cost: 5220", font_3, (255,255,255), 135, 680)
                draw_text("9", font_3, (255,255,255), 520, 680)
                screen.blit(money_im_sml,(415, 660))
                screen.blit(diamond_im_sml,(560, 660))

            if gun_which == 33:
                if guns_player_have[32] == 2 or guns_player_have[32] == 1:
                    pass
                elif money >= 5760 and money_diamond >= 9:
                    if button_buy.draw(screen):
                        money -= 5760
                        money_diamond -= 9
                        guns_player_have[guns_player_have.index(2)] = 1
                        guns_player_have[32] = 2
                else:
                    draw_text("You can't buy it!", font_3, (255,255,255), 670, 680)

                gun = pygame.image.load(f"project-VAK/img/gui/guns/33.png").convert_alpha()
                gun = pygame.transform.scale(gun, (int(gun.get_width() * 13), int(gun.get_height() * 13)))
                screen.blit(gun,(0, 250))
                draw_text("Photon Blaster", font_3, (52, 235, 222), 450, 228)
                draw_text("Photon Blaster", font_3, (255,255,255), 450, 230)
                draw_text("absolute", font_3, (52, 235, 222), 450, 280)
                draw_text("----------------------------------------------------------------------------------", font_4, (52,235,222), 0, 802)
                draw_text("- 10 charges", font_3, (255,255,255), 450, 350)
                draw_text("- 1 per shoot", font_3, (255,255,255), 450, 400)
                draw_text("- 480 damage", font_3, (255,255,255), 450, 450)
                draw_text("- 1 Speed", font_3, (255,255,255), 450, 500)
                draw_text("Cost: 5760", font_3, (255,255,255), 135, 680)
                draw_text("9", font_3, (255,255,255), 520, 680)
                screen.blit(money_im_sml,(415, 660))
                screen.blit(diamond_im_sml,(560, 660))


            if gun_which == 34:
                if guns_player_have[33] == 2 or guns_player_have[33] == 1:
                    pass
                elif money >= 5620 and money_diamond >= 9:
                    if button_buy.draw(screen):
                        money -= 5620
                        money_diamond -= 9
                        guns_player_have[guns_player_have.index(2)] = 1
                        guns_player_have[33] = 2
                else:
                    draw_text("You can't buy it!", font_3, (255,255,255), 670, 680)

                gun = pygame.image.load(f"project-VAK/img/gui/guns/34.png").convert_alpha()
                gun = pygame.transform.scale(gun, (int(gun.get_width() * 13), int(gun.get_height() * 13)))
                screen.blit(gun,(0, 250))
                draw_text("Ion Storm Rifle", font_3, (52, 235, 222), 450, 228)
                draw_text("Ion Storm Rifle", font_3, (255,255,255), 450, 230)
                draw_text("absolute", font_3, (52, 235, 222), 450, 280)
                draw_text("----------------------------------------------------------------------------------", font_4, (52,235,222), 0, 802)
                draw_text("- 40 charges", font_3, (255,255,255), 450, 350)
                draw_text("- burst shooting", font_3, (255,255,255), 450, 400)
                draw_text("- 400 damage", font_3, (255,255,255), 450, 450)
                draw_text("- 1 Speed", font_3, (255,255,255), 450, 500)
                draw_text("Cost: 5620", font_3, (255,255,255), 135, 680)
                draw_text("9", font_3, (255,255,255), 520, 680)
                screen.blit(money_im_sml,(415, 660))
                screen.blit(diamond_im_sml,(560, 660))


            if gun_which == 35:
                if guns_player_have[34] == 2 or guns_player_have[34] == 1:
                    pass
                elif money >= 9000 and money_diamond >= 9:
                    if button_buy.draw(screen):
                        money -= 9000
                        money_diamond -= 9
                        guns_player_have[guns_player_have.index(2)] = 1
                        guns_player_have[34] = 2
                else:
                    draw_text("You can't buy it!", font_3, (255,255,255), 670, 680)

                gun = pygame.image.load(f"project-VAK/img/gui/guns/35.png").convert_alpha()
                gun = pygame.transform.scale(gun, (int(gun.get_width() * 13), int(gun.get_height() * 13)))
                screen.blit(gun,(0, 250))
                draw_text("Comet Carnage", font_3, (52, 235, 222), 450, 228)
                draw_text("Comet Carnage", font_3, (255,255,255), 450, 230)
                draw_text("absolute", font_3, (52, 235, 222), 450, 280)
                draw_text("----------------------------------------------------------------------------------", font_4, (52,235,222), 0, 802)
                draw_text("- 1 charges", font_3, (255,255,255), 450, 350)
                draw_text("- 1 per shoot", font_3, (255,255,255), 450, 400)
                draw_text("- 700 damage", font_3, (255,255,255), 450, 450)
                draw_text("- 0.4 Speed", font_3, (255,255,255), 450, 500)
                draw_text("Cost: 9000", font_3, (255,255,255), 135, 680)
                draw_text("9", font_3, (255,255,255), 520, 680)
                screen.blit(money_im_sml,(415, 660))
                screen.blit(diamond_im_sml,(560, 660))

        if back_button.draw(screen):
            start_intro = True
            intro_fade.fade_counter = 0
            shop_fade.fade_counter = 0
            flag_shop = 1
            current_window_selected = "home"
            city_noise.play(-1)

        if start_intro == True:
            if shop_fade.fade():
                start_intro = False
                shop_fade.fade_counter = 0 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False


    if current_window_selected == "food":

        is_moving_left = False
        is_moving_right = False
        back_shop = pygame.image.load("project-VAK/img/gui/shops_back/food.png").convert_alpha()
        back_shop = pygame.transform.scale(back_shop, (int(back_shop.get_width() * 3), int(back_shop.get_height() * 3)))
        screen.blit(back_shop, (650,-25))
        screen.blit(back_shop, (0,-25))
        table_im = pygame.image.load("project-VAK/img/gui/shops_back/food_table.png").convert_alpha()
        table_im = pygame.transform.scale(table_im, (int(table_im.get_width() * 8), int(table_im.get_height() * 8)))
        back_im = pygame.image.load("project-VAK/img/gui/button_back_for_food.png").convert_alpha()
        back_im_s = pygame.image.load("project-VAK/img/gui/button_back_for_food_select.png").convert_alpha()
        back_button = Button(1430, 20, back_im, 5, back_im_s)

        money_im_sml = pygame.image.load(f"project-VAK/img/gui/money/money_sml.png").convert_alpha()
        money_im_sml = pygame.transform.scale(money_im_sml, (int(money_im_sml.get_width() * 5), int(money_im_sml.get_height() * 5)))

        diamond_im_sml = pygame.image.load(f"project-VAK/img/gui/money/diamond_sml.png").convert_alpha()
        diamond_im_sml = pygame.transform.scale(diamond_im_sml, (int(diamond_im_sml.get_width() * 5), int(diamond_im_sml.get_height() * 5)))   

        if back_button.draw(screen):
            start_intro = True
            intro_fade.fade_counter = 0
            shop_fade.fade_counter = 0
            flag_shop = 1
            current_window_selected = "home"
            city_noise.play(-1)
            
        screen.blit(table_im, (-20,-5))
        Alla.update()
        Alla.draw(screen, 1090, 110)

        diamond_im = pygame.image.load(f"project-VAK/img/gui/money/diamond.png").convert_alpha()
        diamond_im = pygame.transform.scale(diamond_im, (int(diamond_im.get_width() * 3), int(diamond_im.get_height() * 3)))
        screen.blit(diamond_im,(400, 90))

        money_im = pygame.image.load(f"project-VAK/img/gui/money/money.png").convert_alpha()
        money_im = pygame.transform.scale(money_im, (int(money_im.get_width() * 5), int(money_im.get_height() * 5)))
        screen.blit(money_im,(40, 50))

        draw_text(f"{money}", font_3, (255,255,255), 220, 130)
        draw_text(f"{money_diamond}", font_3, (255,255,255), 520, 130)

        draw_text(f"small fruit", font_3, (255,255,255), 70, 250)
        draw_text(f"restores", font_3, (255,255,255), 85, 560)
        draw_text("12 hp", font_3, (255,255,255), 140, 610)
        draw_text("COST: 56", font_3, (255,255,255), 60, 670)
        screen.blit(money_im_sml, (270, 650))
        draw_text(f"fresh fruit", font_3, (255,255,255), 430, 250)
        draw_text(f"restores", font_3, (255,255,255), 435, 560)
        draw_text("60 hp", font_3, (255,255,255), 490, 610)
        draw_text("COST: 355", font_3, (255,255,255), 430, 670)
        screen.blit(money_im_sml, (670, 650))
        draw_text(f"delicacy", font_3, (255,255,255), 805, 250)
        draw_text(f"restores", font_3, (255,255,255), 775, 560)
        draw_text("95 hp", font_3, (255,255,255), 830, 610)
        draw_text("COST: 5", font_3, (255,255,255), 810, 670)
        screen.blit(diamond_im_sml, (995, 650))

        buy_im = pygame.image.load(f"project-VAK/img/gui/button_buy_for_food.png").convert_alpha()
        buy_im = pygame.transform.scale(buy_im, (int(buy_im.get_width() * 3), int(buy_im.get_height() * 3)))
        buy_im_select = pygame.image.load(f"project-VAK/img/gui/button_buy_for_food_select.png").convert_alpha()
        buy_im_select = pygame.transform.scale(buy_im_select, (int(buy_im_select.get_width() * 3), int(buy_im_select.get_height() * 3)))
        buy_im_press = pygame.image.load(f"project-VAK/img/gui/button_buy_for_food_press.png").convert_alpha()
        buy_im_press = pygame.transform.scale(buy_im_press, (int(buy_im_press.get_width() * 3), int(buy_im_press.get_height() * 3)))
        buy_b_for_small = Button(90, 720, buy_im, 2, buy_im_select, buy_im_press)
        buy_b_for_good = Button(450, 720, buy_im, 2, buy_im_select, buy_im_press)
        buy_b_for_best = Button(790, 720, buy_im, 2, buy_im_select, buy_im_press)
        normal_food = pygame.image.load(f"project-VAK/img/gui/food/normal_food.png").convert_alpha()
        normal_food = pygame.transform.scale(normal_food, (int(normal_food.get_width() * 5), int(normal_food.get_height() * 5)))
        screen.blit(normal_food, (657, 55))
        draw_text(f"{small_fruit}", font_3, (255,255,255), 727, 48)
        good_food = pygame.image.load(f"project-VAK/img/gui/food/good_food.png").convert_alpha()
        good_food = pygame.transform.scale(good_food, (int(good_food.get_width() * 5), int(good_food.get_height() * 5)))
        screen.blit(good_food, (784, 61))
        draw_text(f"{fresh_fruit}", font_3, (255,255,255), 864, 48)
        best_food = pygame.image.load(f"project-VAK/img/gui/food/best_food.png").convert_alpha()
        best_food = pygame.transform.scale(best_food, (int(best_food.get_width() * 5), int(best_food.get_height() * 5)))
        screen.blit(best_food, (910, 61))
        draw_text(f"{big_fruit}", font_3, (255,255,255), 990, 48)
        if money >= 56:
            buy_b_for_small.draw(screen)
        if money >= 355:
            buy_b_for_good.draw(screen)
        if money_diamond >= 5:
            buy_b_for_best.draw(screen)
        
        if buy_b_for_small.clicked is True:
            if make_action < 1:
                make_action += 1
                print(make_action)
                money -= 56
                small_fruit += 1
        elif buy_b_for_good.clicked is True:
            if make_action < 1:
                make_action += 1
                money -= 355
                fresh_fruit += 1
        elif buy_b_for_best.clicked is True:
            if make_action < 1:
                make_action += 1
                money_diamond -= 5
                big_fruit += 1
        else:
            make_action = 0
            
        if start_intro == True:
            if shop_fade.fade():
                start_intro = False
                shop_fade.fade_counter = 0 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False

    if current_window_selected == "options":
        color_menu()
        back_im = pygame.image.load("project-VAK/img/gui/button_back.png").convert_alpha()
        back_im_s = pygame.image.load("project-VAK/img/gui/button_back_select.png").convert_alpha()
        back_button = Button(20, 20, back_im, 7, back_im_s)
        mouse_pos = pygame.mouse.get_pos()
        button_left_im = pygame.image.load("project-VAK/img/gui/button_left.png").convert_alpha()
        button_left_im_press = pygame.image.load("project-VAK/img/gui/button_left_press.png").convert_alpha()
        button_right_im = pygame.image.load("project-VAK/img/gui/button_right.png").convert_alpha()
        button_right_im_press = pygame.image.load("project-VAK/img/gui/button_right_press.png").convert_alpha()
        button_left = Button(SCREEN_WIDTH // 30, 260, button_left_im, 7, button_left_im, button_left_im_press)
        button_right = Button(SCREEN_WIDTH // 30 + 450, 260, button_right_im, 7, button_right_im, button_right_im_press)
        button_left1 = Button(SCREEN_WIDTH // 30, 600, button_left_im, 7, button_left_im, button_left_im_press)
        button_right1 = Button(SCREEN_WIDTH // 30 + 450, 600, button_right_im, 7, button_right_im, button_right_im_press)
        draw_text("music volume", font_3, (255,255,255), SCREEN_WIDTH // 30 + 10, 380)
        draw_text("sound volume", font_3, (255,255,255), SCREEN_WIDTH // 30 + 10, 720)
        button_left.draw(screen)
        button_left1.draw(screen)
        button_right.draw(screen)
        button_right1.draw(screen)
        if button_left.clicked == True:
            if make_action < 1 and bar_of_volume_game_music != 0:
                bar_of_volume_game_music -= 1
                volume_game_music -= 0.2
                pygame.mixer.music.set_volume(volume_game_music)
                make_action += 1
        elif button_right.clicked == True:
            if make_action < 1 and bar_of_volume_game_music != 5:
                bar_of_volume_game_music += 1
                volume_game_music += 0.2
                pygame.mixer.music.set_volume(volume_game_music)
                make_action += 1
        elif button_left1.clicked == True:
            if make_action < 1 and bar_of_volume_game_sounds != 0:
                bar_of_volume_game_sounds -= 1 
                volume_game_sound -= 0.2
                for sound in sounds_group:
                    sound.set_volume(volume_game_sound)
                make_action += 1
        elif button_right1.clicked == True:
            if make_action < 1 and bar_of_volume_game_sounds != 5:
                bar_of_volume_game_sounds += 1 
                volume_game_sound += 0.2
                for sound in sounds_group:
                    sound.set_volume(volume_game_sound)
                make_action += 1
        else:
            make_action = 0

        bar_volume = pygame.image.load(f"project-VAK/img/gui/bar_op_{bar_of_volume_game_music}.png").convert_alpha()
        bar_volume = pygame.transform.scale(bar_volume, (int(bar_volume.get_width() * 7), int(bar_volume.get_height() * 7)))

        bar_volume_sound = pygame.image.load(f"project-VAK/img/gui/bar_op_{bar_of_volume_game_sounds}.png").convert_alpha()
        bar_volume_sound = pygame.transform.scale(bar_volume_sound, (int(bar_volume_sound.get_width() * 7), int(bar_volume_sound.get_height() * 7)))
        
        screen.blit(bar_volume, (SCREEN_WIDTH // 30 + 120, 260))
        screen.blit(bar_volume_sound, (SCREEN_WIDTH // 30 + 120, 600))

        wasd = pygame.image.load("project-VAK/img/gui/options/movements.png").convert_alpha()
        wasd = pygame.transform.scale(wasd, (int(wasd.get_width() * 5), int(wasd.get_height() * 5)))
        screen.blit(wasd, (680, 40))
        draw_text("Move forward, move back,", font_4, (255,255,255), 950, 80)
        draw_text("move left, move right", font_4, (255,255,255), 980, 120)

        numb = pygame.image.load("project-VAK/img/gui/options/eat-food.png").convert_alpha()
        numb = pygame.transform.scale(numb, (int(numb.get_width() * 5), int(numb.get_height() * 5)))
        screen.blit(numb, (680, 300))
        draw_text("eat normal food, eat good food,", font_4, (255,255,255), 950, 290)
        draw_text("eat high quality food", font_4, (255,255,255), 1020, 340)

        gre = pygame.image.load("project-VAK/img/gui/options/throwing grenade.png").convert_alpha()
        gre = pygame.transform.scale(gre, (int(gre.get_width() * 5), int(gre.get_height() * 5)))
        screen.blit(gre, (720, 450))
        draw_text("throw a grenade", font_4, (255,255,255), 630, 540)
    
        rel = pygame.image.load("project-VAK/img/gui/options/reloading.png").convert_alpha()
        rel = pygame.transform.scale(rel, (int(rel.get_width() * 5), int(rel.get_height() * 5)))
        screen.blit(rel, (1020, 450))
        draw_text("reloading", font_4, (255,255,255), 980, 540)


        light_b = pygame.image.load("project-VAK/img/gui/options/make_light.png").convert_alpha()
        light_b = pygame.transform.scale(light_b, (int(light_b.get_width() * 5), int(light_b.get_height() * 5)))
        screen.blit(light_b, (1320, 450))
        draw_text("throw an electric", font_4, (255,255,255), 1200, 540)
        draw_text("grenade", font_4, (255,255,255), 1300, 590)

        stop_b = pygame.image.load("project-VAK/img/gui/options/exit_game.png").convert_alpha()
        stop_b = pygame.transform.scale(stop_b, (int(stop_b.get_width() * 5), int(stop_b.get_height() * 5)))
        screen.blit(stop_b, (940, 625))
        draw_text("exit game", font_4, (255,255,255), 1080, 650)
        pause_b = pygame.image.load("project-VAK/img/gui/options/stop_game.png").convert_alpha()
        pause_b = pygame.transform.scale(pause_b, (int(pause_b.get_width() * 5), int(pause_b.get_height() * 5)))
        screen.blit(pause_b, (650, 620))
        draw_text("pause", font_4, (255,255,255), 830, 650)
        shoot = pygame.image.load("project-VAK/img/gui/options/shoot.png").convert_alpha()
        shoot = pygame.transform.scale(shoot,  (int(shoot.get_width() * 5), int(shoot.get_height() * 5)))  
        screen.blit(shoot, (640, 750))
        draw_text("shoot / interact", font_4, (255,255,255), 1050, 770)
        if back_button.draw(screen):
            current_window_selected = "main_menu"
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False

    if current_window_selected == "play on planet":
        clock.tick(FPS)
        health_bars = {75: "health_bar4.png", 40: "health_bar3.png", 10: "health_bar2.png", 0: "health_bar1.png",
                    -1: "health_bar0.png"}
        ammo_bars = {15: "ammo5.png", 10: "ammo4.png", 5: "ammo3.png", 1: "ammo2.png", 0: "ammo1.png", -1: "ammo0.png"}

        draw_background()
        draw_text(f'AMMO', font, (0, 0, 0), 1023, 15)
        draw_status_bar(player.ammo, ammo_bars, 940, 25)
        draw_text(f'HEALTH', font, (0, 0, 0), 1370, 15)
        draw_status_bar(player.health, health_bars, 1170, 23)

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
            if is_moving_left or is_moving_right or is_moving_down or is_moving_up:
                if (is_moving_left and is_moving_right) and not is_moving_up and not is_moving_down:
                    player.update_action(0)
                elif (is_moving_down and is_moving_up) and not is_moving_right and not is_moving_left:
                    player.update_action(0)
                else:
                    player.update_action(1)
            else:
                player.update_action(0)
            player.move(is_moving_left, is_moving_right, is_moving_down, is_moving_up)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    is_moving_left = True
                if event.key == pygame.K_d:
                    is_moving_right = True
                if event.key == pygame.K_w:
                    is_moving_up = True
                if event.key == pygame.K_s:
                    is_moving_down = True
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
                if event.key == pygame.K_w:
                    is_moving_up = False
                if event.key == pygame.K_s:
                    is_moving_down = False
    
    if current_window_selected == "credits":
        color_menu()
        brown_cat.update()
        white_cat.update()
        draw_text("This game was made by", font_3, (255,55,255), SCREEN_WIDTH // 3 - 25, 298)
        draw_text("This game was made by", font_3, (255,255,255), SCREEN_WIDTH // 3 - 25, 300)
        draw_text("Emil", font_3, (255,55,255), SCREEN_WIDTH // 3 + 120, 508)
        draw_text("Emil", font_3, (255,255,255), SCREEN_WIDTH // 3 + 120, 510)
        draw_text("Sanya", font_3, (255,55,255), SCREEN_WIDTH // 3 + 300, 508)
        draw_text("Sanya", font_3, (255,255,255), SCREEN_WIDTH // 3 + 300, 510)
        white_cat.draw(screen, 830, 400)
        brown_cat.draw(screen, 630, 400)
        back_im = pygame.image.load("project-VAK/img/gui/button_back.png").convert_alpha()
        back_im_s = pygame.image.load("project-VAK/img/gui/button_back_select.png").convert_alpha()

        back_button = Button(20, 20, back_im, 7, back_im_s)
        mouse_pos = pygame.mouse.get_pos()
        if mouse_pos[0] >= 600 and mouse_pos[0] <= 740:
            if mouse_pos[1] >= 408 and mouse_pos[1] <= 550:
                draw_text("worked on character design and setting,", font_3, (255,255,255), 250 , 610)
                draw_text("wrote sound work, basic character", font_3, (255,255,255), 300 , 680)
                draw_text("mechanics and character leveling.", font_3, (255,255,255), 320 , 750)
        if mouse_pos[0] >= 820 and mouse_pos[0] <= 970:
            if mouse_pos[1] >= 408 and mouse_pos[1] <= 550:
                draw_text("wrote the code for shooting mechanics,", font_3, (255,255,255), 250 , 610)
                draw_text("mobs and bosses. Made the code more", font_3, (255,255,255), 280 , 680)
                draw_text("readable and clean.", font_3, (255,255,255), 520 , 750)
        if back_button.draw(screen):
            current_window_selected = "main_menu"
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False
    pygame.display.update()

pygame.quit()
