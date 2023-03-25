from pygame import *
from random import *
from time import time as timer

init()
mixer.init()

info = display.Info()

WIDTH = info.current_w
HEIGHT = info.current_h

clock = time.Clock()
FPS = 60

window = display.set_mode((WIDTH, HEIGHT))
display.set_caption("Shooter")
background = transform.scale(image.load("image/galaxy.jpg"), (WIDTH, HEIGHT))

shoot = mixer.Sound("sounds/fire.ogg")
shoot.set_volume(0.1)

mixer.music.load("sounds/space.ogg")
mixer.music.set_volume(0.01)
mixer.music.play()

font_interface = font.Font(None, HEIGHT // 25)
font_finish = font.Font(None, HEIGHT // 5)

text_win = font_finish.render("You WIN!", True, (50, 250, 50))
text_lose = font_finish.render("You LOSE!", True, (250, 50, 50))

lost = 0
text_lost = font_interface.render("Пропущено: " + str(lost), True, (255, 255, 255))

score = 0
text_score = font_interface.render("Рахунок:" + str(score), True, (255, 255, 255))


class GameSprite(sprite.Sprite):
    def __init__(self, sprite_image, x, y, width, height, speed):
        super().__init__()
        self.image = transform.scale(image.load(sprite_image), (width, height))
        self.speed = speed
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))


