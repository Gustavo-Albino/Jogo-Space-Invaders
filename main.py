import pygame
from pygame import mixer
from pygame.locals import *
import random

pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()

#define o fps
clock = pygame.time.Clock()
fps = 60

screen_width = 600
screen_height = 800

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Space Invaders')

#define as fontes
font30 = pygame.font.SysFont('Constantia', 30)
font40 = pygame.font.SysFont('Constantia', 40)


#carrega os sons
explosion_fx = pygame.mixer.Sound('img/explosion.wav')
explosion_fx.set_volume(0.25)

explosion2_fx = pygame.mixer.Sound('img/explosion2.wav')
explosion2_fx.set_volume(0.25)

laser_fx = pygame.mixer.Sound('img/laser.wav')
laser_fx.set_volume(0.25)

#define variaveis do jogo
rows = 5
cols = 5
alien_cooldown = 1000 #milisegundos
last_alien_shot = pygame.time.get_ticks()
countdown = 3
last_count = pygame.time.get_ticks()
game_over = 0

#define as cores
red = (255, 0, 0)
green = (0, 255, 0)
white = (255, 255, 255)

#carrega imagem de background
bg = pygame.image.load('img/bg.png')

def draw_bg():
	screen.blit(bg, (0, 0))

#define função para criação de texto
def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))


#cria a classe spaceship
class Spaceship(pygame.sprite.Sprite):
	def __init__(self, x, y, health):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load('img/spaceship.png')
		self.rect = self.image.get_rect()
		self.rect.center = [x, y]
		self.health_start = health
		self.health_remaining = health
		self.last_shot = pygame.time.get_ticks()

	def update(self):
		#define a velocidade de movimento
		speed = 8
		#define a cooldown
		cooldown = 500 #milisegundos
		game_over = 0

		#verifica a tecla pressionada
		key = pygame.key.get_pressed()

		if key[pygame.K_LEFT] and self.rect.left > 0 or key[pygame.K_a] and self.rect.left > 0:
			self.rect.x -= speed
		if key[pygame.K_RIGHT] and self.rect.right < screen_width or key[pygame.K_d] and self.rect.right < screen_width:
			self.rect.x += speed

		#grava o tempo atual
		time_now = pygame.time.get_ticks()
		#tiro
		if key[pygame.K_SPACE] and time_now - self.last_shot > cooldown:
			bullet = Bullets(self.rect.centerx, self.rect.top)
			bullet_group.add(bullet)
			self.last_shot = time_now
			laser_fx.play()

		#atualiza a máscara
		self.mask = pygame.mask.from_surface(self.image)

		#desenha a barra de vidas
		pygame.draw.rect(screen, red, (self.rect.x, (self.rect.bottom + 10), self.rect.width, 15))
		if self.health_remaining > 0:
			pygame.draw.rect(screen, green, (self.rect.x, (self.rect.bottom + 10), int(self.rect.width * (self.health_remaining / self.health_start)), 15))
		elif self.health_remaining <= 0:
			explosion = Explosion(self.rect.centerx, self.rect.centery, 3)
			explosion_group.add(explosion)
			self.kill()
			game_over = -1
		return game_over
		
