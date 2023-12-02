import pygame
import os


pygame.init()

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('SPACE-V')


clock = pygame.time.Clock()
FPS = 60

#define game variables
GRAVITY = 0.8

#define player action variables
moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_thrown = False

bullet_img = pygame.image.load('project-VAK/img/shoot/player-shoot-hit1.png').convert_alpha()
grenade_img = pygame.image.load('project-VAK/img/items/grenade.png').convert_alpha()

BG = (144, 201, 120)
RED = (255, 0, 0)

font = pygame.font.Font("project-VAK/img/gui/ThaleahFat.ttf", 48)


def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))

def draw_bg():
	screen.fill(BG)
	pygame.draw.line(screen, RED, (0, 300), (SCREEN_WIDTH, 300))


class Player(pygame.sprite.Sprite):
	def __init__(self, x, y, scale, speed, ammo, grenades):
		pygame.sprite.Sprite.__init__(self)
		self.alive = True
		self.speed = speed
		self.ammo = ammo
		self.start_ammo = ammo
		self.shoot_coldown = 0
		self.direction = 1
		self.grenades = grenades 
		self.health = 100
		self.health_m = self.health
		self.vel_y = 0
		self.jump = False
		self.in_air = True
		self.flip = False
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
			if self.shoot_coldown == 0 and self.ammo > 0:
				self.shoot_coldown = 20
				bullet = Bullet(self.rect.centerx + (0.9 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
				bullet_group.add(bullet)
				self.ammo -= 1

	def update(self):
		self.update_animation()
		self.check_alive()
		if self.shoot_coldown != 0:
			self.shoot_coldown -= 1

	def move(self, moving_left, moving_right):
		if moving_left and moving_right:
			dx = 0
		else:
			dx = -self.speed if moving_left else self.speed if moving_right else 0

		self.flip = moving_left
		self.direction = -1 if moving_left else 1 if moving_right else self.direction

		if self.jump and not self.in_air:
			self.vel_y, self.jump, self.in_air = -11, False, True

		self.vel_y = min(self.vel_y + GRAVITY, 10)
		dy = self.vel_y
		if self.rect.bottom + dy > 300:
			dy, self.in_air = 300 - self.rect.bottom, False

		self.rect.x += dx
		self.rect.y += dy


	def update_animation(self):
		ANIMATION_COOLDOWN = 150
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
			self.alive = False
			self.update_action(3)

	def draw(self):
		screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

class Bullet(pygame.sprite.Sprite):
	def __init__(self, x, y, direction):
		pygame.sprite.Sprite.__init__(self)
		self.speed = 10
		self.image = bullet_img
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.direction = direction
	
	def update(self):
		self.rect.x += (self.direction * self.speed)
		if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
			self.kill()

		if pygame.sprite.spritecollide(player, bullet_group, False):
			if player.alive:
				player.health -= 20
				self.kill()
		for enemy in enemys_group:
			if pygame.sprite.spritecollide(enemy, bullet_group, False):
				if enemy.alive:
					enemy.health -= 25
					self.kill()

class Grenade(pygame.sprite.Sprite):
	def __init__(self, x, y, direction):
		pygame.sprite.Sprite.__init__(self)
		self.timer = 38
		self.vel_y = -11
		self.speed = 7
		self.image = grenade_img
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.direction = direction
	
	def update(self):
		self.vel_y += GRAVITY
		dx = self.direction * self.speed
		dy = self.vel_y

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
			explosi = Expl(self.rect.x, self.rect.y, 6)
			expl_group.add(explosi)

			if abs(self.rect.centerx - player.rect.centerx) < 90 and abs(self.rect.centery - player.rect.centery) < 90:
				player.health -= 100
			for i in enemys_group:
				if abs(self.rect.centerx - i.rect.centerx) < 90 and abs(self.rect.centery - i.rect.centery) < 90:
					i.health -= 100




class Expl(pygame.sprite.Sprite):
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
		speed_of_exp = 5
		self.counter += 1

		if self.counter >= speed_of_exp:
			self.counter = 0
			self.frame_index += 1
			if self.frame_index >= len(self.images):
				self.kill()
			else:
				self.image = self.images[self.frame_index]



enemys_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
expl_group = pygame.sprite.Group()


player = Player(200, 200, 3, 5, 20, 5)
enemy = Player(400, 200, 3, 5, 20, 0)
enemy1 = Player(400, 400, 3, 5, 20, 0)
enemys_group.add(enemy)
enemys_group.add(enemy1)
run = True
while run:

	clock.tick(FPS)

	draw_bg()
	draw_text(f'HEALTH', font, (0, 0, 0), 843, 15)

	if player.health > 75:
		img_bar_health = pygame.image.load("project-VAK/img/gui/health_bar4.png").convert_alpha()
		img_bar_health  = pygame.transform.scale(img_bar_health, (int(img_bar_health.get_width() * 4), int(img_bar_health.get_height() * 4)))
		screen.blit(img_bar_health, (670, 23))
	if player.health <= 75 and player.health > 40:
		img_bar_health = pygame.image.load("project-VAK/img/gui/health_bar3.png").convert_alpha()
		img_bar_health  = pygame.transform.scale(img_bar_health, (int(img_bar_health.get_width() * 4), int(img_bar_health.get_height() * 4)))
		screen.blit(img_bar_health, (670, 23))
	if player.health <= 40 and player.health > 10:
		img_bar_health = pygame.image.load("project-VAK/img/gui/health_bar2.png").convert_alpha()
		img_bar_health  = pygame.transform.scale(img_bar_health, (int(img_bar_health.get_width() * 4), int(img_bar_health.get_height() * 4)))
		screen.blit(img_bar_health, (670, 23))
	if player.health <= 10 and player.health > 0:
		img_bar_health = pygame.image.load("project-VAK/img/gui/health_bar1.png").convert_alpha()
		img_bar_health  = pygame.transform.scale(img_bar_health, (int(img_bar_health.get_width() * 4), int(img_bar_health.get_height() * 4)))
		screen.blit(img_bar_health, (670, 23))
	if player.health == 0:
		img_bar_health = pygame.image.load("project-VAK/img/gui/health_bar0.png").convert_alpha()
		img_bar_health  = pygame.transform.scale(img_bar_health, (int(img_bar_health.get_width() * 4), int(img_bar_health.get_height() * 4)))
		screen.blit(img_bar_health, (670, 23))
	
	draw_text(f'AMMO', font, (0, 0, 0), 523, 15)
	if player.ammo > 15:
		img_bar_ammo = pygame.image.load("project-VAK/img/gui/ammo5.png").convert_alpha()
		img_bar_ammo  = pygame.transform.scale(img_bar_ammo , (int(img_bar_ammo .get_width() * 4), int(img_bar_ammo.get_height() * 4)))
		screen.blit(img_bar_ammo, (440, 25))
	if player.ammo <= 15 and player.ammo > 10:
		img_bar_ammo = pygame.image.load("project-VAK/img/gui/ammo4.png").convert_alpha()
		img_bar_ammo = pygame.transform.scale(img_bar_ammo , (int(img_bar_ammo .get_width() * 4), int(img_bar_ammo.get_height() * 4)))
		screen.blit(img_bar_ammo, (440, 25))
	if player.ammo <= 10 and player.ammo > 5:
		img_bar_ammo = pygame.image.load("project-VAK/img/gui/ammo3.png").convert_alpha()
		img_bar_ammo = pygame.transform.scale(img_bar_ammo, (int(img_bar_ammo.get_width() * 4), int(img_bar_ammo .get_height() * 4)))
		screen.blit(img_bar_ammo, (440, 25))
	if player.ammo <= 5 and player.ammo > 0:
		img_bar_ammo = pygame.image.load("project-VAK/img/gui/ammo2.png").convert_alpha()
		img_bar_ammo = pygame.transform.scale(img_bar_ammo , (int(img_bar_ammo .get_width() * 4), int(img_bar_ammo.get_height() * 4)))
		screen.blit(img_bar_ammo, (440, 25))
	if player.ammo == 1:
		img_bar_ammo = pygame.image.load("project-VAK/img/gui/ammo1.png").convert_alpha()
		img_bar_ammo = pygame.transform.scale(img_bar_ammo , (int(img_bar_ammo.get_width() * 4), int(img_bar_ammo.get_height() * 4)))
		screen.blit(img_bar_ammo, (440, 25))
	if player.ammo == 0:
		img_bar_ammo= pygame.image.load("project-VAK/img/gui/ammo0.png").convert_alpha()
		img_bar_ammo = pygame.transform.scale(img_bar_ammo , (int(img_bar_ammo.get_width() * 4), int(img_bar_ammo.get_height() * 4)))
		screen.blit(img_bar_ammo, (440, 25))
	


	player.update()
	player.draw()
	for enemy in enemys_group:
		enemy.update()
		enemy.draw()

	bullet_group.update()
	grenade_group.update()
	expl_group.update()
	bullet_group.draw(screen)
	grenade_group.draw(screen)
	expl_group.draw(screen)
	if player.alive:
		if shoot:
			player.shoot()
			shoot = False
		elif grenade and grenade_thrown == False and player.grenades > 0:
			grenade = Grenade(player.rect.centerx + (0.5 * player.rect.size[0] * player.direction), player.rect.top, player.direction)
			grenade_group.add(grenade)
			player.grenades -= 1
			grenade_thrown = True  
		if player.in_air:
			player.update_action(2)#2: jump
		elif moving_left or moving_right:
			player.update_action(1)#1: run
		else:
			player.update_action(0)#0: idle
		player.move(moving_left, moving_right)


	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False

		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_a:
				moving_left = True
			if event.key == pygame.K_d:
				moving_right = True
			if event.key == pygame.K_w and player.alive:
				player.jump = True
			if event.key == pygame.K_ESCAPE:
				run = False
			if event.key == pygame.K_q:
				grenade = True
			if event.key == pygame.K_SPACE:
				shoot = True

		if event.type == pygame.KEYUP:
			if event.key == pygame.K_a:
				moving_left = False
			if event.key == pygame.K_d:
				moving_right = False
			if event.key == pygame.K_q:
				grenade = False
				grenade_thrown = False



	pygame.display.update()

pygame.quit()