class Player(GameSprite):
    def __init__(self, x, y):
        super().__init__("image/rocket.png", x, y, HEIGHT // 6, HEIGHT // 5, HEIGHT // 50)
        self.kd = 0
        self.hp = 3
        self.clip = 10
        self.reload = False
        self.start_reload = 0

    def update(self):
        global interface_clip
        keys_pressed = key.get_pressed()

        if keys_pressed[K_a] and self.rect.x > 5:
            self.rect.x -= self.speed
        if keys_pressed[K_d] and self.rect.x < WIDTH - self.rect.width - 5:
            self.rect.x += self.speed
        if (keys_pressed[K_SPACE] and self.kd <= 0) and (self.clip >= 0 and not self.reload):
            bullet = Bullet(self.rect.centerx - HEIGHT // 50, self.rect.top)
            bullets.add(bullet)
            shoot.play()
            self.clip -= 1
            interface_clip = interface_clip[:-1]
            self.kd = 10
        else:
            self.kd -= 1
        if self.clip <= 0:
            self.reload = True
            self.clip = 10
            self.start_reload = timer()

        if self.reload:
            current_time = timer()
            if current_time - self.start_reload >= 1.5:
                self.reload = False
                interface_clip = []
                ammo_x = WIDTH // 20
                for i in range (player.clip):
                    ammo = GameSprite("image/bullet.png", ammo_x, HEIGHT - HEIGHT // 9, HEIGHT // 20, HEIGHT // 12, 0)
                    interface_clip.append(ammo)
                    ammo_x += HEIGHT // 25


class Enemy(GameSprite):
    def __init__(self):
        super().__init__("image/ufo.png", randint(0, WIDTH - HEIGHT // 5), randint(-HEIGHT, -HEIGHT // 7), HEIGHT // 5,
                         HEIGHT // 8, HEIGHT // 300)

    def update(self):
        global text_lost
        global lost
        self.rect.y += self.speed
        if self.rect.y >= HEIGHT:
            lost += 1
            self.rect.y = -HEIGHT // 7
            self.rect.x = randint(0, WIDTH - HEIGHT // 5)
            text_lost = font_interface.render("Пропущено: " + str(lost), True, (255, 255, 255))


class UfoBoss(GameSprite):
    def __init__(self):
        super().__init__("image/ufo.png", randint(0, WIDTH - HEIGHT // 5), -HEIGHT // 4, HEIGHT // 2.5, HEIGHT // 4,
                         HEIGHT // 500)

    def update(self):
        global text_lost
        global lost
        self.rect.y += self.speed
        if self.rect.y >= HEIGHT:
            lost += 3
            self.kill()
            text_lost = font_interface.render("Пропущено: " + str(lost), True, (255, 255, 255))


class Bullet(GameSprite):
    def __init__(self, x, y):
        super().__init__("image/bullet.png", x, y, HEIGHT // 25, HEIGHT // 15, HEIGHT // 50)

    def update(self):
        self.rect.y -= self.speed
        if self.rect.y <= -self.rect.height:
            self.kill()

class Asteroid(GameSprite):
    def __init__(self):
        self.size = randint(HEIGHT // 15, HEIGHT // 7)
        super().__init__("image/asteroid.png", randint(0, WIDTH - HEIGHT // 6), randint(-HEIGHT, -HEIGHT // 7), self.size, self.size, HEIGHT // 150)

    def update(self):
        self.rect.y += self.speed
        if self.rect.y >= HEIGHT:
            self.rect.y = -HEIGHT // 7
            self.rect.x = randint(0, WIDTH - HEIGHT // 5)

game = True

player = Player((WIDTH - HEIGHT // 6) // 2, HEIGHT - HEIGHT // 4.5)

asteroids = sprite.Group()
for i in range(3):
    asteroid = Asteroid()
    asteroids.add(asteroid)

monsters = sprite.Group()
for i in range(10):
    monster = Enemy()
    monsters.add(monster)

interface_clip = []
ammo_x = WIDTH // 20
for i in range(player.clip):
    ammo = GameSprite("image/bullet.png", ammo_x, HEIGHT - HEIGHT // 9, HEIGHT // 20, HEIGHT // 12, 0)
    interface_clip.append(ammo)
    ammo_x += HEIGHT // 25

boss = 0

bullets = sprite.Group()

health = []

heart_x = WIDTH - WIDTH // 12
for i in range(player.hp):
    heart = GameSprite("image/health.png", heart_x, HEIGHT // 15, HEIGHT // 14, HEIGHT // 14, 0)
    heart_x -= HEIGHT // 12
    health.append(heart)
finish = False
while game:
    for e in event.get():
        if e.type == QUIT:
            game = False
        if e.type == KEYDOWN:
            if e.key == K_ESCAPE:
                game = False
    if not finish:

        window.blit(background, (0, 0))

        player.update()
        player.reset()

        bullets.update()
        bullets.draw(window)

        asteroids.update()
        asteroids.draw(window)

        crush_list = sprite.spritecollide(player, monsters, False)

        crush_list_asteroids = sprite.spritecollide(player, asteroids, False)

        dead_monsters = sprite.groupcollide(monsters, bullets, False, True)

        hit_asteroids = sprite.groupcollide(asteroids, bullets, False, True)

        if not boss:
            if score % 20 == 0 and score != 0:
                boss = UfoBoss()
        else:
            boss.update()
            boss.reset()
            hit_boss = sprite.spritecollide(boss, bullets, True)
            if sprite.collide_rect(player, boss):
                boss = 0
                player.hp -= 2
                try:
                    health = health[:-1]
                    health = health[:-1]
                except:
                    health.clear()
            if len(hit_boss) != 0:
                for hit in hit_boss:
                    boss.hp -= 1
                    print(boss.hp)
                if boss.hp <= 0:
                    boss = 0
                    player.hp += 1
                    heart_x = (WIDTH - WIDTH // 12) - (HEIGHT // 12 * (player.hp - 1))
                    heart = GameSprite("image/health.png", heart_x, HEIGHT // 15, HEIGHT // 14, HEIGHT // 14, 0)
                    health.append(heart)

        if len(dead_monsters) != 0:
            score += 1
            text_score = font_interface.render("Рахунок:" + str(score), True, (255, 255, 255))
            for monster in dead_monsters:
                monster.rect.x = randint(0, WIDTH - HEIGHT // 5)
                monster.rect.y = randint(-HEIGHT, -HEIGHT // 7)
        if len(crush_list) != 0:
            player.hp -= 1
            try:
                health = health[:-1]
            except:
                health.clear()
            for monster in crush_list:
                monster.rect.x = randint(0, WIDTH - HEIGHT // 5)
                monster.rect.y = randint(-HEIGHT, -HEIGHT // 7)

        if len(crush_list_asteroids) != 0:
            player.hp -= 1
            try:
                health = health[:-1]
            except:
                health.clear()
            for asteroid in crush_list_asteroids:
                asteroid.rect.x = randint(0, WIDTH - HEIGHT // 6)
                asteroid.rect.y = randint(-HEIGHT, -HEIGHT // 6)


        if player.hp <= 0 or lost >= 10:
            window.blit(text_lose, (WIDTH // 3.2, HEIGHT // 2.5))
            finish = True
        if score >= 100:
            window.blit(text_win, (WIDTH // 3, HEIGHT // 2.5))
            finish = True

        monsters.update()
        monsters.draw(window)

        asteroids.update()
        asteroids.draw(window)

        for heart in health:
            heart.reset()

        for ammo in interface_clip:
            ammo.reset()

        window.blit(text_score, (WIDTH // 15, HEIGHT // 7))
        window.blit(text_lost, (WIDTH // 15, HEIGHT // 10))

        display.update()
        clock.tick(FPS)












