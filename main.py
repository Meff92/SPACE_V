import pygame
import os
import random
import math

pygame.init()


# Screen
info = pygame.display.Info()
SCREEN_WIDTH = 1536
SCREEN_HEIGHT = 864



screen = pygame.display.set_mode((1536, 864),pygame.FULLSCREEN)
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
is_using_grenade_el = False
is_grenade_thrown_el = False

# Images
bullet_image = pygame.image.load('project-VAK/img/shoot/player-shoot-hit1.png').convert_alpha()
grenade_image = pygame.image.load('project-VAK/img/shoot/grenade.png').convert_alpha()
grenade_image = pygame.transform.scale(grenade_image, (int(grenade_image.get_width() * 4), int(grenade_image.get_height() * 4)))
grenade_image_el = pygame.image.load('project-VAK/img/shoot/grenade_el.png').convert_alpha()
grenade_image_el = pygame.transform.scale(grenade_image_el, (int(grenade_image_el.get_width() * 4), int(grenade_image_el.get_height() * 4)))

grenade_image_for_gui = pygame.transform.scale(grenade_image, (int(grenade_image.get_width() * 4), int(grenade_image.get_height() * 4)))
el_grenade_image = pygame.image.load('project-VAK/img/shoot/grenade_el.png').convert_alpha()
el_grenade_image = pygame.transform.scale(el_grenade_image, (int(el_grenade_image.get_width() * 4), int(el_grenade_image.get_height() * 4)))
el_grenade_image_for_gui = pygame.transform.scale(el_grenade_image, (int(el_grenade_image.get_width() * 3), int(el_grenade_image.get_height() * 3)))
# Colors
BACKGROUND_COLOR = (144, 201, 120)
RED_COLOR = (255, 0, 0)

# Fonts
font = pygame.font.Font("project-VAK/img/gui/ThaleahFat.ttf", 48)
font_2 = pygame.font.Font("project-VAK/img/gui/Stacked pixel.ttf", 320)
font_3 = pygame.font.Font("project-VAK/img/gui/Stacked pixel.ttf", 58)
font_4 =  pygame.font.Font("project-VAK/img/gui/Stacked pixel.ttf", 38)
font_5 =  pygame.font.Font("project-VAK/img/gui/Stacked pixel.ttf", 28)
def draw_text(text, font, text_col, x, y):
    text_image = font.render(text, True, text_col)
    screen.blit(text_image, (x, y))


def draw_background():
    screen.fill((23,255,255))


