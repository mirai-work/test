import pyxel
import math
import random

WIDTH = 160
HEIGHT = 120
CHARGE_MAX = 30
GRAZE_DIST = 8


# ==================================================
# Bullet
# ==================================================
class Bullet:
    def __init__(self, x, y, vx, vy, owner, suit, penetrate=False):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.owner = owner
        self.suit = suit
        self.dead = False
        self.grazed = False
        self.penetrate = penetrate

    def update(self, game):
        # ハート弾は微ホーミング
        if self.owner == "player" and self.suit == "heart":
            dx = game.boss.x - self.x
            dy = game.boss.y - self.y
            ang = math.atan2(dy, dx)
            self.vx += math.cos(ang) * 0.05
            self.vy += math.sin(ang) * 0.05

        self.x += self.vx
        self.y += self.vy

        if self.x < 0 or self.x > WIDTH or self.y < 0 or self.y > HEIGHT:
            self.dead = True

    def draw(self):
        colors = {"diamond": 10, "heart": 8, "club": 3, "spade": 13}
        pyxel.circ(self.x, self.y, 2, colors[self.suit])


# ==================================================
# Bullet Manager
# ==================================================
class BulletManager:
    def __init__(self):
        self.bullets = []

    def add(self, b):
        self.bullets.append(b)

    def update(self, game):
        for b in self.bullets:
            b.update(game)
        self.bullets = [b for b in self.bullets if not b.dead]

    def draw(self):
        for b in self.bullets:
            b.draw()


# ==================================================
# Player
# ==================================================
class Player:
    def __init__(self):
        self.x = 80
        self.y = 100
        self.hp = 30
        self.invincible = 0
        self.charge = 0
        self.score = 0
        self.auto_timer = 0

    def update(self, game):
        if pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT):
            self.x -= 2
        if pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT):
            self.x += 2
        if pyxel.btn(pyxel.KEY_UP) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_UP):
            self.y -= 2
        if pyxel.btn(pyxel.KEY_DOWN) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN):
            self.y += 2

        self.x = max(10, min(150, self.x))
        self.y = max(10, min(110, self.y))

        if self.invincible > 0:
            self.invincible -= 1

        # ===== SHIFT + Z で通常弾連射 =====
        if pyxel.btn(pyxel.KEY_SHIFT) and pyxel.btn(pyxel.KEY_Z):
            self.auto_timer += 1
            if self.auto_timer % 5 == 0:
                game.player_bullets.add(
                    Bullet(self.x, self.y - 4, 0, -4,
                           "player", "diamond", False)
                )
            self.charge = 0
            return
        else:
            self.auto_timer = 0

        # ===== 通常チャージ =====
        if pyxel.btn(pyxel.KEY_Z):
            self.charge = min(self.charge + 1, CHARGE_MAX)
        else:
            if self.charge > 0:
                self.fire(game)
            self.charge = 0

    def fire(self, game):
        if self.charge < 10:
            suit = "diamond"
            vx = 0
            vy = -4
            penetrate = False

        elif self.charge < 20:
            suit = "heart"
            dx = game.boss.x - self.x
            dy = game.boss.y - (self.y - 4)
            ang = math.atan2(dy, dx)
            vx = math.cos(ang) * 4
            vy = math.sin(ang) * 4
            penetrate = False

        else:
            suit = "spade"
            vx = 0
            vy = -4
            penetrate = True

        game.player_bullets.add(
            Bullet(self.x, self.y - 4, vx, vy, "player", suit, penetrate)
        )

    def draw(self):
        if self.invincible % 4 < 2:
            pyxel.circ(self.x, self.y, 3, 7)

        if self.charge > 0:
            pyxel.rect(self.x - 10, self.y - 8, self.charge, 2, 9)


