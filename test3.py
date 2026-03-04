import pyxel

pyxel.init(160, 120, title="状態管理")

class Game:
    def __init__(self):
        self.state = "TITLE"
        self.score = 0

    def update(self):
        if self.state == "TITLE":
            if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A):
                self.state = "PLAYING"
        elif self.state == "PLAYING":
            self.score += 1
            if self.score >= 10:
                self.state = "GAMEOVER"
        elif self.state == "GAMEOVER":
            if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A):
                self.score = 0
                self.state = "TITLE"
        
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

    def draw(self):
        pyxel.cls(0)
        if self.state == "TITLE":
            pyxel.text(60, 60, "PRESS SPACE", 7)
        elif self.state == "PLAYING":
            pyxel.text(10, 10, f"Score: {self.score}", 7)
        elif self.state == "GAMEOVER":
            pyxel.text(60, 60, "GAME OVER", 8)
            pyxel.text(45, 70, "PRESS SPACE TO RESTART", 7)

game = Game()
pyxel.run(game.update, game.draw)