#cria a classe de disparos (bullets)
class Bullets(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load('img/bullet.png')
		self.rect = self.image.get_rect()
		self.rect.center = [x, y]

	def update(self):
		self.rect.y -= 5
		if self.rect.bottom < 0:
			self.kill()
		if pygame.sprite.spritecollide(self, alien_group, True):
			self.kill()
			explosion_fx.play()
			explosion = Explosion(self.rect.centerx, self.rect.centery, 2)
			explosion_group.add(explosion)

#cria a classe de Aliens
class Aliens(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load('img/alien' + str(random.randint(1, 5)) + '.png')
		self.rect = self.image.get_rect()
		self.rect.center = [x, y]
		self.move_counter = 0
		self.move_direction = 1

	def update(self):
		self.rect.x += self.move_direction
		self.move_counter += 1
		if abs(self.move_counter) > 75:
			self.move_direction *= -1
			self.move_counter *= self.move_direction


#cria a classe de disparos dos aliens
class AllienBullets(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load('img/alien_bullet.png')
		self.rect = self.image.get_rect()
		self.rect.center = [x, y]

	def update(self):
		self.rect.y += 2
		if self.rect.top > screen_height:
			self.kill()
		if pygame.sprite.spritecollide(self, spaceship_group, False, pygame.sprite.collide_mask):
			self.kill()
			#reduz a "vida" da nave
			spaceship.health_remaining -= 1
			explosion = Explosion(self.rect.centerx, self.rect.centery, 1)
			explosion_group.add(explosion)

#cria uma classe explosão
class Explosion(pygame.sprite.Sprite):
	def __init__(self, x, y, size):
		pygame.sprite.Sprite.__init__(self)
		self.images = []
		for num in range(1, 6):
			img = pygame.image.load(f'img/exp{num}.png')
			if size == 1:
				img = pygame.transform.scale(img, (20, 20))
			if size == 2:
				img = pygame.transform.scale(img, (40, 40))
			if size == 3:
				img = pygame.transform.scale(img, (160, 160))
			#adiciona imagem à lista
			self.images.append(img)

		self.index = 0
		self.image = self.images[self.index]
		self.rect = self.image.get_rect()
		self.rect.center = [x, y]
		self.counter = 0

	def update(self):
		explosion_speed = 3
		#atualiza animação de explosão
		self.counter += 1

		if self.counter >= explosion_speed and self.index < len(self.images) - 1:
			self.counter = 0
			self.index += 1
			self.image = self.images[self.index]

		#se a animação estiver completa, deleta a explosão
		if self.index >= len(self.images) - 1 and self.counter >= explosion_speed:
			self.kill()

#cria grupos de sprite
spaceship_group = pygame.sprite.Group()	
bullet_group = pygame.sprite.Group()
alien_group = pygame.sprite.Group()
alien_bullet_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()

#cria os inimigos/Aliens
def create_aliens():
	#gera aliens
	for row in range(rows):
		for item in range(cols):
			alien = Aliens(100 + item * 100, 100 + row * 70)
			alien_group.add(alien)

create_aliens()

#cria jogador
spaceship = Spaceship(int(screen_width/2), screen_height-100, 3)
spaceship_group.add(spaceship)


run = True
while run:

	clock.tick(fps)

	#desenha o background
	draw_bg()

	if countdown == 0:

		#cria ataques de aliens aleatórios
		#grava o tempo atual
		time_now = pygame.time.get_ticks()
		#disparo
		if time_now - last_alien_shot > alien_cooldown and len(alien_bullet_group) < 5 and len(alien_group) > 0:
			attacking_alien = random.choice(alien_group.sprites())
			alien_bullet = AllienBullets(attacking_alien.rect.centerx, attacking_alien.rect.bottom)
			alien_bullet_group.add(alien_bullet)
			last_alien_shot = time_now
    
	#tratando eventos
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False

	if countdown > 0:
		draw_text('GET READY!', font40, white, int(screen_width / 2 - 110), int(screen_height / 2 + 50))
		draw_text(str(countdown), font40, white, int(screen_width / 2 - 10), int(screen_height / 2 + 10))
		count_timer = pygame.time.get_ticks()
		if count_timer - last_count > 1000:
			countdown -= 1
			last_count = count_timer
	
	#verifica se todos os aliens foram mortos
	if len(alien_group) == 0:
		game_over = 1

	if game_over == 0:
		#atualiza as naves
		game_over = spaceship.update()

		#atualiza o grupo de sprite
		bullet_group.update()

		#atualiza os aliens
		alien_group.update()

		#atualiza os tiros dos aliens
		alien_bullet_group.update()

		#atualiza a explosão
		explosion_group.update()
	else:
		if game_over == -1:
			draw_text('GAME OVER!', font40, white, int(screen_width / 2 - 100), int(screen_height / 2 + 50))
		if game_over == 1:
			draw_text('YOU WIN!', font40, white, int(screen_width / 2 - 100), int(screen_height / 2 + 50))
		

	#desenha grupos de sprites
	spaceship_group.draw(screen)
	bullet_group.draw(screen)
	alien_group.draw(screen)
	alien_bullet_group.draw(screen)
	explosion_group.draw(screen)

	#atualiza o display
	pygame.display.update()

pygame.quit()