# ==================================================
# Boss
# ==================================================
class Boss:
    def __init__(self, game):
        self.game = game
        self.x = 80
        self.y = 40
        self.max_hp = 200
        self.hp = 200
        self.phase = 1
        self.timer = 0
        self.dead = False
        self.phase_intro = 0
        self.true_mode = False

    def update(self):
        if self.phase_intro > 0:
            self.phase_intro -= 1
            return

        self.timer += 1
        self.x = 80 + math.sin(self.timer * 0.02) * 30

        if self.hp < 140 and self.phase == 1:
            self.phase = 2
            self.phase_intro = 60

        if self.hp < 70 and self.phase == 2:
            self.phase = 3
            self.phase_intro = 60

        if self.hp <= 0 and not self.true_mode:
            self.true_mode = True
            self.hp = 150
            self.phase_intro = 90

        if self.true_mode and self.hp <= 0:
            self.dead = True

        if not self.true_mode:
            if self.phase == 1:
                self.phase_one()
            elif self.phase == 2:
                self.phase_two()
            elif self.phase == 3:
                self.phase_three()
        else:
            self.true_phase()

    def phase_one(self):
        if self.timer % 30 == 0:
            for i in range(12):
                ang = math.radians(i * 30)
                self.game.enemy_bullets.add(
                    Bullet(self.x, self.y,
                           math.cos(ang) * 2,
                           math.sin(ang) * 2,
                           "enemy", "diamond")
                )

    def phase_two(self):
        if self.timer % 5 == 0:
            ang = math.radians(self.timer * 6)
            self.game.enemy_bullets.add(
                Bullet(self.x, self.y,
                       math.cos(ang) * 2.5,
                       math.sin(ang) * 2.5,
                       "enemy", "heart")
            )

    def phase_three(self):
        if self.timer % 15 == 0:
            for i in range(16):
                ang = math.radians(i * 22.5)
                suit = random.choice(["club", "spade"])
                self.game.enemy_bullets.add(
                    Bullet(self.x, self.y,
                           math.cos(ang) * 3,
                           math.sin(ang) * 3,
                           "enemy", suit)
                )

    def true_phase(self):
        if self.timer % 5 == 0:
            ang = math.radians(self.timer * 10)
            for i in range(6):
                a = ang + math.radians(i * 60)
                self.game.enemy_bullets.add(
                    Bullet(self.x, self.y,
                           math.cos(a) * 3.5,
                           math.sin(a) * 3.5,
                           "enemy", "spade")
                )

    def draw(self):
        pyxel.circ(self.x, self.y, 10, 9)

        ratio = self.hp / self.max_hp
        pyxel.rect(30, 10, 100, 4, 1)
        pyxel.rect(30, 10, 100 * ratio, 4, 8)

        if self.phase_intro > 0:
            pyxel.text(55, 60, f"PHASE {self.phase}", 10)


# ==================================================
# Game
# ==================================================
class Game:
    def __init__(self):
        pyxel.init(WIDTH, HEIGHT, title="Chaos Pro Final")
        self.reset()
        pyxel.run(self.update, self.draw)

    def reset(self):
        self.player = Player()
        self.player_bullets = BulletManager()
        self.enemy_bullets = BulletManager()
        self.boss = Boss(self)
        self.state = "playing"

    def update(self):
        if pyxel.btnp(pyxel.KEY_R):
            self.reset()

        if self.state == "playing":
            self.player.update(self)
            self.boss.update()
            self.player_bullets.update(self)
            self.enemy_bullets.update(self)

            # プレイヤー弾 → ボス
            for b in self.player_bullets.bullets:
                if abs(b.x - self.boss.x) < 12 and abs(b.y - self.boss.y) < 12:
                    self.boss.hp -= 2
                    if not b.penetrate:
                        b.dead = True

            # 敵弾 → プレイヤー
            for b in self.enemy_bullets.bullets:
                dx = b.x - self.player.x
                dy = b.y - self.player.y
                dist = math.hypot(dx, dy)

                if dist < 4 and self.player.invincible == 0:
                    self.player.hp -= 1
                    self.player.invincible = 30
                elif dist < GRAZE_DIST and not b.grazed:
                    self.player.score += 1
                    b.grazed = True

            # HP0でGAMEOVER
            if self.player.hp <= 0:
                self.state = "gameover"

            if self.boss.dead:
                self.state = "clear"

    def draw(self):
        pyxel.cls(0)

        self.boss.draw()
        self.player_bullets.draw()
        self.enemy_bullets.draw()
        self.player.draw()

        pyxel.text(5, 5, f"HP:{self.player.hp}", 7)
        pyxel.text(5, 15, f"SCORE:{self.player.score}", 7)

        if self.state == "clear":
            pyxel.text(55, 60, "ALL CLEAR", 10)

        if self.state == "gameover":
            pyxel.text(50, 55, "GAME OVER", 8)
            pyxel.text(45, 65, "PRESS R TO RETRY", 7)


Game()

