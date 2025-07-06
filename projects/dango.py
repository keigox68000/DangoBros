import pyxel
import random

# --- ゲーム設定 ---
SCREEN_WIDTH = 320
SCREEN_HEIGHT = 240
TARGET_RADIUS = 16  # 32x32ドットの円
TARGET_COUNT = 5
BAR_LENGTH = 100
BAR_SPEED = 8
HIT_TOLERANCE_Y = 4


class Target:
    """上下に動く円（ターゲット）"""

    def __init__(self, x):
        self.initial_x = x
        self.x = x
        self.y = random.randint(TARGET_RADIUS, SCREEN_HEIGHT - TARGET_RADIUS)
        self.speed_y = random.uniform(1.5, 4.0) * random.choice([-1, 1])
        self.is_hit = False
        self.is_stuck = False

    def update(self):
        """座標を更新"""
        if not self.is_stuck:
            self.y += self.speed_y
            if self.y <= TARGET_RADIUS or self.y >= SCREEN_HEIGHT - TARGET_RADIUS:
                self.speed_y *= -1

    def draw(self):
        """円を描画"""
        color = pyxel.COLOR_YELLOW if self.is_hit else pyxel.COLOR_PINK
        pyxel.circ(self.x, self.y, TARGET_RADIUS, color)

    def reset(self):
        """ターゲットの状態を初期位置・状態に戻す"""
        self.x = self.initial_x
        self.is_hit = False
        self.is_stuck = False
        self.y = random.randint(TARGET_RADIUS, SCREEN_HEIGHT - TARGET_RADIUS)
        self.speed_y = random.uniform(1.5, 4.0) * random.choice([-1, 1])


class Bar:
    """プレイヤーが操作する棒"""

    def __init__(self):
        self.x = SCREEN_WIDTH
        self.y = SCREEN_HEIGHT // 2
        self.length = BAR_LENGTH
        self.is_firing = False
        self.hit_count = 0

    def update(self):
        """棒の状態を更新"""
        if self.is_firing:
            if self.x > 0:
                self.x -= BAR_SPEED
            else:
                self.x = 0
        else:
            self.y = pyxel.mouse_y

    def draw(self):
        """棒を描画"""
        if self.is_firing:
            pyxel.rect(self.x, self.y - 1, self.length, 3, pyxel.COLOR_WHITE)
        else:
            pyxel.rect(SCREEN_WIDTH - 8, self.y - 1, 8, 3, pyxel.COLOR_WHITE)

    def fire(self):
        """棒を発射する"""
        if not self.is_firing:
            self.is_firing = True
            self.hit_count = 0
            self.x = SCREEN_WIDTH

    def reset(self):
        """棒の状態を初期位置に戻す"""
        self.is_firing = False


class Game:
    """ゲーム全体を管理"""

    def __init__(self):
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="Bar Shooter v8", fps=60)
        pyxel.mouse(True)
        self.score = 0
        self.player_bar = Bar()
        self.targets = []
        for i in range(TARGET_COUNT):
            x_pos = 40 + i * 60
            self.targets.append(Target(x_pos))

        self.game_state = "ready"
        self.last_hit_count = 0
        # ★修正：虹色のリスト。COLOR_BLUE を正しい定数名 COLOR_CYAN に変更
        self.RAINBOW_COLORS = [
            pyxel.COLOR_RED,
            pyxel.COLOR_ORANGE,
            pyxel.COLOR_YELLOW,
            pyxel.COLOR_LIME,
            pyxel.COLOR_CYAN,
            pyxel.COLOR_PURPLE,
        ]
        pyxel.run(self.update, self.draw)

    def update(self):
        # 刺さっていない団子を更新
        for target in self.targets:
            if not target.is_stuck:
                target.update()

        if self.game_state == "ready":
            self.player_bar.update()
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                self.player_bar.fire()
                self.game_state = "firing"

        elif self.game_state == "firing":
            self.player_bar.update()

            # 刺さった団子を棒と一緒に移動させる
            for target in self.targets:
                if target.is_stuck:
                    if self.player_bar.x > 0:
                        target.x -= BAR_SPEED

            self.check_collision()

            if self.player_bar.x <= 0:
                self.game_state = "stuck"
                self.last_hit_count = self.player_bar.hit_count
                if self.last_hit_count > 0:
                    self.score += self.last_hit_count**2

        elif self.game_state == "stuck":
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                self.reset_turn()
                self.game_state = "ready"

    def check_collision(self):
        """当たり判定"""
        bar = self.player_bar
        for target in self.targets:
            if not target.is_hit:
                is_x_hit = bar.x <= target.x <= bar.x + bar.length
                is_y_hit = abs(bar.y - target.y) < HIT_TOLERANCE_Y

                if is_x_hit and is_y_hit:
                    target.is_hit = True
                    target.is_stuck = True
                    bar.hit_count += 1

    def reset_turn(self):
        """ターンをリセットする処理"""
        self.player_bar.reset()
        for target in self.targets:
            target.reset()

    def draw(self):
        pyxel.cls(pyxel.COLOR_NAVY)

        self.player_bar.draw()
        for target in self.targets:
            target.draw()

        pyxel.text(5, 5, f"SCORE: {self.score}", pyxel.COLOR_WHITE)
        if self.player_bar.is_firing:
            pyxel.text(
                SCREEN_WIDTH - 60,
                5,
                f"HIT: {self.player_bar.hit_count}",
                pyxel.COLOR_LIME,
            )

        if self.game_state == "stuck":
            # 結果メッセージを作成
            if self.last_hit_count > 0:
                result_msg = f"DANGO {self.last_hit_count} Bros.!"
            else:
                result_msg = "MISS!"

            # 結果メッセージを描画
            text_width = len(result_msg) * pyxel.FONT_WIDTH
            pyxel.text(
                (SCREEN_WIDTH - text_width) / 2,
                SCREEN_HEIGHT / 2 - 20,
                result_msg,
                pyxel.COLOR_WHITE,
            )

            # ヒット数に応じた祝福メッセージを表示
            celebration_msg = ""
            if self.last_hit_count == 3:
                celebration_msg = "Congratulations!!"
            elif self.last_hit_count == 4:
                celebration_msg = "Amazing!!"
            elif self.last_hit_count == 5:
                celebration_msg = "Legendary!!"

            if celebration_msg:
                # 虹色に光らせる処理
                msg_width = len(celebration_msg) * pyxel.FONT_WIDTH
                start_x = (SCREEN_WIDTH - msg_width) / 2
                y_pos = SCREEN_HEIGHT / 2 - 4
                for i, char in enumerate(celebration_msg):
                    # フレームカウントと文字の位置によって色を決定
                    color = self.RAINBOW_COLORS[
                        (i + pyxel.frame_count // 3) % len(self.RAINBOW_COLORS)
                    ]
                    pyxel.text(start_x + i * pyxel.FONT_WIDTH, y_pos, char, color)

            # 継続メッセージを描画
            continue_msg = "CLICK TO CONTINUE"
            text_width = len(continue_msg) * pyxel.FONT_WIDTH
            pyxel.text(
                (SCREEN_WIDTH - text_width) / 2,
                SCREEN_HEIGHT / 2 + 20,
                continue_msg,
                pyxel.COLOR_WHITE,
            )


# ゲームを開始
Game()