def get_angle_to_cursor(player_rect):
    mouseX, mouseY = pygame.mouse.get_pos()
    delta_x, delta_y = mouseX - player_rect.centerx, mouseY - player_rect.centery
    angle_rad = math.atan2(delta_y, delta_x)

    # Переводим радианы в градусы
    angle_deg = math.degrees(angle_rad)

    # Отрицательные углы преобразуем в положительные
    if angle_deg < 0:
        angle_deg += 360

    return angle_deg

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, scale, speed, ammo, grenades, grenades_elect=3):
        pygame.sprite.Sprite.__init__(self)
        self.is_alive = True
        self.speed = speed
        self.ammo = ammo
        self.start_ammo = ammo
        self.shoot_cooldown = 0
        self.direction = 1
        self.grenades = grenades
        self.grenades_elect = grenades_elect
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
        self.speed = 12
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
    def __init__(self, x, y, direction, which=1):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 35
        self.v_vel = -11
        self.speed = 11
        if which == 1:
            self.image = grenade_image
        if which == 2:
            self.image = grenade_image_el
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
        self.which = which
    def update(self):
        if self.which == 1:
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
                expl_sfx = pygame.mixer.Sound("project-VAK/img/sfx/game/explosion_big_01.wav")
                expl_sfx.set_volume(volume_game_sound)
                expl_sfx.play()
                self.kill()
                explosion = Explosion(self.rect.x, self.rect.y, 10)
                explosion_group.add(explosion)

                if abs(self.rect.centerx - player.rect.centerx) < 120 and abs(
                        self.rect.centery - player.rect.centery) < 120:
                    player.health -= 500
                for enemy in enemies_group:
                    if abs(self.rect.centerx - enemy.rect.centerx) < 120 and abs(
                            self.rect.centery - enemy.rect.centery) < 120:
                        enemy.health -= 500
        if self.which == 2:
                self.v_vel += 0.8
                dx = self.direction * self.speed
                dy = self.v_vel

                if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                    self.direction *= -1
                    dx = self.direction * self.speed

                self.rect.x += dx
                self.rect.y += dy

                self.timer -= 1.15
                print(self.timer)

                    
                if self.timer <= 0:
                    expl_sfx = pygame.mixer.Sound("project-VAK/img/sfx/game/EL-blow_35.wav")
                    expl_sfx.set_volume(volume_game_sound)
                    expl_sfx.play()
                    explosion = Explosion(self.rect.x, self.rect.y, 14, "project-VAK/img/exp/exp2/Explosion 2 SpriteSheet_")
                    explosion_group.add(explosion)
                    self.kill()
                    if abs(self.rect.centerx - player.rect.centerx) < 180 and abs(
                            self.rect.centery - player.rect.centery) < 180:
                        player.health -= 1200
                    for enemy in enemies_group:
                        if abs(self.rect.centerx - enemy.rect.centerx) < 180 and abs(
                                self.rect.centery - enemy.rect.centery) < 180:
                            enemy.health -= 1200

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale, deff_or_not = True, num_of_i = 18):
        pygame.sprite.Sprite.__init__(self)
        self.images = list()
        if deff_or_not is True:
            for i in range(1, 17):
                img = pygame.image.load(f'project-VAK/img/exp/Explosion SpriteSheet_{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                self.images.append(img)
        else:
            for i in range(7, num_of_i + 1):
                img = pygame.image.load(f'{deff_or_not}{i}.png').convert_alpha()
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
    def __init__(self, update, num_of_i, path_to, need_to_scale_by_screen, scale_w=0, scale_h=0):
        pygame.sprite.Sprite.__init__(self)
        self.images = list()
        self.num_of_i = num_of_i
        for i in range(self.num_of_i):
            img_sd = pygame.image.load(f'project-VAK/img/{path_to}{i+1}.png').convert_alpha()
            if need_to_scale_by_screen:
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

player = Player(780, 460, 3, 5, 20, 5)
player_for_menu = Player(500, 760, 2.7, 5, 20, 5)
enemy = Player(400, 600, 3, 5, 20, 0)
enemy1 = Player(300, 600, 3, 5, 20, 0)
enemy2 = Player(200, 600, 3, 5, 20, 0)
enemy3 = Player(700, 600, 3, 5, 20, 0)
enemy4 = Player(800, 600, 3, 5, 20, 0)
enemy5 = Player(900, 600, 3, 5, 20, 0)
enemies_group.add(enemy)
enemies_group.add(enemy1)
enemies_group.add(enemy3)
enemies_group.add(enemy4)
enemies_group.add(enemy5)
run = True

stars = Animate_smt(random.randint(250, 280), 4, "gui/bg_men/menu_", True, 0.5, 0.5)
stars1 = Animate_smt(random.randint(250, 280), 4, "gui/bg_men/menu_", True, 0.5, 0.5)
stars2 = Animate_smt(random.randint(250, 280), 4, "gui/bg_men/menu_", True, 0.5, 0.5)
stars3 = Animate_smt(random.randint(250, 280), 4, "gui/bg_men/menu_", True, 0.5, 0.5)
white_cat = Animate_smt(100, 15, "gui/white_cat/white_grey", False, 5, 5)
brown_cat = Animate_smt(50, 5, "gui/brown_cat/brown", False, 5, 5)

galaxy_1_for_ui = Animate_smt(50, 8, "gui/planets/first/galaxy/", False, 1.5, 1.5)
galaxy_2_for_ui = Animate_smt(50, 8, "gui/planets/second/galaxy/", False, 1.5, 1.5)
galaxy_3_for_ui = Animate_smt(50, 8, "gui/planets/third/galaxy/", False, 1.5, 1.5)
galaxy_4_for_ui = Animate_smt(50, 8, "gui/planets/four/galaxy/", False, 1.5, 1.5)
galaxy_5_for_ui = Animate_smt(50, 8, "gui/planets/five/galaxy/", False, 1.5, 1.5)
galaxy_6_for_ui = Animate_smt(50, 8, "gui/planets/six/galaxy/", False, 1.5, 1.5)






galaxy_1 = Animate_smt(30, 8, "gui/planets/first/galaxy/", False, 5, 5)
galaxy_2 = Animate_smt(30, 8, "gui/planets/second/galaxy/", False, 5, 5)
galaxy_3 = Animate_smt(30, 8, "gui/planets/third/galaxy/", False, 5, 5)
galaxy_4 = Animate_smt(30, 8, "gui/planets/four/galaxy/", False, 5, 5)
galaxy_5 = Animate_smt(30, 8, "gui/planets/five/galaxy/", False, 5, 5)
galaxy_6 = Animate_smt(30, 8, "gui/planets/six/galaxy/", False, 5, 5)
galaxy_uk = Animate_smt(30, 8, "gui/planets/unk/1135258434_", False, 5, 5)

Nova_prime1 = Animate_smt(60, 8, "gui/planets/first/Nova prime1/4095930381_", False, 6, 6)
Astoria2 = Animate_smt(60, 8, "gui/planets/first/Astoria2/889057430_", False, 6, 6)
Olympus3 = Animate_smt(60, 8, "gui/planets/first/Olympus3/2921353398_", False, 6, 6)
Nebulous4 = Animate_smt(60, 8, "gui/planets/first/Nebulous4/2096131777_", False, 6, 6)
Infinity5 = Animate_smt(60, 8, "gui/planets/first/Infinity5/1758289008_", False, 6, 6)

Genesis1 = Animate_smt(60, 8, "gui/planets/second/Genesis1/1758289008_", False, 6, 6)
Equinox2 = Animate_smt(60, 8, "gui/planets/second/Equinox2/3956320167_", False, 6, 6)
Orpheus3 = Animate_smt(60, 8, "gui/planets/second/Orpheus3/4095930381_", False, 6, 6)
Utopia4 = Animate_smt(60, 8, "gui/planets/second/Utopia4/2292993999_", False, 6, 6)
Nexus5 = Animate_smt(60, 8, "gui/planets/second/Nexus5/3180152060_", False, 6, 6)

Andromeda1 = Animate_smt(60, 8, "gui/planets/third/Andromeda1/56720320_", False, 6, 6)
Epoch2 = Animate_smt(60, 8, "gui/planets/third/Epoch2/42803208554_", False, 6, 6)
Arcadia3 = Animate_smt(60, 8, "gui/planets/third/Arcadia3/1280320855_", False, 6, 6)
Apollo4 = Animate_smt(60, 8, "gui/planets/third/Apollo4/3400360043_", False, 6, 6)
Polaris5 = Animate_smt(60, 8, "gui/planets/third/Polaris5/43280320855_", False, 6, 6)

Ethereal1 = Animate_smt(60, 8, "gui/planets/four/Ethereal1/3537661925_", False, 5, 5)
Solstice2 = Animate_smt(60, 8, "gui/planets/four/Solstice2/2921353398_", False, 6, 6)
Scepter3 = Animate_smt(60, 8, "gui/planets/four/Scepter3/4280320855_", False, 6, 6)
Prisma4 = Animate_smt(60, 8, "gui/planets/four/Prisma4/2718817553_", False, 6, 6)
Fantasia5 = Animate_smt(60, 8, "gui/planets/four/Fantasia5/4229076021_", False, 6, 6)

New_Earth1 = Animate_smt(60, 8, "gui/planets/five/New Earth1/140156066_", False, 6, 6)
Horizon2 = Animate_smt(60, 8, "gui/planets/five/Horizon2/2154258418(1)_", False, 6, 6)
Valhalla3 = Animate_smt(60, 8, "gui/planets/five/Valhalla3/2403736513_", False, 6, 6)
Radiance4 = Animate_smt(60, 8, "gui/planets/five/Radiance4/2403736513_", False, 6, 6)

PlanetV = Animate_smt(60, 8, "gui/planets/six/Planet V/2403736513_", False, 5, 5)

PlanetV_back = Animate_smt(60, 9, "planets_play/six/back", False, 2, 2)





Jack = Animate_smt(10, 4, "gui/Jack_guns/Idle", False, 12, 12)
Jenifer = Animate_smt(20, 4, "gui/Jenifer_skills/Idle-", False, 15, 15)
Robert = Animate_smt(18, 4, "gui/Robert_junk/big_demon_idle_anim_f", False, 15, 15)
Alla = Animate_smt(15, 8, "gui/Alla_food/balancing", False, 15, 15)
running_pers = Animate_smt(15, 5, "sprites/player-run/", False, 3, 3)
enemy_explode = Animate_smt(8, 17, "gui/skills_dop/vampirism/", False, 3, 3)

bg_for_dice = Animate_smt(8, 6, "gui/dice/bg/lines01-Sheet_", True, 1.5, 1.4)
dice = Animate_smt(8, 6, "gui/dice/anim/", False, 16, 16)
#---------
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
enter_galaxy_sound = pygame.mixer.Sound("project-VAK/img/sfx/main_menu/enter galaxy.wav")
counter_sound_not_one = pygame.mixer.Sound("project-VAK/img/sfx/main_menu/23.wav")
counter_sound_one = pygame.mixer.Sound("project-VAK/img/sfx/main_menu/1.wav")
select_but = pygame.mixer.Sound("project-VAK/img/sfx/main_menu/select_but.mp3")
city_noise = pygame.mixer.Sound("project-VAK/img/sfx/main_menu/home_noise.mp3")
sounds_group.append(click_sound)
sounds_group.append(enter_galaxy_sound)
sounds_group.append(counter_sound_not_one)
sounds_group.append(counter_sound_one)

sounds_group.append(select_but)
sounds_group.append(city_noise)
random_track = [1,2,3,4]
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
        if sound_make is not True and sound_make is not False:
            self.current_sound_want_to_make = pygame.mixer.Sound(sound_make)
            self.current_sound_want_to_make.set_volume(volume_game_sound)


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
                elif self.sound_make == False:
                    pass
                else:
                    self.current_sound_want_to_make.stop()
                    self.current_sound_want_to_make.play()
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
            pygame.draw.rect(screen, self.clr, (SCREEN_WIDTH//2 + 50 + self.fade_counter, 0, SCREEN_WIDTH, SCREEN_HEIGHT + 300))
        if self.direc == 2:
            pygame.draw.rect(screen, self.clr, (0,0, SCREEN_WIDTH, 0 + self.fade_counter))
        if self.direc == 3:
            pygame.draw.rect(screen, self.clr, (0 - self.fade_counter * 7, 0, SCREEN_WIDTH//2, SCREEN_HEIGHT + 300))
            pygame.draw.rect(screen, self.clr, (SCREEN_WIDTH//2 + 50 + self.fade_counter * 7, 0, SCREEN_WIDTH, SCREEN_HEIGHT + 300))
        if self.fade_counter > SCREEN_WIDTH - 500:
            fade_complete = True
        
        return fade_complete

intro_fade = ScreenFade(1, (0,0,0), 4)
death_fade = ScreenFade(2, (0,0,0), 4)
shop_fade = ScreenFade(3, (0,0,0), 4)

def gradientRect( window, left_colour, right_colour, target_rect, alpha=20):
    """ Draw a horizontal-gradient filled rectangle covering <target_rect> """
    colour_rect = pygame.Surface( (2, 2) )                                   # tiny! 2x2 bitmap
    pygame.draw.line( colour_rect, left_colour,  ( 0,0 ), ( 0,1 ) )            # left colour line
    pygame.draw.line( colour_rect, right_colour, ( 1,0 ), ( 1,1 ) )            # right colour line
    colour_rect = pygame.transform.smoothscale( colour_rect, ( target_rect.width, target_rect.height ) )  # stretch!
    colour_rect.set_alpha(alpha)
    window.blit(colour_rect, target_rect)    

#---------------
with open("project-VAK/save/saving.txt", "r") as f:
    saving = f.readlines()
    f.close()

money = int(saving[0])
money_diamond = int(saving[1])

ship_level = int(saving[3])
to_next_lvl_ship = int(saving[4])

star_gal1 = int(saving[6])
star_gal2 = int(saving[7])
star_gal3 = int(saving[8])
star_gal4 = int(saving[9])
star_gal5 = int(saving[10])
star_gal6 = int(saving[11])

stars_on_planets_gal1 = list(map(int, saving[13].split(",")))
stars_on_planets_gal2 = list(map(int, saving[14].split(",")))
stars_on_planets_gal3 = list(map(int, saving[15].split(",")))
stars_on_planets_gal4 = list(map(int, saving[16].split(",")))
stars_on_planets_gal5 = list(map(int, saving[17].split(",")))
stars_on_planets_gal6 = [int(saving[18])]

bar_of_volume_game_music = int(saving[20]) 
bar_of_volume_game_sounds = int(saving[21])
volume_game_music = float(saving[22])
volume_game_sound = float(saving[23])

guns_player_have = list(map(int, saving[25].split(",")))
#1;morehealth 2;faster 3;les_toxic 4;les_cold 5;vampire
#6;bomb 7;shield 8;determ 9;occultism 10;goodfood
#11;reload 12;secondbreath 13;luckforfight 14;black 15;higher
#16;gold 17;electric
skill_player_have = list(map(int, saving[26].split(",")))
small_fruit = int(saving[27])
fresh_fruit = int(saving[28])
big_fruit = int(saving[29])



grass_cnt = int(saving[31])
best_det_cnt = int(saving[32])
power_det_cnt = int(saving[33])
toxic_det_cnt = int(saving[34])
water_det_cnt = int(saving[35])
rare_det_cnt = int(saving[36])
black_det_cnt = int(saving[37])
def_det_cnt = int(saving[38])
better_stl_cnt = int(saving[39])
gold_cnt = int(saving[40])
steel_cnt = int(saving[41])
week_steel_cnt = int(saving[42])
#---------------


dice_pos = 320
dice_rol = 0.7
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
skill_which = 1
planet_which_you_ch = 1
diff_ch = 0
counters_constat = 250


def saving_game():
    with open("project-VAK/save/saving.txt", "w") as f:
        f.write(str(money) + '\n')
        f.write(str(money_diamond) + '\n')
        f.write('\n')
        f.write(str(ship_level) + '\n')
        f.write(str(to_next_lvl_ship) + '\n')
        f.write('\n')
        f.write(str(star_gal1) + '\n')
        f.write(str(star_gal2) + '\n')
        f.write(str(star_gal3) + '\n')
        f.write(str(star_gal4) + '\n')
        f.write(str(star_gal5) + '\n')
        f.write(str(star_gal6) + '\n')
        f.write('\n')
        for i in range(len(stars_on_planets_gal1)):
            if i != 4:
                f.write(f'{stars_on_planets_gal1[i]},')
            else:
                f.write(f'{stars_on_planets_gal1[i]}\n')
        for i in range(len(stars_on_planets_gal2)):
            if i != 4:
                f.write(f'{stars_on_planets_gal2[i]},')
            else:
                f.write(f'{stars_on_planets_gal2[i]}\n')
        for i in range(len(stars_on_planets_gal3)):
            if i != 4:
                f.write(f'{stars_on_planets_gal3[i]},')
            else:
                f.write(f'{stars_on_planets_gal3[i]}\n')
        for i in range(len(stars_on_planets_gal4)):
            if i != 4:
                f.write(f'{stars_on_planets_gal4[i]},')
            else:
                f.write(f'{stars_on_planets_gal4[i]}\n')
        for i in range(len(stars_on_planets_gal5)):
            if i != 3:
                f.write(f'{stars_on_planets_gal5[i]},')
            else:
                f.write(f'{stars_on_planets_gal5[i]}\n')
        f.write(str(stars_on_planets_gal6[0]) + '\n')
        f.write('\n')
        f.write(str(bar_of_volume_game_music) + '\n')
        f.write(str(bar_of_volume_game_sounds) + '\n')
        f.write(str(volume_game_music) + '\n')
        f.write(str(volume_game_sound) + '\n')
        f.write('\n')
        for i in range(len(guns_player_have)):
            if i != 40:
                f.write(f'{guns_player_have[i]},')
            else:
                f.write(f'{guns_player_have[i]}\n')
        for i in range(len(skill_player_have)):
            if i != 16:
                f.write(f'{skill_player_have[i]},')
            else:
                f.write(f'{skill_player_have[i]}\n')
        f.write(str(small_fruit) + "\n")
        f.write(str(fresh_fruit) + "\n")
        f.write(str(big_fruit) + "\n")
        f.write('\n')
        f.write(str(grass_cnt) + "\n")
        f.write(str(best_det_cnt) + "\n")
        f.write(str(power_det_cnt) + "\n")
        f.write(str(toxic_det_cnt) + "\n")
        f.write(str(water_det_cnt) + "\n")
        f.write(str(rare_det_cnt) + "\n")
        f.write(str(black_det_cnt) + "\n")
        f.write(str(def_det_cnt) + "\n")
        f.write(str(better_stl_cnt) + "\n")
        f.write(str(gold_cnt) + "\n")
        f.write(str(steel_cnt) + "\n")
        f.write(str(week_steel_cnt) + "\n")

while run:
    if current_window_selected == "main_menu":
        color_menu()
        start_im = pygame.image.load("project-VAK/img/gui/button_start.png").convert_alpha()
        start_im_s = pygame.image.load("project-VAK/img/gui/button_start_select.png").convert_alpha()
        option_im = pygame.image.load("project-VAK/img/gui/button_options.png").convert_alpha()
        option_im_s = pygame.image.load("project-VAK/img/gui/button_options_select.png").convert_alpha()
        credit_im = pygame.image.load("project-VAK/img/gui/button_credits.png").convert_alpha()
        credit_im_s = pygame.image.load("project-VAK/img/gui/button_credits_select.png").convert_alpha()
        exit_im = pygame.image.load("project-VAK/img/gui/button_exit.png").convert_alpha()
        exit_im_s = pygame.image.load("project-VAK/img/gui/button_exit_select.png").convert_alpha()

        if ship_level == 1:
            ship_im = pygame.image.load("project-VAK/img/gui/ships/ship1.png").convert_alpha()
            ship_im = pygame.transform.scale(ship_im, (int(ship_im.get_width() * 5), int(ship_im.get_height() * 5)))
            screen.blit(ship_im, (680, y_for_ship_pos + 180))
        if ship_level == 2:
            ship_im = pygame.image.load("project-VAK/img/gui/ships/ship2.png").convert_alpha()
            ship_im = pygame.transform.scale(ship_im, (int(ship_im.get_width() * 5), int(ship_im.get_height() * 5)))
            screen.blit(ship_im, (680, y_for_ship_pos))     
        if ship_level == 3:
            ship_im = pygame.image.load("project-VAK/img/gui/ships/ship3.png").convert_alpha()
            ship_im = pygame.transform.scale(ship_im, (int(ship_im.get_width() * 5), int(ship_im.get_height() * 5)))
            screen.blit(ship_im, (580, y_for_ship_pos))
        if ship_level == 4:
            ship_im = pygame.image.load("project-VAK/img/gui/ships/ship4.png").convert_alpha()
            ship_im = pygame.transform.scale(ship_im, (int(ship_im.get_width() * 5), int(ship_im.get_height() * 5)))
            screen.blit(ship_im, (580, y_for_ship_pos))
        if ship_level == 5:
            ship_im = pygame.image.load("project-VAK/img/gui/ships/ship5.png").convert_alpha()
            ship_im = pygame.transform.scale(ship_im, (int(ship_im.get_width() * 5), int(ship_im.get_height() * 5)))
            screen.blit(ship_im, (580, y_for_ship_pos))
        if ship_level == 6:
            ship_im = pygame.image.load("project-VAK/img/gui/ships/ship6.png").convert_alpha()
            ship_im = pygame.transform.scale(ship_im, (int(ship_im.get_width() * 5), int(ship_im.get_height() * 5)))
            screen.blit(ship_im, (580, y_for_ship_pos))

        draw_text("SPACE V", font_2, (255, 255, 255), 10, 90)
        draw_text("ver 0.6", font, (155, 55, 95), 1440, 860)
        draw_text("ver 0.6", font, (90, 90, 90), 1440, 858)
        
        y_for_ship_pos += floating_ship_speed
        if y_for_ship_pos >= 320:
            floating_ship_speed = -floating_ship_speed
        if y_for_ship_pos <= 290:
            floating_ship_speed = -floating_ship_speed

        credit_button = Button(SCREEN_WIDTH // 45, SCREEN_HEIGHT // 2 + 210, credit_im, 7, credit_im_s)
        start_button = Button(SCREEN_WIDTH // 45, SCREEN_HEIGHT // 2 - 10, start_im, 7, start_im_s, start_im, "project-VAK/img/sfx/main_menu/start_game.mp3")
        option_button = Button(SCREEN_WIDTH // 45, SCREEN_HEIGHT // 2 + 100, option_im, 7, option_im_s)
        exit_button = Button(SCREEN_WIDTH // 45, SCREEN_HEIGHT // 2 + 320, exit_im, 7, exit_im_s)

        if credit_button.draw(screen):
            current_window_selected = "credits"
        if start_button.draw(screen):
                city_noise.play(-1)
                start_intro = True
                current_window_selected = "home"
        if option_button.draw(screen):
            current_window_selected = "options"
        if exit_button.draw(screen):
            run = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                saving_game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False
                    saving_game()

    if current_window_selected == "home":
        page = 1
        enter_shop = None
        clock.tick(FPS)
        back_ground_for_home = pygame.image.load("project-VAK/img/gui/menu_in_play.png").convert_alpha()
        back_ground_for_home = pygame.transform.scale(back_ground_for_home, (int(back_ground_for_home.get_width() * 4), int(back_ground_for_home.get_height() * 5.1)))
        pygame.draw.rect(screen, (0,0,0), (-20, 0, 2500, 2600))
        screen.blit(back_ground_for_home, (0,-80))
        
        if ship_level == 1:
            ship_im = pygame.image.load("project-VAK/img/gui/ships/ship1.png").convert_alpha()
            ship_im = pygame.transform.scale(ship_im, (int(ship_im.get_width() * 4), int(ship_im.get_height() * 4)))
            screen.blit(ship_im, (460, y_for_ship_pos_for_menu))
        if ship_level == 2:
            ship_im = pygame.image.load("project-VAK/img/gui/ships/ship2.png").convert_alpha()
            ship_im = pygame.transform.scale(ship_im, (int(ship_im.get_width() * 4.2), int(ship_im.get_height() * 4.2)))
            screen.blit(ship_im, (330, y_for_ship_pos_for_menu - 130))     
        if ship_level == 3:
            ship_im = pygame.image.load("project-VAK/img/gui/ships/ship3.png").convert_alpha()
            ship_im = pygame.transform.scale(ship_im, (int(ship_im.get_width() * 4.4), int(ship_im.get_height() * 4.4)))
            screen.blit(ship_im, (300 , y_for_ship_pos_for_menu - 150))
        if ship_level == 4:
            ship_im = pygame.image.load("project-VAK/img/gui/ships/ship4.png").convert_alpha()
            ship_im = pygame.transform.scale(ship_im, (int(ship_im.get_width() * 4.4), int(ship_im.get_height() * 4.4)))
            screen.blit(ship_im, (310, y_for_ship_pos_for_menu - 170))
        if ship_level == 5:
            ship_im = pygame.image.load("project-VAK/img/gui/ships/ship5.png").convert_alpha()
            ship_im = pygame.transform.scale(ship_im, (int(ship_im.get_width() * 4.6), int(ship_im.get_height() * 4.6)))
            screen.blit(ship_im, (310, y_for_ship_pos_for_menu - 230))
        if ship_level == 6:
            ship_im = pygame.image.load("project-VAK/img/gui/ships/ship6.png").convert_alpha()
            ship_im = pygame.transform.scale(ship_im, (int(ship_im.get_width() * 4.5), int(ship_im.get_height() * 4.5)))
            screen.blit(ship_im, (290, y_for_ship_pos_for_menu - 200))
        player_for_menu.update()
        player_for_menu.draw()
        
        y_for_ship_pos_for_menu += floating_ship_speed
        if y_for_ship_pos_for_menu >= 525:
            floating_ship_speed = -floating_ship_speed
        if y_for_ship_pos_for_menu <= 535:
            floating_ship_speed = -floating_ship_speed

        if player_for_menu.rect.x >= 500 and player_for_menu.rect.x <= 590:
            draw_text("PRESS SPACE TO FLY INTO THE SPACE", font_4, (255,255,255), 20, 12)
            enter_shop = "select planet"
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
                saving_game()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    is_moving_left = True
                if event.key == pygame.K_d:
                    is_moving_right = True
                if event.key == pygame.K_ESCAPE:
                    run = False
                    saving_game()
                if event.key == pygame.K_SPACE:
                    if enter_shop != None:
                        if enter_shop != "select planet":
                
                            start_intro = True
                            intro_fade.fade_counter = 0
                            shop_fade.fade_counter = 0
                            current_window_selected = enter_shop
                            city_noise.stop()
                        else:
                            start_intro = True
                            intro_fade.fade_counter = 0
                            shop_fade.fade_counter = 0
                            current_window_selected = enter_shop
                            city_noise.stop()
                            flag_shop = 1
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    is_moving_left = False
                if event.key == pygame.K_d:
                    is_moving_right = False


    if current_window_selected == "select planet":
        if page == 1:
            star_gal1 = min(stars_on_planets_gal1)
            star_gal2 = min(stars_on_planets_gal2)
            star_gal3 = min(stars_on_planets_gal3)      
            star_gal4 = min(stars_on_planets_gal4)
            star_gal5 = min(stars_on_planets_gal5)
            star_gal6 = min(stars_on_planets_gal6)
            clock.tick(FPS)
            is_moving_left = False
            is_moving_right = False
            color_menu()
            galaxy_1.update()
            galaxy_1.draw(screen, 20, 5)
            galaxy_uk.update()
            star_galx1_im = pygame.image.load(f"project-VAK/img/gui/stars/{star_gal1}.png").convert_alpha()
            star_galx1_im = pygame.transform.scale(star_galx1_im, (int(star_galx1_im.get_width() * 3), int(star_galx1_im.get_height() * 3)))
            screen.blit(star_galx1_im, (370 , 325))

            back_im = pygame.image.load("project-VAK/img/gui/button_back.png").convert_alpha()
            back_im_s = pygame.image.load("project-VAK/img/gui/button_back_select.png").convert_alpha()
            back_button = Button(30, 20, back_im, 5, back_im_s)

            if back_button.draw(screen):
                start_intro = True
                intro_fade.fade_counter = 0
                shop_fade.fade_counter = 0
                flag_shop = 1
                current_window_selected = "home"
                city_noise.play(-1)

            if ship_level > 1:
                galaxy_2.update()
                galaxy_2.draw(screen, 520, 5)
                star_galx2_im = pygame.image.load(f"project-VAK/img/gui/stars/{star_gal2}.png").convert_alpha()
                star_galx2_im = pygame.transform.scale(star_galx2_im, (int(star_galx2_im.get_width() * 3), int(star_galx2_im.get_height() * 3)))
                screen.blit(star_galx2_im, (890 , 325))
            else:
                galaxy_uk.draw(screen, 520, 5)
                
            if ship_level > 2:
                galaxy_3.update()
                galaxy_3.draw(screen, 1020, 5)
                star_galx3_im = pygame.image.load(f"project-VAK/img/gui/stars/{star_gal3}.png").convert_alpha()
                star_galx3_im = pygame.transform.scale(star_galx3_im, (int(star_galx3_im.get_width() * 3), int(star_galx3_im.get_height() * 3)))
                screen.blit(star_galx3_im, (1390 , 335))
            else:
                galaxy_uk.draw(screen, 1020, 5)

            if ship_level > 3:
                galaxy_4.update()
                galaxy_4.draw(screen, 20, 400)
                star_galx4_im = pygame.image.load(f"project-VAK/img/gui/stars/{star_gal4}.png").convert_alpha()
                star_galx4_im = pygame.transform.scale(star_galx4_im, (int(star_galx4_im.get_width() * 3), int(star_galx4_im.get_height() * 3)))
                screen.blit(star_galx4_im, (370 , 725))
            else:
                galaxy_uk.draw(screen, 20, 400)

            if ship_level > 4:
                galaxy_5.update()
                galaxy_5.draw(screen, 520, 400)
                star_galx5_im = pygame.image.load(f"project-VAK/img/gui/stars/{star_gal5}.png").convert_alpha()
                star_galx5_im = pygame.transform.scale(star_galx5_im, (int(star_galx5_im.get_width() * 3), int(star_galx5_im.get_height() * 3)))
                screen.blit(star_galx5_im, (890 , 725))
            else:
                galaxy_uk.draw(screen, 520, 400)

            if ship_level > 5:
                galaxy_6.update()
                galaxy_6.draw(screen, 1020, 400)
                star_galx6_im = pygame.image.load(f"project-VAK/img/gui/stars/{star_gal6}.png").convert_alpha()
                star_galx6_im = pygame.transform.scale(star_galx6_im, (int(star_galx6_im.get_width() * 3), int(star_galx6_im.get_height() * 3)))
                screen.blit(star_galx6_im, (1390 , 725))
            else:
                galaxy_uk.draw(screen, 1020, 400)

            if start_intro == True:
                    if flag_shop != 1:
                        if intro_fade.fade():
                            start_intro = False
                            intro_fade.fade_counter = 0
                    else:
                        if shop_fade.fade():
                            start_intro = False
                            shop_fade.fade_counter = 0


            mouse_pos = pygame.mouse.get_pos()         
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        run = False
                if event.type == pygame.MOUSEBUTTONUP:
                    if mouse_pos[0] >= 50 and mouse_pos[0] <= 400:
                        if mouse_pos[1] >= 90 and mouse_pos[1] <= 400:
                            page = 10
                            enter_galaxy_sound.play()
                    if mouse_pos[0] >= 560 and mouse_pos[0] <= 910:
                        if mouse_pos[1] >= 90 and mouse_pos[1] <= 400:
                            page = 20
                            enter_galaxy_sound.play()
                    if mouse_pos[0] >= 1070 and mouse_pos[0] <= 1420:
                        if mouse_pos[1] >= 90 and mouse_pos[1] <= 400:
                            page = 30
                            enter_galaxy_sound.play()

                    if mouse_pos[0] >= 50 and mouse_pos[0] <= 400:
                        if mouse_pos[1] >= 520 and mouse_pos[1] <= 810:
                            page = 40
                            enter_galaxy_sound.play()
                    if mouse_pos[0] >= 560 and mouse_pos[0] <= 910:
                        if mouse_pos[1] >= 520 and mouse_pos[1] <= 810:
                            page = 50
                            enter_galaxy_sound.play()
                    if mouse_pos[0] >= 1070 and mouse_pos[0] <= 1420:
                        if mouse_pos[1] >= 520 and mouse_pos[1] <= 810:
                            page = 60
                            enter_galaxy_sound.play()
        if page == 2:
            color_menu()
            back_im = pygame.image.load("project-VAK/img/gui/button_back.png").convert_alpha()
            back_im_s = pygame.image.load("project-VAK/img/gui/button_back_select.png").convert_alpha()
            back_button = Button(30, 20, back_im, 5, back_im_s)
            if back_button.draw(screen):
                make_action = 1
            table_im = pygame.image.load("project-VAK/img/gui/shops_back/guns_table.png").convert_alpha()
            table_im = pygame.transform.scale(table_im, (int(table_im.get_width() * 7), int(table_im.get_height() * 7.5)))
            screen.blit(table_im, (280,40))
            draw_text("choose the difficulty:", font_3, (85, 157, 230), 350 , 217)
            draw_text("choose the difficulty:", font_3, (255,255,255), 350 , 220)
            draw_text("difficulty affects the damage of mobs and the number of mobs", font_5, (11, 17, 38), 350 , 470)
            draw_text("that can spawn. The higher the difficulty, the higher", font_5, (11, 17, 38), 350 , 490)
            draw_text("the reward after the game", font_5, (11, 17, 38), 350 , 510)
            start_play_on_planet = Button(957, 106, start_im, 6, start_im_s, start_im, "project-VAK/img/sfx/main_menu/magic_003.wav")
            if diff_ch != 0:
                if start_play_on_planet.draw(screen):
                    start_intro = True
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load("project-VAK/img/sfx/main_menu/cyber city 2-b.mp3")
                    current_window_selected = "play on planet"
                draw_text("selected difficulty:", font_3, (85, 157, 230), 350 , 567)
                draw_text("selected difficulty:", font_3, (255,255,255), 350 ,570)
            if diff_ch == 1:
                draw_text("pacifism and puppies", font_4, (85, 157, 230), 350 , 617)
                draw_text("pacifism and puppies", font_4, (255,255,255), 350 ,620)
                draw_text("This mode is extremely light and simple.", font_5, (255,255,255), 710 ,625)
                draw_text("it is suitable for those who have not yet got used to the planet and ", font_5, (255,255,255), 350 ,655)
                draw_text("are just trying to master it. the loot after the game is ", font_5, (255,255,255), 350 ,685)
                draw_text("extremely small, do not count on a large amount of resources", font_5, (255,255,255), 350 ,715)
                draw_text("on this difficulty", font_5, (255,255,255), 350 ,745)
            if diff_ch == 2:
                draw_text("normal mode", font_4, (85, 157, 230), 350 , 617)
                draw_text("normal mode", font_4, (255,255,255), 350 ,620)
                draw_text("This is a normal calm mode. There is more damage and", font_5, (255,255,255), 580 ,625)
                draw_text("danger from mobs. this mode is more suitable if you are not", font_5, (255,255,255), 350 ,655)
                draw_text("sure that you are strong enough for higher difficulties, but you  ", font_5, (255,255,255), 350 ,685)
                draw_text("are sure that difficulty mode 1 is too easy for you. also, in order", font_5, (255,255,255), 350 ,715)
                draw_text("to earn new resources, this mode will be better for you", font_5, (255,255,255), 350 ,745)
            if diff_ch == 3:
                draw_text("hypersensitivity", font_4, (85, 157, 230), 350 , 617)
                draw_text("hypersensitivity", font_4, (255,255,255), 350 ,620)
                draw_text("this mode is more strict and complex. In this", font_5, (255,255,255), 630 ,625)
                draw_text("mode, your sensitivity increases and the damage from mobs increases ", font_5, (255,255,255), 350 ,655)
                draw_text("very much. it is not recommended if you do not have perks to ", font_5, (255,255,255), 350 ,685)
                draw_text("increase hp and if you do not have enough food. More chance to ", font_5, (255,255,255), 350 ,715)
                draw_text("get valuable loot in this game mode", font_5, (255,255,255), 350 ,745)
            if diff_ch == 4:
                draw_text("Fear and hunger", font_4, (85, 157, 230), 350 , 617)
                draw_text("Fear and hunger", font_4, (255,255,255), 350 ,620)
                draw_text("This mode is suitable for those who are confident", font_5, (255,255,255), 630 ,625)
                draw_text("and ready for obstacles. At this difficulty level, food restores 5 hp ", font_5, (255,255,255), 350 ,655)
                draw_text("less than usual, and enemies deal very heavy damage and their speed ", font_5, (255,255,255), 350 ,685)
                draw_text("increases very much. After playing at this difficulty level, you get  ", font_5, (255,255,255), 350 ,715)
                draw_text("a significant loot reward", font_5, (255,255,255), 350 ,745)
            if diff_ch == 5:
                draw_text("Horror and exhaustion", font_4, (85, 157, 230), 350 , 617)
                draw_text("Horror and exhaustion", font_4, (255,255,255), 350 ,620)
                draw_text("This mode is only for strong players.", font_5, (255,255,255), 740 ,625)
                draw_text("no mercy, the enemies are hitting with all their might, the HP of mobs", font_5, (255,255,255), 350 ,655)
                draw_text("is doubled and their speed is also at a height, food restores half as ", font_5, (255,255,255), 350 ,685)
                draw_text("much hp as it should, and the horror of death takes away 1 hp  ", font_5, (255,255,255), 350 ,715)
                draw_text("from you every minute. if you survive, you get a very valuable loot", font_5, (255,255,255), 350 ,745)     
                draw_text("but if you lose on the planet, then you lose all your money  ", font_5, (110, 14, 30), 350 ,775)     
                draw_text("and the details that you had before the raid", font_5, (110, 14, 30), 350 ,805)     
            emp_sm = pygame.image.load(f"project-VAK/img/gui/empty_small.png").convert_alpha()
            yes_sm = pygame.image.load(f"project-VAK/img/gui/yes_small.png").convert_alpha()
            if diff_ch == 1:
                b1 = Button(405, 396, yes_sm, 4, yes_sm)
            else:
                b1 = Button(405, 396, emp_sm, 4, emp_sm)
            if b1.draw(screen):
                diff_ch = 1

            if diff_ch == 2:
                b2 = Button(572, 396, yes_sm, 4, yes_sm)
            else:
                b2 = Button(572, 396, emp_sm, 4, emp_sm)
            if b2.draw(screen):
                diff_ch = 2
            if diff_ch == 3:
                b3 = Button(757, 396, yes_sm, 4, yes_sm)
            else:
                b3 = Button(757, 396, emp_sm, 4, emp_sm)
            if b3.draw(screen):
                diff_ch = 3
            if diff_ch == 4:
                b4 = Button(937, 396, yes_sm, 4, yes_sm)
            else:
                b4 = Button(937, 396, emp_sm, 4, emp_sm)
            if b4.draw(screen):
                diff_ch = 4
            if diff_ch == 5:
                b5 = Button(1115, 396, yes_sm, 4, yes_sm)
            else:
                b5 = Button(1115, 396, emp_sm, 4, emp_sm)
            if b5.draw(screen):
                diff_ch = 5
            star_galx1_im = pygame.image.load(f"project-VAK/img/gui/stars/1.png").convert_alpha()
            star_galx1_im = pygame.transform.scale(star_galx1_im, (int(star_galx1_im.get_width() * 5), int(star_galx1_im.get_height() * 5)))
            screen.blit(star_galx1_im, (380 , 285))
            star_galx2_im = pygame.image.load(f"project-VAK/img/gui/stars/2.png").convert_alpha()
            star_galx2_im = pygame.transform.scale(star_galx2_im, (int(star_galx2_im.get_width() * 5), int(star_galx2_im.get_height() * 5)))
            screen.blit(star_galx2_im, (550 , 285))
            star_galx2_im = pygame.image.load(f"project-VAK/img/gui/stars/3.png").convert_alpha()
            star_galx2_im = pygame.transform.scale(star_galx2_im, (int(star_galx2_im.get_width() * 5), int(star_galx2_im.get_height() * 5)))
            screen.blit(star_galx2_im, (720 , 285))
            star_galx2_im = pygame.image.load(f"project-VAK/img/gui/stars/4.png").convert_alpha()
            star_galx2_im = pygame.transform.scale(star_galx2_im, (int(star_galx2_im.get_width() * 5), int(star_galx2_im.get_height() * 5)))
            screen.blit(star_galx2_im, (900 , 285))
            star_galx2_im = pygame.image.load(f"project-VAK/img/gui/stars/5.png").convert_alpha()
            star_galx2_im = pygame.transform.scale(star_galx2_im, (int(star_galx2_im.get_width() * 5), int(star_galx2_im.get_height() * 5)))
            screen.blit(star_galx2_im, (1080 , 250))
            if planet_which_you_ch == 1:
                draw_text("planet: Nova prime", font_3, (85, 157, 230), 350 , 117)
                draw_text("planet: Nova prime", font_3, (255,255,255), 350 , 120)
            if planet_which_you_ch == 2:
                draw_text("planet: Astoria", font_3, (85, 157, 230), 350 , 117)
                draw_text("planet: Astoria", font_3, (255,255,255), 350 , 120)
            if planet_which_you_ch == 3:
                draw_text("planet: Olympus", font_3, (85, 157, 230), 350 , 117)
                draw_text("planet: Olympus", font_3, (255,255,255), 350 , 120)
            if planet_which_you_ch == 4:
                draw_text("planet: Nebulous", font_3, (85, 157, 230), 350 , 117)
                draw_text("planet: Nebulous", font_3, (255,255,255), 350 , 120)
            if planet_which_you_ch == 5:
                draw_text("planet: Infinity", font_3, (85, 157, 230), 350 , 117)
                draw_text("planet: Infinity", font_3, (255,255,255), 350 , 120)
            if planet_which_you_ch == 6:
                draw_text("planet: Genesis", font_3, (85, 157, 230), 350 , 117)
                draw_text("planet: Genesis", font_3, (255,255,255), 350 , 120)
            if planet_which_you_ch == 7:
                draw_text("planet: Equinox", font_3, (85, 157, 230), 350 , 117)
                draw_text("planet: Equinox", font_3, (255,255,255), 350 , 120)
            if planet_which_you_ch == 8:
                draw_text("planet: Orpheus", font_3, (85, 157, 230), 350 , 117)
                draw_text("planet: Orpheus", font_3, (255,255,255), 350 , 120)
            if planet_which_you_ch == 9:
                draw_text("planet: Utopia", font_3, (85, 157, 230), 350 , 117)
                draw_text("planet: Utopia", font_3, (255,255,255), 350 , 120)
            if planet_which_you_ch == 10:
                draw_text("planet: Nexus", font_3, (85, 157, 230), 350 , 117)
                draw_text("planet: Nexus", font_3, (255,255,255), 350 , 120)
            if planet_which_you_ch == 11:
                draw_text("planet: Andromeda", font_3, (85, 157, 230), 350 , 117)
                draw_text("planet: Andromeda", font_3, (255,255,255), 350 , 120)
            if planet_which_you_ch == 12:
                draw_text("planet: Epoch", font_3, (85, 157, 230), 350 , 117)
                draw_text("planet: Epoch", font_3, (255,255,255), 350 , 120)
            if planet_which_you_ch == 13:
                draw_text("planet: Arcadia", font_3, (85, 157, 230), 350 , 117)
                draw_text("planet: Arcadia", font_3, (255,255,255), 350 , 120)
            if planet_which_you_ch == 14:
                draw_text("planet: Apollo", font_3, (85, 157, 230), 350 , 117)
                draw_text("planet: Apollo", font_3, (255,255,255), 350 , 120)
            if planet_which_you_ch == 15:
                draw_text("planet: Polaris", font_3, (85, 157, 230), 350 , 117)
                draw_text("planet: Polaris", font_3, (255,255,255), 350 , 120)
            if planet_which_you_ch == 16:
                draw_text("planet: Ethereal", font_3, (85, 157, 230), 350 , 117)
                draw_text("planet: Ethereal", font_3, (255,255,255), 350 , 120)
            if planet_which_you_ch == 17:
                draw_text("planet: Solstice", font_3, (85, 157, 230), 350 , 117)
                draw_text("planet: Solstice", font_3, (255,255,255), 350 , 120)
            if planet_which_you_ch == 18:
                draw_text("planet: Scepter", font_3, (85, 157, 230), 350 , 117)
                draw_text("planet: Scepter", font_3, (255,255,255), 350 , 120)
            if planet_which_you_ch == 19:
                draw_text("planet: Prisma", font_3, (85, 157, 230), 350 , 117)
                draw_text("planet: Prisma", font_3, (255,255,255), 350 , 120)
            if planet_which_you_ch == 20:
                draw_text("planet: Fantasia", font_3, (85, 157, 230), 350 , 117)
                draw_text("planet: Fantasia", font_3, (255,255,255), 350 , 120)
            if planet_which_you_ch == 21:
                draw_text("planet: New_Earth", font_3, (85, 157, 230), 350 , 117)
                draw_text("planet: New_Earth", font_3, (255,255,255), 350 , 120)
            if planet_which_you_ch == 22:
                draw_text("planet: Horizon", font_3, (85, 157, 230), 350 , 117)
                draw_text("planet: Horizon", font_3, (255,255,255), 350 , 120)
            if planet_which_you_ch == 23:
                draw_text("planet: Valhalla", font_3, (85, 157, 230), 350 , 117)
                draw_text("planet: Valhalla", font_3, (255,255,255), 350 , 120)
            if planet_which_you_ch == 24:
                draw_text("planet: Radiance", font_3, (85, 157, 230), 350 , 117)
                draw_text("planet: Radiance", font_3, (255,255,255), 350 , 120)
            if planet_which_you_ch == 25:
                draw_text("planet: PlanetV", font_3, (85, 157, 230), 350 , 117)
                draw_text("planet: PlanetV", font_3, (255,255,255), 350 , 120)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        run = False
                if event.type == pygame.MOUSEBUTTONUP:
                    if make_action == 1:
                        page = 1
                        diff_ch = 0
                        make_action = 0
        if page == 30:
            color_menu()

            galaxy_3_for_ui.update()
            galaxy_3_for_ui.draw(screen, 10, 5)
            back_im = pygame.image.load("project-VAK/img/gui/button_back.png").convert_alpha()
            back_im_s = pygame.image.load("project-VAK/img/gui/button_back_select.png").convert_alpha()
            back_button = Button(30, 130, back_im, 4, back_im_s)
            if back_button.draw(screen):
                make_action = 3
            Andromeda1.update()
            Andromeda1.draw(screen, 480, 70)
            draw_text("Andromeda", font_3, (255,255,255), 32 , 790)

            star_galx1_im = pygame.image.load(f"project-VAK/img/gui/stars/{stars_on_planets_gal3[0]}.png").convert_alpha()
            star_galx1_im = pygame.transform.scale(star_galx1_im, (int(star_galx1_im.get_width() * 5), int(star_galx1_im.get_height() * 5)))
            screen.blit(star_galx1_im, (1030 , 585))

            button_right_im = pygame.image.load("project-VAK/img/gui/button_right.png").convert_alpha()
            button_right_im_press = pygame.image.load("project-VAK/img/gui/button_right_press.png").convert_alpha()
            button_right = Button(1450, 400, button_right_im, 8, button_right_im, button_right_im_press)

            if button_right.draw(screen):
                make_action = 2

            button_left_im = pygame.image.load("project-VAK/img/gui/button_left.png").convert_alpha()
            button_left_im_press = pygame.image.load("project-VAK/img/gui/button_left_press.png").convert_alpha()
            button_left = Button(20, 400, button_left_im, 8, button_left_im, button_left_im_press)
            
            if button_left.draw(screen):
                make_action = 1

            start_im = pygame.image.load("project-VAK/img/gui/button_start.png").convert_alpha()
            start_im_s = pygame.image.load("project-VAK/img/gui/button_start_select.png").convert_alpha()
            
            start_button = Button(590, 770, start_im, 8, start_im_s, start_im, "project-VAK/img/sfx/main_menu/start_game.mp3")
            
            if start_button.draw(screen):
                page = 2
                planet_which_you_ch = 11

            mouse_pos = pygame.mouse.get_pos()   
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        run = False
                if event.type == pygame.MOUSEBUTTONUP:
                    if make_action == 3:
                        page = 1
                    if make_action == 2:
                        make_action = 0
                        page = 31
                    if make_action == 1:
                        make_action = 0
                        page = 34

        if page == 31:
            color_menu()

            galaxy_3_for_ui.update()
            galaxy_3_for_ui.draw(screen, 10, 5)
            back_im = pygame.image.load("project-VAK/img/gui/button_back.png").convert_alpha()
            back_im_s = pygame.image.load("project-VAK/img/gui/button_back_select.png").convert_alpha()
            back_button = Button(30, 130, back_im, 4, back_im_s)
            if back_button.draw(screen):
                make_action = 3
            Epoch2.update()
            Epoch2.draw(screen, 480, 70)
            draw_text("Epoch", font_3, (255,255,255), 32 , 790)

            star_galx1_im = pygame.image.load(f"project-VAK/img/gui/stars/{stars_on_planets_gal3[1]}.png").convert_alpha()
            star_galx1_im = pygame.transform.scale(star_galx1_im, (int(star_galx1_im.get_width() * 5), int(star_galx1_im.get_height() * 5)))
            screen.blit(star_galx1_im, (1030 , 585))

            button_right_im = pygame.image.load("project-VAK/img/gui/button_right.png").convert_alpha()
            button_right_im_press = pygame.image.load("project-VAK/img/gui/button_right_press.png").convert_alpha()
            button_right = Button(1450, 400, button_right_im, 8, button_right_im, button_right_im_press)

            if button_right.draw(screen):
                make_action = 2

            button_left_im = pygame.image.load("project-VAK/img/gui/button_left.png").convert_alpha()
            button_left_im_press = pygame.image.load("project-VAK/img/gui/button_left_press.png").convert_alpha()
            button_left = Button(20, 400, button_left_im, 8, button_left_im, button_left_im_press)
            
            if button_left.draw(screen):
                make_action = 1

            start_im = pygame.image.load("project-VAK/img/gui/button_start.png").convert_alpha()
            start_im_s = pygame.image.load("project-VAK/img/gui/button_start_select.png").convert_alpha()
            
            start_button = Button(590, 770, start_im, 8, start_im_s, start_im, "project-VAK/img/sfx/main_menu/start_game.mp3")
            
            if start_button.draw(screen):
                page = 2
                planet_which_you_ch = 12

            mouse_pos = pygame.mouse.get_pos()   
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        run = False
                if event.type == pygame.MOUSEBUTTONUP:
                    if make_action == 3:
                        page = 1
                    if make_action == 2:
                        make_action = 0
                        page = 32
                    if make_action == 1:
                        make_action = 0
                        page = 30

        if page == 32:
            color_menu()

            galaxy_3_for_ui.update()
            galaxy_3_for_ui.draw(screen, 10, 5)
            back_im = pygame.image.load("project-VAK/img/gui/button_back.png").convert_alpha()
            back_im_s = pygame.image.load("project-VAK/img/gui/button_back_select.png").convert_alpha()
            back_button = Button(30, 130, back_im, 4, back_im_s)
            if back_button.draw(screen):
                make_action = 3
            Arcadia3.update()
            Arcadia3.draw(screen, 480, 70)
            draw_text("Arcadia", font_3, (255,255,255), 32 , 790)

            star_galx1_im = pygame.image.load(f"project-VAK/img/gui/stars/{stars_on_planets_gal3[2]}.png").convert_alpha()
            star_galx1_im = pygame.transform.scale(star_galx1_im, (int(star_galx1_im.get_width() * 5), int(star_galx1_im.get_height() * 5)))
            screen.blit(star_galx1_im, (1030 , 585))

            button_right_im = pygame.image.load("project-VAK/img/gui/button_right.png").convert_alpha()
            button_right_im_press = pygame.image.load("project-VAK/img/gui/button_right_press.png").convert_alpha()
            button_right = Button(1450, 400, button_right_im, 8, button_right_im, button_right_im_press)

            if button_right.draw(screen):
                make_action = 2

            button_left_im = pygame.image.load("project-VAK/img/gui/button_left.png").convert_alpha()
            button_left_im_press = pygame.image.load("project-VAK/img/gui/button_left_press.png").convert_alpha()
            button_left = Button(20, 400, button_left_im, 8, button_left_im, button_left_im_press)
            
            if button_left.draw(screen):
                make_action = 1

            start_im = pygame.image.load("project-VAK/img/gui/button_start.png").convert_alpha()
            start_im_s = pygame.image.load("project-VAK/img/gui/button_start_select.png").convert_alpha()
            
            start_button = Button(590, 770, start_im, 8, start_im_s, start_im, "project-VAK/img/sfx/main_menu/start_game.mp3")
            
            if start_button.draw(screen):
                page = 2
                planet_which_you_ch = 13

            mouse_pos = pygame.mouse.get_pos()   
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        run = False
                if event.type == pygame.MOUSEBUTTONUP:
                    if make_action == 3:
                        page = 1
                    if make_action == 2:
                        make_action = 0
                        page = 33
                    if make_action == 1:
                        make_action = 0
                        page = 31

        if page == 33:
            color_menu()

            galaxy_3_for_ui.update()
            galaxy_3_for_ui.draw(screen, 10, 5)
            back_im = pygame.image.load("project-VAK/img/gui/button_back.png").convert_alpha()
            back_im_s = pygame.image.load("project-VAK/img/gui/button_back_select.png").convert_alpha()
            back_button = Button(30, 130, back_im, 4, back_im_s)
            if back_button.draw(screen):
                make_action = 3
            Apollo4.update()
            Apollo4.draw(screen, 480, 70)
            draw_text("Apollo", font_3, (255,255,255), 32 , 790)

            star_galx1_im = pygame.image.load(f"project-VAK/img/gui/stars/{stars_on_planets_gal3[3]}.png").convert_alpha()
            star_galx1_im = pygame.transform.scale(star_galx1_im, (int(star_galx1_im.get_width() * 5), int(star_galx1_im.get_height() * 5)))
            screen.blit(star_galx1_im, (1030 , 585))

            button_right_im = pygame.image.load("project-VAK/img/gui/button_right.png").convert_alpha()
            button_right_im_press = pygame.image.load("project-VAK/img/gui/button_right_press.png").convert_alpha()
            button_right = Button(1450, 400, button_right_im, 8, button_right_im, button_right_im_press)

            if button_right.draw(screen):
                make_action = 2

            button_left_im = pygame.image.load("project-VAK/img/gui/button_left.png").convert_alpha()
            button_left_im_press = pygame.image.load("project-VAK/img/gui/button_left_press.png").convert_alpha()
            button_left = Button(20, 400, button_left_im, 8, button_left_im, button_left_im_press)
            
            if button_left.draw(screen):
                make_action = 1

            start_im = pygame.image.load("project-VAK/img/gui/button_start.png").convert_alpha()
            start_im_s = pygame.image.load("project-VAK/img/gui/button_start_select.png").convert_alpha()
            
            start_button = Button(590, 770, start_im, 8, start_im_s, start_im, "project-VAK/img/sfx/main_menu/start_game.mp3")
            
            if start_button.draw(screen):
                page = 2
                planet_which_you_ch = 14

            mouse_pos = pygame.mouse.get_pos()   
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        run = False
                if event.type == pygame.MOUSEBUTTONUP:
                    if make_action == 3:
                        page = 1
                    if make_action == 2:
                        make_action = 0
                        page = 34
                    if make_action == 1:
                        make_action = 0
                        page = 32

        if page == 34:
            color_menu()

            galaxy_3_for_ui.update()
            galaxy_3_for_ui.draw(screen, 10, 5)
            back_im = pygame.image.load("project-VAK/img/gui/button_back.png").convert_alpha()
            back_im_s = pygame.image.load("project-VAK/img/gui/button_back_select.png").convert_alpha()
            back_button = Button(30, 130, back_im, 4, back_im_s)
            if back_button.draw(screen):
                make_action = 3
            Polaris5.update()
            Polaris5.draw(screen, 480, 70)
            draw_text("Polaris", font_3, (255,255,255), 32 , 790)

            star_galx1_im = pygame.image.load(f"project-VAK/img/gui/stars/{stars_on_planets_gal3[4]}.png").convert_alpha()
            star_galx1_im = pygame.transform.scale(star_galx1_im, (int(star_galx1_im.get_width() * 5), int(star_galx1_im.get_height() * 5)))
            screen.blit(star_galx1_im, (1030 , 585))

            button_right_im = pygame.image.load("project-VAK/img/gui/button_right.png").convert_alpha()
            button_right_im_press = pygame.image.load("project-VAK/img/gui/button_right_press.png").convert_alpha()
            button_right = Button(1450, 400, button_right_im, 8, button_right_im, button_right_im_press)

            if button_right.draw(screen):
                make_action = 2

            button_left_im = pygame.image.load("project-VAK/img/gui/button_left.png").convert_alpha()
            button_left_im_press = pygame.image.load("project-VAK/img/gui/button_left_press.png").convert_alpha()
            button_left = Button(20, 400, button_left_im, 8, button_left_im, button_left_im_press)
            
            if button_left.draw(screen):
                make_action = 1

            start_im = pygame.image.load("project-VAK/img/gui/button_start.png").convert_alpha()
            start_im_s = pygame.image.load("project-VAK/img/gui/button_start_select.png").convert_alpha()
            
            start_button = Button(590, 770, start_im, 8, start_im_s, start_im, "project-VAK/img/sfx/main_menu/start_game.mp3")
            
            if start_button.draw(screen):
                page = 2
                planet_which_you_ch = 15

            mouse_pos = pygame.mouse.get_pos()   
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        run = False
                if event.type == pygame.MOUSEBUTTONUP:
                    if make_action == 3:
                        page = 1
                    if make_action == 2:
                        make_action = 0
                        page = 30
                    if make_action == 1:
                        make_action = 0
                        page = 33

        if page == 40:
            color_menu()

            galaxy_4_for_ui.update()
            galaxy_4_for_ui.draw(screen, 10, 5)
            back_im = pygame.image.load("project-VAK/img/gui/button_back.png").convert_alpha()
            back_im_s = pygame.image.load("project-VAK/img/gui/button_back_select.png").convert_alpha()
            back_button = Button(30, 130, back_im, 4, back_im_s)
            if back_button.draw(screen):
                make_action = 3
            Ethereal1.update()
            Ethereal1.draw(screen, 30, -370)
            draw_text("Ethereal", font_3, (255,255,255), 32 , 790)

            star_galx1_im = pygame.image.load(f"project-VAK/img/gui/stars/{stars_on_planets_gal4[0]}.png").convert_alpha()
            star_galx1_im = pygame.transform.scale(star_galx1_im, (int(star_galx1_im.get_width() * 5), int(star_galx1_im.get_height() * 5)))
            screen.blit(star_galx1_im, (1030 , 585))

            button_right_im = pygame.image.load("project-VAK/img/gui/button_right.png").convert_alpha()
            button_right_im_press = pygame.image.load("project-VAK/img/gui/button_right_press.png").convert_alpha()
            button_right = Button(1450, 400, button_right_im, 8, button_right_im, button_right_im_press)

            if button_right.draw(screen):
                make_action = 2

            button_left_im = pygame.image.load("project-VAK/img/gui/button_left.png").convert_alpha()
            button_left_im_press = pygame.image.load("project-VAK/img/gui/button_left_press.png").convert_alpha()
            button_left = Button(20, 400, button_left_im, 8, button_left_im, button_left_im_press)
            
            if button_left.draw(screen):
                make_action = 1

            start_im = pygame.image.load("project-VAK/img/gui/button_start.png").convert_alpha()
            start_im_s = pygame.image.load("project-VAK/img/gui/button_start_select.png").convert_alpha()
            
            start_button = Button(590, 770, start_im, 8, start_im_s, start_im, "project-VAK/img/sfx/main_menu/start_game.mp3")
            
            if start_button.draw(screen):
                page = 2
                planet_which_you_ch = 16

            mouse_pos = pygame.mouse.get_pos()   
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        run = False
                if event.type == pygame.MOUSEBUTTONUP:
                    if make_action == 3:
                        page = 1
                    if make_action == 2:
                        make_action = 0
                        page = 41
                    if make_action == 1:
                        make_action = 0
                        page = 44

        if page == 41:
            color_menu()

            galaxy_4_for_ui.update()
            galaxy_4_for_ui.draw(screen, 10, 5)
            back_im = pygame.image.load("project-VAK/img/gui/button_back.png").convert_alpha()
            back_im_s = pygame.image.load("project-VAK/img/gui/button_back_select.png").convert_alpha()
            back_button = Button(30, 130, back_im, 4, back_im_s)
            if back_button.draw(screen):
                make_action = 3
            Solstice2.update()
            Solstice2.draw(screen, 480, 70)
            draw_text("Solstice", font_3, (255,255,255), 32 , 790)

            star_galx1_im = pygame.image.load(f"project-VAK/img/gui/stars/{stars_on_planets_gal4[1]}.png").convert_alpha()
            star_galx1_im = pygame.transform.scale(star_galx1_im, (int(star_galx1_im.get_width() * 5), int(star_galx1_im.get_height() * 5)))
            screen.blit(star_galx1_im, (1030 , 585))

            button_right_im = pygame.image.load("project-VAK/img/gui/button_right.png").convert_alpha()
            button_right_im_press = pygame.image.load("project-VAK/img/gui/button_right_press.png").convert_alpha()
            button_right = Button(1450, 400, button_right_im, 8, button_right_im, button_right_im_press)

            if button_right.draw(screen):
                make_action = 2

            button_left_im = pygame.image.load("project-VAK/img/gui/button_left.png").convert_alpha()
            button_left_im_press = pygame.image.load("project-VAK/img/gui/button_left_press.png").convert_alpha()
            button_left = Button(20, 400, button_left_im, 8, button_left_im, button_left_im_press)
            
            if button_left.draw(screen):
                make_action = 1

            start_im = pygame.image.load("project-VAK/img/gui/button_start.png").convert_alpha()
            start_im_s = pygame.image.load("project-VAK/img/gui/button_start_select.png").convert_alpha()
            
            start_button = Button(590, 770, start_im, 8, start_im_s, start_im, "project-VAK/img/sfx/main_menu/start_game.mp3")
            
            if start_button.draw(screen):
                page = 2
                planet_which_you_ch = 17

            mouse_pos = pygame.mouse.get_pos()   
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        run = False
                if event.type == pygame.MOUSEBUTTONUP:
                    if make_action == 3:
                        page = 1
                    if make_action == 2:
                        make_action = 0
                        page = 42
                    if make_action == 1:
                        make_action = 0
                        page = 40
        if page == 42:
            color_menu()

            galaxy_4_for_ui.update()
            galaxy_4_for_ui.draw(screen, 10, 5)
            back_im = pygame.image.load("project-VAK/img/gui/button_back.png").convert_alpha()
            back_im_s = pygame.image.load("project-VAK/img/gui/button_back_select.png").convert_alpha()
            back_button = Button(30, 130, back_im, 4, back_im_s)
            if back_button.draw(screen):
                make_action = 3
            Scepter3.update()
            Scepter3.draw(screen, 480, 70)
            draw_text("Scepter", font_3, (255,255,255), 32 , 790)

            star_galx1_im = pygame.image.load(f"project-VAK/img/gui/stars/{stars_on_planets_gal4[2]}.png").convert_alpha()
            star_galx1_im = pygame.transform.scale(star_galx1_im, (int(star_galx1_im.get_width() * 5), int(star_galx1_im.get_height() * 5)))
            screen.blit(star_galx1_im, (1030 , 585))

            button_right_im = pygame.image.load("project-VAK/img/gui/button_right.png").convert_alpha()
            button_right_im_press = pygame.image.load("project-VAK/img/gui/button_right_press.png").convert_alpha()
            button_right = Button(1450, 400, button_right_im, 8, button_right_im, button_right_im_press)

            if button_right.draw(screen):
                make_action = 2

            button_left_im = pygame.image.load("project-VAK/img/gui/button_left.png").convert_alpha()
            button_left_im_press = pygame.image.load("project-VAK/img/gui/button_left_press.png").convert_alpha()
            button_left = Button(20, 400, button_left_im, 8, button_left_im, button_left_im_press)
            
            if button_left.draw(screen):
                make_action = 1

            start_im = pygame.image.load("project-VAK/img/gui/button_start.png").convert_alpha()
            start_im_s = pygame.image.load("project-VAK/img/gui/button_start_select.png").convert_alpha()
            
            start_button = Button(590, 770, start_im, 8, start_im_s, start_im, "project-VAK/img/sfx/main_menu/start_game.mp3")
            
            if start_button.draw(screen):
                page = 2
                planet_which_you_ch = 18

            mouse_pos = pygame.mouse.get_pos()   
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        run = False
                if event.type == pygame.MOUSEBUTTONUP:
                    if make_action == 3:
                        page = 1
                    if make_action == 2:
                        make_action = 0
                        page = 43
                    if make_action == 1:
                        make_action = 0
                        page = 41
        if page == 43:
            color_menu()

            galaxy_4_for_ui.update()
            galaxy_4_for_ui.draw(screen, 10, 5)
            back_im = pygame.image.load("project-VAK/img/gui/button_back.png").convert_alpha()
            back_im_s = pygame.image.load("project-VAK/img/gui/button_back_select.png").convert_alpha()
            back_button = Button(30, 130, back_im, 4, back_im_s)
            if back_button.draw(screen):
                make_action = 3
            Prisma4.update()
            Prisma4.draw(screen, 480, 70)
            draw_text("Prisma", font_3, (255,255,255), 32 , 790)

            star_galx1_im = pygame.image.load(f"project-VAK/img/gui/stars/{stars_on_planets_gal4[3]}.png").convert_alpha()
            star_galx1_im = pygame.transform.scale(star_galx1_im, (int(star_galx1_im.get_width() * 5), int(star_galx1_im.get_height() * 5)))
            screen.blit(star_galx1_im, (1030 , 585))

            button_right_im = pygame.image.load("project-VAK/img/gui/button_right.png").convert_alpha()
            button_right_im_press = pygame.image.load("project-VAK/img/gui/button_right_press.png").convert_alpha()
            button_right = Button(1450, 400, button_right_im, 8, button_right_im, button_right_im_press)

            if button_right.draw(screen):
                make_action = 2

            button_left_im = pygame.image.load("project-VAK/img/gui/button_left.png").convert_alpha()
            button_left_im_press = pygame.image.load("project-VAK/img/gui/button_left_press.png").convert_alpha()
            button_left = Button(20, 400, button_left_im, 8, button_left_im, button_left_im_press)
            
            if button_left.draw(screen):
                make_action = 1

            start_im = pygame.image.load("project-VAK/img/gui/button_start.png").convert_alpha()
            start_im_s = pygame.image.load("project-VAK/img/gui/button_start_select.png").convert_alpha()
            
            start_button = Button(590, 770, start_im, 8, start_im_s, start_im, "project-VAK/img/sfx/main_menu/start_game.mp3")
            
            if start_button.draw(screen):
                page = 2
                planet_which_you_ch = 19

            mouse_pos = pygame.mouse.get_pos()   
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        run = False
                if event.type == pygame.MOUSEBUTTONUP:
                    if make_action == 3:
                        page = 1
                    if make_action == 2:
                        make_action = 0
                        page = 44
                    if make_action == 1:
                        make_action = 0
                        page = 42
        if page == 44:
            color_menu()

            galaxy_4_for_ui.update()
            galaxy_4_for_ui.draw(screen, 10, 5)
            back_im = pygame.image.load("project-VAK/img/gui/button_back.png").convert_alpha()
            back_im_s = pygame.image.load("project-VAK/img/gui/button_back_select.png").convert_alpha()
            back_button = Button(30, 130, back_im, 4, back_im_s)
            if back_button.draw(screen):
                make_action = 3
            Fantasia5.update()
            Fantasia5.draw(screen, 480, 70)
            draw_text("Fantasia", font_3, (255,255,255), 32 , 790)

            star_galx1_im = pygame.image.load(f"project-VAK/img/gui/stars/{stars_on_planets_gal4[4]}.png").convert_alpha()
            star_galx1_im = pygame.transform.scale(star_galx1_im, (int(star_galx1_im.get_width() * 5), int(star_galx1_im.get_height() * 5)))
            screen.blit(star_galx1_im, (1030 , 585))

            button_right_im = pygame.image.load("project-VAK/img/gui/button_right.png").convert_alpha()
            button_right_im_press = pygame.image.load("project-VAK/img/gui/button_right_press.png").convert_alpha()
            button_right = Button(1450, 400, button_right_im, 8, button_right_im, button_right_im_press)

            if button_right.draw(screen):
                make_action = 2

            button_left_im = pygame.image.load("project-VAK/img/gui/button_left.png").convert_alpha()
            button_left_im_press = pygame.image.load("project-VAK/img/gui/button_left_press.png").convert_alpha()
            button_left = Button(20, 400, button_left_im, 8, button_left_im, button_left_im_press)
            
            if button_left.draw(screen):
                make_action = 1

            start_im = pygame.image.load("project-VAK/img/gui/button_start.png").convert_alpha()
            start_im_s = pygame.image.load("project-VAK/img/gui/button_start_select.png").convert_alpha()
            
            start_button = Button(590, 770, start_im, 8, start_im_s, start_im, "project-VAK/img/sfx/main_menu/start_game.mp3")
            
            if start_button.draw(screen):
                page = 2
                planet_which_you_ch = 20

            mouse_pos = pygame.mouse.get_pos()   
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        run = False
                if event.type == pygame.MOUSEBUTTONUP:
                    if make_action == 3:
                        page = 1
                    if make_action == 2:
                        make_action = 0
                        page = 40
                    if make_action == 1:
                        make_action = 0
                        page = 43

        if page == 50:
            color_menu()

            galaxy_5_for_ui.update()
            galaxy_5_for_ui.draw(screen, 10, 5)
            back_im = pygame.image.load("project-VAK/img/gui/button_back.png").convert_alpha()
            back_im_s = pygame.image.load("project-VAK/img/gui/button_back_select.png").convert_alpha()
            back_button = Button(30, 130, back_im, 4, back_im_s)
            if back_button.draw(screen):
                make_action = 3
            New_Earth1.update()
            New_Earth1.draw(screen, 480, 70)
            draw_text("New Earth", font_3, (255,255,255), 32 , 790)

            star_galx1_im = pygame.image.load(f"project-VAK/img/gui/stars/{stars_on_planets_gal5[0]}.png").convert_alpha()
            star_galx1_im = pygame.transform.scale(star_galx1_im, (int(star_galx1_im.get_width() * 5), int(star_galx1_im.get_height() * 5)))
            screen.blit(star_galx1_im, (1030 , 585))

            button_right_im = pygame.image.load("project-VAK/img/gui/button_right.png").convert_alpha()
            button_right_im_press = pygame.image.load("project-VAK/img/gui/button_right_press.png").convert_alpha()
            button_right = Button(1450, 400, button_right_im, 8, button_right_im, button_right_im_press)

            if button_right.draw(screen):
                make_action = 2

            button_left_im = pygame.image.load("project-VAK/img/gui/button_left.png").convert_alpha()
            button_left_im_press = pygame.image.load("project-VAK/img/gui/button_left_press.png").convert_alpha()
            button_left = Button(20, 400, button_left_im, 8, button_left_im, button_left_im_press)
            
            if button_left.draw(screen):
                make_action = 1

            start_im = pygame.image.load("project-VAK/img/gui/button_start.png").convert_alpha()
            start_im_s = pygame.image.load("project-VAK/img/gui/button_start_select.png").convert_alpha()
            
            start_button = Button(590, 770, start_im, 8, start_im_s, start_im, "project-VAK/img/sfx/main_menu/start_game.mp3")
            
            if start_button.draw(screen):
                page = 2
                planet_which_you_ch = 21

            mouse_pos = pygame.mouse.get_pos()   
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        run = False
                if event.type == pygame.MOUSEBUTTONUP:
                    if make_action == 3:
                        page = 1
                    if make_action == 2:
                        make_action = 0
                        page = 51
                    if make_action == 1:
                        make_action = 0
                        page = 53

        if page == 51:
            color_menu()

            galaxy_5_for_ui.update()
            galaxy_5_for_ui.draw(screen, 10, 5)
            back_im = pygame.image.load("project-VAK/img/gui/button_back.png").convert_alpha()
            back_im_s = pygame.image.load("project-VAK/img/gui/button_back_select.png").convert_alpha()
            back_button = Button(30, 130, back_im, 4, back_im_s)
            if back_button.draw(screen):
                make_action = 3
            Horizon2.update()
            Horizon2.draw(screen, 480, 70)
            draw_text("Horizon", font_3, (255,255,255), 32 , 790)

            star_galx1_im = pygame.image.load(f"project-VAK/img/gui/stars/{stars_on_planets_gal5[1]}.png").convert_alpha()
            star_galx1_im = pygame.transform.scale(star_galx1_im, (int(star_galx1_im.get_width() * 5), int(star_galx1_im.get_height() * 5)))
            screen.blit(star_galx1_im, (1030 , 585))

            button_right_im = pygame.image.load("project-VAK/img/gui/button_right.png").convert_alpha()
            button_right_im_press = pygame.image.load("project-VAK/img/gui/button_right_press.png").convert_alpha()
            button_right = Button(1450, 400, button_right_im, 8, button_right_im, button_right_im_press)

            if button_right.draw(screen):
                make_action = 2

            button_left_im = pygame.image.load("project-VAK/img/gui/button_left.png").convert_alpha()
            button_left_im_press = pygame.image.load("project-VAK/img/gui/button_left_press.png").convert_alpha()
            button_left = Button(20, 400, button_left_im, 8, button_left_im, button_left_im_press)
            
            if button_left.draw(screen):
                make_action = 1

            start_im = pygame.image.load("project-VAK/img/gui/button_start.png").convert_alpha()
            start_im_s = pygame.image.load("project-VAK/img/gui/button_start_select.png").convert_alpha()
            
            start_button = Button(590, 770, start_im, 8, start_im_s, start_im, "project-VAK/img/sfx/main_menu/start_game.mp3")
            
            if start_button.draw(screen):
                page = 2
                planet_which_you_ch = 22

            mouse_pos = pygame.mouse.get_pos()   
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        run = False
                if event.type == pygame.MOUSEBUTTONUP:
                    if make_action == 3:
                        page = 1
                    if make_action == 2:
                        make_action = 0
                        page = 52
                    if make_action == 1:
                        make_action = 0
                        page = 50
        if page == 52:
            color_menu()

            galaxy_5_for_ui.update()
            galaxy_5_for_ui.draw(screen, 10, 5)
            back_im = pygame.image.load("project-VAK/img/gui/button_back.png").convert_alpha()
            back_im_s = pygame.image.load("project-VAK/img/gui/button_back_select.png").convert_alpha()
            back_button = Button(30, 130, back_im, 4, back_im_s)
            if back_button.draw(screen):
                make_action = 3
            Valhalla3.update()
            Valhalla3.draw(screen, 480, 70)
            draw_text("Valhalla", font_3, (255,255,255), 32 , 790)

            star_galx1_im = pygame.image.load(f"project-VAK/img/gui/stars/{stars_on_planets_gal5[2]}.png").convert_alpha()
            star_galx1_im = pygame.transform.scale(star_galx1_im, (int(star_galx1_im.get_width() * 5), int(star_galx1_im.get_height() * 5)))
            screen.blit(star_galx1_im, (1030 , 585))

            button_right_im = pygame.image.load("project-VAK/img/gui/button_right.png").convert_alpha()
            button_right_im_press = pygame.image.load("project-VAK/img/gui/button_right_press.png").convert_alpha()
            button_right = Button(1450, 400, button_right_im, 8, button_right_im, button_right_im_press)

            if button_right.draw(screen):
                make_action = 2

            button_left_im = pygame.image.load("project-VAK/img/gui/button_left.png").convert_alpha()
            button_left_im_press = pygame.image.load("project-VAK/img/gui/button_left_press.png").convert_alpha()
            button_left = Button(20, 400, button_left_im, 8, button_left_im, button_left_im_press)
            
            if button_left.draw(screen):
                make_action = 1

            start_im = pygame.image.load("project-VAK/img/gui/button_start.png").convert_alpha()
            start_im_s = pygame.image.load("project-VAK/img/gui/button_start_select.png").convert_alpha()
            
            start_button = Button(590, 770, start_im, 8, start_im_s, start_im, "project-VAK/img/sfx/main_menu/start_game.mp3")
            
            if start_button.draw(screen):
                page = 2
                planet_which_you_ch = 23

            mouse_pos = pygame.mouse.get_pos()   
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        run = False
                if event.type == pygame.MOUSEBUTTONUP:
                    if make_action == 3:
                        page = 1
                    if make_action == 2:
                        make_action = 0
                        page = 53
                    if make_action == 1:
                        make_action = 0
                        page = 51

        if page == 53:
            color_menu()

            galaxy_5_for_ui.update()
            galaxy_5_for_ui.draw(screen, 10, 5)
            back_im = pygame.image.load("project-VAK/img/gui/button_back.png").convert_alpha()
            back_im_s = pygame.image.load("project-VAK/img/gui/button_back_select.png").convert_alpha()
            back_button = Button(30, 130, back_im, 4, back_im_s)
            if back_button.draw(screen):
                make_action = 3
            Radiance4.update()
            Radiance4.draw(screen, 170, -170)
            draw_text("Radiance", font_3, (255,255,255), 32 , 790)

            star_galx1_im = pygame.image.load(f"project-VAK/img/gui/stars/{stars_on_planets_gal5[3]}.png").convert_alpha()
            star_galx1_im = pygame.transform.scale(star_galx1_im, (int(star_galx1_im.get_width() * 5), int(star_galx1_im.get_height() * 5)))
            screen.blit(star_galx1_im, (1030 , 585))

            button_right_im = pygame.image.load("project-VAK/img/gui/button_right.png").convert_alpha()
            button_right_im_press = pygame.image.load("project-VAK/img/gui/button_right_press.png").convert_alpha()
            button_right = Button(1450, 400, button_right_im, 8, button_right_im, button_right_im_press)

            if button_right.draw(screen):
                make_action = 2

            button_left_im = pygame.image.load("project-VAK/img/gui/button_left.png").convert_alpha()
            button_left_im_press = pygame.image.load("project-VAK/img/gui/button_left_press.png").convert_alpha()
            button_left = Button(20, 400, button_left_im, 8, button_left_im, button_left_im_press)
            
            if button_left.draw(screen):
                make_action = 1

            start_im = pygame.image.load("project-VAK/img/gui/button_start.png").convert_alpha()
            start_im_s = pygame.image.load("project-VAK/img/gui/button_start_select.png").convert_alpha()
            
            start_button = Button(590, 770, start_im, 8, start_im_s, start_im, "project-VAK/img/sfx/main_menu/start_game.mp3")
            
            if start_button.draw(screen):
                page = 2
                planet_which_you_ch = 24

            mouse_pos = pygame.mouse.get_pos()   
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        run = False
                if event.type == pygame.MOUSEBUTTONUP:
                    if make_action == 3:
                        page = 1
                    if make_action == 2:
                        make_action = 0
                        page = 50
                    if make_action == 1:
                        make_action = 0
                        page = 52

        if page == 60:
            color_menu()

            galaxy_6_for_ui.update()
            galaxy_6_for_ui.draw(screen, 10, 5)
            back_im = pygame.image.load("project-VAK/img/gui/button_back.png").convert_alpha()
            back_im_s = pygame.image.load("project-VAK/img/gui/button_back_select.png").convert_alpha()
            back_button = Button(30, 130, back_im, 4, back_im_s)
            if back_button.draw(screen):
                make_action = 3
            PlanetV.update()
            PlanetV.draw(screen, 280, -120)
            draw_text("Planet V", font_3, (255,255,255), 32 , 790)

            star_galx1_im = pygame.image.load(f"project-VAK/img/gui/stars/{stars_on_planets_gal6[0]}.png").convert_alpha()
            star_galx1_im = pygame.transform.scale(star_galx1_im, (int(star_galx1_im.get_width() * 5), int(star_galx1_im.get_height() * 5)))
            screen.blit(star_galx1_im, (1030 , 585))

            start_im = pygame.image.load("project-VAK/img/gui/button_start.png").convert_alpha()
            start_im_s = pygame.image.load("project-VAK/img/gui/button_start_select.png").convert_alpha()
            
            start_button = Button(590, 770, start_im, 8, start_im_s, start_im, "project-VAK/img/sfx/main_menu/start_game.mp3")
            
            if start_button.draw(screen):
                page = 2
                planet_which_you_ch = 25

            mouse_pos = pygame.mouse.get_pos()   
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        run = False
                if event.type == pygame.MOUSEBUTTONUP:
                    if make_action == 3:
                        page = 1





        if page == 10:
            color_menu()

            galaxy_1_for_ui.update()
            galaxy_1_for_ui.draw(screen, 10, 5)
            back_im = pygame.image.load("project-VAK/img/gui/button_back.png").convert_alpha()
            back_im_s = pygame.image.load("project-VAK/img/gui/button_back_select.png").convert_alpha()
            back_button = Button(30, 130, back_im, 4, back_im_s)
            if back_button.draw(screen):
                make_action = 3
            Nova_prime1.update()
            Nova_prime1.draw(screen, 480, 70)
            draw_text("Nova prime", font_3, (255,255,255), 32 , 790)

            star_galx1_im = pygame.image.load(f"project-VAK/img/gui/stars/{stars_on_planets_gal1[0]}.png").convert_alpha()
            star_galx1_im = pygame.transform.scale(star_galx1_im, (int(star_galx1_im.get_width() * 5), int(star_galx1_im.get_height() * 5)))
            screen.blit(star_galx1_im, (1030 , 585))

            button_right_im = pygame.image.load("project-VAK/img/gui/button_right.png").convert_alpha()
            button_right_im_press = pygame.image.load("project-VAK/img/gui/button_right_press.png").convert_alpha()
            button_right = Button(1450, 400, button_right_im, 8, button_right_im, button_right_im_press)

            if button_right.draw(screen):
                make_action = 2

            button_left_im = pygame.image.load("project-VAK/img/gui/button_left.png").convert_alpha()
            button_left_im_press = pygame.image.load("project-VAK/img/gui/button_left_press.png").convert_alpha()
            button_left = Button(20, 400, button_left_im, 8, button_left_im, button_left_im_press)
            
            if button_left.draw(screen):
                make_action = 1

            start_im = pygame.image.load("project-VAK/img/gui/button_start.png").convert_alpha()
            start_im_s = pygame.image.load("project-VAK/img/gui/button_start_select.png").convert_alpha()
            
            start_button = Button(590, 770, start_im, 8, start_im_s, start_im, "project-VAK/img/sfx/main_menu/start_game.mp3")
            
            if start_button.draw(screen):
                page = 2
                planet_which_you_ch = 1

            mouse_pos = pygame.mouse.get_pos()   
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        run = False
                if event.type == pygame.MOUSEBUTTONUP:
                    if make_action == 3:
                        page = 1
                    if make_action == 2:
                        make_action = 0
                        page = 11
                    if make_action == 1:
                        make_action = 0
                        page = 14



        if page == 20:
            color_menu()

            galaxy_2_for_ui.update()
            galaxy_2_for_ui.draw(screen, 10, 5)
            back_im = pygame.image.load("project-VAK/img/gui/button_back.png").convert_alpha()
            back_im_s = pygame.image.load("project-VAK/img/gui/button_back_select.png").convert_alpha()
            back_button = Button(30, 130, back_im, 4, back_im_s)
            if back_button.draw(screen):
                make_action = 3
            Genesis1.update()
            Genesis1.draw(screen, 480, 70)
            draw_text("Genesis", font_3, (255,255,255), 32 , 790)

            star_galx1_im = pygame.image.load(f"project-VAK/img/gui/stars/{stars_on_planets_gal2[0]}.png").convert_alpha()
            star_galx1_im = pygame.transform.scale(star_galx1_im, (int(star_galx1_im.get_width() * 5), int(star_galx1_im.get_height() * 5)))
            screen.blit(star_galx1_im, (1030 , 585))

            button_right_im = pygame.image.load("project-VAK/img/gui/button_right.png").convert_alpha()
            button_right_im_press = pygame.image.load("project-VAK/img/gui/button_right_press.png").convert_alpha()
            button_right = Button(1450, 400, button_right_im, 8, button_right_im, button_right_im_press)

            if button_right.draw(screen):
                make_action = 2

            button_left_im = pygame.image.load("project-VAK/img/gui/button_left.png").convert_alpha()
            button_left_im_press = pygame.image.load("project-VAK/img/gui/button_left_press.png").convert_alpha()
            button_left = Button(20, 400, button_left_im, 8, button_left_im, button_left_im_press)
            
            if button_left.draw(screen):
                make_action = 1

            start_im = pygame.image.load("project-VAK/img/gui/button_start.png").convert_alpha()
            start_im_s = pygame.image.load("project-VAK/img/gui/button_start_select.png").convert_alpha()
            
            start_button = Button(590, 770, start_im, 8, start_im_s, start_im, "project-VAK/img/sfx/main_menu/start_game.mp3")
            
            if start_button.draw(screen):
                page = 2
                planet_which_you_ch = 6

            mouse_pos = pygame.mouse.get_pos()   
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        run = False
                if event.type == pygame.MOUSEBUTTONUP:
                    if make_action == 3:
                        page = 1
                    if make_action == 2:
                        make_action = 0
                        page = 21
                    if make_action == 1:
                        make_action = 0
                        page = 24

        if page == 21:
            color_menu()

            galaxy_2_for_ui.update()
            galaxy_2_for_ui.draw(screen, 10, 5)
            back_im = pygame.image.load("project-VAK/img/gui/button_back.png").convert_alpha()
            back_im_s = pygame.image.load("project-VAK/img/gui/button_back_select.png").convert_alpha()
            back_button = Button(30, 130, back_im, 4, back_im_s)

            if back_button.draw(screen):
                make_action = 3

            Equinox2.update()
            Equinox2.draw(screen, 480, 70)
            draw_text("Equinox", font_3, (255,255,255), 32 , 790)

            star_galx1_im = pygame.image.load(f"project-VAK/img/gui/stars/{stars_on_planets_gal2[1]}.png").convert_alpha()
            star_galx1_im = pygame.transform.scale(star_galx1_im, (int(star_galx1_im.get_width() * 5), int(star_galx1_im.get_height() * 5)))
            screen.blit(star_galx1_im, (1030 , 585))

            button_right_im = pygame.image.load("project-VAK/img/gui/button_right.png").convert_alpha()
            button_right_im_press = pygame.image.load("project-VAK/img/gui/button_right_press.png").convert_alpha()
            button_right = Button(1450, 400, button_right_im, 8, button_right_im, button_right_im_press)

            if button_right.draw(screen):
                make_action = 2

            button_left_im = pygame.image.load("project-VAK/img/gui/button_left.png").convert_alpha()
            button_left_im_press = pygame.image.load("project-VAK/img/gui/button_left_press.png").convert_alpha()
            button_left = Button(20, 400, button_left_im, 8, button_left_im, button_left_im_press)
            
            if button_left.draw(screen):
                make_action = 1

            start_im = pygame.image.load("project-VAK/img/gui/button_start.png").convert_alpha()
            start_im_s = pygame.image.load("project-VAK/img/gui/button_start_select.png").convert_alpha()
            
            start_button = Button(590, 770, start_im, 8, start_im_s, start_im, "project-VAK/img/sfx/main_menu/start_game.mp3")
            
            if start_button.draw(screen):
                page = 2
                planet_which_you_ch = 7

            mouse_pos = pygame.mouse.get_pos()   
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        run = False
                if event.type == pygame.MOUSEBUTTONUP:
                    if make_action == 3:
                        page = 1
                    if make_action == 2:
                        make_action = 0
                        page = 22
                    if make_action == 1:
                        make_action = 0
                        page = 20

        if page == 22:
            color_menu()

            galaxy_2_for_ui.update()
            galaxy_2_for_ui.draw(screen, 10, 5)
            back_im = pygame.image.load("project-VAK/img/gui/button_back.png").convert_alpha()
            back_im_s = pygame.image.load("project-VAK/img/gui/button_back_select.png").convert_alpha()
            back_button = Button(30, 130, back_im, 4, back_im_s)
            if back_button.draw(screen):
                make_action = 3
            Orpheus3.update()
            Orpheus3.draw(screen, 480, 70)
            draw_text("Orpheus", font_3, (255,255,255), 32 , 790)

            star_galx1_im = pygame.image.load(f"project-VAK/img/gui/stars/{stars_on_planets_gal2[2]}.png").convert_alpha()
            star_galx1_im = pygame.transform.scale(star_galx1_im, (int(star_galx1_im.get_width() * 5), int(star_galx1_im.get_height() * 5)))
            screen.blit(star_galx1_im, (1030 , 585))

            button_right_im = pygame.image.load("project-VAK/img/gui/button_right.png").convert_alpha()
            button_right_im_press = pygame.image.load("project-VAK/img/gui/button_right_press.png").convert_alpha()
            button_right = Button(1450, 400, button_right_im, 8, button_right_im, button_right_im_press)

            if button_right.draw(screen):
                make_action = 2

            button_left_im = pygame.image.load("project-VAK/img/gui/button_left.png").convert_alpha()
            button_left_im_press = pygame.image.load("project-VAK/img/gui/button_left_press.png").convert_alpha()
            button_left = Button(20, 400, button_left_im, 8, button_left_im, button_left_im_press)
            
            if button_left.draw(screen):
                make_action = 1

            start_im = pygame.image.load("project-VAK/img/gui/button_start.png").convert_alpha()
            start_im_s = pygame.image.load("project-VAK/img/gui/button_start_select.png").convert_alpha()
            
            start_button = Button(590, 770, start_im, 8, start_im_s, start_im, "project-VAK/img/sfx/main_menu/start_game.mp3")
            
            if start_button.draw(screen):
                page = 2
                planet_which_you_ch = 8

            mouse_pos = pygame.mouse.get_pos()   
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        run = False
                if event.type == pygame.MOUSEBUTTONUP:
                    if make_action == 3:
                        page = 1
                    if make_action == 2:
                        make_action = 0
                        page = 23
                    if make_action == 1:
                        make_action = 0
                        page = 21

        if page == 23:
            color_menu()

            galaxy_2_for_ui.update()
            galaxy_2_for_ui.draw(screen, 10, 5)
            back_im = pygame.image.load("project-VAK/img/gui/button_back.png").convert_alpha()
            back_im_s = pygame.image.load("project-VAK/img/gui/button_back_select.png").convert_alpha()
            back_button = Button(30, 130, back_im, 4, back_im_s)
            if back_button.draw(screen):
                make_action = 3
            Utopia4.update()
            Utopia4.draw(screen, 480, 70)
            draw_text("Utopia", font_3, (255,255,255), 32 , 790)

            star_galx1_im = pygame.image.load(f"project-VAK/img/gui/stars/{stars_on_planets_gal2[3]}.png").convert_alpha()
            star_galx1_im = pygame.transform.scale(star_galx1_im, (int(star_galx1_im.get_width() * 5), int(star_galx1_im.get_height() * 5)))
            screen.blit(star_galx1_im, (1030 , 585))

            button_right_im = pygame.image.load("project-VAK/img/gui/button_right.png").convert_alpha()
            button_right_im_press = pygame.image.load("project-VAK/img/gui/button_right_press.png").convert_alpha()
            button_right = Button(1450, 400, button_right_im, 8, button_right_im, button_right_im_press)

            if button_right.draw(screen):
                make_action = 2

            button_left_im = pygame.image.load("project-VAK/img/gui/button_left.png").convert_alpha()
            button_left_im_press = pygame.image.load("project-VAK/img/gui/button_left_press.png").convert_alpha()
            button_left = Button(20, 400, button_left_im, 8, button_left_im, button_left_im_press)
            
            if button_left.draw(screen):
                make_action = 1

            start_im = pygame.image.load("project-VAK/img/gui/button_start.png").convert_alpha()
            start_im_s = pygame.image.load("project-VAK/img/gui/button_start_select.png").convert_alpha()
            
            start_button = Button(590, 770, start_im, 8, start_im_s, start_im, "project-VAK/img/sfx/main_menu/start_game.mp3")
            
            if start_button.draw(screen):
                page = 2
                planet_which_you_ch = 9

            mouse_pos = pygame.mouse.get_pos()   
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        run = False
                if event.type == pygame.MOUSEBUTTONUP:
                    if make_action == 3:
                        page = 1
                    if make_action == 2:
                        make_action = 0
                        page = 24
                    if make_action == 1:
                        make_action = 0
                        page = 22

        if page == 24:
            color_menu()

            galaxy_2_for_ui.update()
            galaxy_2_for_ui.draw(screen, 10, 5)
            back_im = pygame.image.load("project-VAK/img/gui/button_back.png").convert_alpha()
            back_im_s = pygame.image.load("project-VAK/img/gui/button_back_select.png").convert_alpha()
            back_button = Button(30, 130, back_im, 4, back_im_s)
            if back_button.draw(screen):
                make_action = 3
            Nexus5.update()
            Nexus5.draw(screen, 480, 70)
            draw_text("Nexus", font_3, (255,255,255), 32 , 790)

            star_galx1_im = pygame.image.load(f"project-VAK/img/gui/stars/{stars_on_planets_gal2[4]}.png").convert_alpha()
            star_galx1_im = pygame.transform.scale(star_galx1_im, (int(star_galx1_im.get_width() * 5), int(star_galx1_im.get_height() * 5)))
            screen.blit(star_galx1_im, (1030 , 585))

            button_right_im = pygame.image.load("project-VAK/img/gui/button_right.png").convert_alpha()
            button_right_im_press = pygame.image.load("project-VAK/img/gui/button_right_press.png").convert_alpha()
            button_right = Button(1450, 400, button_right_im, 8, button_right_im, button_right_im_press)

            if button_right.draw(screen):
                make_action = 2

            button_left_im = pygame.image.load("project-VAK/img/gui/button_left.png").convert_alpha()
            button_left_im_press = pygame.image.load("project-VAK/img/gui/button_left_press.png").convert_alpha()
            button_left = Button(20, 400, button_left_im, 8, button_left_im, button_left_im_press)
            
            if button_left.draw(screen):
                make_action = 1

            start_im = pygame.image.load("project-VAK/img/gui/button_start.png").convert_alpha()
            start_im_s = pygame.image.load("project-VAK/img/gui/button_start_select.png").convert_alpha()
            
            start_button = Button(590, 770, start_im, 8, start_im_s, start_im, "project-VAK/img/sfx/main_menu/start_game.mp3")
            
            if start_button.draw(screen):
                page = 2
                planet_which_you_ch = 10

            mouse_pos = pygame.mouse.get_pos()   
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        run = False
                if event.type == pygame.MOUSEBUTTONUP:
                    if make_action == 3:
                        page = 1
                    if make_action == 2:
                        make_action = 0
                        page = 20
                    if make_action == 1:
                        make_action = 0
                        page = 23



        if page == 10:
            color_menu()

            galaxy_1_for_ui.update()
            galaxy_1_for_ui.draw(screen, 10, 5)
            back_im = pygame.image.load("project-VAK/img/gui/button_back.png").convert_alpha()
            back_im_s = pygame.image.load("project-VAK/img/gui/button_back_select.png").convert_alpha()
            back_button = Button(30, 130, back_im, 4, back_im_s)
            if back_button.draw(screen):
                make_action = 3
            Nova_prime1.update()
            Nova_prime1.draw(screen, 480, 70)
            draw_text("Nova prime", font_3, (255,255,255), 32 , 790)

            star_galx1_im = pygame.image.load(f"project-VAK/img/gui/stars/{stars_on_planets_gal1[0]}.png").convert_alpha()
            star_galx1_im = pygame.transform.scale(star_galx1_im, (int(star_galx1_im.get_width() * 5), int(star_galx1_im.get_height() * 5)))
            screen.blit(star_galx1_im, (1030 , 585))

            button_right_im = pygame.image.load("project-VAK/img/gui/button_right.png").convert_alpha()
            button_right_im_press = pygame.image.load("project-VAK/img/gui/button_right_press.png").convert_alpha()
            button_right = Button(1450, 400, button_right_im, 8, button_right_im, button_right_im_press)

            if button_right.draw(screen):
                make_action = 2

            button_left_im = pygame.image.load("project-VAK/img/gui/button_left.png").convert_alpha()
            button_left_im_press = pygame.image.load("project-VAK/img/gui/button_left_press.png").convert_alpha()
            button_left = Button(20, 400, button_left_im, 8, button_left_im, button_left_im_press)
            
            if button_left.draw(screen):
                make_action = 1

            start_im = pygame.image.load("project-VAK/img/gui/button_start.png").convert_alpha()
            start_im_s = pygame.image.load("project-VAK/img/gui/button_start_select.png").convert_alpha()
            
            start_button = Button(590, 770, start_im, 8, start_im_s, start_im, "project-VAK/img/sfx/main_menu/start_game.mp3")
            
            if start_button.draw(screen):
                page = 2
                planet_which_you_ch = 1

            mouse_pos = pygame.mouse.get_pos()   
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        run = False
                if event.type == pygame.MOUSEBUTTONUP:
                    if make_action == 3:
                        page = 1
                    if make_action == 2:
                        make_action = 0
                        page = 11
                    if make_action == 1:
                        make_action = 0
                        page = 14
        if page == 11:
            color_menu()

            galaxy_1_for_ui.update()
            galaxy_1_for_ui.draw(screen, 10, 5)
            back_im = pygame.image.load("project-VAK/img/gui/button_back.png").convert_alpha()
            back_im_s = pygame.image.load("project-VAK/img/gui/button_back_select.png").convert_alpha()
            back_button = Button(30, 130, back_im, 4, back_im_s)
            if back_button.draw(screen):
                make_action = 3
            Astoria2.update()
            Astoria2.draw(screen, 480, 70)
            draw_text("Astoria", font_3, (255,255,255), 32 , 790)

            star_galx1_im = pygame.image.load(f"project-VAK/img/gui/stars/{stars_on_planets_gal1[1]}.png").convert_alpha()
            star_galx1_im = pygame.transform.scale(star_galx1_im, (int(star_galx1_im.get_width() * 5), int(star_galx1_im.get_height() * 5)))
            screen.blit(star_galx1_im, (1030 , 585))

            button_right_im = pygame.image.load("project-VAK/img/gui/button_right.png").convert_alpha()
            button_right_im_press = pygame.image.load("project-VAK/img/gui/button_right_press.png").convert_alpha()
            button_right = Button(1450, 400, button_right_im, 8, button_right_im, button_right_im_press)

            if button_right.draw(screen):
                make_action = 2

            button_left_im = pygame.image.load("project-VAK/img/gui/button_left.png").convert_alpha()
            button_left_im_press = pygame.image.load("project-VAK/img/gui/button_left_press.png").convert_alpha()
            button_left = Button(20, 400, button_left_im, 8, button_left_im, button_left_im_press)
            
            if button_left.draw(screen):
                make_action = 1

            start_im = pygame.image.load("project-VAK/img/gui/button_start.png").convert_alpha()
            start_im_s = pygame.image.load("project-VAK/img/gui/button_start_select.png").convert_alpha()
            
            start_button = Button(590, 770, start_im, 8, start_im_s, start_im, "project-VAK/img/sfx/main_menu/start_game.mp3")
            
            if start_button.draw(screen):
                page = 2
                planet_which_you_ch = 2

            mouse_pos = pygame.mouse.get_pos()   
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        run = False
                if event.type == pygame.MOUSEBUTTONUP:
                    if make_action == 3:
                        page = 1
                    if make_action == 2:
                        make_action = 0
                        page = 12
                    if make_action == 1:
                        make_action = 0
                        page = 10

        if page == 12:
            color_menu()

            galaxy_1_for_ui.update()
            galaxy_1_for_ui.draw(screen, 10, 5)
            back_im = pygame.image.load("project-VAK/img/gui/button_back.png").convert_alpha()
            back_im_s = pygame.image.load("project-VAK/img/gui/button_back_select.png").convert_alpha()
            back_button = Button(30, 130, back_im, 4, back_im_s)
            if back_button.draw(screen):
                make_action = 3
            Olympus3.update()
            Olympus3.draw(screen, 480, 70)
            draw_text("Olympus", font_3, (255,255,255), 32 , 790)

            star_galx1_im = pygame.image.load(f"project-VAK/img/gui/stars/{stars_on_planets_gal1[2]}.png").convert_alpha()
            star_galx1_im = pygame.transform.scale(star_galx1_im, (int(star_galx1_im.get_width() * 5), int(star_galx1_im.get_height() * 5)))
            screen.blit(star_galx1_im, (1030 , 585))

            button_right_im = pygame.image.load("project-VAK/img/gui/button_right.png").convert_alpha()
            button_right_im_press = pygame.image.load("project-VAK/img/gui/button_right_press.png").convert_alpha()
            button_right = Button(1450, 400, button_right_im, 8, button_right_im, button_right_im_press)

            if button_right.draw(screen):
                make_action = 2

            button_left_im = pygame.image.load("project-VAK/img/gui/button_left.png").convert_alpha()
            button_left_im_press = pygame.image.load("project-VAK/img/gui/button_left_press.png").convert_alpha()
            button_left = Button(20, 400, button_left_im, 8, button_left_im, button_left_im_press)
            
            if button_left.draw(screen):
                make_action = 1

            start_im = pygame.image.load("project-VAK/img/gui/button_start.png").convert_alpha()
            start_im_s = pygame.image.load("project-VAK/img/gui/button_start_select.png").convert_alpha()
            
            start_button = Button(590, 770, start_im, 8, start_im_s, start_im, "project-VAK/img/sfx/main_menu/start_game.mp3")
            
            if start_button.draw(screen):
                page = 2
                planet_which_you_ch = 3

            mouse_pos = pygame.mouse.get_pos()   
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        run = False
                if event.type == pygame.MOUSEBUTTONUP:
                    if make_action == 3:
                        page = 1
                    if make_action == 2:
                        make_action = 0
                        page = 13
                    if make_action == 1:
                        make_action = 0
                        page = 11


        if page == 13:
            color_menu()

            galaxy_1_for_ui.update()
            galaxy_1_for_ui.draw(screen, 10, 5)
            back_im = pygame.image.load("project-VAK/img/gui/button_back.png").convert_alpha()
            back_im_s = pygame.image.load("project-VAK/img/gui/button_back_select.png").convert_alpha()
            back_button = Button(30, 130, back_im, 4, back_im_s)
            if back_button.draw(screen):
                make_action = 3
            Nebulous4.update()
            Nebulous4.draw(screen, 480, 70)
            draw_text("Nebulous", font_3, (255,255,255), 32 , 790)

            star_galx1_im = pygame.image.load(f"project-VAK/img/gui/stars/{stars_on_planets_gal1[3]}.png").convert_alpha()
            star_galx1_im = pygame.transform.scale(star_galx1_im, (int(star_galx1_im.get_width() * 5), int(star_galx1_im.get_height() * 5)))
            screen.blit(star_galx1_im, (1030 , 585))

            button_right_im = pygame.image.load("project-VAK/img/gui/button_right.png").convert_alpha()
            button_right_im_press = pygame.image.load("project-VAK/img/gui/button_right_press.png").convert_alpha()
            button_right = Button(1450, 400, button_right_im, 8, button_right_im, button_right_im_press)

            if button_right.draw(screen):
                make_action = 2

            button_left_im = pygame.image.load("project-VAK/img/gui/button_left.png").convert_alpha()
            button_left_im_press = pygame.image.load("project-VAK/img/gui/button_left_press.png").convert_alpha()
            button_left = Button(20, 400, button_left_im, 8, button_left_im, button_left_im_press)
            
            if button_left.draw(screen):
                make_action = 1

            start_im = pygame.image.load("project-VAK/img/gui/button_start.png").convert_alpha()
            start_im_s = pygame.image.load("project-VAK/img/gui/button_start_select.png").convert_alpha()
            
            start_button = Button(590, 770, start_im, 8, start_im_s, start_im, "project-VAK/img/sfx/main_menu/start_game.mp3")
            
            if start_button.draw(screen):
                page = 2
                planet_which_you_ch = 4

            mouse_pos = pygame.mouse.get_pos()   
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        run = False
                if event.type == pygame.MOUSEBUTTONUP:
                    if make_action == 3:
                        page = 1
                    if make_action == 2:
                        make_action = 0
                        page = 14
                    if make_action == 1:
                        make_action = 0
                        page = 12

        if page == 14:
            color_menu()

            galaxy_1_for_ui.update()
            galaxy_1_for_ui.draw(screen, 10, 5)
            back_im = pygame.image.load("project-VAK/img/gui/button_back.png").convert_alpha()
            back_im_s = pygame.image.load("project-VAK/img/gui/button_back_select.png").convert_alpha()
            back_button = Button(30, 130, back_im, 4, back_im_s)
            if back_button.draw(screen):
                make_action = 3
            Infinity5.update()
            Infinity5.draw(screen, 480, 70)
            draw_text("Infinity", font_3, (255,255,255), 32 , 790)

            star_galx1_im = pygame.image.load(f"project-VAK/img/gui/stars/{stars_on_planets_gal1[4]}.png").convert_alpha()
            star_galx1_im = pygame.transform.scale(star_galx1_im, (int(star_galx1_im.get_width() * 5), int(star_galx1_im.get_height() * 5)))
            screen.blit(star_galx1_im, (1030 , 585))

            button_right_im = pygame.image.load("project-VAK/img/gui/button_right.png").convert_alpha()
            button_right_im_press = pygame.image.load("project-VAK/img/gui/button_right_press.png").convert_alpha()
            button_right = Button(1450, 400, button_right_im, 8, button_right_im, button_right_im_press)

            if button_right.draw(screen):
                make_action = 2

            button_left_im = pygame.image.load("project-VAK/img/gui/button_left.png").convert_alpha()
            button_left_im_press = pygame.image.load("project-VAK/img/gui/button_left_press.png").convert_alpha()
            button_left = Button(20, 400, button_left_im, 8, button_left_im, button_left_im_press)
            
            if button_left.draw(screen):
                make_action = 1

            start_im = pygame.image.load("project-VAK/img/gui/button_start.png").convert_alpha()
            start_im_s = pygame.image.load("project-VAK/img/gui/button_start_select.png").convert_alpha()
            
            start_button = Button(590, 770, start_im, 8, start_im_s, start_im, "project-VAK/img/sfx/main_menu/start_game.mp3")
            
            if start_button.draw(screen):
                page = 2
                planet_which_you_ch = 5

            mouse_pos = pygame.mouse.get_pos()   
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        run = False
                if event.type == pygame.MOUSEBUTTONUP:
                    if make_action == 3:
                        page = 1
                    if make_action == 2:
                        make_action = 0
                        page = 10
                    if make_action == 1:
                        make_action = 0
                        page = 13
                    
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
            for i in range(len(guns_player_have) - 17):
                    if i == 0:
                        if guns_player_have[i] == 2:
                            b1 = Button(14, 110, sml_button_yes, 7, sml_button_yes, sml_button_yes)
                        if guns_player_have[i] == 1:
                            b1 = Button(14, 110, sml_button_empty, 7, sml_button_empty, sml_button_empty)
                        if guns_player_have[i] == 0:
                            b1 = Button(14, 110, sml_button_clossed, 7, sml_button_clossed, sml_button_clossed)
                    if i == 1:
                        if guns_player_have[i] == 2:
                            b2 = Button(164, 110, sml_button_yes, 7, sml_button_yes, sml_button_yes)
                        if guns_player_have[i] == 1:
                            b2 = Button(164, 110, sml_button_empty, 7, sml_button_empty, sml_button_empty)
                        if guns_player_have[i] == 0:
                            b2 = Button(164, 110, sml_button_clossed, 7, sml_button_clossed, sml_button_clossed)
                    if i == 2:
                        if guns_player_have[i] == 2:
                            b3 = Button(334,110, sml_button_yes, 7, sml_button_yes, sml_button_yes)
                        if guns_player_have[i] == 1:
                            b3 = Button(334, 110, sml_button_empty, 7, sml_button_empty, sml_button_empty)
                        if guns_player_have[i] == 0:
                            b3 = Button(334, 110, sml_button_clossed, 7, sml_button_clossed, sml_button_clossed)
                    if i == 3:
                        if guns_player_have[i] == 2:
                            b4 = Button(494, 110, sml_button_yes, 7, sml_button_yes, sml_button_yes)
                        if guns_player_have[i] == 1:
                            b4 = Button(494, 110, sml_button_empty, 7, sml_button_empty, sml_button_empty)
                        if guns_player_have[i] == 0:
                            b4 = Button(494, 110, sml_button_clossed, 7, sml_button_clossed, sml_button_clossed)
                    if i == 4:
                        if guns_player_have[i] == 2:
                            b5 = Button(655, 110, sml_button_yes, 7, sml_button_yes, sml_button_yes)
                        if guns_player_have[i] == 1:
                            b5 = Button(655, 110, sml_button_empty, 7, sml_button_empty, sml_button_empty)
                        if guns_player_have[i] == 0:
                            b5 = Button(655, 110, sml_button_clossed, 7, sml_button_clossed, sml_button_clossed)
                    if i == 5:
                        if guns_player_have[i] == 2:
                            b6 = Button(865, 110, sml_button_yes, 7, sml_button_yes, sml_button_yes)
                        if guns_player_have[i] == 1:
                            b6 = Button(865, 110, sml_button_empty, 7, sml_button_empty, sml_button_empty)
                        if guns_player_have[i] == 0:
                            b6 = Button(865, 110, sml_button_clossed, 7, sml_button_clossed, sml_button_clossed)

                    if i == 6:
                        if guns_player_have[i] == 2:
                            b7 = Button(14, 320, sml_button_yes, 7, sml_button_yes, sml_button_yes)
                        if guns_player_have[i] == 1:
                            b7 = Button(14, 320, sml_button_empty, 7, sml_button_empty, sml_button_empty)
                        if guns_player_have[i] == 0:
                            b7 = Button(14, 320, sml_button_clossed, 7, sml_button_clossed, sml_button_clossed)
                    if i == 7:
                        if guns_player_have[i] == 2:
                            b8 = Button(184, 320, sml_button_yes, 7, sml_button_yes, sml_button_yes)
                        if guns_player_have[i] == 1:
                            b8 = Button(184, 320, sml_button_empty, 7, sml_button_empty, sml_button_empty)
                        if guns_player_have[i] == 0:
                            b8 = Button(184, 320, sml_button_clossed, 7, sml_button_clossed, sml_button_clossed)
                    if i == 8:
                        if guns_player_have[i] == 2:
                            b9 = Button(344, 320, sml_button_yes, 7, sml_button_yes, sml_button_yes)
                        if guns_player_have[i] == 1:
                            b9 = Button(344, 320, sml_button_empty, 7, sml_button_empty, sml_button_empty)
                        if guns_player_have[i] == 0:
                            b9 = Button(344, 320, sml_button_clossed, 7, sml_button_clossed, sml_button_clossed)
                    if i == 9:
                        if guns_player_have[i] == 2:
                            b10 = Button(564, 320, sml_button_yes, 7, sml_button_yes, sml_button_yes)
                        if guns_player_have[i] == 1:
                            b10 = Button(564, 320, sml_button_empty, 7, sml_button_empty, sml_button_empty)
                        if guns_player_have[i] == 0:
                            b10 = Button(564, 320, sml_button_clossed, 7, sml_button_clossed, sml_button_clossed)
                    if i == 10:
                        if guns_player_have[i] == 2:
                            b11 = Button(744, 320, sml_button_yes, 7, sml_button_yes, sml_button_yes)
                        if guns_player_have[i] == 1:
                            b11 = Button(744, 320, sml_button_empty, 7, sml_button_empty, sml_button_empty)
                        if guns_player_have[i] == 0:
                            b11 = Button(744, 320, sml_button_clossed, 7, sml_button_clossed, sml_button_clossed) 
                    if i == 11:
                        if guns_player_have[i] == 2:
                            b12 = Button(914, 320, sml_button_yes, 7, sml_button_yes, sml_button_yes)
                        if guns_player_have[i] == 1:
                            b12 = Button(914, 320, sml_button_empty, 7, sml_button_empty, sml_button_empty)
                        if guns_player_have[i] == 0:
                            b12 = Button(914, 320, sml_button_clossed, 7, sml_button_clossed, sml_button_clossed)    

                    if i == 12:
                        if guns_player_have[i] == 2:
                            b13 = Button(14, 540, sml_button_yes, 7, sml_button_yes, sml_button_yes)
                        if guns_player_have[i] == 1:
                            b13 = Button(14, 540, sml_button_empty, 7, sml_button_empty, sml_button_empty)
                        if guns_player_have[i] == 0:
                            b13 = Button(14, 540, sml_button_clossed, 7, sml_button_clossed, sml_button_clossed)
                    if i == 13:
                        if guns_player_have[i] == 2:
                            b14 = Button(174, 540, sml_button_yes, 7, sml_button_yes, sml_button_yes)
                        if guns_player_have[i] == 1:
                            b14 = Button(174, 540, sml_button_empty, 7, sml_button_empty, sml_button_empty)
                        if guns_player_have[i] == 0:
                            b14 = Button(174, 540, sml_button_clossed, 7, sml_button_clossed, sml_button_clossed)
                    if i == 14:
                        if guns_player_have[i] == 2:
                            b15 = Button(344, 540, sml_button_yes, 7, sml_button_yes, sml_button_yes)
                        if guns_player_have[i] == 1:
                            b15 = Button(344, 540, sml_button_empty, 7, sml_button_empty, sml_button_empty)
                        if guns_player_have[i] == 0:
                            b15 = Button(344, 540, sml_button_clossed, 7, sml_button_clossed, sml_button_clossed)
                    if i == 15:
                        if guns_player_have[i] == 2:
                            b16= Button(534, 540, sml_button_yes, 7, sml_button_yes, sml_button_yes)
                        if guns_player_have[i] == 1:
                            b16 = Button(534, 540, sml_button_empty, 7, sml_button_empty, sml_button_empty)
                        if guns_player_have[i] == 0:
                            b16 = Button(534, 540, sml_button_clossed, 7, sml_button_clossed, sml_button_clossed)
                    if i == 16:
                        if guns_player_have[i] == 2:
                            b17 = Button(684, 540, sml_button_yes, 7, sml_button_yes, sml_button_yes)
                        if guns_player_have[i] == 1:
                            b17 = Button(684, 540, sml_button_empty, 7, sml_button_empty, sml_button_empty)
                        if guns_player_have[i] == 0:
                            b17 = Button(684, 540, sml_button_clossed, 7, sml_button_clossed, sml_button_clossed)
                    if i == 17:
                        if guns_player_have[i] == 2:
                            b18 = Button(884, 540, sml_button_yes, 7, sml_button_yes, sml_button_yes)
                        if guns_player_have[i] == 1:
                            b18 = Button(884, 540, sml_button_empty, 7, sml_button_empty, sml_button_empty)
                        if guns_player_have[i] == 0:
                            b18 = Button(884, 540, sml_button_clossed, 7, sml_button_clossed, sml_button_clossed)

                    if i == 18:
                        if guns_player_have[i] == 2:
                            b19 = Button(10, 740, sml_button_yes, 7, sml_button_yes, sml_button_yes)
                        if guns_player_have[i] == 1:
                            b19 = Button(10, 740, sml_button_empty, 7, sml_button_empty, sml_button_empty)
                        if guns_player_have[i] == 0:
                            b19 = Button(10, 740, sml_button_clossed, 7, sml_button_clossed, sml_button_clossed)
                    if i == 19:
                        if guns_player_have[i] == 2:
                            b20 = Button(170, 740, sml_button_yes, 7, sml_button_yes, sml_button_yes)
                        if guns_player_have[i] == 1:
                            b20 = Button(170, 740, sml_button_empty, 7, sml_button_empty, sml_button_empty)
                        if guns_player_have[i] == 0:
                            b20 = Button(170, 740, sml_button_clossed, 7, sml_button_clossed, sml_button_clossed)
                    if i == 20:
                        if guns_player_have[i] == 2:
                            b21 = Button(344, 740, sml_button_yes, 7, sml_button_yes, sml_button_yes)
                        if guns_player_have[i] == 1:
                            b21 = Button(344, 740, sml_button_empty, 7, sml_button_empty, sml_button_empty)
                        if guns_player_have[i] == 0:
                            b21 = Button(344, 740, sml_button_clossed, 7, sml_button_clossed, sml_button_clossed)
                    if i == 21:
                        if guns_player_have[i] == 2:
                            b22 = Button(514, 740, sml_button_yes, 7, sml_button_yes, sml_button_yes)
                        if guns_player_have[i] == 1:
                            b22 = Button(514, 740, sml_button_empty, 7, sml_button_empty, sml_button_empty)
                        if guns_player_have[i] == 0:
                            b22 = Button(514, 740, sml_button_clossed, 7, sml_button_clossed, sml_button_clossed)
                    if i == 22:
                        if guns_player_have[i] == 2:
                            b23 = Button(684, 740, sml_button_yes, 7, sml_button_yes, sml_button_yes)
                        if guns_player_have[i] == 1:
                            b23 = Button(684, 740, sml_button_empty, 7, sml_button_empty, sml_button_empty)
                        if guns_player_have[i] == 0:
                            b23 = Button(684, 740, sml_button_clossed, 7, sml_button_clossed, sml_button_clossed)
                    if i == 23:
                        if guns_player_have[i] == 2:
                            b24 = Button(864, 740, sml_button_yes, 7, sml_button_yes, sml_button_yes)
                        if guns_player_have[i] == 1:
                            b24 = Button(864, 740, sml_button_empty, 7, sml_button_empty, sml_button_empty)
                        if guns_player_have[i] == 0:
                            b24 = Button(864, 740, sml_button_clossed, 7, sml_button_clossed, sml_button_clossed)
            if b1.draw(screen):
                if guns_player_have[0] == 0:
                    page = 3
                    gun_which = 1
                if guns_player_have[0] == 1 or guns_player_have[0] == 2:
                    guns_player_have[guns_player_have.index(2)] = 1
                    guns_player_have[0] = 2
                    page = 3
                    gun_which = 1
            if b2.draw(screen):
                if guns_player_have[1] == 0:
                    page = 3
                    gun_which = 2
                if guns_player_have[1] == 1 or guns_player_have[1] == 2:
                    guns_player_have[guns_player_have.index(2)] = 1
                    guns_player_have[1] = 2
                    page = 3
                    gun_which = 2
            if b3.draw(screen):
                if guns_player_have[2] == 0 :
                    page = 3
                    gun_which = 3
                if guns_player_have[2] == 1 or guns_player_have[2] == 2:
                    guns_player_have[guns_player_have.index(2)] = 1
                    guns_player_have[2] = 2
                    page = 3
                    gun_which = 3
            if b4.draw(screen):
                if guns_player_have[3] == 0 or guns_player_have[3] == 2:
                    page = 3
                    gun_which = 4
                if guns_player_have[3] == 1:
                    guns_player_have[guns_player_have.index(2)] = 1
                    guns_player_have[3] = 2
                    page = 3
                    gun_which = 4
            if b5.draw(screen):
                if guns_player_have[4] == 0:
                    page = 3
                    gun_which = 5
                if guns_player_have[4] == 1 or guns_player_have[4] == 2:
                    guns_player_have[guns_player_have.index(2)] = 1
                    guns_player_have[4] = 2
                    page = 3
                    gun_which = 5
            if b6.draw(screen):
                if guns_player_have[5] == 0:
                    page = 3
                    gun_which = 6
                if guns_player_have[5] == 1 or guns_player_have[4] == 2:
                    guns_player_have[guns_player_have.index(2)] = 1
                    guns_player_have[5] = 2
                    page = 3
                    gun_which = 6

            if b7.draw(screen):
                if guns_player_have[6] == 0:
                    page = 3
                    gun_which = 7
                if guns_player_have[6] == 1 or guns_player_have[6] == 2:
                    guns_player_have[guns_player_have.index(2)] = 1
                    guns_player_have[6] = 2
                    page = 3
                    gun_which = 7 
            if b8.draw(screen):
                if guns_player_have[7] == 0:
                    page = 3
                    gun_which = 8
                if guns_player_have[7] == 1:
                    guns_player_have[guns_player_have.index(2)] = 1
                    guns_player_have[7] = 2
                    page = 3
                    gun_which = 8
            if b9.draw(screen):
                if guns_player_have[8] == 0:
                    page = 3
                    gun_which = 9
                if guns_player_have[8] == 1 or guns_player_have[8] == 2:
                    guns_player_have[guns_player_have.index(2)] = 1
                    guns_player_have[8] = 2
                    page = 3
                    gun_which = 9
            if b10.draw(screen):
                if guns_player_have[9] == 0:
                    page = 3
                    gun_which = 10
                if guns_player_have[9] == 1 or guns_player_have[8] == 2:
                    guns_player_have[guns_player_have.index(2)] = 1
                    guns_player_have[9] = 2
                    page = 3
                    gun_which = 10
            if b11.draw(screen):
                if guns_player_have[10] == 0:
                    page = 3
                    gun_which = 11
                if guns_player_have[10] == 1 or guns_player_have[10] == 2:
                    guns_player_have[guns_player_have.index(2)] = 1
                    guns_player_have[10] = 2
                    page = 3
                    gun_which = 11
            if b12.draw(screen):
                if guns_player_have[11] == 0:
                    page = 3
                    gun_which = 12
                if guns_player_have[11] == 1 or guns_player_have[11] == 2:
                    guns_player_have[guns_player_have.index(2)] = 1
                    guns_player_have[11] = 2
                    page = 3
                    gun_which = 12
            if b13.draw(screen):
                if guns_player_have[12] == 0 :
                    page = 3
                    gun_which = 13
                if guns_player_have[12] == 1 or guns_player_have[12] == 2:
                    guns_player_have[guns_player_have.index(2)] = 1
                    guns_player_have[12] = 2
                    page = 3
                    gun_which = 13
            if b14.draw(screen):
                if guns_player_have[13] == 0:
                    page = 3
                    gun_which = 14
                if guns_player_have[13] == 1 or guns_player_have[13] == 2:
                    guns_player_have[guns_player_have.index(2)] = 1
                    guns_player_have[13] = 2
                    page = 3
                    gun_which = 14
            if b15.draw(screen):
                if guns_player_have[14] == 0:
                    page = 3
                    gun_which = 15
                if guns_player_have[14] == 1 or guns_player_have[14] == 2:
                    guns_player_have[guns_player_have.index(2)] = 1
                    guns_player_have[14] = 2
                    page = 3
                    gun_which = 15
            if b16.draw(screen):
                if guns_player_have[15] == 0:
                    page = 3
                    gun_which = 16
                if guns_player_have[15] == 1 or guns_player_have[15] == 2:
                    guns_player_have[guns_player_have.index(2)] = 1
                    guns_player_have[15] = 2
                    page = 3
                    gun_which = 16
            if b17.draw(screen):
                if guns_player_have[16] == 0 :
                    page = 3
                    gun_which = 17
                if guns_player_have[16] == 1 or guns_player_have[16] == 2:
                    guns_player_have[guns_player_have.index(2)] = 1
                    guns_player_have[16] = 2
                    page = 3
                    gun_which = 17
            if b18.draw(screen):
                if guns_player_have[17] == 0:
                    page = 3
                    gun_which = 18
                if guns_player_have[17] == 1 or guns_player_have[17] == 2:
                    guns_player_have[guns_player_have.index(2)] = 1
                    guns_player_have[17] = 2
                    page = 3
                    gun_which = 18
            if b19.draw(screen):
                if guns_player_have[18] == 0:
                    page = 3
                    gun_which = 19
                if guns_player_have[18] == 1 or guns_player_have[18] == 2:
                    guns_player_have[guns_player_have.index(2)] = 1
                    guns_player_have[18] = 2                    
                    page = 3
                    gun_which = 19
            if b20.draw(screen):
                if guns_player_have[19] == 0 :
                    page = 3
                    gun_which = 20
                if guns_player_have[19] == 1 or guns_player_have[19] == 2:
                    guns_player_have[guns_player_have.index(2)] = 1
                    guns_player_have[19] = 2
                    page = 3
                    gun_which = 20
            if b21.draw(screen):
                if guns_player_have[20] == 0:
                    page = 3
                    gun_which = 21
                if guns_player_have[20] == 1 or guns_player_have[20] == 2:
                    guns_player_have[guns_player_have.index(2)] = 1
                    guns_player_have[20] = 2
                    page = 3
                    gun_which = 21
            if b22.draw(screen):
                if guns_player_have[21] == 0:
                    page = 3
                    gun_which = 22
                if guns_player_have[21] == 1 or guns_player_have[21] == 2:
                    guns_player_have[guns_player_have.index(2)] = 1
                    guns_player_have[21] = 2
                    page = 3
                    gun_which = 22
            if b23.draw(screen):
                if guns_player_have[22] == 0 :
                    page = 3
                    gun_which = 23
                if guns_player_have[22] == 1 or guns_player_have[22] == 2:
                    guns_player_have[guns_player_have.index(2)] = 1
                    guns_player_have[22] = 2
                    page = 3
                    gun_which = 23
            if b24.draw(screen):
                if guns_player_have[23] == 0 :
                    page = 3
                    gun_which = 24
                if guns_player_have[23] == 1 or guns_player_have[23] == 2:
                    guns_player_have[guns_player_have.index(2)] = 1
                    guns_player_have[23] = 2
                    page = 3
                    gun_which = 24

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
            

            draw_text("---------------------------------------------------------------------------------", font_4, (255,255,255), 0, 800)

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
                draw_text("---------------------------------------------------------------------------------", font_4, (255,205,205), 0, 802)
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
                draw_text("---------------------------------------------------------------------------------", font_4, (255,205,205), 0, 802)
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
                draw_text("---------------------------------------------------------------------------------", font_4, (255,205,205), 0, 802)
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
                draw_text("---------------------------------------------------------------------------------", font_4, (255,205,205), 0, 802)
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
                draw_text("---------------------------------------------------------------------------------", font_4, (255,205,205), 0, 802)
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
                draw_text("---------------------------------------------------------------------------------", font_4, (255,205,205), 0, 802)
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
                draw_text("---------------------------------------------------------------------------------", font_4, (60,205,60), 0, 802)
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
                draw_text("---------------------------------------------------------------------------------", font_4, (60,205,60), 0, 802)
                draw_text("- 10 charges", font_3, (255,255,255), 450, 350)
                draw_text("- lazer", font_3, (255,255,255), 450, 400)
                draw_text("- 20 damage", font_3, (255,255,255), 450, 450)
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
                draw_text("---------------------------------------------------------------------------------", font_4, (60,205,60), 0, 802)
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
                draw_text("---------------------------------------------------------------------------------", font_4, (60,205,60), 0, 802)
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
                draw_text("---------------------------------------------------------------------------------", font_4, (60,205,60), 0, 802)
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
                draw_text("---------------------------------------------------------------------------------", font_4, (60,205,60), 0, 802)
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
                draw_text("---------------------------------------------------------------------------------", font_4, (255,255,10), 0, 802)
                draw_text("- 5 charges", font_3, (255,255,255), 450, 350)
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
                draw_text("---------------------------------------------------------------------------------", font_4, (255,255,10), 0, 802)
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
                draw_text("---------------------------------------------------------------------------------", font_4, (255,255,10), 0, 802)
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
                draw_text("---------------------------------------------------------------------------------", font_4, (255,255,10), 0, 802)
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
                draw_text("---------------------------------------------------------------------------------", font_4, (255,255,10), 0, 802)
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
                draw_text("---------------------------------------------------------------------------------", font_4, (255,255,10), 0, 802)
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
                draw_text("---------------------------------------------------------------------------------", font_4, (255,55,200), 0, 802)
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
                draw_text("---------------------------------------------------------------------------------", font_4, (255,55,200), 0, 802)
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
                draw_text("---------------------------------------------------------------------------------", font_4, (255,55,200), 0, 802)
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
                draw_text("---------------------------------------------------------------------------------", font_4, (255,55,200), 0, 802)
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
                draw_text("---------------------------------------------------------------------------------", font_4, (255,55,200), 0, 802)
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
                draw_text("---------------------------------------------------------------------------------", font_4, (255,0,90), 0, 802)
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
                draw_text("---------------------------------------------------------------------------------", font_4, (235,186,52), 0, 802)
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
                draw_text("---------------------------------------------------------------------------------", font_4, (235,186,52), 0, 802)
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
                draw_text("---------------------------------------------------------------------------------", font_4, (235,186,52), 0, 802)
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
                draw_text("---------------------------------------------------------------------------------", font_4, (235,186,52), 0, 802)
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
                draw_text("---------------------------------------------------------------------------------", font_4, (235,186,52), 0, 802)
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
                draw_text("---------------------------------------------------------------------------------", font_4, (235,186,52), 0, 802)
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
                draw_text("---------------------------------------------------------------------------------", font_4, (52,235,222), 0, 802)
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
                draw_text("---------------------------------------------------------------------------------", font_4, (52,235,222), 0, 802)
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
                draw_text("---------------------------------------------------------------------------------", font_4, (52,235,222), 0, 802)
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
                draw_text("---------------------------------------------------------------------------------", font_4, (52,235,222), 0, 802)
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
                draw_text("---------------------------------------------------------------------------------", font_4, (52,235,222), 0, 802)
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
                saving_game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False
                    saving_game()


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
        else:
            draw_text("you can't buy it", font_4, (255,255,255), 75, 738)
        if money >= 355:
            buy_b_for_good.draw(screen)
        else:
            draw_text("you can't buy it", font_4, (255,255,255), 435, 738)
        if money_diamond >= 5:
            buy_b_for_best.draw(screen)
        else:
            draw_text("you can't buy it", font_4, (255,255,255), 758, 738)

        if buy_b_for_small.clicked is True:
            if make_action < 1:
                make_action += 1

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
                saving_game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False
                    saving_game()
    
    if current_window_selected == "skill":
        is_moving_left = False
        is_moving_right = False
        back_shop = pygame.image.load("project-VAK/img/gui/shops_back/skills.png").convert_alpha()
        back_shop = pygame.transform.scale(back_shop, (int(back_shop.get_width() * 2.8), int(back_shop.get_height() * 2.8)))
        screen.blit(back_shop, (650,0))
        screen.blit(back_shop, (-180,0))
        Jenifer.update()
        Jenifer.draw(screen, 860, -90)
        back_im = pygame.image.load("project-VAK/img/gui/button_back_for_skill.png").convert_alpha()
        back_im_s = pygame.image.load("project-VAK/img/gui/button_back_for_skill_select.png").convert_alpha()
        back_button = Button(1430, 20, back_im, 5, back_im_s)
        table_im = pygame.image.load("project-VAK/img/gui/shops_back/skills_table.png").convert_alpha()
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

        closed_im = pygame.image.load("project-VAK/img/gui/closed_small_for_skill.png").convert_alpha()
        closed_im = pygame.transform.scale(closed_im, (int(closed_im.get_width() * 6), int(closed_im.get_height() * 6)))
        get_im = pygame.image.load("project-VAK/img/gui/yes_small_for_skill.png").convert_alpha()
        get_im = pygame.transform.scale(get_im, (int(get_im.get_width() * 6), int(get_im.get_height() * 6)))
        if page == 1:
            for i in range(len(skill_player_have)):
                if i == 0:
                    if skill_player_have[i] == 0:
                        screen.blit(closed_im, (90, 190))
                    if skill_player_have[i] == 1:
                        screen.blit(get_im, (90, 190))
                if i == 1:
                    if skill_player_have[i] == 0:
                        screen.blit(closed_im, (290, 190))
                    if skill_player_have[i] == 1:
                        screen.blit(get_im, (290, 190))
                if i == 2:
                    if skill_player_have[i] == 0:
                        screen.blit(closed_im, (490, 190))
                    if skill_player_have[i] == 1:
                        screen.blit(get_im, (490, 190))
                if i == 3:
                    if skill_player_have[i] == 0:
                        screen.blit(closed_im, (690, 190))
                    if skill_player_have[i] == 1:
                        screen.blit(get_im, (690, 190))
                if i == 4:
                    if skill_player_have[i] == 0:
                        screen.blit(closed_im, (890, 190))
                    if skill_player_have[i] == 1:
                        screen.blit(get_im, (890, 190))

                if i == 5:
                    if skill_player_have[i] == 0:
                        screen.blit(closed_im, (90, 390))
                    if skill_player_have[i] == 1:
                        screen.blit(get_im, (90, 390))
                if i == 6:
                    if skill_player_have[i] == 0:
                        screen.blit(closed_im, (290, 390))
                    if skill_player_have[i] == 1:
                        screen.blit(get_im, (290, 390))
                if i == 7:
                    if skill_player_have[i] == 0:
                        screen.blit(closed_im, (490, 390))
                    if skill_player_have[i] == 1:
                        screen.blit(get_im, (490, 390))
                if i == 8:
                    if skill_player_have[i] == 0:
                        screen.blit(closed_im, (690, 390))
                    if skill_player_have[i] == 1:
                        screen.blit(get_im, (690, 390))
                if i == 9:
                    if skill_player_have[i] == 0:
                        screen.blit(closed_im, (890, 390))
                    if skill_player_have[i] == 1:
                        screen.blit(get_im, (890, 390))
        
                if i == 10:
                    if skill_player_have[i] == 0:
                        screen.blit(closed_im, (90, 590))
                    if skill_player_have[i] == 1:
                        screen.blit(get_im, (90, 590))
                if i == 11:
                    if skill_player_have[i] == 0:
                        screen.blit(closed_im, (290, 590))
                    if skill_player_have[i] == 1:
                        screen.blit(get_im, (290, 590))
                if i == 12:
                    if skill_player_have[i] == 0:
                        screen.blit(closed_im, (490, 590))
                    if skill_player_have[i] == 1:
                        screen.blit(get_im, (490, 590))
                if i == 13:
                    if skill_player_have[i] == 0:
                        screen.blit(closed_im, (690, 590))
                    if skill_player_have[i] == 1:
                        screen.blit(get_im, (690, 590))
                if i == 14:
                    if skill_player_have[i] == 0:
                        screen.blit(closed_im, (890, 590))
                    if skill_player_have[i] == 1:
                        screen.blit(get_im, (890, 590))

                if i == 15:
                    if skill_player_have[i] == 0:
                        screen.blit(closed_im, (90, 790))
                    if skill_player_have[i] == 1:
                        screen.blit(get_im, (90, 790))
                if i == 16:
                    if skill_player_have[i] == 0:
                        screen.blit(closed_im, (290, 790))
                    if skill_player_have[i] == 1:
                        screen.blit(get_im, (290, 790))
            electric_grenad_im = pygame.image.load(f"project-VAK/img/gui/skills/electric_grenad.png").convert_alpha()
            buy_electric_grenad = Button(290, 700, electric_grenad_im, 1, electric_grenad_im, electric_grenad_im)

            if buy_electric_grenad.draw(screen):
                skill_which = 17
                page = 2

            morehealth_im = pygame.image.load(f"project-VAK/img/gui/skills/morehealth.png").convert_alpha()
            buy_morehealth = Button(90, 100, morehealth_im, 1, morehealth_im, morehealth_im)

            if buy_morehealth.draw(screen):
                skill_which = 1
                page = 2

            fast_im = pygame.image.load(f"project-VAK/img/gui/skills/faster.png").convert_alpha()
            # buy_im = pygame.image.load(f"project-VAK/img/gui/button_buy_for_food.png").convert_alpha()
            # buy_im = pygame.transform.scale(buy_im, (int(buy_im.get_width() * 3), int(buy_im.get_height() * 3)))
            # buy_im_select = pygame.image.load(f"project-VAK/img/gui/button_buy_for_food_select.png").convert_alpha()
            # buy_im_select = pygame.transform.scale(buy_im_select, (int(buy_im_select.get_width() * 3), int(buy_im_select.get_height() * 3)))
            # buy_im_press = pygame.image.load(f"project-VAK/img/gui/button_buy_for_food_press.png").convert_alpha()
            # buy_im_press = pygame.transform.scale(buy_im_press, (int(buy_im_press.get_width() * 3), int(buy_im_press.get_height() * 3)))
            buy_faster = Button(290, 100, fast_im, 1, fast_im, fast_im)

            if buy_faster.draw(screen):
                skill_which = 2
                page = 2

            les_toxic_im = pygame.image.load(f"project-VAK/img/gui/skills/tocsin.png").convert_alpha()
            buy_les_toxic = Button(490, 100, les_toxic_im, 1, les_toxic_im, les_toxic_im)

            if buy_les_toxic.draw(screen):
                skill_which = 3
                page = 2


            les_cold_im = pygame.image.load(f"project-VAK/img/gui/skills/freeze.png").convert_alpha()
            buy_les_cold = Button(690, 100, les_cold_im, 1, les_cold_im, les_cold_im)

            if buy_les_cold.draw(screen):
                skill_which = 4
                page = 2


            vampire_im = pygame.image.load(f"project-VAK/img/gui/skills/vampirism.png").convert_alpha()
            buy_vampire = Button(890, 100, vampire_im, 1, vampire_im, vampire_im)

            if buy_vampire.draw(screen):
                skill_which = 5
                page = 2

            bombing_im = pygame.image.load(f"project-VAK/img/gui/skills/granades.png").convert_alpha()
            buy_bombing = Button(90, 300, bombing_im, 1, bombing_im, bombing_im)

            if buy_bombing.draw(screen):
                skill_which = 6
                page = 2



            shield_im = pygame.image.load(f"project-VAK/img/gui/skills/shield.png").convert_alpha()
            buy_shield = Button(290, 300, shield_im, 1, shield_im, shield_im)

            if buy_shield.draw(screen):
                skill_which = 7
                page = 2


            determ_im = pygame.image.load(f"project-VAK/img/gui/skills/determ.png").convert_alpha()
            buy_determ = Button(490, 300, determ_im, 1, determ_im, determ_im)


            if buy_determ.draw(screen):
                skill_which = 8
                page = 2

            occultism_im = pygame.image.load(f"project-VAK/img/gui/skills/occultism.png").convert_alpha()
            buy_occultism = Button(690, 300, occultism_im, 1, occultism_im, occultism_im)

            if buy_occultism.draw(screen):
                skill_which = 9
                page = 2

            goodfood_im = pygame.image.load(f"project-VAK/img/gui/skills/goodfood.png").convert_alpha()
            buy_goodfood = Button(890, 300, goodfood_im, 1, goodfood_im, goodfood_im)

            if buy_goodfood.draw(screen):
                skill_which = 10
                page = 2


            reload_im = pygame.image.load(f"project-VAK/img/gui/skills/reload.png").convert_alpha()
            buy_reload = Button(90, 500, reload_im, 1, reload_im, reload_im)

            if buy_reload.draw(screen):
                skill_which = 11
                page = 2

            secondbreath_im = pygame.image.load(f"project-VAK/img/gui/skills/secondbreath.png").convert_alpha()
            buy_secondbreath = Button(290, 500, secondbreath_im, 1, secondbreath_im, secondbreath_im)

            if buy_secondbreath.draw(screen):
                skill_which = 12
                page = 2
    
            luckforfight_im = pygame.image.load(f"project-VAK/img/gui/skills/luckforfight.png").convert_alpha()
            buy_luckforfight = Button(490, 500, luckforfight_im, 1, luckforfight_im, luckforfight_im)

            if buy_luckforfight.draw(screen):
                skill_which = 13
                page = 2

            black_im = pygame.image.load(f"project-VAK/img/gui/skills/black.png").convert_alpha()
            buy_black = Button(690, 500, black_im, 1, black_im, black_im)

            if buy_black.draw(screen):
                skill_which = 14
                page = 2

            higher_im = pygame.image.load(f"project-VAK/img/gui/skills/higher.png").convert_alpha()
            buy_higher = Button(890, 500, higher_im, 1, higher_im, higher_im)

            if buy_higher.draw(screen):
                skill_which = 15
                page = 2

            gold_im = pygame.image.load(f"project-VAK/img/gui/skills/gold.png").convert_alpha()
            buy_gold = Button(90, 700, gold_im, 1, gold_im, gold_im)

            if buy_gold.draw(screen):
                skill_which = 16
                page = 2


        if page == 2:
            left_im = pygame.image.load("project-VAK/img/gui/button_left_for_skill.png").convert_alpha()
            left_im = pygame.transform.scale(left_im, (int(left_im.get_width() * 8), int(left_im.get_height() * 8)))
            left_im_p  = pygame.image.load("project-VAK/img/gui/button_left_press_for_skill.png").convert_alpha()
            left_im_p = pygame.transform.scale(left_im_p, (int(left_im_p.get_width() * 8), int(left_im_p.get_height() * 8))) 
            left_button = Button(980, 690, left_im, 1, left_im, left_im_p)
            buy_im = pygame.image.load(f"project-VAK/img/gui/button_buy_for_skill.png").convert_alpha()
            buy_im_select = pygame.image.load(f"project-VAK/img/gui/button_buy_for_skill_select.png").convert_alpha()
            buy_skill = Button(470, 690, buy_im, 8, buy_im_select, buy_im)

            if left_button.draw(screen):
                page = 1

            if skill_which == 1:
                if skill_player_have[0] == 1:
                    pass
                elif money_diamond >= 10:
                    if buy_skill.draw(screen):
                        money_diamond -= 10
                        skill_player_have[0] = 1
                else:
                    draw_text("You can't buy it!", font_3, (255,255,255), 480, 720)
                    
                morehealth_im = pygame.image.load(f"project-VAK/img/gui/skills/morehealth.png").convert_alpha()
                morehealth_im = pygame.transform.scale(morehealth_im, (int(morehealth_im.get_width() * 2), int(morehealth_im.get_height() * 2)))
                screen.blit(morehealth_im, (90, 90))
                draw_text("It's great to live", font_3, (255,25,25), 320, 139)
                draw_text("It's great to live", font_3, (255,255,255), 320, 140)
                draw_text("category: survival rate", font_4, (255,25,25), 320, 220)
                draw_text("With the", font_4, (255,255,255), 120, 350)
                draw_text("'It's great to live'", font_4, (255,25,25), 300, 350)
                draw_text("perk", font_4, (255,255,255), 650, 350)
                draw_text("your HP supply increases by 50 points", font_4, (255,255,255), 120, 420)
                health_im = pygame.image.load(f"project-VAK/img/gui/health_bar4.png").convert_alpha()
                health_im = pygame.transform.scale(health_im, (int(health_im.get_width() * 6), int(health_im.get_height() * 6)))
                screen.blit(health_im, (120, 520))
                draw_text("100 HP -> 150 Hp", font_4, (255,255,255), 420, 530)
                
                diamond_im = pygame.image.load(f"project-VAK/img/gui/money/diamond.png").convert_alpha()
                diamond_im = pygame.transform.scale(diamond_im, (int(diamond_im.get_width() * 3), int(diamond_im.get_height() * 3)))
                screen.blit(diamond_im,(870, 90))
                draw_text(f"{money_diamond}", font_3, (255,255,255), 980, 120)
                draw_text(f"{money_diamond}", font_3, (255,255,255), 980, 120)

                diamond_im_sml = pygame.image.load(f"project-VAK/img/gui/money/diamond_sml.png").convert_alpha()
                diamond_im_sml = pygame.transform.scale(diamond_im_sml, (int(diamond_im_sml.get_width() * 5), int(diamond_im_sml.get_height() * 5)))   
                screen.blit(diamond_im_sml, (320, 700))
                draw_text(f"cost: 10", font_3, (255,255,255), 80, 720)

            if skill_which == 2:
                if skill_player_have[1] == 1:
                    pass
                elif money_diamond >= 10:
                    if buy_skill.draw(screen):
                        money_diamond -= 10
                        skill_player_have[1] = 1
                else:
                    draw_text("You can't buy it!", font_3, (255,255,255), 480, 720)
                    
                morehealth_im = pygame.image.load(f"project-VAK/img/gui/skills/faster.png").convert_alpha()
                morehealth_im = pygame.transform.scale(morehealth_im, (int(morehealth_im.get_width() * 2), int(morehealth_im.get_height() * 2)))
                screen.blit(morehealth_im, (90, 90))
                draw_text("faster better", font_3, (240, 230, 140), 320, 138)
                draw_text("faster better", font_3, (255,255,255), 320, 140)
                draw_text("category : speed", font_4, (240, 230, 140), 320, 220)
                draw_text("With the", font_4, (255,255,255), 120, 350)
                draw_text("'faster better'", font_4, (240, 230, 140), 300, 350)
                draw_text("perk", font_4, (255,255,255), 590, 350)
                draw_text("The player moves 3 units faster", font_4, (255,255,255), 120, 420)
                running_pers.update()
                running_pers.draw(screen, 360, 480)
                draw_text("5 u -> 8 u", font_4, (255,255,255), 460, 530)
                
                diamond_im = pygame.image.load(f"project-VAK/img/gui/money/diamond.png").convert_alpha()
                diamond_im = pygame.transform.scale(diamond_im, (int(diamond_im.get_width() * 3), int(diamond_im.get_height() * 3)))
                screen.blit(diamond_im,(870, 90))
                draw_text(f"{money_diamond}", font_3, (255,255,255), 980, 120)
                draw_text(f"{money_diamond}", font_3, (255,255,255), 980, 120)

                diamond_im_sml = pygame.image.load(f"project-VAK/img/gui/money/diamond_sml.png").convert_alpha()
                diamond_im_sml = pygame.transform.scale(diamond_im_sml, (int(diamond_im_sml.get_width() * 5), int(diamond_im_sml.get_height() * 5)))   
                screen.blit(diamond_im_sml, (320, 700))
                draw_text(f"cost: 10", font_3, (255,255,255), 80, 720)

            if skill_which == 3:
                if skill_player_have[2] == 1:
                    pass
                elif money_diamond >= 10:
                    if buy_skill.draw(screen):
                        money_diamond -= 10
                        skill_player_have[2] = 1
                else:
                    draw_text("You can't buy it!", font_3, (255,255,255), 480, 720)
                    
                morehealth_im = pygame.image.load(f"project-VAK/img/gui/skills/tocsin.png").convert_alpha()
                morehealth_im = pygame.transform.scale(morehealth_im, (int(morehealth_im.get_width() * 2), int(morehealth_im.get_height() * 2)))
                screen.blit(morehealth_im, (90, 90))
                draw_text("resistance to toxins", font_3, (176, 196, 222), 320, 138)
                draw_text("resistance to toxins", font_3, (255,255,255), 320, 140)
                draw_text("category : access to the planets", font_4, (176, 196, 222), 320, 220)
                draw_text("With the", font_4, (255,255,255), 120, 350)
                draw_text("'resistance to toxins'", font_4, (176, 196, 222), 300, 350)
                draw_text("perk", font_4, (255,255,255), 710, 350)
                draw_text("You will be able to travel to", font_4, (255,255,255), 120, 420)
                draw_text("planets with too much toxin", font_4, (255,255,255), 120, 480)
                # running_pers.update()
                # running_pers.draw(screen, 360, 480)
                # draw_text("5 u -> 8 u", font_4, (255,255,255), 460, 530)
                
                diamond_im = pygame.image.load(f"project-VAK/img/gui/money/diamond.png").convert_alpha()
                diamond_im = pygame.transform.scale(diamond_im, (int(diamond_im.get_width() * 3), int(diamond_im.get_height() * 3)))
                screen.blit(diamond_im,(870, 90))
                draw_text(f"{money_diamond}", font_3, (255,255,255), 980, 120)
                draw_text(f"{money_diamond}", font_3, (255,255,255), 980, 120)

                diamond_im_sml = pygame.image.load(f"project-VAK/img/gui/money/diamond_sml.png").convert_alpha()
                diamond_im_sml = pygame.transform.scale(diamond_im_sml, (int(diamond_im_sml.get_width() * 5), int(diamond_im_sml.get_height() * 5)))   
                screen.blit(diamond_im_sml, (320, 700))
                draw_text(f"cost: 10", font_3, (255,255,255), 80, 720)

            if skill_which == 4:
                if skill_player_have[3] == 1:
                    pass
                elif money_diamond >= 10:
                    if buy_skill.draw(screen):
                        money_diamond -= 10
                        skill_player_have[3] = 1
                else:
                    draw_text("You can't buy it!", font_3, (255,255,255), 480, 720)
                    
                morehealth_im = pygame.image.load(f"project-VAK/img/gui/skills/freeze.png").convert_alpha()
                morehealth_im = pygame.transform.scale(morehealth_im, (int(morehealth_im.get_width() * 2), int(morehealth_im.get_height() * 2)))
                screen.blit(morehealth_im, (90, 90))
                draw_text("resistance to cold", font_3, (176, 196, 222), 320, 138)
                draw_text("resistance to cold", font_3, (255,255,255), 320, 140)
                draw_text("category : access to the planets", font_4, (176, 196, 222), 320, 220)
                draw_text("With the", font_4, (255,255,255), 120, 350)
                draw_text("'resistance to cold'", font_4, (176, 196, 222), 300, 350)
                draw_text("perk", font_4, (255,255,255), 690, 350)
                draw_text("You will be able to travel to", font_4, (255,255,255), 120, 420)
                draw_text("planets that are too cold", font_4, (255,255,255), 120, 480)
                # running_pers.update()
                # running_pers.draw(screen, 360, 480)
                # draw_text("5 u -> 8 u", font_4, (255,255,255), 460, 530)
                
                diamond_im = pygame.image.load(f"project-VAK/img/gui/money/diamond.png").convert_alpha()
                diamond_im = pygame.transform.scale(diamond_im, (int(diamond_im.get_width() * 3), int(diamond_im.get_height() * 3)))
                screen.blit(diamond_im,(870, 90))
                draw_text(f"{money_diamond}", font_3, (255,255,255), 980, 120)
                draw_text(f"{money_diamond}", font_3, (255,255,255), 980, 120)

                diamond_im_sml = pygame.image.load(f"project-VAK/img/gui/money/diamond_sml.png").convert_alpha()
                diamond_im_sml = pygame.transform.scale(diamond_im_sml, (int(diamond_im_sml.get_width() * 5), int(diamond_im_sml.get_height() * 5)))   
                screen.blit(diamond_im_sml, (320, 700))
                draw_text(f"cost: 10", font_3, (255,255,255), 80, 720)

            if skill_which == 5:
                if skill_player_have[4] == 1:
                    pass
                elif money_diamond >= 10:
                    if buy_skill.draw(screen):
                        money_diamond -= 10
                        skill_player_have[4] = 1
                else:
                    draw_text("You can't buy it!", font_3, (255,255,255), 480, 720)
                    
                morehealth_im = pygame.image.load(f"project-VAK/img/gui/skills/vampirism.png").convert_alpha()
                morehealth_im = pygame.transform.scale(morehealth_im, (int(morehealth_im.get_width() * 2), int(morehealth_im.get_height() * 2)))
                screen.blit(morehealth_im, (90, 90))
                draw_text("vampirism", font_3, (255,25,25), 320, 138)
                draw_text("vampirism", font_3, (255,255,255), 320, 140)
                draw_text("category: survival rate", font_4, (255,25,25), 320, 220)
                draw_text("With the", font_4, (255,255,255), 120, 350)
                draw_text("'vampirism'", font_4, (255,25,25), 300, 350)
                draw_text("perk", font_4, (255,255,255), 520, 350)
                draw_text("For every enemy you kill, you get 1 hp", font_4, (255,255,255), 120, 420)
                enemy_explode.update()
                enemy_explode.draw(screen, 356, 480)
                # running_pers.update()
                # running_pers.draw(screen, 360, 480)
                draw_text("+ 1hp", font_4, (255,255,255), 460, 530)
                
                diamond_im = pygame.image.load(f"project-VAK/img/gui/money/diamond.png").convert_alpha()
                diamond_im = pygame.transform.scale(diamond_im, (int(diamond_im.get_width() * 3), int(diamond_im.get_height() * 3)))
                screen.blit(diamond_im,(870, 90))
                draw_text(f"{money_diamond}", font_3, (255,255,255), 980, 120)


                diamond_im_sml = pygame.image.load(f"project-VAK/img/gui/money/diamond_sml.png").convert_alpha()
                diamond_im_sml = pygame.transform.scale(diamond_im_sml, (int(diamond_im_sml.get_width() * 5), int(diamond_im_sml.get_height() * 5)))   
                screen.blit(diamond_im_sml, (320, 700))
                draw_text(f"cost: 10", font_3, (255,255,255), 80, 720)

            if skill_which == 6:
                if skill_player_have[5] == 1:
                    pass
                elif money_diamond >= 10:
                    if buy_skill.draw(screen):
                        money_diamond -= 10
                        skill_player_have[5] = 1
                else:
                    draw_text("You can't buy it!", font_3, (255,255,255), 480, 720)
                    
                morehealth_im = pygame.image.load(f"project-VAK/img/gui/skills/granades.png").convert_alpha()
                morehealth_im = pygame.transform.scale(morehealth_im, (int(morehealth_im.get_width() * 2), int(morehealth_im.get_height() * 2)))
                screen.blit(morehealth_im, (90, 90))
                draw_text("Bombing", font_3, (233, 150, 122), 320, 138)
                draw_text("Bombing", font_3, (255,255,255), 320, 140)
                draw_text("category: fighting", font_4, (233, 150, 122), 320, 220)
                draw_text("With the", font_4, (255,255,255), 120, 350)
                draw_text("'Bombing'", font_4, (233, 150, 122), 300, 350)
                draw_text("perk", font_4, (255,255,255), 490, 350)
                draw_text("you can throw grenades by pressing the q key", font_4, (255,255,255), 120, 420)

                # running_pers.update()
                # running_pers.draw(screen, 360, 480)
                draw_text("- the number of grenades = 5", font_4, (255,255,255), 260, 530)
                draw_text("- the damage from grenades = 500", font_4, (255,255,255), 260, 590)
                screen.blit(grenade_image_for_gui, (100, 510))
                diamond_im = pygame.image.load(f"project-VAK/img/gui/money/diamond.png").convert_alpha()
                diamond_im = pygame.transform.scale(diamond_im, (int(diamond_im.get_width() * 3), int(diamond_im.get_height() * 3)))
                screen.blit(diamond_im,(870, 90))
                draw_text(f"{money_diamond}", font_3, (255,255,255), 980, 120)


                diamond_im_sml = pygame.image.load(f"project-VAK/img/gui/money/diamond_sml.png").convert_alpha()
                diamond_im_sml = pygame.transform.scale(diamond_im_sml, (int(diamond_im_sml.get_width() * 5), int(diamond_im_sml.get_height() * 5)))   
                screen.blit(diamond_im_sml, (320, 700))
                draw_text(f"cost: 10", font_3, (255,255,255), 80, 720)


            if skill_which == 7:
                if skill_player_have[6] == 1:
                    pass
                elif money_diamond >= 10:
                    if buy_skill.draw(screen):
                        money_diamond -= 10
                        skill_player_have[6] = 1
                else:
                    draw_text("You can't buy it!", font_3, (255,255,255), 480, 720)
                    
                morehealth_im = pygame.image.load(f"project-VAK/img/gui/skills/shield.png").convert_alpha()
                morehealth_im = pygame.transform.scale(morehealth_im, (int(morehealth_im.get_width() * 2), int(morehealth_im.get_height() * 2)))
                screen.blit(morehealth_im, (90, 90))
                draw_text("Give him a shield", font_3, (255,25,25), 320, 138)
                draw_text("Give him a shield", font_3, (255,255,255), 320, 140)
                draw_text("category: survival rate", font_4, (255,25,25), 320, 220)
                draw_text("With the", font_4, (255,255,255), 120, 350)
                draw_text("'Give him a shield'", font_4, (255,25,25), 300, 350)
                draw_text("perk", font_4, (255,255,255), 620, 350)
                draw_text("At the beginning of the round", font_4, (255,255,255), 120, 420)
                draw_text("you have a shield with 50 hp", font_4, (255,255,255), 120, 470)
                draw_text("the damage will first pass through the shield", font_4, (255,255,255), 120, 530)
                draw_text("after it breaks, the damage will begin to", font_4, (255,255,255), 120, 580)
                draw_text("pass through your main health.", font_4, (255,255,255), 120, 630)
                health_im = pygame.image.load(f"project-VAK/img/gui/shield_bar4.png").convert_alpha()
                health_im = pygame.transform.scale(health_im, (int(health_im.get_width() * 6), int(health_im.get_height() * 6)))
                screen.blit(health_im, (650, 460))
                draw_text("50 Hp", font_4, (255,255,255), 950, 470)
                
                diamond_im = pygame.image.load(f"project-VAK/img/gui/money/diamond.png").convert_alpha()
                diamond_im = pygame.transform.scale(diamond_im, (int(diamond_im.get_width() * 3), int(diamond_im.get_height() * 3)))
                screen.blit(diamond_im,(870, 90))
                draw_text(f"{money_diamond}", font_3, (255,255,255), 980, 120)
                draw_text(f"{money_diamond}", font_3, (255,255,255), 980, 120)

                diamond_im_sml = pygame.image.load(f"project-VAK/img/gui/money/diamond_sml.png").convert_alpha()
                diamond_im_sml = pygame.transform.scale(diamond_im_sml, (int(diamond_im_sml.get_width() * 5), int(diamond_im_sml.get_height() * 5)))   
                screen.blit(diamond_im_sml, (320, 700))
                draw_text(f"cost: 10", font_3, (255,255,255), 80, 720)


            if skill_which == 8:
                if skill_player_have[7] == 1:
                    pass
                elif money_diamond >= 10:
                    if buy_skill.draw(screen):
                        money_diamond -= 10
                        skill_player_have[7] = 1
                else:
                    draw_text("You can't buy it!", font_3, (255,255,255), 480, 720)
                    
                morehealth_im = pygame.image.load(f"project-VAK/img/gui/skills/determ.png").convert_alpha()
                morehealth_im = pygame.transform.scale(morehealth_im, (int(morehealth_im.get_width() * 2), int(morehealth_im.get_height() * 2)))
                screen.blit(morehealth_im, (90, 90))
                draw_text("Determination", font_3, (233, 150, 122), 320, 138)
                draw_text("Determination", font_3, (255,255,255), 320, 140)
                draw_text("category: fighting", font_4, (233, 150, 122), 320, 220)
                draw_text("With the", font_4, (255,255,255), 120, 350)
                draw_text("'Determination'", font_4, (233, 150, 122), 300, 350)
                draw_text("perk", font_4, (255,255,255), 580, 350)
                draw_text("when the player is less than 10 hp", font_4, (255,255,255), 120, 420)
                draw_text("your damage to enemies increases by 1.5 times", font_4, (255,255,255), 120, 470)
                
                diamond_im = pygame.image.load(f"project-VAK/img/gui/money/diamond.png").convert_alpha()
                diamond_im = pygame.transform.scale(diamond_im, (int(diamond_im.get_width() * 3), int(diamond_im.get_height() * 3)))
                screen.blit(diamond_im,(870, 90))
                draw_text(f"{money_diamond}", font_3, (255,255,255), 980, 120)
                draw_text(f"{money_diamond}", font_3, (255,255,255), 980, 120)

                diamond_im_sml = pygame.image.load(f"project-VAK/img/gui/money/diamond_sml.png").convert_alpha()
                diamond_im_sml = pygame.transform.scale(diamond_im_sml, (int(diamond_im_sml.get_width() * 5), int(diamond_im_sml.get_height() * 5)))   
                screen.blit(diamond_im_sml, (320, 700))
                draw_text(f"cost: 10", font_3, (255,255,255), 80, 720)

            if skill_which == 9:
                if skill_player_have[8] == 1:
                    pass
                elif money_diamond >= 10:
                    if buy_skill.draw(screen):
                        money_diamond -= 10
                        skill_player_have[8] = 1
                else:
                    draw_text("You can't buy it!", font_3, (255,255,255), 480, 720)
                    
                morehealth_im = pygame.image.load(f"project-VAK/img/gui/skills/occultism.png").convert_alpha()
                morehealth_im = pygame.transform.scale(morehealth_im, (int(morehealth_im.get_width() * 2), int(morehealth_im.get_height() * 2)))
                screen.blit(morehealth_im, (90, 90))
                draw_text("occultism", font_3, (233, 150, 122), 320, 138)
                draw_text("occultism", font_3, (255,255,255), 320, 140)
                draw_text("category: fighting", font_4, (233, 150, 122), 320, 220)
                draw_text("With the", font_4, (255,255,255), 120, 350)
                draw_text("'occultism'", font_4, (233, 150, 122), 300, 350)
                draw_text("perk", font_4, (255,255,255), 540, 350)
                draw_text("damage to skeletons, spirits, demons", font_4, (255,255,255), 120, 420)
                draw_text("increases by 1.5 times", font_4, (255,255,255), 120, 470)
                
                diamond_im = pygame.image.load(f"project-VAK/img/gui/money/diamond.png").convert_alpha()
                diamond_im = pygame.transform.scale(diamond_im, (int(diamond_im.get_width() * 3), int(diamond_im.get_height() * 3)))
                screen.blit(diamond_im,(870, 90))
                draw_text(f"{money_diamond}", font_3, (255,255,255), 980, 120)
                draw_text(f"{money_diamond}", font_3, (255,255,255), 980, 120)

                diamond_im_sml = pygame.image.load(f"project-VAK/img/gui/money/diamond_sml.png").convert_alpha()
                diamond_im_sml = pygame.transform.scale(diamond_im_sml, (int(diamond_im_sml.get_width() * 5), int(diamond_im_sml.get_height() * 5)))   
                screen.blit(diamond_im_sml, (320, 700))
                draw_text(f"cost: 10", font_3, (255,255,255), 80, 720)
        

            if skill_which == 10:
                if skill_player_have[9] == 1:
                    pass
                elif money_diamond >= 10:
                    if buy_skill.draw(screen):
                        money_diamond -= 10
                        skill_player_have[9] = 1
                else:
                    draw_text("You can't buy it!", font_3, (255,255,255), 480, 720)
                    
                morehealth_im = pygame.image.load(f"project-VAK/img/gui/skills/goodfood.png").convert_alpha()
                morehealth_im = pygame.transform.scale(morehealth_im, (int(morehealth_im.get_width() * 2), int(morehealth_im.get_height() * 2)))
                screen.blit(morehealth_im, (90, 90))
                draw_text("Healthy eating", font_3, (255,25,25), 320, 138)
                draw_text("Healthy eating", font_3, (255,255,255), 320, 140)
                draw_text("category: survival rate", font_4, (255,25,25), 320, 220)
                draw_text("With the", font_4, (255,255,255), 120, 350)
                draw_text("'Healthy eating'", font_4, (255,25,25), 300, 350)
                draw_text("perk", font_4, (255,255,255), 620, 350)
                draw_text("if the amount of small food is more than 10,", font_4, (255,255,255), 120, 420)
                draw_text("then each small food eaten restores 40 hp more", font_4, (255,255,255), 120, 470)
                draw_text("than by default", font_4, (255,255,255), 120, 530)
                normal_food = pygame.image.load(f"project-VAK/img/gui/food/normal_food.png").convert_alpha()
                normal_food = pygame.transform.scale(normal_food, (int(normal_food.get_width() * 5), int(normal_food.get_height() * 5)))
                screen.blit(normal_food, (230, 575))
                draw_text(">10", font_4, (255,255,255), 161, 610)
                draw_text("12 hp -> 52 hp", font_4, (255,255,255), 380, 610)
                diamond_im = pygame.image.load(f"project-VAK/img/gui/money/diamond.png").convert_alpha()
                diamond_im = pygame.transform.scale(diamond_im, (int(diamond_im.get_width() * 3), int(diamond_im.get_height() * 3)))
                screen.blit(diamond_im,(870, 90))
                draw_text(f"{money_diamond}", font_3, (255,255,255), 980, 120)
                draw_text(f"{money_diamond}", font_3, (255,255,255), 980, 120)

                diamond_im_sml = pygame.image.load(f"project-VAK/img/gui/money/diamond_sml.png").convert_alpha()
                diamond_im_sml = pygame.transform.scale(diamond_im_sml, (int(diamond_im_sml.get_width() * 5), int(diamond_im_sml.get_height() * 5)))   
                screen.blit(diamond_im_sml, (320, 700))
                draw_text(f"cost: 10", font_3, (255,255,255), 80, 720)

            if skill_which == 11:
                if skill_player_have[10] == 1:
                    pass
                elif money_diamond >= 10:
                    if buy_skill.draw(screen):
                        money_diamond -= 10
                        skill_player_have[10] = 1
                else:
                    draw_text("You can't buy it!", font_3, (255,255,255), 480, 720)
                    
                morehealth_im = pygame.image.load(f"project-VAK/img/gui/skills/reload.png").convert_alpha()
                morehealth_im = pygame.transform.scale(morehealth_im, (int(morehealth_im.get_width() * 2), int(morehealth_im.get_height() * 2)))
                screen.blit(morehealth_im, (90, 90))
                draw_text("fast recharge", font_3, (240, 230, 140), 320, 138)
                draw_text("fast recharge", font_3, (255,255,255), 320, 140)
                draw_text("category : speed", font_4, (240, 230, 140), 320, 220)
                draw_text("With the", font_4, (255,255,255), 120, 350)
                draw_text("'fast recharge'", font_4, (240, 230, 140), 300, 350)
                draw_text("perk", font_4, (255,255,255), 630, 350)
                draw_text("You reload your weapon 2 seconds faster", font_4, (255,255,255), 120, 420)
                diamond_im = pygame.image.load(f"project-VAK/img/gui/money/diamond.png").convert_alpha()
                diamond_im = pygame.transform.scale(diamond_im, (int(diamond_im.get_width() * 3), int(diamond_im.get_height() * 3)))
                screen.blit(diamond_im,(870, 90))
                draw_text(f"{money_diamond}", font_3, (255,255,255), 980, 120)
                draw_text(f"{money_diamond}", font_3, (255,255,255), 980, 120)

                diamond_im_sml = pygame.image.load(f"project-VAK/img/gui/money/diamond_sml.png").convert_alpha()
                diamond_im_sml = pygame.transform.scale(diamond_im_sml, (int(diamond_im_sml.get_width() * 5), int(diamond_im_sml.get_height() * 5)))   
                screen.blit(diamond_im_sml, (320, 700))
                draw_text(f"cost: 10", font_3, (255,255,255), 80, 720)


            if skill_which == 12:
                if skill_player_have[11] == 1:
                    pass
                elif money_diamond >= 10:
                    if buy_skill.draw(screen):
                        money_diamond -= 10
                        skill_player_have[11] = 1
                else:
                    draw_text("You can't buy it!", font_3, (255,255,255), 480, 720)
                    
                morehealth_im = pygame.image.load(f"project-VAK/img/gui/skills/secondbreath.png").convert_alpha()
                morehealth_im = pygame.transform.scale(morehealth_im, (int(morehealth_im.get_width() * 2), int(morehealth_im.get_height() * 2)))
                screen.blit(morehealth_im, (90, 90))
                draw_text("second breath", font_3, (255,25,25), 320, 138)
                draw_text("second breath", font_3, (255,255,255), 320, 140)
                draw_text("category: survival rate", font_4, (255,25,25), 320, 220)
                draw_text("With the", font_4, (255,255,255), 120, 350)
                draw_text("'second breath'", font_4, (255,25,25), 300, 350)
                draw_text("perk", font_4, (255,255,255), 630, 350)
                draw_text("on the 10th wave of the round", font_4, (255,255,255), 120, 420)
                draw_text("-HP is restored to the maximum", font_4, (255,255,255), 120, 470)
                draw_text("-if the shield is there or was broken in the round, ", font_4, (255,255,255), 120, 530)
                draw_text("it is fully restored", font_4, (255,255,255), 120, 580)
                draw_text("-movement speed increases by 1 unit.", font_4, (255,255,255), 120, 630)
                
                # running_pers.update()
                # running_pers.draw(screen, 360, 480)
                diamond_im = pygame.image.load(f"project-VAK/img/gui/money/diamond.png").convert_alpha()
                diamond_im = pygame.transform.scale(diamond_im, (int(diamond_im.get_width() * 3), int(diamond_im.get_height() * 3)))
                screen.blit(diamond_im,(870, 90))
                draw_text(f"{money_diamond}", font_3, (255,255,255), 980, 120)
                draw_text(f"{money_diamond}", font_3, (255,255,255), 980, 120)

                diamond_im_sml = pygame.image.load(f"project-VAK/img/gui/money/diamond_sml.png").convert_alpha()
                diamond_im_sml = pygame.transform.scale(diamond_im_sml, (int(diamond_im_sml.get_width() * 5), int(diamond_im_sml.get_height() * 5)))   
                screen.blit(diamond_im_sml, (320, 700))
                draw_text(f"cost: 10", font_3, (255,255,255), 80, 720)

            if skill_which == 13:
                if skill_player_have[12] == 1:
                    pass
                elif money_diamond >= 10:
                    if buy_skill.draw(screen):
                        money_diamond -= 10
                        skill_player_have[12] = 1
                else:
                    draw_text("You can't buy it!", font_3, (255,255,255), 480, 720)
                    
                morehealth_im = pygame.image.load(f"project-VAK/img/gui/skills/luckforfight.png").convert_alpha()
                morehealth_im = pygame.transform.scale(morehealth_im, (int(morehealth_im.get_width() * 2), int(morehealth_im.get_height() * 2)))
                screen.blit(morehealth_im, (90, 90))
                draw_text("Luck is on your side", font_3, (32, 178, 170), 320, 138)
                draw_text("Luck is on your side", font_3, (255,255,255), 320, 140)
                draw_text("category: luck", font_4, (32, 178, 170), 320, 220)
                draw_text("With the", font_4, (255,255,255), 120, 350)
                draw_text("'Luck is on your side'", font_4, (32, 178, 170), 300, 350)
                draw_text("perk", font_4, (255,255,255), 690, 350)
                draw_text("the longer you do not drop hp, the higher the chance", font_4, (255,255,255), 120, 420)
                draw_text("of additional loot items at the end of the round", font_4, (255,255,255), 120, 470)

                # running_pers.update()
                # running_pers.draw(screen, 360, 480)
                diamond_im = pygame.image.load(f"project-VAK/img/gui/money/diamond.png").convert_alpha()
                diamond_im = pygame.transform.scale(diamond_im, (int(diamond_im.get_width() * 3), int(diamond_im.get_height() * 3)))
                screen.blit(diamond_im,(870, 90))
                draw_text(f"{money_diamond}", font_3, (255,255,255), 980, 120)
                draw_text(f"{money_diamond}", font_3, (255,255,255), 980, 120)

                diamond_im_sml = pygame.image.load(f"project-VAK/img/gui/money/diamond_sml.png").convert_alpha()
                diamond_im_sml = pygame.transform.scale(diamond_im_sml, (int(diamond_im_sml.get_width() * 5), int(diamond_im_sml.get_height() * 5)))   
                screen.blit(diamond_im_sml, (320, 700))
                draw_text(f"cost: 10", font_3, (255,255,255), 80, 720)



            if skill_which == 14:
                if skill_player_have[13] == 1:
                    pass
                elif money_diamond >= 10:
                    if buy_skill.draw(screen):
                        money_diamond -= 10
                        skill_player_have[13] = 1
                else:
                    draw_text("You can't buy it!", font_3, (255,255,255), 480, 720)
                    
                morehealth_im = pygame.image.load(f"project-VAK/img/gui/skills/black.png").convert_alpha()
                morehealth_im = pygame.transform.scale(morehealth_im, (int(morehealth_im.get_width() * 2), int(morehealth_im.get_height() * 2)))
                screen.blit(morehealth_im, (90, 90))
                draw_text("black matter", font_3, (176, 196, 222), 320, 138)
                draw_text("black matter", font_3, (255,255,255), 320, 140)
                draw_text("category : access to the planets", font_4, (176, 196, 222), 320, 220)
                draw_text("With the", font_4, (255,255,255), 120, 350)
                draw_text("'black matter'", font_4, (176, 196, 222), 300, 350)
                draw_text("perk", font_4, (255,255,255), 600, 350)
                draw_text("You can upgrade your ship to level 6 in the 'junk' store", font_4, (255,255,255), 120, 420)
                draw_text("5 level -> 6 level", font_4, (255,255,255), 420, 520)
                diamond_im = pygame.image.load(f"project-VAK/img/gui/money/diamond.png").convert_alpha()
                diamond_im = pygame.transform.scale(diamond_im, (int(diamond_im.get_width() * 3), int(diamond_im.get_height() * 3)))
                screen.blit(diamond_im,(870, 90))
                draw_text(f"{money_diamond}", font_3, (255,255,255), 980, 120)
                draw_text(f"{money_diamond}", font_3, (255,255,255), 980, 120)
                ship_im = pygame.image.load("project-VAK/img/gui/ships/ship6.png").convert_alpha()
                ship_im = pygame.transform.scale(ship_im, (int(ship_im.get_width() * 2), int(ship_im.get_height() * 2)))
                screen.blit(ship_im, (150, 420))

                diamond_im_sml = pygame.image.load(f"project-VAK/img/gui/money/diamond_sml.png").convert_alpha()
                diamond_im_sml = pygame.transform.scale(diamond_im_sml, (int(diamond_im_sml.get_width() * 5), int(diamond_im_sml.get_height() * 5)))   
                screen.blit(diamond_im_sml, (320, 700))
                draw_text(f"cost: 10", font_3, (255,255,255), 80, 720)

            if skill_which == 15:
                if skill_player_have[14] == 1:
                    pass
                elif money_diamond >= 10:
                    if buy_skill.draw(screen):
                        money_diamond -= 10
                        skill_player_have[14] = 1
                else:
                    draw_text("You can't buy it!", font_3, (255,255,255), 480, 720)
                    
                morehealth_im = pygame.image.load(f"project-VAK/img/gui/skills/higher.png").convert_alpha()
                morehealth_im = pygame.transform.scale(morehealth_im, (int(morehealth_im.get_width() * 2), int(morehealth_im.get_height() * 2)))
                screen.blit(morehealth_im, (90, 90))
                draw_text("Above the pain", font_3, (255,25,25), 320, 138)
                draw_text("Above the pain", font_3, (255,255,255), 320, 140)
                draw_text("category: survival rate", font_4, (255,25,25), 320, 220)
                draw_text("With the", font_4, (255,255,255), 120, 350)
                draw_text("'Above the painr'", font_4, (255,25,25), 300, 350)
                draw_text("perk", font_4, (255,255,255), 600, 350)
                draw_text("You won't be able to die on the first two waves", font_4, (255,255,255), 120, 420)
                diamond_im = pygame.image.load(f"project-VAK/img/gui/money/diamond.png").convert_alpha()
                diamond_im = pygame.transform.scale(diamond_im, (int(diamond_im.get_width() * 3), int(diamond_im.get_height() * 3)))
                screen.blit(diamond_im,(870, 90))
                draw_text(f"{money_diamond}", font_3, (255,255,255), 980, 120)
                draw_text(f"{money_diamond}", font_3, (255,255,255), 980, 120)

                diamond_im_sml = pygame.image.load(f"project-VAK/img/gui/money/diamond_sml.png").convert_alpha()
                diamond_im_sml = pygame.transform.scale(diamond_im_sml, (int(diamond_im_sml.get_width() * 5), int(diamond_im_sml.get_height() * 5)))   
                screen.blit(diamond_im_sml, (320, 700))
                draw_text(f"cost: 10", font_3, (255,255,255), 80, 720)


            if skill_which == 16:
                if skill_player_have[15] == 1:
                    pass
                elif money_diamond >= 10:
                    if buy_skill.draw(screen):
                        money_diamond -= 10
                        skill_player_have[15] = 1
                else:
                    draw_text("You can't buy it!", font_3, (255,255,255), 480, 720)
                    
                morehealth_im = pygame.image.load(f"project-VAK/img/gui/skills/gold.png").convert_alpha()
                morehealth_im = pygame.transform.scale(morehealth_im, (int(morehealth_im.get_width() * 2), int(morehealth_im.get_height() * 2)))
                screen.blit(morehealth_im, (90, 90))
                draw_text("The Gold Seeker", font_3, (32, 178, 170), 320, 138)
                draw_text("The Gold Seeker", font_3, (255,255,255), 320, 140)
                draw_text("category: luck", font_4, (32, 178, 170), 320, 220)
                draw_text("With the", font_4, (255,255,255), 120, 350)
                draw_text("'The Gold Seeker'", font_4, (32, 178, 170), 300, 350)
                draw_text("perk", font_4, (255,255,255), 600, 350)
                draw_text("the chance of getting gold and better steel", font_4, (255,255,255), 120, 420)
                draw_text("increases by 20 %", font_4, (255,255,255), 120, 470)
                diamond_im = pygame.image.load(f"project-VAK/img/gui/money/diamond.png").convert_alpha()
                diamond_im = pygame.transform.scale(diamond_im, (int(diamond_im.get_width() * 3), int(diamond_im.get_height() * 3)))
                screen.blit(diamond_im,(870, 90))
                draw_text("10% - 30%", font_4, (255,255,255), 300, 560)
                gold_im = pygame.image.load(f"project-VAK/img/gui/money/gold.png").convert_alpha()
                gold_im = pygame.transform.scale(gold_im, (int(gold_im.get_width() * 5), int(gold_im.get_height() * 5)))
                screen.blit(gold_im, (470, 520))
                better_steel_im = pygame.image.load(f"project-VAK/img/gui/money/better_steel.png").convert_alpha()
                better_steel_im = pygame.transform.scale(better_steel_im, (int(better_steel_im.get_width() * 5), int(better_steel_im.get_height() * 5)))
                draw_text("5% - 25%", font_4, (255,255,255), 730, 560)
                screen.blit(better_steel_im,(890, 520))
                draw_text(f"{money_diamond}", font_3, (255,255,255), 980, 120)
                draw_text(f"{money_diamond}", font_3, (255,255,255), 980, 120)

                diamond_im_sml = pygame.image.load(f"project-VAK/img/gui/money/diamond_sml.png").convert_alpha()
                diamond_im_sml = pygame.transform.scale(diamond_im_sml, (int(diamond_im_sml.get_width() * 5), int(diamond_im_sml.get_height() * 5)))   
                screen.blit(diamond_im_sml, (320, 700))
                draw_text(f"cost: 10", font_3, (255,255,255), 80, 720)

            if skill_which == 17:
                if skill_player_have[16] == 1:
                    pass
                elif money_diamond >= 10:
                    if buy_skill.draw(screen):
                        money_diamond -= 10
                        skill_player_have[16] = 1
                else:
                    draw_text("You can't buy it!", font_3, (255,255,255), 480, 720)
                    
                morehealth_im = pygame.image.load(f"project-VAK/img/gui/skills/electric_grenad.png").convert_alpha()
                morehealth_im = pygame.transform.scale(morehealth_im, (int(morehealth_im.get_width() * 2), int(morehealth_im.get_height() * 2)))
                screen.blit(morehealth_im, (90, 90))
                draw_text("The comet", font_3, (233, 150, 122), 320, 138)
                draw_text("The comet", font_3, (255,255,255), 320, 140)
                draw_text("category: fighting", font_4, (233, 150, 122), 320, 220)
                draw_text("With the", font_4, (255,255,255), 120, 350)
                draw_text("'The comet'", font_4, (233, 150, 122), 300, 350)
                draw_text("perk", font_4, (255,255,255), 530, 350)
                draw_text("you can throw electric grenades by pressing the v key", font_4, (255,255,255), 120, 420)

                draw_text("- the number of grenades = 3", font_4, (255,255,255), 260, 530)
                draw_text("- the damage from grenades = 1200", font_4, (255,255,255), 260, 590)
                screen.blit(el_grenade_image_for_gui, (100, 490))
                diamond_im = pygame.image.load(f"project-VAK/img/gui/money/diamond.png").convert_alpha()
                diamond_im = pygame.transform.scale(diamond_im, (int(diamond_im.get_width() * 3), int(diamond_im.get_height() * 3)))
                screen.blit(diamond_im,(870, 90))
                draw_text(f"{money_diamond}", font_3, (255,255,255), 980, 120)
                draw_text(f"{money_diamond}", font_3, (255,255,255), 980, 120)

                diamond_im_sml = pygame.image.load(f"project-VAK/img/gui/money/diamond_sml.png").convert_alpha()
                diamond_im_sml = pygame.transform.scale(diamond_im_sml, (int(diamond_im_sml.get_width() * 5), int(diamond_im_sml.get_height() * 5)))   
                screen.blit(diamond_im_sml, (320, 700))
                draw_text(f"cost: 10", font_3, (255,255,255), 80, 720)


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
                saving_game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False
                    saving_game()


    if current_window_selected == "junk":
        is_moving_left = False
        is_moving_right = False
        back_shop = pygame.image.load("project-VAK/img/gui/shops_back/junk.png").convert_alpha()
        back_shop = pygame.transform.scale(back_shop, (int(back_shop.get_width() * 2.8), int(back_shop.get_height() * 2.8)))
        screen.blit(back_shop, (650,0))
        screen.blit(back_shop, (-180,0))
        back_im = pygame.image.load("project-VAK/img/gui/button_back_for_food.png").convert_alpha()
        back_im_s = pygame.image.load("project-VAK/img/gui/button_back_for_food_select.png").convert_alpha()
        back_button = Button(1430, 20, back_im, 5, back_im_s)
        table_im = pygame.image.load("project-VAK/img/gui/shops_back/junk_table.png").convert_alpha()
        table_im = pygame.transform.scale(table_im, (int(table_im.get_width() * 9), int(table_im.get_height() * 8.35)))
        Robert.update()
        Robert.draw(screen, 1160, 175)
        table_r_im = pygame.image.load("project-VAK/img/gui/shops_back/robert_table.png").convert_alpha()
        table_r_im = pygame.transform.scale(table_r_im, (int(table_r_im.get_width() * 7), int(table_r_im.get_height() * 7)))
        screen.blit(table_im, (-120,-15))
        screen.blit(table_r_im, (1125, 615))
        if page == 1:
            upgrade_im = pygame.image.load("project-VAK/img/gui/button_up.png").convert_alpha()
            upgrade_select_im = pygame.image.load("project-VAK/img/gui/button_up_select.png").convert_alpha()
            craft_im = pygame.image.load("project-VAK/img/gui/button_craft.png").convert_alpha()
            craft_select_im = pygame.image.load("project-VAK/img/gui/button_craft_select.png").convert_alpha()
            
            play_im = pygame.image.load("project-VAK/img/gui/button_play.png").convert_alpha()
            play_select_im = pygame.image.load("project-VAK/img/gui/button_play_select.png").convert_alpha()
            

            button_upgrade = Button(20, 125, upgrade_im , 12, upgrade_select_im , upgrade_im )
            button_craft = Button(20, 365, craft_im, 12, craft_select_im, craft_im)
            button_play_game = Button(20, 602, play_im, 12, play_select_im)

            draw_text("upgrade your ship using", font_4, (26, 5, 5), 590, 135)
            draw_text("the parts that you get after", font_4, (26, 5, 5), 590, 185)
            draw_text("a sortie on the planet", font_4, (26, 5, 5), 590, 235)


            draw_text("Craft unique weapons using", font_4, (26, 5, 5), 590, 375)
            draw_text("the parts that you get after", font_4, (26, 5, 5), 590, 425)
            draw_text("a sortie on the planet", font_4, (26, 5, 5), 590, 475)


            draw_text("Play a 'fair' game with Robert", font_4, (26, 5, 5), 590, 635)
            draw_text("in which you can get loot", font_4, (26, 5, 5), 590, 685)

            if button_upgrade.draw(screen):
                page = 2
            if button_craft.draw(screen):
                page = 3
            if button_play_game.draw(screen):
                page = 4

        if page == 2:
            button_right_im = pygame.image.load("project-VAK/img/gui/button_left_junk.png").convert_alpha()
            button_right_im_press = pygame.image.load("project-VAK/img/gui/button_left_junk_press.png").convert_alpha()
            left_butt = Button(1020, 760, button_right_im, 6,button_right_im, button_right_im_press)
            if left_butt.draw(screen):
                page = 1
            week_stl_im = pygame.image.load("project-VAK/img/gui/money/week_steel.png").convert_alpha()
            week_stl_im = pygame.transform.scale(week_stl_im, (int(week_stl_im.get_width() * 3), int(week_stl_im.get_height() * 3)))
            screen.blit(week_stl_im, (20,35))
            steel_im = pygame.image.load("project-VAK/img/gui/money/steel.png").convert_alpha()
            steel_im = pygame.transform.scale(steel_im, (int(steel_im.get_width() * 3), int(steel_im.get_height() * 3)))
            screen.blit(steel_im, (100,30))
            gold_im = pygame.image.load("project-VAK/img/gui/money/gold.png").convert_alpha()
            gold_im = pygame.transform.scale(gold_im, (int(gold_im.get_width() * 3), int(gold_im.get_height() * 3)))
            screen.blit(gold_im, (180,30))
            better_steel_im = pygame.image.load("project-VAK/img/gui/money/better_steel.png").convert_alpha()
            better_steel_im = pygame.transform.scale(better_steel_im, (int(better_steel_im.get_width() * 3), int(better_steel_im.get_height() * 3)))
            screen.blit(better_steel_im, (260,30))
            def_detail_im = pygame.image.load("project-VAK/img/gui/money/def_detail.png").convert_alpha()
            def_detail_im = pygame.transform.scale(def_detail_im, (int(def_detail_im.get_width() * 3), int(def_detail_im.get_height() * 3)))
            screen.blit(def_detail_im, (380,40))
            black_detail_im = pygame.image.load("project-VAK/img/gui/money/black_detail.png").convert_alpha()
            black_detail_im = pygame.transform.scale(black_detail_im, (int(black_detail_im.get_width() * 3), int(black_detail_im.get_height() * 3)))
            screen.blit(black_detail_im, (460,40))
            water_detail_im = pygame.image.load("project-VAK/img/gui/money/water_detail.png").convert_alpha()
            water_detail_im = pygame.transform.scale(water_detail_im, (int(water_detail_im.get_width() * 3), int(water_detail_im.get_height() * 3)))
            screen.blit(water_detail_im, (540,40))
            toxic_detail_im = pygame.image.load("project-VAK/img/gui/money/toxic_detail.png").convert_alpha()
            toxic_detail_im = pygame.transform.scale(toxic_detail_im, (int(toxic_detail_im.get_width() * 3), int(toxic_detail_im.get_height() * 3)))
            screen.blit(toxic_detail_im, (620,40))
            rare_detail_im = pygame.image.load("project-VAK/img/gui/money/rare_detail.png").convert_alpha()
            rare_detail_im = pygame.transform.scale(rare_detail_im, (int(rare_detail_im.get_width() * 3), int(rare_detail_im.get_height() * 3)))
            screen.blit(rare_detail_im, (680,40))
            power_detail_im = pygame.image.load("project-VAK/img/gui/money/power_detail.png").convert_alpha()
            power_detail_im = pygame.transform.scale(power_detail_im, (int(power_detail_im.get_width() * 3), int(power_detail_im.get_height() * 3)))
            screen.blit(power_detail_im, (830,40))
            best_detail_im = pygame.image.load("project-VAK/img/gui/money/best_detail.png").convert_alpha()
            best_detail_im = pygame.transform.scale(best_detail_im, (int(best_detail_im.get_width() * 3), int(best_detail_im.get_height() * 3)))
            screen.blit(best_detail_im, (910,40))
            paporotnik_im = pygame.image.load("project-VAK/img/gui/money/paporotnik.png").convert_alpha()
            paporotnik_im = pygame.transform.scale(paporotnik_im, (int(paporotnik_im.get_width() * 3), int(paporotnik_im.get_height() * 3)))
            screen.blit(paporotnik_im, (1050,30))
            draw_text(f"{week_steel_cnt}", font_4, (255,255,255), 45, 95)
            draw_text(f"{steel_cnt}", font_4, (255,255,255), 125, 95)
            draw_text(f"{gold_cnt}", font_4, (255,255,255), 205, 95)
            draw_text(f"{better_stl_cnt}", font_4, (255,255,255), 285, 95)
            draw_text(f"{def_det_cnt}", font_4, (255,255,255), 405, 95)
            draw_text(f"{black_det_cnt}", font_4, (255,255,255), 485, 95)
            draw_text(f"{toxic_det_cnt}", font_4, (255,255,255), 640, 95)
            draw_text(f"{water_det_cnt}", font_4, (255,255,255), 565, 95)
            draw_text(f"{rare_det_cnt}", font_4, (255,255,255), 715, 95)
            draw_text(f"{power_det_cnt}", font_4, (255,255,255), 845, 95)
            draw_text(f"{best_det_cnt}", font_4, (255,255,255), 925, 95)
            draw_text(f"{grass_cnt}", font_4, (255,255,255), 1065, 95)
            upgrade_im = pygame.image.load("project-VAK/img/gui/button_up.png").convert_alpha()
            upgrade_select_im = pygame.image.load("project-VAK/img/gui/button_up_select.png").convert_alpha()
            button_upgrade = Button(450, 520, upgrade_im , 5, upgrade_select_im , upgrade_im)
            button_upgrade_antiglobal = Button(50, 800, upgrade_im , 5, upgrade_select_im , upgrade_im)
            if ship_level == 1:
                    

                ship_im = pygame.image.load("project-VAK/img/gui/ships/ship1.png").convert_alpha()
                ship_im = pygame.transform.scale(ship_im, (int(ship_im.get_width() * 4), int(ship_im.get_height() * 4)))
                draw_text(f"your ship level: 1", font_4, (255,205,205), 40, 198)
                draw_text(f"your ship level: 1", font_4, (255,255,255), 40, 200)
                draw_text(f"access to galaxies", font_4, (255,255,255), 40, 420)
                galaxy_1_for_ui.update()
                galaxy_1_for_ui.draw(screen, 7, 450)


                galaxy_1_for_ui.update()
                galaxy_1_for_ui.draw(screen, 717, 450)
                galaxy_2_for_ui.update()
                galaxy_2_for_ui.draw(screen, 817, 450)

                screen.blit(ship_im, (60, 190))
                ship_im_s = pygame.image.load("project-VAK/img/gui/ships/ship2.png").convert_alpha()
                ship_im_s = pygame.transform.scale(ship_im_s, (int(ship_im_s.get_width() * 4), int(ship_im_s.get_height() * 4)))
                draw_text(f"next ship level: 2", font_4, (60,255,60), 740, 198)
                draw_text(f"next ship level: 2", font_4, (255,255,255), 740, 200)
                draw_text(f"access to galaxies", font_4, (255,255,255), 740, 420)                
                screen.blit(ship_im_s, (650, 60))
                draw_text(f"->", font_2, (255,255,255), 415, 175)
                if to_next_lvl_ship == 0:
                    bar_to_ship = pygame.image.load("project-VAK/img/gui/proggress to next_ship_0.png").convert_alpha()
                    bar_to_ship = pygame.transform.scale(bar_to_ship, (int(bar_to_ship.get_width() * 7), int(bar_to_ship.get_height() * 7)))
                    screen.blit(bar_to_ship, (450, 420))
                    draw_text(f"details you need: 10         5", font_4, (255,255,255), 40, 750)
                    screen.blit(week_stl_im, (390,740))
                    screen.blit(def_detail_im, (520,745))
                    if week_steel_cnt >= 10 and def_det_cnt >= 5:
                        if button_upgrade_antiglobal.draw(screen):
                            for event in pygame.event.get():
                                if event.type ==pygame.MOUSEBUTTONUP:
                                    to_next_lvl_ship += 1
                                    week_steel_cnt -= 10
                                    def_det_cnt -= 5

                    else:
                        draw_text("not enough details", font_3, (255,255,255), 20, 820)
                if to_next_lvl_ship == 1:
                    bar_to_ship = pygame.image.load("project-VAK/img/gui/proggress to next_ship_1.png").convert_alpha()
                    bar_to_ship = pygame.transform.scale(bar_to_ship, (int(bar_to_ship.get_width() * 7), int(bar_to_ship.get_height() * 7)))
                    screen.blit(bar_to_ship, (450, 420))
                    draw_text(f"details you need:  1        5", font_4, (255,255,255), 40, 750)
                    screen.blit(power_detail_im, (390,740))
                    screen.blit(def_detail_im, (520,740))
                    if power_det_cnt >= 1 and def_det_cnt >= 5:
                        if button_upgrade_antiglobal.draw(screen):
                            for event in pygame.event.get():
                                if event.type ==pygame.MOUSEBUTTONUP:
                                    to_next_lvl_ship += 1
                                    power_det_cnt -= 1
                                    def_det_cnt -= 5
                    else:
                        draw_text("not enough details", font_3, (255,255,255), 20, 820)
                if to_next_lvl_ship == 2:
                    bar_to_ship = pygame.image.load("project-VAK/img/gui/proggress to next_ship_2.png").convert_alpha()
                    bar_to_ship = pygame.transform.scale(bar_to_ship, (int(bar_to_ship.get_width() * 7), int(bar_to_ship.get_height() * 7)))
                    screen.blit(bar_to_ship, (450, 420))   
                    draw_text(f"details you need: 20        2", font_4, (255,255,255), 40, 750)
                    screen.blit(week_stl_im, (390,740))
                    screen.blit(steel_im, (510,735))
                    if week_steel_cnt >= 20 and steel_cnt >= 2:
                        if button_upgrade_antiglobal.draw(screen):
                            for event in pygame.event.get():
                                if event.type ==pygame.MOUSEBUTTONUP:
                                    to_next_lvl_ship += 1
                                    week_steel_cnt -= 20
                                    steel_cnt -= 2
                    else:
                        draw_text("not enough details", font_3, (255,255,255), 20, 820)
                if to_next_lvl_ship == 3:
                    bar_to_ship = pygame.image.load("project-VAK/img/gui/proggress to next_ship_3.png").convert_alpha()
                    bar_to_ship = pygame.transform.scale(bar_to_ship, (int(bar_to_ship.get_width() * 7), int(bar_to_ship.get_height() * 7)))
                    screen.blit(bar_to_ship, (450, 420)) 
                    draw_text(f"details you need:  2 ", font_4, (255,255,255), 40, 750)
                    screen.blit(power_detail_im, (390,740))
                    if power_det_cnt >= 2:
                        if button_upgrade_antiglobal.draw(screen):
                            for event in pygame.event.get():
                                if event.type == pygame.MOUSEBUTTONUP:
                                    to_next_lvl_ship += 1
                                    power_det_cnt -= 2
                    else:
                        draw_text("not enough details", font_3, (255,255,255), 20, 820)
                if to_next_lvl_ship == 4:
                    bar_to_ship = pygame.image.load("project-VAK/img/gui/proggress to next_ship_4.png").convert_alpha()
                    bar_to_ship = pygame.transform.scale(bar_to_ship, (int(bar_to_ship.get_width() * 7), int(bar_to_ship.get_height() * 7)))
                    screen.blit(bar_to_ship, (450, 420))
                    draw_text(f"details you need:  5", font_4, (255,255,255), 40, 750)
                    screen.blit(steel_im, (395,735)) 
                    if steel_cnt >= 5:
                        if button_upgrade_antiglobal.draw(screen):
                            for event in pygame.event.get():
                                if event.type ==pygame.MOUSEBUTTONUP:
                                    to_next_lvl_ship += 1
                                    steel_cnt -= 5
                    else:
                        draw_text("not enough details", font_3, (255,255,255), 20, 820)
                if to_next_lvl_ship == 5:
                    bar_to_ship = pygame.image.load("project-VAK/img/gui/proggress to next_ship_5.png").convert_alpha()
                    bar_to_ship = pygame.transform.scale(bar_to_ship, (int(bar_to_ship.get_width() * 7), int(bar_to_ship.get_height() * 7)))
                    screen.blit(bar_to_ship, (450, 420))
                    draw_text(f"now you can upgrade your ship", font_4, (255,255,255), 40, 750)
                    if button_upgrade.draw(screen):
                        ship_level = 2
                        to_next_lvl_ship = 0
            if ship_level == 2:
                ship_im = pygame.image.load("project-VAK/img/gui/ships/ship2.png").convert_alpha()
                ship_im = pygame.transform.scale(ship_im, (int(ship_im.get_width() * 4), int(ship_im.get_height() * 4)))
                draw_text(f"your ship level: 2", font_4, (60,255,60), 40, 198)
                draw_text(f"your ship level: 2", font_4, (255,255,255), 40, 200)
                draw_text(f"access to galaxies", font_4, (255,255,255), 40, 420)
                galaxy_1_for_ui.update()
                galaxy_1_for_ui.draw(screen, 7, 450)
                galaxy_2_for_ui.update()
                galaxy_2_for_ui.draw(screen, 107, 450)


                galaxy_1_for_ui.update()
                galaxy_1_for_ui.draw(screen, 717, 450)
                galaxy_2_for_ui.update()
                galaxy_2_for_ui.draw(screen, 817, 450)
                galaxy_3_for_ui.update()
                galaxy_3_for_ui.draw(screen, 917, 450)
                screen.blit(ship_im, (-50, 60))
                ship_im_s = pygame.image.load("project-VAK/img/gui/ships/ship3.png").convert_alpha()
                ship_im_s = pygame.transform.scale(ship_im_s, (int(ship_im_s.get_width() * 4), int(ship_im_s.get_height() * 4)))
                draw_text(f"next ship level: 3", font_4, (255,255,10), 740, 198)
                draw_text(f"next ship level: 3", font_4, (255,255,255), 740, 200)
                draw_text(f"access to galaxies", font_4, (255,255,255), 740, 420)                
                screen.blit(ship_im_s, (650, 60))
                draw_text(f"->", font_2, (255,255,255), 415, 175)
                if to_next_lvl_ship == 0:
                    bar_to_ship = pygame.image.load("project-VAK/img/gui/proggress to next_ship_0.png").convert_alpha()
                    bar_to_ship = pygame.transform.scale(bar_to_ship, (int(bar_to_ship.get_width() * 7), int(bar_to_ship.get_height() * 7)))
                    screen.blit(bar_to_ship, (450, 420))
                    draw_text(f"details you need: 30        10", font_4, (255,255,255), 40, 750)
                    screen.blit(week_stl_im, (390,740))
                    screen.blit(def_detail_im, (530,745))
                    if week_steel_cnt >= 30 and def_det_cnt >= 10:
                        if button_upgrade_antiglobal.draw(screen):
                            for event in pygame.event.get():
                                if event.type ==pygame.MOUSEBUTTONUP:
                                    to_next_lvl_ship += 1
                                    week_steel_cnt -= 30
                                    def_det_cnt -= 10 
                    else:
                        draw_text("not enough details", font_3, (255,255,255), 20, 820)
                if to_next_lvl_ship == 1:
                    bar_to_ship = pygame.image.load("project-VAK/img/gui/proggress to next_ship_1.png").convert_alpha()
                    bar_to_ship = pygame.transform.scale(bar_to_ship, (int(bar_to_ship.get_width() * 7), int(bar_to_ship.get_height() * 7)))
                    screen.blit(bar_to_ship, (450, 420))
                    draw_text(f"details you need:  1        15", font_4, (255,255,255), 40, 750)
                    screen.blit(power_detail_im, (390,740))
                    screen.blit(def_detail_im, (520,740))
                    if power_det_cnt >= 1 and def_det_cnt >= 15:
                        if button_upgrade_antiglobal.draw(screen):
                            for event in pygame.event.get():
                                if event.type ==pygame.MOUSEBUTTONUP:
                                    to_next_lvl_ship += 1
                                    power_det_cnt -= 1
                                    def_det_cnt -= 15
                    else:
                        draw_text("not enough details", font_3, (255,255,255), 20, 820)
                if to_next_lvl_ship == 2:
                    bar_to_ship = pygame.image.load("project-VAK/img/gui/proggress to next_ship_2.png").convert_alpha()
                    bar_to_ship = pygame.transform.scale(bar_to_ship, (int(bar_to_ship.get_width() * 7), int(bar_to_ship.get_height() * 7)))
                    screen.blit(bar_to_ship, (450, 420))    
                    draw_text(f"details you need:  5        5", font_4, (255,255,255), 40, 750)
                    screen.blit(steel_im, (390,735)) 
                    screen.blit(def_detail_im, (520,740))
                    if steel_cnt >= 5 and def_det_cnt >= 5:
                        if button_upgrade_antiglobal.draw(screen):
                            for event in pygame.event.get():
                                if event.type ==pygame.MOUSEBUTTONUP:
                                    to_next_lvl_ship += 1
                                    steel_cnt -= 5
                                    def_det_cnt -= 5
                    else:
                        draw_text("not enough details", font_3, (255,255,255), 20, 820)
                if to_next_lvl_ship == 3:
                    bar_to_ship = pygame.image.load("project-VAK/img/gui/proggress to next_ship_3.png").convert_alpha()
                    bar_to_ship = pygame.transform.scale(bar_to_ship, (int(bar_to_ship.get_width() * 7), int(bar_to_ship.get_height() * 7)))
                    screen.blit(bar_to_ship, (450, 420))    
                    draw_text(f"details you need:  5         3", font_4, (255,255,255), 40, 750)
                    screen.blit(steel_im, (390,735)) 
                    screen.blit(power_detail_im, (520,740))
                    if steel_cnt >= 5 and power_det_cnt >= 3:
                        if button_upgrade_antiglobal.draw(screen):
                            for event in pygame.event.get():
                                if event.type ==pygame.MOUSEBUTTONUP:
                                    to_next_lvl_ship += 1
                                    steel_cnt -= 5
                                    power_det_cnt -= 3
                    else:
                        draw_text("not enough details", font_3, (255,255,255), 20, 820)
                if to_next_lvl_ship == 4:
                    bar_to_ship = pygame.image.load("project-VAK/img/gui/proggress to next_ship_4.png").convert_alpha()
                    bar_to_ship = pygame.transform.scale(bar_to_ship, (int(bar_to_ship.get_width() * 7), int(bar_to_ship.get_height() * 7)))
                    screen.blit(bar_to_ship, (450, 420))
                    draw_text(f"details you need:  2        ", font_4, (255,255,255), 40, 750)
                    screen.blit(black_detail_im, (390,740)) 
                    if black_det_cnt >= 2:
                        if button_upgrade_antiglobal.draw(screen):
                            for event in pygame.event.get():
                                if event.type ==pygame.MOUSEBUTTONUP:
                                    to_next_lvl_ship += 1
                                    black_det_cnt -= 2
                    else:
                        draw_text("not enough details", font_3, (255,255,255), 20, 820)
                if to_next_lvl_ship == 5:
                    bar_to_ship = pygame.image.load("project-VAK/img/gui/proggress to next_ship_5.png").convert_alpha()
                    bar_to_ship = pygame.transform.scale(bar_to_ship, (int(bar_to_ship.get_width() * 7), int(bar_to_ship.get_height() * 7)))
                    screen.blit(bar_to_ship, (450, 420))
                    if button_upgrade.draw(screen):
                        ship_level = 3
                        to_next_lvl_ship = 0





            if ship_level == 3:
                ship_im = pygame.image.load("project-VAK/img/gui/ships/ship3.png").convert_alpha()
                ship_im = pygame.transform.scale(ship_im, (int(ship_im.get_width() * 4), int(ship_im.get_height() * 4)))
                draw_text(f"your ship level: 3", font_4, (255,255,10), 40, 198)
                draw_text(f"your ship level: 3", font_4, (255,255,255), 40, 200)
                draw_text(f"access to galaxies", font_4, (255,255,255), 40, 420)
                galaxy_1_for_ui.update()
                galaxy_1_for_ui.draw(screen, 7, 450)
                galaxy_2_for_ui.update()
                galaxy_2_for_ui.draw(screen, 107, 450)
                galaxy_3_for_ui.update()
                galaxy_3_for_ui.draw(screen, 207, 450)


                galaxy_1_for_ui.update()
                galaxy_1_for_ui.draw(screen, 717, 450)
                galaxy_2_for_ui.update()
                galaxy_2_for_ui.draw(screen, 817, 450)
                galaxy_3_for_ui.update()
                galaxy_3_for_ui.draw(screen, 917, 450)
                galaxy_4_for_ui.update()
                galaxy_4_for_ui.draw(screen, 717, 570)
                screen.blit(ship_im, (-50, 60))
                ship_im_s = pygame.image.load("project-VAK/img/gui/ships/ship4.png").convert_alpha()
                ship_im_s = pygame.transform.scale(ship_im_s, (int(ship_im_s.get_width() * 3.5), int(ship_im_s.get_height() * 3.5)))
                draw_text(f"next ship level: 4", font_4, (255,55,200), 740, 198)
                draw_text(f"next ship level: 4", font_4, (255,255,255), 740, 200)
                draw_text(f"access to galaxies", font_4, (255,255,255), 740, 420)                
                screen.blit(ship_im_s, (690, 90))
                draw_text(f"->", font_2, (255,255,255), 415, 175)
                if to_next_lvl_ship == 0:
                    bar_to_ship = pygame.image.load("project-VAK/img/gui/proggress to next_ship_0.png").convert_alpha()
                    bar_to_ship = pygame.transform.scale(bar_to_ship, (int(bar_to_ship.get_width() * 7), int(bar_to_ship.get_height() * 7)))
                    screen.blit(bar_to_ship, (450, 420))
                    draw_text(f"details you need: 10        10", font_4, (255,255,255), 40, 750)
                    screen.blit(steel_im, (390,735)) 
                    screen.blit(def_detail_im, (520,745))
                    if steel_cnt >= 10 and def_det_cnt >= 10:
                        if button_upgrade_antiglobal.draw(screen):
                            for event in pygame.event.get():
                                if event.type ==pygame.MOUSEBUTTONUP:
                                    to_next_lvl_ship += 1
                                    steel_cnt -= 10
                                    def_det_cnt -= 10
                    else:
                        draw_text("not enough details", font_3, (255,255,255), 20, 820)
                if to_next_lvl_ship == 1:
                    bar_to_ship = pygame.image.load("project-VAK/img/gui/proggress to next_ship_1.png").convert_alpha()
                    bar_to_ship = pygame.transform.scale(bar_to_ship, (int(bar_to_ship.get_width() * 7), int(bar_to_ship.get_height() * 7)))
                    screen.blit(bar_to_ship, (450, 420))
                    draw_text(f"details you need:  5        35", font_4, (255,255,255), 40, 750)
                    screen.blit(power_detail_im, (390,735)) 
                    screen.blit(week_stl_im, (520,735))
                    if power_det_cnt >= 5 and week_steel_cnt >= 35:
                        if button_upgrade_antiglobal.draw(screen):
                            for event in pygame.event.get():
                                if event.type ==pygame.MOUSEBUTTONUP:
                                    to_next_lvl_ship += 1
                                    power_det_cnt -= 5
                                    week_steel_cnt -= 35
                    else:
                        draw_text("not enough details", font_3, (255,255,255), 20, 820)
                if to_next_lvl_ship == 2:
                    bar_to_ship = pygame.image.load("project-VAK/img/gui/proggress to next_ship_2.png").convert_alpha()
                    bar_to_ship = pygame.transform.scale(bar_to_ship, (int(bar_to_ship.get_width() * 7), int(bar_to_ship.get_height() * 7)))
                    screen.blit(bar_to_ship, (450, 420))
                    draw_text(f"details you need: 10         2", font_4, (255,255,255), 40, 750)
                    screen.blit(steel_im, (390,735)) 
                    screen.blit(black_detail_im, (520,745))
                    if steel_cnt >= 10 and black_det_cnt >= 2:
                        if button_upgrade_antiglobal.draw(screen):
                            for event in pygame.event.get():
                                if event.type ==pygame.MOUSEBUTTONUP:
                                    to_next_lvl_ship += 1
                                    steel_cnt -= 10
                                    black_det_cnt -= 2
                    else:
                        draw_text("not enough details", font_3, (255,255,255), 20, 820)
                if to_next_lvl_ship == 3:
                    bar_to_ship = pygame.image.load("project-VAK/img/gui/proggress to next_ship_3.png").convert_alpha()
                    bar_to_ship = pygame.transform.scale(bar_to_ship, (int(bar_to_ship.get_width() * 7), int(bar_to_ship.get_height() * 7)))
                    screen.blit(bar_to_ship, (450, 420)) 
                    draw_text(f"details you need: 15         3", font_4, (255,255,255), 40, 750)
                    screen.blit(def_detail_im, (390,745)) 
                    screen.blit(power_detail_im, (520,740))
                    if def_det_cnt >= 15 and power_det_cnt >= 3:
                        if button_upgrade_antiglobal.draw(screen):
                            for event in pygame.event.get():
                                if event.type ==pygame.MOUSEBUTTONUP:
                                    to_next_lvl_ship += 1
                                    def_det_cnt -= 15
                                    power_det_cnt -= 3
                    else:
                        draw_text("not enough details", font_3, (255,255,255), 20, 820)
                if to_next_lvl_ship == 4:
                    bar_to_ship = pygame.image.load("project-VAK/img/gui/proggress to next_ship_4.png").convert_alpha()
                    bar_to_ship = pygame.transform.scale(bar_to_ship, (int(bar_to_ship.get_width() * 7), int(bar_to_ship.get_height() * 7)))
                    screen.blit(bar_to_ship, (450, 420))
                    draw_text(f"details you need:  1", font_4, (255,255,255), 40, 750)
                    screen.blit(rare_detail_im, (390,740))   
                    if rare_det_cnt >= 1:
                        if button_upgrade_antiglobal.draw(screen):
                            for event in pygame.event.get():
                                if event.type ==pygame.MOUSEBUTTONUP:
                                    to_next_lvl_ship += 1
                                    rare_det_cnt -= 1
                    else:
                        draw_text("not enough details", font_3, (255,255,255), 20, 820)
                if to_next_lvl_ship == 5:
                    bar_to_ship = pygame.image.load("project-VAK/img/gui/proggress to next_ship_5.png").convert_alpha()
                    bar_to_ship = pygame.transform.scale(bar_to_ship, (int(bar_to_ship.get_width() * 7), int(bar_to_ship.get_height() * 7)))
                    screen.blit(bar_to_ship, (450, 420))
                    if button_upgrade.draw(screen):
                        ship_level = 4
                        to_next_lvl_ship = 0
            if ship_level == 4:
                ship_im = pygame.image.load("project-VAK/img/gui/ships/ship4.png").convert_alpha()
                ship_im = pygame.transform.scale(ship_im, (int(ship_im.get_width() * 3.5), int(ship_im.get_height() * 3.5)))
                draw_text(f"your ship level: 4", font_4, (255,55,200), 40, 198)
                draw_text(f"your ship level: 4", font_4, (255,255,255), 40, 200)
                draw_text(f"access to galaxies", font_4, (255,255,255), 40, 420)
                galaxy_1_for_ui.update()
                galaxy_1_for_ui.draw(screen, 7, 450)
                galaxy_2_for_ui.update()
                galaxy_2_for_ui.draw(screen, 107, 450)
                galaxy_3_for_ui.update()
                galaxy_3_for_ui.draw(screen, 207, 450)
                galaxy_4_for_ui.update()
                galaxy_4_for_ui.draw(screen, 7, 570)


                galaxy_1_for_ui.update()
                galaxy_1_for_ui.draw(screen, 717, 450)
                galaxy_2_for_ui.update()
                galaxy_2_for_ui.draw(screen, 817, 450)
                galaxy_3_for_ui.update()
                galaxy_3_for_ui.draw(screen, 917, 450)
                galaxy_4_for_ui.update()
                galaxy_4_for_ui.draw(screen, 717, 570)
                galaxy_5_for_ui.update()
                galaxy_5_for_ui.draw(screen, 817, 570)
                screen.blit(ship_im, (-30, 90))
                ship_im_s = pygame.image.load("project-VAK/img/gui/ships/ship5.png").convert_alpha()
                ship_im_s = pygame.transform.scale(ship_im_s, (int(ship_im_s.get_width() * 3), int(ship_im_s.get_height() * 3)))
                draw_text(f"next ship level: 5", font_4, (235, 186, 52), 740, 188)
                draw_text(f"next ship level: 5", font_4, (255,255,255), 740, 190)
                draw_text(f"access to galaxies", font_4, (255,255,255), 740, 420)                
                screen.blit(ship_im_s, (720, 120))
                draw_text(f"->", font_2, (255,255,255), 415, 175)
                if to_next_lvl_ship == 0:
                    bar_to_ship = pygame.image.load("project-VAK/img/gui/proggress to next_ship_0.png").convert_alpha()
                    bar_to_ship = pygame.transform.scale(bar_to_ship, (int(bar_to_ship.get_width() * 7), int(bar_to_ship.get_height() * 7)))
                    screen.blit(bar_to_ship, (450, 420))
                    draw_text(f"details you need: 25         5", font_4, (255,255,255), 40, 750)
                    screen.blit(steel_im, (390,735)) 
                    screen.blit(power_detail_im, (520,740))
                    if steel_cnt >= 25 and power_det_cnt >= 5:
                        if button_upgrade_antiglobal.draw(screen):
                            for event in pygame.event.get():
                                if event.type ==pygame.MOUSEBUTTONUP:
                                    to_next_lvl_ship += 1
                                    steel_cnt -= 25
                                    power_det_cnt -= 5
                    else:
                        draw_text("not enough details", font_3, (255,255,255), 20, 820)
                if to_next_lvl_ship == 1:
                    bar_to_ship = pygame.image.load("project-VAK/img/gui/proggress to next_ship_1.png").convert_alpha()
                    bar_to_ship = pygame.transform.scale(bar_to_ship, (int(bar_to_ship.get_width() * 7), int(bar_to_ship.get_height() * 7)))
                    screen.blit(bar_to_ship, (450, 420))
                    draw_text(f"details you need:  3         5", font_4, (255,255,255), 40, 750)
                    screen.blit(toxic_detail_im, (390,740)) 
                    screen.blit(gold_im, (520,735))
                    if toxic_det_cnt >= 3 and gold_cnt >= 5:
                        if button_upgrade_antiglobal.draw(screen):
                            for event in pygame.event.get():
                                if event.type ==pygame.MOUSEBUTTONUP:
                                    to_next_lvl_ship += 1
                                    toxic_det_cnt -= 3
                                    gold_cnt -= 5
                    else:
                        draw_text("not enough details", font_3, (255,255,255), 20, 820)
                if to_next_lvl_ship == 2:
                    bar_to_ship = pygame.image.load("project-VAK/img/gui/proggress to next_ship_2.png").convert_alpha()
                    bar_to_ship = pygame.transform.scale(bar_to_ship, (int(bar_to_ship.get_width() * 7), int(bar_to_ship.get_height() * 7)))
                    screen.blit(bar_to_ship, (450, 420))    
                    draw_text(f"details you need: 15        20", font_4, (255,255,255), 40, 750)
                    screen.blit(black_detail_im, (390,745)) 
                    screen.blit(steel_im, (520,735))
                    if black_det_cnt >= 15 and steel_cnt >= 20:
                        if button_upgrade_antiglobal.draw(screen):
                            for event in pygame.event.get():
                                if event.type ==pygame.MOUSEBUTTONUP:
                                    to_next_lvl_ship += 1
                                    black_det_cnt -= 15
                                    steel_cnt -= 20
                    else:
                        draw_text("not enough details", font_3, (255,255,255), 20, 820)
                if to_next_lvl_ship == 3:
                    bar_to_ship = pygame.image.load("project-VAK/img/gui/proggress to next_ship_3.png").convert_alpha()
                    bar_to_ship = pygame.transform.scale(bar_to_ship, (int(bar_to_ship.get_width() * 7), int(bar_to_ship.get_height() * 7)))
                    screen.blit(bar_to_ship, (450, 420))  
                    draw_text(f"details you need:   1        50", font_4, (255,255,255), 40, 750)
                    screen.blit(rare_detail_im, (390,745)) 
                    screen.blit(week_stl_im, (520,740))
                    if rare_det_cnt >= 1 and week_steel_cnt >= 50:
                        if button_upgrade_antiglobal.draw(screen):
                            for event in pygame.event.get():
                                if event.type ==pygame.MOUSEBUTTONUP:
                                    to_next_lvl_ship += 1
                                    rare_det_cnt -= 1
                                    week_steel_cnt -= 50
                    else:
                        draw_text("not enough details", font_3, (255,255,255), 20, 820)
                if to_next_lvl_ship == 4:
                    bar_to_ship = pygame.image.load("project-VAK/img/gui/proggress to next_ship_4.png").convert_alpha()
                    bar_to_ship = pygame.transform.scale(bar_to_ship, (int(bar_to_ship.get_width() * 7), int(bar_to_ship.get_height() * 7)))
                    screen.blit(bar_to_ship, (450, 420))    
                    draw_text(f"details you need: 10         1", font_4, (255,255,255), 40, 750)
                    screen.blit(gold_im, (390,740)) 
                    screen.blit(best_detail_im, (520,740))
                    if gold_cnt >= 10 and best_det_cnt >= 1:
                        if button_upgrade_antiglobal.draw(screen):
                            for event in pygame.event.get():
                                if event.type ==pygame.MOUSEBUTTONUP:
                                    to_next_lvl_ship += 1
                                    gold_cnt -= 10
                                    best_det_cnt -= 1
                    else:
                        draw_text("not enough details", font_3, (255,255,255), 20, 820)
                if to_next_lvl_ship == 5:
                    bar_to_ship = pygame.image.load("project-VAK/img/gui/proggress to next_ship_5.png").convert_alpha()
                    bar_to_ship = pygame.transform.scale(bar_to_ship, (int(bar_to_ship.get_width() * 7), int(bar_to_ship.get_height() * 7)))
                    screen.blit(bar_to_ship, (450, 420))
                    if button_upgrade.draw(screen):
                        ship_level = 5
                        to_next_lvl_ship = 0
            if ship_level == 5:
                ship_im = pygame.image.load("project-VAK/img/gui/ships/ship5.png").convert_alpha()
                ship_im = pygame.transform.scale(ship_im, (int(ship_im.get_width() * 3), int(ship_im.get_height() * 3)))
                draw_text(f"your ship level: 5", font_4, (235, 186, 52), 40, 188)
                draw_text(f"your ship level: 5", font_4, (255,255,255), 40, 190)
                draw_text(f"access to galaxies", font_4, (255,255,255), 40, 420)
                galaxy_1_for_ui.update()
                galaxy_1_for_ui.draw(screen, 7, 450)
                galaxy_2_for_ui.update()
                galaxy_2_for_ui.draw(screen, 107, 450)
                galaxy_3_for_ui.update()
                galaxy_3_for_ui.draw(screen, 207, 450)
                galaxy_4_for_ui.update()
                galaxy_4_for_ui.draw(screen, 7, 570)
                galaxy_5_for_ui.update()
                galaxy_5_for_ui.draw(screen, 107, 570)


                galaxy_1_for_ui.update()
                galaxy_1_for_ui.draw(screen, 717, 450)
                galaxy_2_for_ui.update()
                galaxy_2_for_ui.draw(screen, 817, 450)
                galaxy_3_for_ui.update()
                galaxy_3_for_ui.draw(screen, 917, 450)
                galaxy_4_for_ui.update()
                galaxy_4_for_ui.draw(screen, 717, 570)
                galaxy_5_for_ui.update()
                galaxy_5_for_ui.draw(screen, 817, 570)
                galaxy_6_for_ui.update()
                galaxy_6_for_ui.draw(screen, 917, 570)
                screen.blit(ship_im, (20, 120))
                ship_im_s = pygame.image.load("project-VAK/img/gui/ships/ship6.png").convert_alpha()
                ship_im_s = pygame.transform.scale(ship_im_s, (int(ship_im_s.get_width() * 2.6), int(ship_im_s.get_height() * 2.6)))
                draw_text(f"next ship level: 6", font_4, (255,0,90), 740, 188)
                draw_text(f"next ship level: 6", font_4, (255,255,255), 740, 190)
                draw_text(f"access to galaxies", font_4, (255,255,255), 740, 420)                
                screen.blit(ship_im_s, (735, 152))
                draw_text(f"->", font_2, (255,255,255), 415, 175)
                if to_next_lvl_ship == 0:
                    bar_to_ship = pygame.image.load("project-VAK/img/gui/proggress to next_ship_0.png").convert_alpha()
                    bar_to_ship = pygame.transform.scale(bar_to_ship, (int(bar_to_ship.get_width() * 7), int(bar_to_ship.get_height() * 7)))
                    screen.blit(bar_to_ship, (450, 420))
                    draw_text(f"details you need: 20        45", font_4, (255,255,255), 40, 750)
                    screen.blit(gold_im, (390,740)) 
                    screen.blit(steel_im, (520,735))
                    if gold_cnt >= 20 and steel_cnt >= 45:
                        if button_upgrade_antiglobal.draw(screen):
                            for event in pygame.event.get():
                                if event.type ==pygame.MOUSEBUTTONUP:
                                    to_next_lvl_ship += 1
                                    gold_cnt -= 20
                                    steel_cnt -= 45
                    else:
                        draw_text("not enough details", font_3, (255,255,255), 20, 820)
                if to_next_lvl_ship == 1:
                    bar_to_ship = pygame.image.load("project-VAK/img/gui/proggress to next_ship_1.png").convert_alpha()
                    bar_to_ship = pygame.transform.scale(bar_to_ship, (int(bar_to_ship.get_width() * 7), int(bar_to_ship.get_height() * 7)))
                    screen.blit(bar_to_ship, (450, 420))
                    draw_text(f"details you need:  5         5", font_4, (255,255,255), 40, 750)
                    screen.blit(best_detail_im, (390,740)) 
                    screen.blit(rare_detail_im, (520,740))
                    if best_det_cnt >= 5 and rare_det_cnt >= 5:
                        if button_upgrade_antiglobal.draw(screen):
                            for event in pygame.event.get():
                                if event.type ==pygame.MOUSEBUTTONUP:
                                    to_next_lvl_ship += 1
                                    best_det_cnt -= 5
                                    rare_det_cnt -= 5
                    else:
                        draw_text("not enough details", font_3, (255,255,255), 20, 820)
                if to_next_lvl_ship == 2:
                    bar_to_ship = pygame.image.load("project-VAK/img/gui/proggress to next_ship_2.png").convert_alpha()
                    bar_to_ship = pygame.transform.scale(bar_to_ship, (int(bar_to_ship.get_width() * 7), int(bar_to_ship.get_height() * 7)))
                    screen.blit(bar_to_ship, (450, 420))    
                    draw_text(f"details you need: 10        20", font_4, (255,255,255), 40, 750)
                    screen.blit(paporotnik_im, (390,730)) 
                    screen.blit(toxic_detail_im, (520,740))
                    if grass_cnt >= 20 and toxic_det_cnt >= 20:
                        if button_upgrade_antiglobal.draw(screen):
                            for event in pygame.event.get():
                                if event.type ==pygame.MOUSEBUTTONUP:
                                    to_next_lvl_ship += 1
                                    grass_cnt -= 20
                                    toxic_det_cnt -= 20
                    else:
                        draw_text("not enough details", font_3, (255,255,255), 20, 820)
                if to_next_lvl_ship == 3:
                    bar_to_ship = pygame.image.load("project-VAK/img/gui/proggress to next_ship_3.png").convert_alpha()
                    bar_to_ship = pygame.transform.scale(bar_to_ship, (int(bar_to_ship.get_width() * 7), int(bar_to_ship.get_height() * 7)))
                    screen.blit(bar_to_ship, (450, 420))   
                    draw_text(f"details you need: 30        30", font_4, (255,255,255), 40, 750)
                    screen.blit(gold_im, (390,740)) 
                    screen.blit(water_detail_im, (520,745))
                    if week_steel_cnt >= 30 and water_det_cnt >= 30:
                        if button_upgrade_antiglobal.draw(screen):
                            for event in pygame.event.get():
                                if event.type ==pygame.MOUSEBUTTONUP:
                                    to_next_lvl_ship += 1
                                    week_steel_cnt -= 30
                                    water_det_cnt -= 30
                    else:
                        draw_text("not enough details", font_3, (255,255,255), 20, 820)
                if to_next_lvl_ship == 4:
                    bar_to_ship = pygame.image.load("project-VAK/img/gui/proggress to next_ship_4.png").convert_alpha()
                    bar_to_ship = pygame.transform.scale(bar_to_ship, (int(bar_to_ship.get_width() * 7), int(bar_to_ship.get_height() * 7)))
                    screen.blit(bar_to_ship, (450, 420))    
                    draw_text(f"details you need: 30        20", font_4, (255,255,255), 40, 750)
                    screen.blit(black_detail_im, (390,740)) 
                    screen.blit(paporotnik_im, (520,730))
                    if black_det_cnt >= 30 and grass_cnt >= 20:
                        if button_upgrade_antiglobal.draw(screen):
                            for event in pygame.event.get():
                                if event.type ==pygame.MOUSEBUTTONUP:
                                    to_next_lvl_ship += 1
                                    grass_cnt -= 20
                                    black_det_cnt -= 30
                    else:
                        draw_text("not enough details", font_3, (255,255,255), 20, 820)
                if to_next_lvl_ship == 5:
                    bar_to_ship = pygame.image.load("project-VAK/img/gui/proggress to next_ship_5.png").convert_alpha()
                    bar_to_ship = pygame.transform.scale(bar_to_ship, (int(bar_to_ship.get_width() * 7), int(bar_to_ship.get_height() * 7)))
                    screen.blit(bar_to_ship, (450, 420))
                    if skill_player_have[13] == 0:
                        # you can't upgrade your ship to level 6 if you dont have perk 'black matter'
                        draw_text("you can't upgrade", font_5, (255,255,255), 450, 510)
                        draw_text("your ship to level 6", font_5, (255,255,255), 430, 560)
                        draw_text("if you dont have perk", font_5, (255,255,255), 430, 610)
                        draw_text("'black matter'", font_5, (255,255,255), 470, 660)
                        black = pygame.image.load("project-VAK/img/gui/skills/black.png").convert_alpha()
                        black = pygame.transform.scale(black, (int(black.get_width() * 1), int(black.get_height() * 1)))
                        screen.blit(black, (515, 700))
                    
                    else:
                        if button_upgrade.draw(screen):
                            ship_level = 6
                            to_next_lvl_ship = 0
            if ship_level == 6:
                ship_im = pygame.image.load("project-VAK/img/gui/ships/ship6.png").convert_alpha()
                ship_im = pygame.transform.scale(ship_im, (int(ship_im.get_width() * 2.6), int(ship_im.get_height() * 2.6)))
                draw_text(f"your ship level: 6", font_4, (235, 186, 52), 40, 188)
                draw_text(f"your ship level: 6", font_4, (255,255,255), 40, 190)
                draw_text(f"access to galaxies", font_4, (255,255,255), 40, 420)
                galaxy_1_for_ui.update()
                galaxy_1_for_ui.draw(screen, 7, 450)
                galaxy_2_for_ui.update()
                galaxy_2_for_ui.draw(screen, 107, 450)
                galaxy_3_for_ui.update()
                galaxy_3_for_ui.draw(screen, 207, 450)
                galaxy_4_for_ui.update()
                galaxy_4_for_ui.draw(screen, 7, 570)
                galaxy_5_for_ui.update()
                galaxy_5_for_ui.draw(screen, 107, 570)      
                galaxy_6_for_ui.update()
                galaxy_6_for_ui.draw(screen, 207, 570)   
                screen.blit(ship_im, (20, 150))
                draw_text(f"this is maximum. now you can travel", font_4, (104, 104, 104), 500, 186)
                draw_text(f"this is maximum. now you can travel", font_4, (255,255,255), 500, 188)
                draw_text(f"to all planets in all galaxies.", font_4, (104, 104, 104), 500, 226)
                draw_text(f"to all planets in all galaxies.", font_4, (255,255,255), 500, 228)
                draw_text(f"improve your equipment, develop", font_4, (104, 104, 104), 500, 266)
                draw_text(f"improve your equipment, develop", font_4, (255,255,255), 500, 268)
                draw_text(f"your skills.", font_4, (104, 104, 104), 500, 308) 
                draw_text(f"your skills.", font_4, (255,255,255), 500, 308) 
                draw_text(f"when you're ready, go to planet V", font_4, (104, 104, 104), 500, 346)
                draw_text(f"when you're ready, go to planet V", font_4, (255,255,255), 500, 348)
                draw_text(f"to defeat the ruler of the universe", font_4, (104, 104, 104), 500, 386)
                draw_text(f"to defeat the ruler of the universe", font_4, (255,255,255), 500, 388)
        if page == 3:
            sml_button_empty = pygame.image.load("project-VAK/img/gui/empty_small_junk.png").convert_alpha()
            sml_button_empty = pygame.transform.scale(sml_button_empty, (int(sml_button_empty.get_width() * 1), int(sml_button_empty.get_height() * 1)))
            sml_button_clossed = pygame.image.load("project-VAK/img/gui/closed_small_junk.png").convert_alpha()
            sml_button_clossed = pygame.transform.scale(sml_button_clossed, (int(sml_button_clossed.get_width() * 1), int(sml_button_clossed.get_height() * 1)))
            sml_button_yes = pygame.image.load("project-VAK/img/gui/yes_small_junk.png").convert_alpha()
            sml_button_yes = pygame.transform.scale(sml_button_yes, (int(sml_button_yes.get_width() * 1), int(sml_button_yes.get_height() * 1)))
            junkgun_1 = pygame.image.load("project-VAK/img/gui/guns/junk1.png").convert_alpha()
            junkgun_1 = pygame.transform.scale(junkgun_1, (int(junkgun_1.get_width() * 6), int(junkgun_1.get_height() * 6)))
            screen.blit(junkgun_1, (20, 70))
            junkgun_2 = pygame.image.load("project-VAK/img/gui/guns/junk2.png").convert_alpha()
            junkgun_2 = pygame.transform.scale(junkgun_2, (int(junkgun_2.get_width() * 6), int(junkgun_2.get_height() * 6)))
            screen.blit(junkgun_2, (20, 220))
            junkgun_3 = pygame.image.load("project-VAK/img/gui/guns/junk3-20.png").convert_alpha()
            junkgun_3 = pygame.transform.scale(junkgun_3, (int(junkgun_3.get_width() * 6), int(junkgun_3.get_height() * 6)))
            screen.blit(junkgun_3, (660, 70))
            junkgun_4 = pygame.image.load("project-VAK/img/gui/guns/junk4.png").convert_alpha()
            junkgun_4 = pygame.transform.scale(junkgun_4, (int(junkgun_4.get_width() * 6), int(junkgun_4.get_height() * 6)))
            screen.blit(junkgun_4, (660, 220))
            junkgun_5 = pygame.image.load("project-VAK/img/gui/guns/junk5-3.png").convert_alpha()
            junkgun_5 = pygame.transform.scale(junkgun_5, (int(junkgun_5.get_width() * 6), int(junkgun_5.get_height() * 6)))
            screen.blit(junkgun_5, (660, 400))
            junkgun_6 = pygame.image.load("project-VAK/img/gui/guns/junk6-alljunks.png").convert_alpha()
            junkgun_6 = pygame.transform.scale(junkgun_6, (int(junkgun_6.get_width() * 6), int(junkgun_6.get_height() * 6)))
            screen.blit(junkgun_6, (630, 590))

            if guns_player_have[-6] == 2:
                b1 = Button(220, 60, sml_button_yes, 7, sml_button_yes, sml_button_yes)
            if guns_player_have[-6] == 1:
                b1 = Button(220, 60, sml_button_empty, 7, sml_button_empty, sml_button_empty)
            if guns_player_have[-6] == 0:
                b1 = Button(220, 60, sml_button_clossed, 7, sml_button_clossed, sml_button_clossed)

            if guns_player_have[-5] == 2:
                b2 = Button(220, 230, sml_button_yes, 7, sml_button_yes, sml_button_yes)
            if guns_player_have[-5] == 1:
                b2 = Button(220, 230, sml_button_empty, 7, sml_button_empty, sml_button_empty)
            if guns_player_have[-5] == 0:
                b2 = Button(220, 230, sml_button_clossed, 7, sml_button_clossed, sml_button_clossed)


            if guns_player_have[-4] == 2:
                b3 = Button(850, 60, sml_button_yes, 7, sml_button_yes, sml_button_yes)
            if guns_player_have[-4] == 1:
                b3 = Button(850, 60, sml_button_empty, 7, sml_button_empty, sml_button_empty)
            if guns_player_have[-4] == 0:
                b3 = Button(850, 60 , sml_button_clossed, 7, sml_button_clossed, sml_button_clossed)

            if guns_player_have[-3] == 2:
                b4 = Button(850, 240, sml_button_yes, 7, sml_button_yes, sml_button_yes)
            if guns_player_have[-3] == 1:
                b4 = Button(850, 240, sml_button_empty, 7, sml_button_empty, sml_button_empty)
            if guns_player_have[-3] == 0:
                b4 = Button(850, 240, sml_button_clossed, 7, sml_button_clossed, sml_button_clossed)

            if guns_player_have[-2] == 2:
                b5 = Button(850, 420, sml_button_yes, 7, sml_button_yes, sml_button_yes)
            if guns_player_have[-2] == 1:
                b5 = Button(850, 420, sml_button_empty, 7, sml_button_empty, sml_button_empty)
            if guns_player_have[-2] == 0:
                b5 = Button(850, 420, sml_button_clossed, 7, sml_button_clossed, sml_button_clossed)

            if guns_player_have[-1] == 2:
                b6 = Button(850, 600, sml_button_yes, 7, sml_button_yes, sml_button_yes)
            if guns_player_have[-1] == 1:
                b6 = Button(850, 600, sml_button_empty, 7, sml_button_empty, sml_button_empty)
            if guns_player_have[-1] == 0:
                b6 = Button(850, 600, sml_button_clossed, 7, sml_button_clossed, sml_button_clossed)
            
            if b1.draw(screen):
                page = 5
                gun_which = 1
            if b2.draw(screen):
                page = 5
                gun_which = 2
            if b3.draw(screen):
                page = 5
                gun_which = 3    
            if b4.draw(screen):
                page = 5
                gun_which = 4  
            if b5.draw(screen):
                page = 5
                gun_which = 5
            if b6.draw(screen):
                page = 5
                gun_which = 6
            draw_text("-----------------------------------------------------------", font_5, (26,5,5), 0, 430)
            draw_text("-----------------------------------------------------------", font_5, (26,5,5), 0, 758)
            draw_text("Only unique weapons can be obtained here.", font_5, (26,5,5), 20, 478)
            draw_text("Only unique weapons can be obtained here.", font_5, (255,255,255), 20, 480)
            draw_text("Each weapon has its own specific properties.", font_5, (26,5,5), 20, 518)
            draw_text("Each weapon has its own specific properties.", font_5, (255,255,255), 20, 520)
            draw_text("To get some kind of weapon, you need to use", font_5, (26,5,5), 20, 578)
            draw_text("To get some kind of weapon, you need to use", font_5, (255,255,255), 20, 580)
            draw_text("the parts that you get from sorties.", font_5, (26,5,5), 20, 618)
            draw_text("the parts that you get from sorties.", font_5, (255,255,255), 20, 620)
            draw_text("To craft some weapons, you need to first buy", font_5, (26,5,5), 20, 678)
            draw_text("To craft some weapons, you need to first buy", font_5, (255,255,255), 20, 680)
            draw_text("a certain weapon to craft its improved version", font_5, (26,5,5), 20, 718)
            draw_text("a certain weapon to craft its improved version", font_5, (255,255,255), 20, 720)
            button_right_im = pygame.image.load("project-VAK/img/gui/button_left_junk.png").convert_alpha()
            button_right_im_press = pygame.image.load("project-VAK/img/gui/button_left_junk_press.png").convert_alpha()
            left_butt = Button(20, 780, button_right_im, 6,button_right_im, button_right_im_press)
            if left_butt.draw(screen):
                page = 1
        
        
        
        if page == 5:
            button_right_im = pygame.image.load("project-VAK/img/gui/button_left_junk.png").convert_alpha()
            button_right_im_press = pygame.image.load("project-VAK/img/gui/button_left_junk_press.png").convert_alpha()
            left_butt = Button(1020, 760, button_right_im, 6,button_right_im, button_right_im_press)
            if left_butt.draw(screen):
                page = 3
            week_stl_im = pygame.image.load("project-VAK/img/gui/money/week_steel.png").convert_alpha()
            week_stl_im = pygame.transform.scale(week_stl_im, (int(week_stl_im.get_width() * 3), int(week_stl_im.get_height() * 3)))
            screen.blit(week_stl_im, (20,35))
            steel_im = pygame.image.load("project-VAK/img/gui/money/steel.png").convert_alpha()
            steel_im = pygame.transform.scale(steel_im, (int(steel_im.get_width() * 3), int(steel_im.get_height() * 3)))
            screen.blit(steel_im, (100,30))
            gold_im = pygame.image.load("project-VAK/img/gui/money/gold.png").convert_alpha()
            gold_im = pygame.transform.scale(gold_im, (int(gold_im.get_width() * 3), int(gold_im.get_height() * 3)))
            screen.blit(gold_im, (180,30))
            better_steel_im = pygame.image.load("project-VAK/img/gui/money/better_steel.png").convert_alpha()
            better_steel_im = pygame.transform.scale(better_steel_im, (int(better_steel_im.get_width() * 3), int(better_steel_im.get_height() * 3)))
            screen.blit(better_steel_im, (260,30))
            def_detail_im = pygame.image.load("project-VAK/img/gui/money/def_detail.png").convert_alpha()
            def_detail_im = pygame.transform.scale(def_detail_im, (int(def_detail_im.get_width() * 3), int(def_detail_im.get_height() * 3)))
            screen.blit(def_detail_im, (380,40))
            black_detail_im = pygame.image.load("project-VAK/img/gui/money/black_detail.png").convert_alpha()
            black_detail_im = pygame.transform.scale(black_detail_im, (int(black_detail_im.get_width() * 3), int(black_detail_im.get_height() * 3)))
            screen.blit(black_detail_im, (460,40))
            water_detail_im = pygame.image.load("project-VAK/img/gui/money/water_detail.png").convert_alpha()
            water_detail_im = pygame.transform.scale(water_detail_im, (int(water_detail_im.get_width() * 3), int(water_detail_im.get_height() * 3)))
            screen.blit(water_detail_im, (540,40))
            toxic_detail_im = pygame.image.load("project-VAK/img/gui/money/toxic_detail.png").convert_alpha()
            toxic_detail_im = pygame.transform.scale(toxic_detail_im, (int(toxic_detail_im.get_width() * 3), int(toxic_detail_im.get_height() * 3)))
            screen.blit(toxic_detail_im, (620,40))
            rare_detail_im = pygame.image.load("project-VAK/img/gui/money/rare_detail.png").convert_alpha()
            rare_detail_im = pygame.transform.scale(rare_detail_im, (int(rare_detail_im.get_width() * 3), int(rare_detail_im.get_height() * 3)))
            screen.blit(rare_detail_im, (680,40))
            power_detail_im = pygame.image.load("project-VAK/img/gui/money/power_detail.png").convert_alpha()
            power_detail_im = pygame.transform.scale(power_detail_im, (int(power_detail_im.get_width() * 3), int(power_detail_im.get_height() * 3)))
            screen.blit(power_detail_im, (830,40))
            best_detail_im = pygame.image.load("project-VAK/img/gui/money/best_detail.png").convert_alpha()
            best_detail_im = pygame.transform.scale(best_detail_im, (int(best_detail_im.get_width() * 3), int(best_detail_im.get_height() * 3)))
            screen.blit(best_detail_im, (910,40))
            paporotnik_im = pygame.image.load("project-VAK/img/gui/money/paporotnik.png").convert_alpha()
            paporotnik_im = pygame.transform.scale(paporotnik_im, (int(paporotnik_im.get_width() * 3), int(paporotnik_im.get_height() * 3)))
            screen.blit(paporotnik_im, (1050,30))
            draw_text(f"{week_steel_cnt}", font_4, (255,255,255), 45, 95)
            draw_text(f"{steel_cnt}", font_4, (255,255,255), 125, 95)
            draw_text(f"{gold_cnt}", font_4, (255,255,255), 205, 95)
            draw_text(f"{better_stl_cnt}", font_4, (255,255,255), 285, 95)
            draw_text(f"{def_det_cnt}", font_4, (255,255,255), 405, 95)
            draw_text(f"{black_det_cnt}", font_4, (255,255,255), 485, 95)
            draw_text(f"{toxic_det_cnt}", font_4, (255,255,255), 640, 95)
            draw_text(f"{water_det_cnt}", font_4, (255,255,255), 565, 95)
            draw_text(f"{rare_det_cnt}", font_4, (255,255,255), 715, 95)
            draw_text(f"{power_det_cnt}", font_4, (255,255,255), 845, 95)
            draw_text(f"{best_det_cnt}", font_4, (255,255,255), 925, 95)
            draw_text(f"{grass_cnt}", font_4, (255,255,255), 1065, 95)
            upgrade_im = pygame.image.load("project-VAK/img/gui/button_craft.png").convert_alpha()
            upgrade_select_im = pygame.image.load("project-VAK/img/gui/button_craft_select.png").convert_alpha()
            button_craft_gun = Button(60, 750, upgrade_im , 8, upgrade_select_im , upgrade_im)
            
            if gun_which == 1:
                if guns_player_have[-6] == 2 or guns_player_have[-6] == 1:
                    pass
                elif steel_cnt >= 70 and toxic_det_cnt >= 30 and power_det_cnt >= 7:
                    if button_craft_gun.draw(screen):
                        steel_cnt -= 70
                        toxic_det_cnt -= 30
                        power_det_cnt -= 7
                        guns_player_have[guns_player_have.index(2)] = 1
                        guns_player_have[-6] = 2
                else:
                    draw_text("You can't craft it", font_3, (255,255,255), 20, 780)

                gun = pygame.image.load(f"project-VAK/img/gui/guns/junk1.png").convert_alpha()
                gun = pygame.transform.scale(gun, (int(gun.get_width() * 13), int(gun.get_height() * 13)))
                screen.blit(gun,(0, 250))
                draw_text("On toxic planets, the damage increases", font_4, (255,0,90), 470, 140)
                draw_text("from 200 damage to 650 damage ", font_4, (255,0,90), 530, 170)
                draw_text("Toxic Crusader", font_3, (255,0,90), 450, 228)
                draw_text("Toxic Crusader", font_3, (255,255,255), 450, 230)
                draw_text("unique", font_3, (255,0,90), 450, 280)
                draw_text("- 10 charges", font_3, (255,255,255), 450, 350)
                draw_text("- 1 per shoot", font_3, (255,255,255), 450, 400)
                draw_text("- 200/650 damage", font_3, (255,255,255), 450, 450)
                draw_text("- 1.2 Speed", font_3, (255,255,255), 450, 500)
                draw_text("-------------------------------------------------------------------------------", font_4, (255,0,90), 0, 600)
                draw_text("To craft: 70          30         7", font_4, (255,255,255), 40, 680)
                screen.blit(steel_im, (270,665))
                screen.blit(toxic_detail_im, (420,670))
                screen.blit(power_detail_im, (570,670))
            if gun_which == 2:
                if guns_player_have[-5] == 2 or guns_player_have[-5] == 1:
                    pass
                elif best_det_cnt >= 12 and rare_det_cnt >= 10 and water_det_cnt >= 15:
                    if button_craft_gun.draw(screen):
                        best_det_cnt -= 12
                        rare_det_cnt -= 10
                        water_det_cnt -= 15
                        guns_player_have[guns_player_have.index(2)] = 1
                        guns_player_have[-5] = 2
                else:
                    draw_text("You can't craft it", font_3, (255,255,255), 20, 780)

                gun = pygame.image.load(f"project-VAK/img/gui/guns/junk2.png").convert_alpha()
                gun = pygame.transform.scale(gun, (int(gun.get_width() * 13), int(gun.get_height() * 13)))
                screen.blit(gun,(0, 250))
                draw_text("For every enemy killed on the planet", font_4, (255,0,90), 470, 140)
                draw_text("Damage increases by 2 points", font_4, (255,0,90), 530, 170)
                draw_text("Titan's Thunder", font_3, (255,0,90), 450, 228)
                draw_text("Titan's Thunder", font_3, (255,255,255), 450, 230)
                draw_text("unique", font_3, (255,0,90), 450, 280)
                draw_text("- 10 charges", font_3, (255,255,255), 450, 350)
                draw_text("- Lazer", font_3, (255,255,255), 450, 400)
                draw_text("- 300+ damage", font_3, (255,255,255), 450, 450)
                draw_text("- 1.5 Speed", font_3, (255,255,255), 450, 500)
                draw_text("-------------------------------------------------------------------------------", font_4, (255,0,90), 0, 600)
                draw_text("To craft:   12         10          15", font_4, (255,255,255), 40, 680)
                screen.blit(best_detail_im, (270,665))
                screen.blit(rare_detail_im, (420,670))
                screen.blit(water_detail_im, (570,670))
            if gun_which == 3:
                if guns_player_have[-4] == 2 or guns_player_have[-4] == 1:
                    pass
                elif best_det_cnt >= 15 and guns_player_have[19] > 0:
                    if button_craft_gun.draw(screen):
                        best_det_cnt -= 15
                        guns_player_have[guns_player_have.index(2)] = 1
                        guns_player_have[-4] = 2
                else:
                    draw_text("You can't craft it", font_3, (255,255,255), 20, 780)

                gun = pygame.image.load(f"project-VAK/img/gui/guns/junk3-20.png").convert_alpha()
                gun = pygame.transform.scale(gun, (int(gun.get_width() * 13), int(gun.get_height() * 13)))
                
                gun1 = pygame.image.load(f"project-VAK/img/gui/guns/20.png").convert_alpha()
                gun1 = pygame.transform.scale(gun1, (int(gun1.get_width() * 4), int(gun1.get_height() * 4)))
                
                screen.blit(gun,(0, 250))
                draw_text("shoots 9 bullets in all directions", font_4, (255,0,90), 470, 140)
                draw_text("Unleasher", font_3, (255,0,90), 450, 228)
                draw_text("Unleasher", font_3, (255,255,255), 450, 230)
                draw_text("unique", font_3, (255,0,90), 450, 280)
                draw_text("- 9 charges", font_3, (255,255,255), 450, 350)
                draw_text("- 9 per shoot", font_3, (255,255,255), 450, 400)
                draw_text("- 200 damage", font_3, (255,255,255), 450, 450)
                draw_text("- 1.5 Speed", font_3, (255,255,255), 450, 500)
                draw_text("-------------------------------------------------------------------------------", font_4, (255,0,90), 0, 600)
                draw_text("To craft:  15           1", font_4, (255,255,255), 40, 680)
                screen.blit(best_detail_im, (270,665))
                screen.blit(gun1, (430,670))
            if gun_which == 4:
                if guns_player_have[-3] == 2 or guns_player_have[-3] == 1:
                    pass
                elif gold_cnt >= 65 and power_det_cnt >= 20 and black_det_cnt >= 20:
                    if button_craft_gun.draw(screen):
                        gold_cnt -= 65
                        power_det_cnt -= 20
                        black_det_cnt -= 20
                        guns_player_have[guns_player_have.index(2)] = 1
                        guns_player_have[-3] = 2
                else:
                    draw_text("You can't craft it", font_3, (255,255,255), 20, 780)

                gun = pygame.image.load(f"project-VAK/img/gui/guns/junk4.png").convert_alpha()
                gun = pygame.transform.scale(gun, (int(gun.get_width() * 13), int(gun.get_height() * 13)))
                

                screen.blit(gun,(0, 250))
                draw_text("shoots a very fast burst of bullets", font_4, (255,0,90), 470, 140)
                draw_text("very very fast", font_4, (255,0,90), 530, 170)
                draw_text("Andromeda mingun", font_3, (255,0,90), 450, 228)
                draw_text("Andromeda mingun", font_3, (255,255,255), 450, 230)
                draw_text("unique", font_3, (255,0,90), 450, 280)
                draw_text("- 40 charges", font_3, (255,255,255), 450, 350)
                draw_text("- burst", font_3, (255,255,255), 450, 400)
                draw_text("- 100 damage", font_3, (255,255,255), 450, 450)
                draw_text("- 4 Speed", font_3, (255,255,255), 450, 500)
                draw_text("-------------------------------------------------------------------------------", font_4, (255,0,90), 0, 600)
                draw_text("To craft:  65         20          20", font_4, (255,255,255), 40, 680)
                screen.blit(gold_im, (270,665))
                screen.blit(power_detail_im, (430,670))
                screen.blit(black_detail_im, (570,670))
            if gun_which == 5:
                if guns_player_have[-2] == 2 or guns_player_have[-2] == 1:
                    pass
                elif best_det_cnt >= 32 and guns_player_have[2] > 0:
                    if button_craft_gun.draw(screen):
                        best_det_cnt -= 32
                        guns_player_have[guns_player_have.index(2)] = 1
                        guns_player_have[-2] = 2
                else:
                    draw_text("You can't craft it", font_3, (255,255,255), 20, 780)

                gun = pygame.image.load(f"project-VAK/img/gui/guns/junk5-3.png").convert_alpha()
                gun = pygame.transform.scale(gun, (int(gun.get_width() * 13), int(gun.get_height() * 13)))
                
                gun1 = pygame.image.load(f"project-VAK/img/gui/guns/3.png").convert_alpha()
                gun1 = pygame.transform.scale(gun1, (int(gun1.get_width() * 4), int(gun1.get_height() * 4)))
                
                screen.blit(gun,(0, 250))
                draw_text("shoots 9 bullets in all directions", font_4, (255,0,90), 470, 140)
                draw_text("Ultrazapper", font_3, (255,0,90), 450, 228)
                draw_text("Ultrazapper", font_3, (255,255,255), 450, 230)
                draw_text("unique", font_3, (255,0,90), 450, 280)
                draw_text("- 10 charges", font_3, (255,255,255), 450, 350)
                draw_text("- 1 per shoot", font_3, (255,255,255), 450, 400)
                draw_text("- 400 damage", font_3, (255,255,255), 450, 450)
                draw_text("- 1.5 Speed", font_3, (255,255,255), 450, 500)
                draw_text("-------------------------------------------------------------------------------", font_4, (255,0,90), 0, 600)
                draw_text("To craft:  32           1", font_4, (255,255,255), 40, 680)
                screen.blit(water_detail_im, (270,665))
                screen.blit(gun1, (430,640))

            if gun_which == 6:
                if guns_player_have[-1] == 2 or guns_player_have[-1] == 1:
                    pass
                elif best_det_cnt >= 50 and guns_player_have[-7] > 0 and guns_player_have[-6] > 0 and guns_player_have[-5] > 0 and guns_player_have[-4] > 0 and guns_player_have[-3] > 0 and guns_player_have[-2] > 0:
                    if button_craft_gun.draw(screen):
                        better_stl_cnt -= 50
                        guns_player_have[guns_player_have.index(2)] = 1
                        guns_player_have[-1] = 2
                else:
                    draw_text("You can't craft it", font_3, (255,255,255), 20, 780)

                gun = pygame.image.load(f"project-VAK/img/gui/guns/junk6-alljunks.png").convert_alpha()
                gun = pygame.transform.scale(gun, (int(gun.get_width() * 11), int(gun.get_height() * 11)))
                
                gun1 = pygame.image.load(f"project-VAK/img/gui/guns/35.png").convert_alpha()
                gun1 = pygame.transform.scale(gun1, (int(gun1.get_width() * 4), int(gun1.get_height() * 4)))
                

                
                screen.blit(gun,(0, 250))
                draw_text("It shoots a very strong large beam", font_4, (255,0,90), 470, 140)
                draw_text("It is considered the best weapon in the game", font_4, (255,0,90), 370, 170)
                draw_text("Universe Slayer", font_3, (255,0,90), 450, 228)
                draw_text("Universe Slayer", font_3, (255,255,255), 450, 230)
                draw_text("unique", font_3, (255,0,90), 450, 280)
                draw_text("- 3 charges", font_3, (255,255,255), 450, 350)
                draw_text("- lazer", font_3, (255,255,255), 450, 400)
                draw_text("- 500 damage", font_3, (255,255,255), 450, 450)
                draw_text("- 2 Speed", font_3, (255,255,255), 450, 500)
                draw_text("-------------------------------------------------------------------------------", font_4, (255,0,90), 0, 600)
                draw_text("To craft:  50         1          and all unique guns in 'junk' store", font_4, (255,255,255), 40, 680)
                screen.blit(better_steel_im, (270,665))
                screen.blit(gun1, (390,667))

        if page == 4:
            steel_im = pygame.image.load("project-VAK/img/gui/money/steel.png").convert_alpha()
            steel_im = pygame.transform.scale(steel_im, (int(steel_im.get_width() * 2), int(steel_im.get_height() * 2)))
            screen.blit(steel_im, (283,475))
            gold_im = pygame.image.load("project-VAK/img/gui/money/gold.png").convert_alpha()
            gold_im = pygame.transform.scale(gold_im, (int(gold_im.get_width() * 2), int(gold_im.get_height() * 2)))
            screen.blit(gold_im, (359,475))
            better_steel_im = pygame.image.load("project-VAK/img/gui/money/better_steel.png").convert_alpha()
            better_steel_im = pygame.transform.scale(better_steel_im, (int(better_steel_im.get_width() * 2), int(better_steel_im.get_height() * 2)))
            screen.blit(better_steel_im, (436,475))
            button_right_im = pygame.image.load("project-VAK/img/gui/button_left_junk.png").convert_alpha()
            button_right_im_press = pygame.image.load("project-VAK/img/gui/button_left_junk_press.png").convert_alpha()
            left_butt = Button(20, 780, button_right_im, 6,button_right_im, button_right_im_press)

            money_im_sml = pygame.image.load(f"project-VAK/img/gui/money/money_sml.png").convert_alpha()
            money_im_sml = pygame.transform.scale(money_im_sml, (int(money_im_sml.get_width() * 2), int(money_im_sml.get_height() * 2)))
            rare_det_im_sml = pygame.image.load(f"project-VAK/img/gui/money/rare_detail.png").convert_alpha()
            rare_det_im_sml = pygame.transform.scale(rare_det_im_sml, (int(rare_det_im_sml.get_width() * 2), int(rare_det_im_sml.get_height() * 2)))
            diamond_im_sml = pygame.image.load(f"project-VAK/img/gui/money/diamond_sml.png").convert_alpha()
            diamond_im_sml = pygame.transform.scale(diamond_im_sml, (int(diamond_im_sml.get_width() * 2), int(diamond_im_sml.get_height() * 2)))   
            red_b_im_sml = pygame.image.load(f"project-VAK/img/gui/big_red_b.png").convert_alpha()
            red_b_im_pres_sml = pygame.image.load(f"project-VAK/img/gui/big_red_b_pr.png").convert_alpha()
            button_red = Button(720, 302, red_b_im_sml, 7, red_b_im_sml, red_b_im_pres_sml, "project-VAK/img/sfx/main_menu/Confirm.wav")
            if money_diamond >= 2:
                if button_red.draw(screen):
                    money_diamond -= 2
                    page = 8
            else:
                draw_text("You can't buy", font_4, (255,255,255), 720, 400)
            screen.blit(money_im_sml,(320, 437))
            screen.blit(diamond_im_sml,(280, 400))
            screen.blit(diamond_im_sml,(880, 320))
            screen.blit(diamond_im_sml,(300, 560))
            screen.blit(rare_det_im_sml,(280, 520))
            draw_text("many people say that it is almost impossible to win anything here", font_5, (26, 5, 5), 20, 700)
            if left_butt.draw(screen):
                page = 1
            diamond_im = pygame.image.load(f"project-VAK/img/gui/money/diamond.png").convert_alpha()
            diamond_im = pygame.transform.scale(diamond_im, (int(diamond_im.get_width() * 3), int(diamond_im.get_height() * 3)))
            screen.blit(diamond_im,(40, 70))
            draw_text(f"{money_diamond}", font_3, (255,255,255), 150, 90)
            draw_text("for 2 diamonds you can roll a dice", font_4, (255,255,255), 50, 240)
            draw_text("if on th(e dice falls", font_4, (255,255,255), 50, 280)
            draw_text(" 1 - You get nothing", font_4, (255,255,255), 50, 360)
            draw_text(" 2 - you get 1", font_4, (255,255,255), 50, 400)
            draw_text(" 3 - you get 800", font_4, (255,255,255), 50, 440)
            draw_text(" 4 - you get 9     8     6", font_4, (255,255,255), 50, 480)
            draw_text(" 5 - You get 3", font_4, (255,255,255), 50, 520)
            draw_text(" 6 - You get 20", font_4, (255,255,255), 50, 560)
            draw_text("cost: 2  ", font_4, (255,255,255), 750, 320)
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
                saving_game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False
                    saving_game()
        if page == 8:
            make_action += 1
            bg_for_dice.update()
            bg_for_dice.draw(screen, -315, 0)
            if make_action < 248:
                dice.update()
                dice_pos += dice_rol
                if dice_pos >= 360:
                    dice_rol = -dice_rol
                if dice_pos <= 320:
                    dice_rol = -dice_rol
                dice.draw(screen, 650, dice_pos)
                DICE_FALL_NUMBER_RANDOM = random.randint(1, 225)
            if make_action >= 248:
                left_butt = Button(20, 20, button_right_im, 6,button_right_im, button_right_im_press)
                make_action = 248
                if DICE_FALL_NUMBER_RANDOM > 0 and DICE_FALL_NUMBER_RANDOM <= 150:
                    dice_num = pygame.image.load(f"project-VAK/img/gui/dice/six sided die_1.png").convert_alpha()
                    dice_num = pygame.transform.scale(dice_num, (int(dice_num.get_width() * 16), int(dice_num.get_height() * 16)))
                    screen.blit(dice_num,(650, 340))
                    draw_text("you get nothing!", font_3, (255,255,255), 570, 660)
                    if left_butt.draw(screen):
                        make_action = 0
                        page = 4
                if DICE_FALL_NUMBER_RANDOM > 150 and DICE_FALL_NUMBER_RANDOM <= 180:
                    dice_num = pygame.image.load(f"project-VAK/img/gui/dice/six sided die_2.png").convert_alpha()
                    dice_num = pygame.transform.scale(dice_num, (int(dice_num.get_width() * 16), int(dice_num.get_height() * 16)))
                    screen.blit(dice_num,(650, 340))
                    screen.blit(diamond_im,(820, 630))
                    draw_text("you get 1        !", font_3, (255,255,255), 570, 660)
                    if left_butt.draw(screen):
                        make_action = 0
                        page = 4
                        money_diamond += 1                    
                if DICE_FALL_NUMBER_RANDOM > 180 and DICE_FALL_NUMBER_RANDOM <= 210:
                    dice_num = pygame.image.load(f"project-VAK/img/gui/dice/six sided die_3.png").convert_alpha()
                    dice_num = pygame.transform.scale(dice_num, (int(dice_num.get_width() * 16), int(dice_num.get_height() * 16)))
                    screen.blit(dice_num,(650, 340))
                    draw_text("you get 800      !", font_3, (255,255,255), 570, 660)
                    money_im_sml = pygame.image.load(f"project-VAK/img/gui/money/money.png").convert_alpha()
                    money_im_sml = pygame.transform.scale(money_im_sml, (int(money_im_sml.get_width() * 3), int(money_im_sml.get_height() * 3)))
                    screen.blit(money_im_sml, (870, 630))
                    if left_butt.draw(screen):
                        make_action = 0
                        page = 4
                        money += 800 
                if DICE_FALL_NUMBER_RANDOM > 210 and DICE_FALL_NUMBER_RANDOM <= 220:
                    dice_num = pygame.image.load(f"project-VAK/img/gui/dice/six sided die_4.png").convert_alpha()
                    dice_num = pygame.transform.scale(dice_num, (int(dice_num.get_width() * 16), int(dice_num.get_height() * 16)))
                    screen.blit(dice_num,(650, 340))
                    draw_text("you get 9     8    6    !", font_3, (255,255,255), 570, 660)
                    steel_im = pygame.image.load("project-VAK/img/gui/money/steel.png").convert_alpha()
                    steel_im = pygame.transform.scale(steel_im, (int(steel_im.get_width() * 3), int(steel_im.get_height() * 3)))
                    screen.blit(steel_im, (820, 650))
                    gold_im = pygame.image.load("project-VAK/img/gui/money/gold.png").convert_alpha()
                    gold_im = pygame.transform.scale(gold_im, (int(gold_im.get_width() * 3), int(gold_im.get_height() * 3)))
                    screen.blit(gold_im, (930, 650))
                    better_steel_im = pygame.image.load("project-VAK/img/gui/money/better_steel.png").convert_alpha()
                    better_steel_im = pygame.transform.scale(better_steel_im, (int(better_steel_im.get_width() * 3), int(better_steel_im.get_height() * 3)))
                    screen.blit(better_steel_im, (1030, 650))
                    if left_butt.draw(screen):
                        make_action = 0
                        page = 4
                        steel_cnt += 9
                        gold_cnt += 8
                        better_stl_cnt += 6
                if DICE_FALL_NUMBER_RANDOM > 220 and DICE_FALL_NUMBER_RANDOM <= 223:
                    dice_num = pygame.image.load(f"project-VAK/img/gui/dice/six sided die_5.png").convert_alpha()
                    dice_num = pygame.transform.scale(dice_num, (int(dice_num.get_width() * 16), int(dice_num.get_height() * 16)))
                    screen.blit(dice_num,(650, 340))
                    rare_det_im_sml = pygame.image.load(f"project-VAK/img/gui/money/rare_detail.png").convert_alpha()
                    rare_det_im_sml = pygame.transform.scale(rare_det_im_sml, (int(rare_det_im_sml.get_width() * 4), int(rare_det_im_sml.get_height() * 4)))
                    screen.blit(rare_det_im_sml,(820, 650))
                    draw_text("you get 3        !", font_3, (255,255,255), 570, 660)
                    if left_butt.draw(screen):
                        make_action = 0
                        page = 4
                        rare_det_cnt += 3
                if DICE_FALL_NUMBER_RANDOM > 223 and DICE_FALL_NUMBER_RANDOM <= 225:
                    dice_num = pygame.image.load(f"project-VAK/img/gui/dice/six sided die_6.png").convert_alpha()
                    dice_num = pygame.transform.scale(dice_num, (int(dice_num.get_width() * 16), int(dice_num.get_height() * 16)))
                    screen.blit(dice_num,(650, 340))
                    screen.blit(diamond_im,(840, 630))
                    draw_text("you get 20        !", font_3, (255,255,255), 570, 660)
                    if left_butt.draw(screen):
                        make_action = 0
                        page = 4 
                        money_diamond += 20
    
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
                saving_game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False
                    saving_game()

    if current_window_selected == "play on planet":
        clock.tick(FPS)
        health_bars = {75: "health_bar4.png", 40: "health_bar3.png", 10: "health_bar2.png", 0: "health_bar1.png",
                    -1: "health_bar0.png"}
        ammo_bars = {15: "ammo5.png", 10: "ammo4.png", 5: "ammo3.png", 1: "ammo2.png", 0: "ammo1.png", -1: "ammo0.png"}
        
        if planet_which_you_ch == 1:
            back_ground_for_home = pygame.image.load("project-VAK/img/planets_play/Nova prime1/back1.png").convert_alpha()
        if planet_which_you_ch == 2:
            back_ground_for_home = pygame.image.load("project-VAK/img/planets_play/Astoria2/back1.png").convert_alpha()
        if planet_which_you_ch == 3:
            back_ground_for_home = pygame.image.load("project-VAK/img/planets_play/Olympus3/back1.png").convert_alpha()
        if planet_which_you_ch == 4:
            back_ground_for_home = pygame.image.load("project-VAK/img/planets_play/Nebulous4/back1.png").convert_alpha()
        if planet_which_you_ch == 5:
            back_ground_for_home = pygame.image.load("project-VAK/img/planets_play/Infinity5/back1.png").convert_alpha()
        if planet_which_you_ch == 6:
            back_ground_for_home = pygame.image.load("project-VAK/img/planets_play/second/Genesis1/back1.png").convert_alpha()
        if planet_which_you_ch == 7:
            back_ground_for_home = pygame.image.load("project-VAK/img/planets_play/second/Equinox2/back1.png").convert_alpha()
        if planet_which_you_ch == 8:
            back_ground_for_home = pygame.image.load("project-VAK/img/planets_play/second/Orpheus3/back1.png").convert_alpha()
        if planet_which_you_ch == 9:
            back_ground_for_home = pygame.image.load("project-VAK/img/planets_play/second/Utopia4/back1.png").convert_alpha()
        if planet_which_you_ch == 10:
            back_ground_for_home = pygame.image.load("project-VAK/img/planets_play/second/Nexus5/back1.png").convert_alpha()
        if planet_which_you_ch == 11:
            back_ground_for_home = pygame.image.load("project-VAK/img/planets_play/third/Andromeda1/back1.png").convert_alpha()
        if planet_which_you_ch == 12:
            back_ground_for_home = pygame.image.load("project-VAK/img/planets_play/third/Epoch2/back1.png").convert_alpha()
        if planet_which_you_ch == 13:
            back_ground_for_home = pygame.image.load("project-VAK/img/planets_play/third/Arcadia3/back1.png").convert_alpha()
        if planet_which_you_ch == 14:
            back_ground_for_home = pygame.image.load("project-VAK/img/planets_play/third/Apollo4/back1.png").convert_alpha()
        if planet_which_you_ch == 15:
            back_ground_for_home = pygame.image.load("project-VAK/img/planets_play/third/Polaris5/back1.png").convert_alpha()
        if planet_which_you_ch == 16:
            back_ground_for_home = pygame.image.load("project-VAK/img/planets_play/four/Ethereal1/back1.png").convert_alpha()
        if planet_which_you_ch == 17:
            back_ground_for_home = pygame.image.load("project-VAK/img/planets_play/four/Soltisice2/back1.png").convert_alpha()
        if planet_which_you_ch == 18:
            back_ground_for_home = pygame.image.load("project-VAK/img/planets_play/four/Scepter3/back1.png").convert_alpha()
        if planet_which_you_ch == 19:
            back_ground_for_home = pygame.image.load("project-VAK/img/planets_play/four/Prisma4/back1.png").convert_alpha()
        if planet_which_you_ch == 20:
            back_ground_for_home = pygame.image.load("project-VAK/img/planets_play/four/Fantsia5/back1.png").convert_alpha()
        if planet_which_you_ch == 21:
            back_ground_for_home = pygame.image.load("project-VAK/img/planets_play/five/New Earth1/back1.png").convert_alpha()
        if planet_which_you_ch == 22:
            back_ground_for_home = pygame.image.load("project-VAK/img/planets_play/five/Horizon2/back1.png").convert_alpha()
        if planet_which_you_ch == 23:
            back_ground_for_home = pygame.image.load("project-VAK/img/planets_play/five/Valhalla3/back1.png").convert_alpha()
        if planet_which_you_ch == 24:
            back_ground_for_home = pygame.image.load("project-VAK/img/planets_play/five/Radiance4/back1.png").convert_alpha()
        if planet_which_you_ch != 25:
            back_ground_for_home = pygame.transform.scale(back_ground_for_home, (int(back_ground_for_home.get_width() * 2), int(back_ground_for_home.get_height() * 2)))
            screen.blit(back_ground_for_home, (0,0))
        if planet_which_you_ch == 25:
            PlanetV_back.update()
            PlanetV_back.draw(screen, 0,0)
        if planet_which_you_ch == 3:
            front1 = pygame.image.load(f"project-VAK/img/planets_play/Olympus3/front1.png").convert_alpha()
            front1 = pygame.transform.scale(front1, (int(front1.get_width() * 3), int(front1.get_height() * 3)))
            front2 = pygame.image.load(f"project-VAK/img/planets_play/Olympus3/front2.png").convert_alpha()
            front2 = pygame.transform.scale(front2, (int(front2.get_width() * 3), int(front2.get_height() * 3)))
            screen.blit(front2, (1490 , 385))
            screen.blit(front1, (-120 , 585))
        if planet_which_you_ch == 8:
            front1 = pygame.image.load(f"project-VAK/img/planets_play/second/Orpheus3/front1.png").convert_alpha()
            front1 = pygame.transform.scale(front1, (int(front1.get_width() * 16), int(front1.get_height() * 16)))
            screen.blit(front1, (1300 , 55))
            screen.blit(front1, (-670 , 55))
        if planet_which_you_ch == 9:
            front1 = pygame.image.load(f"project-VAK/img/planets_play/second/Utopia4/front1.png").convert_alpha()
            front1 = pygame.transform.scale(front1, (int(front1.get_width() * 2), int(front1.get_height() * 2)))
            front2 = pygame.image.load(f"project-VAK/img/planets_play/second/Utopia4/front2.png").convert_alpha()
            front2 = pygame.transform.scale(front2, (int(front2.get_width() * 2), int(front2.get_height() * 2)))
            screen.blit(front2, (-200 , 385))
            screen.blit(front1, (1300 , 355))
            screen.blit(front1, (900 , 655))
            screen.blit(front2, (300 , 585))

        if start_intro == True:
            if intro_fade.fade():
                start_intro = False
                intro_fade.fade_counter = 0
        if counters_constat != -1:
            counters_constat -= 1
        if counters_constat == 80 or counters_constat == 160:
            counter_sound_not_one.play()
        if counters_constat == 3:
            counter_sound_one.play()
            pygame.mixer.music.play(-1)
        if counters_constat <= 160 and counters_constat > 80:
            draw_text("3", font_2, (0,0,0), 720, 290)
            draw_text("3", font_2, (0,0,0), 720, 310)
            draw_text("3", font_2, (0,0,0), 710, 290)
            draw_text("3", font_2, (0,0,0), 710, 310)
            draw_text("3", font_2, (0,0,0), 730, 290)
            draw_text("3", font_2, (0,0,0), 730, 310)
            draw_text("3", font_2, (255,255,255), 720, 300)
        if counters_constat <= 80 and counters_constat > 3:
            draw_text("2", font_2, (0,0,0), 720, 290)
            draw_text("2", font_2, (0,0,0), 720, 310)
            draw_text("2", font_2, (0,0,0), 710, 290)
            draw_text("2", font_2, (0,0,0), 710, 310)
            draw_text("2", font_2, (0,0,0), 730, 290)
            draw_text("2", font_2, (0,0,0), 730, 310)
            draw_text("2", font_2, (255,255,255), 720, 300)
        if counters_constat == -1:
            draw_text(f'AMMO', font, (0, 0, 0), 1023, 15)
            draw_status_bar(player.ammo, ammo_bars, 940, 25)
            draw_text(f'HEALTH', font, (0, 0, 0), 1370, 15)
            draw_status_bar(player.health, health_bars, 1170, 23)

            for enemy in enemies_group:
                enemy.update()
                enemy.draw()


            player.update()
            player.draw()

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
                elif is_using_grenade_el and not is_grenade_thrown_el and player.grenades_elect > 0:
                    is_using_grenade_el = Grenade(player.rect.centerx + (0.5 * player.rect.size[0] * player.direction),
                                            player.rect.top,
                                            player.direction, which=2)
                    grenade_group.add(is_using_grenade_el)
                    player.grenades_elect -= 1
                    is_grenade_thrown_el = True
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

            
            if planet_which_you_ch == 3:
                screen.blit(front2, (1490 , 385))
                screen.blit(front1, (-120 , 585))
            if planet_which_you_ch == 8:
                screen.blit(front1, (1300 , 55))
                screen.blit(front1, (-670 , 55))
            if planet_which_you_ch == 9:
                screen.blit(front2, (-200 , 385))
                screen.blit(front1, (1300 , 355))
                screen.blit(front1, (900 , 655))
                screen.blit(front2, (300 , 585))
        if planet_which_you_ch == 1:
            gradientRect( screen, (86, 177, 219), (0, 0, 0), pygame.Rect( 0,0, 2000, 1400 ) )
        if planet_which_you_ch == 2:
            gradientRect( screen, (245, 126, 66), (138, 198, 235), pygame.Rect( 0,0, 2000, 1400 ), alpha=42)
        if planet_which_you_ch == 3:
            gradientRect( screen, (206, 219, 118), (207, 200, 19), pygame.Rect( 0,0, 2000, 1400 ), alpha=52)
        if planet_which_you_ch == 4:
            gradientRect( screen, (217, 145, 167), (186, 7, 61), pygame.Rect( 0,0, 2000, 1400 ), alpha=52)
        if planet_which_you_ch == 5:
            gradientRect( screen, (174, 224, 235), (204, 228, 240), pygame.Rect( 0,0, 2000, 1400 ), alpha=52)
        if planet_which_you_ch == 6:
            gradientRect( screen, (6, 35, 74), (0,0,0), pygame.Rect( 0,0, 2000, 1400 ), alpha=72)
        if planet_which_you_ch == 7:
            gradientRect( screen, (237, 245, 255), (255, 237, 244), pygame.Rect( 0,0, 2000, 1400 ), alpha=62)
        if planet_which_you_ch == 8:
            gradientRect( screen, (74, 102, 80), (0,0,0), pygame.Rect( 0,0, 2000, 1400 ), alpha=62)
        if planet_which_you_ch == 9:
            gradientRect( screen, (173, 66, 87), (0,0,0), pygame.Rect( 0,0, 2000, 1400 ), alpha=52)  
        if planet_which_you_ch == 10:
            gradientRect( screen, (129, 199, 227), (237, 245, 247), pygame.Rect( 0,0, 2000, 1400 ), alpha=32) 
        if planet_which_you_ch == 11:
            gradientRect( screen, (0,0,0), (122, 22, 86), pygame.Rect( 0,0, 2000, 1400 ), alpha=42) 
        if planet_which_you_ch == 12:
            gradientRect( screen, (2, 8, 28), (18, 2, 46), pygame.Rect( 0,0, 2000, 1400 ), alpha=42) 
        if planet_which_you_ch == 13:
            gradientRect( screen, (84, 84, 84), (67, 60, 74), pygame.Rect( 0,0, 2000, 1400 ), alpha=42) 
        if planet_which_you_ch == 14:
            gradientRect( screen, (112, 71, 18), (57, 102, 81), pygame.Rect( 0,0, 2000, 1400 ), alpha=32)
        if planet_which_you_ch == 15:
            gradientRect( screen, (180, 198, 207), (223, 236, 237), pygame.Rect( 0,0, 2000, 1400 ), alpha=72)
        if planet_which_you_ch == 16:
            gradientRect( screen, (125, 88, 66), (18, 9, 1), pygame.Rect( 0,0, 2000, 1400 ), alpha=72)
        if planet_which_you_ch == 17:
            gradientRect( screen, (121, 65, 232), (177, 81, 237), pygame.Rect( 0,0, 2000, 1400 ), alpha=62)
        if planet_which_you_ch == 18:
            gradientRect( screen, (212, 107, 32), (214, 187, 94), pygame.Rect( 0,0, 2000, 1400 ), alpha=72)
        if planet_which_you_ch == 19:
            gradientRect( screen, (163, 162, 160), (120, 119, 116), pygame.Rect( 0,0, 2000, 1400 ), alpha=62)
        if planet_which_you_ch == 20:
            gradientRect( screen, (20, 20, 20), (0, 0, 0), pygame.Rect( 0,0, 2000, 1400 ), alpha=22)
        if planet_which_you_ch == 21:
            gradientRect( screen, (185, 230, 235), (192, 205, 207), pygame.Rect( 0,0, 2000, 1400 ), alpha=52)
        if planet_which_you_ch == 22:
            gradientRect( screen, (58, 39, 69), (41, 37, 43), pygame.Rect( 0,0, 2000, 1400 ), alpha=82)
        if planet_which_you_ch == 23:
            gradientRect( screen, (201, 68, 58), (232, 154, 77), pygame.Rect( 0,0, 2000, 1400 ), alpha=52)
        if planet_which_you_ch == 24:
            gradientRect( screen, (237, 232, 228), (233, 210, 247), pygame.Rect( 0,0, 2000, 1400 ), alpha=52)
        if planet_which_you_ch == 25:
            gradientRect( screen, (130, 255, 209), (226, 189, 240), pygame.Rect( 0,0, 2000, 1400 ), alpha=52)
        
        
        if player.rect.y < 353:
            is_moving_up = False
        if player.rect.y > 800:
            is_moving_down = False
        if player.rect.x < 0:
            is_moving_left = False
        if player.rect.x > 1500:
            is_moving_right = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                saving_game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    if player.rect.x > 0:
                        is_moving_left = True
                if event.key == pygame.K_d:
                    if player.rect.x < 1500:
                        is_moving_right = True
                if event.key == pygame.K_w:
                    if player.rect.y > 353:
                        is_moving_up = True
                if event.key == pygame.K_s:
                    if player.rect.y < 800:
                        is_moving_down = True
                if event.key == pygame.K_ESCAPE:
                    run = False
                    saving_game()
                if skill_player_have[5] == 1:
                    if event.key == pygame.K_q:
                        is_using_grenade = True
                if skill_player_have[16] == 1:
                    if event.key == pygame.K_v:
                        is_using_grenade_el = True
                if event.key == pygame.K_SPACE:
                    is_shooting = True

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    is_moving_left = False
                if event.key == pygame.K_d:
                    is_moving_right = False
                if skill_player_have[5] == 1:
                    if event.key == pygame.K_q:
                        is_using_grenade = False
                        is_grenade_thrown = False
                if skill_player_have[16] == 1:
                    if event.key == pygame.K_v:
                        is_using_grenade_el = False
                        is_grenade_thrown_el = False
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
                draw_text("worked on character design and setting,", font_3, (255,255,255), 20 , 670)
                draw_text("wrote sound work, basic character", font_3, (255,255,255), 20 , 750)
                draw_text("mechanics and character leveling.", font_3, (255,255,255), 20 , 820)
        if mouse_pos[0] >= 820 and mouse_pos[0] <= 970:
            if mouse_pos[1] >= 408 and mouse_pos[1] <= 550:
                draw_text("wrote the code for shooting mechanics,", font_3, (255,255,255), 20 , 670)
                draw_text("mobs and bosses. Made the code more", font_3, (255,255,255), 20 , 750)
                draw_text("readable and clean.", font_3, (255,255,255), 20 , 820)
        if back_button.draw(screen):
            current_window_selected = "main_menu"
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                saving_game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False
                    saving_game()
            if event.type == pygame.MOUSEBUTTONUP:
                if mouse_pos[0] >= 600 and mouse_pos[0] <= 740:
                    if mouse_pos[1] >= 408 and mouse_pos[1] <= 550:
                        maw = pygame.mixer.Sound("project-VAK/img/sfx/main_menu/Cat_Meow.wav")
                        maw.stop()
                        maw.play()
                if mouse_pos[0] >= 820 and mouse_pos[0] <= 970:
                    if mouse_pos[1] >= 408 and mouse_pos[1] <= 550:
                        maw = pygame.mixer.Sound("project-VAK/img/sfx/main_menu/Cat_Meow.wav")
                        maw.stop()
                        maw.play()
                        
    pygame.display.update()

pygame.quit()
