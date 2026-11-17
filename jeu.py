
import random
import tkinter as tk
from pathlib import Path

WIDTH = 700
HEIGHT = 440
FRUIT_COLORS = ("#e84b4b", "#f39c35", "#f2c94c", "#70b852", "#a56bd4")
BEST_SCORE_FILE = Path(__file__).with_name("meilleur_score.txt")


class FruitCatch:
    def __init__(self, root):
        self.root = root
        self.root.title("Attrape les fruits")
        self.root.resizable(False, False)
        self.root.configure(bg="#102033")

        self.score = 0
        self.lives = 3
        self.best_score = self.load_best_score()
        self.fruits = []
        self.running = False
        self.after_id = None
        self.spawn_counter = 0
        self.basket_width = 100
        self.basket_height = 22
        self.basket_x = (WIDTH - self.basket_width) // 2
        self.basket_y = HEIGHT - 48

        hud = tk.Frame(root, bg="#102033", padx=18, pady=12)
        hud.pack(fill="x")
        self.score_label = self.make_hud_label(hud, "Score", 0)
        self.best_label = self.make_hud_label(hud, "Meilleur", self.best_score)
        self.lives_label = self.make_hud_label(hud, "Vies", self.lives)

        self.canvas = tk.Canvas(
            root, width=WIDTH, height=HEIGHT, bg="#a7e4f5",
            highlightthickness=0,
        )
        self.canvas.pack(padx=16)
        self.canvas.create_rectangle(0, HEIGHT - 30, WIDTH, HEIGHT, fill="#398454", outline="")
        self.basket = self.canvas.create_rectangle(
            self.basket_x, self.basket_y,
            self.basket_x + self.basket_width, self.basket_y + self.basket_height,
            fill="#dc8a42", outline="#8d5126", width=3,
        )
        self.canvas.create_arc(
            self.basket_x + 12, self.basket_y - 10,
            self.basket_x + self.basket_width - 12, self.basket_y + 20,
            start=0, extent=180, style=tk.ARC, outline="#8d5126", width=4,
        )

        controls = tk.Frame(root, bg="#102033", pady=12)
        controls.pack(fill="x")
        self.start_button = tk.Button(
            controls, text="Démarrer", command=self.start_game,
            font=("Arial", 12, "bold"), bg="#06d6a0", fg="#073b35",
            activebackground="#00bd8d", relief="flat", padx=24, pady=8,
        )
        self.start_button.pack()
        self.root.bind("<Left>", lambda event: self.move_basket(self.basket_x - 30))
        self.root.bind("<Right>", lambda event: self.move_basket(self.basket_x + 30))
        self.canvas.bind("<Motion>", self.follow_mouse)

        self.show_message("Attrape les fruits !", "Clique sur Démarrer pour jouer")

    @staticmethod
    def make_hud_label(parent, title, value):
        block = tk.Frame(parent, bg="#1d344b", padx=14, pady=7)
        block.pack(side="left", expand=True, fill="x", padx=5)
        tk.Label(block, text=title, bg="#1d344b", fg="#dce8f2", font=("Arial", 10)).pack()
        value_label = tk.Label(
            block, text=str(value), bg="#1d344b", fg="#ffd166",
            font=("Arial", 18, "bold"),
        )
        value_label.pack()
        return value_label

    @staticmethod
    def load_best_score():
        try:
            return int(BEST_SCORE_FILE.read_text(encoding="utf-8").strip())
        except (OSError, ValueError):
            return 0

    def show_message(self, title, subtitle):
        self.canvas.delete("message")
        self.canvas.create_text(
            WIDTH // 2, HEIGHT // 2 - 18, text=title,
            font=("Arial", 28, "bold"), fill="#15314a", tags="message",
        )
        self.canvas.create_text(
            WIDTH // 2, HEIGHT // 2 + 22, text=subtitle,
            font=("Arial", 14), fill="#15314a", tags="message",
        )

    def start_game(self):
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
        self.canvas.delete("fruit")
        self.canvas.delete("message")
        self.fruits.clear()
        self.score = 0
        self.lives = 3
        self.spawn_counter = 0
        self.score_label.config(text="0")
        self.lives_label.config(text="3")
        self.running = True
        self.start_button.config(text="Recommencer")
        self.after_id = self.root.after(30, self.update_game)

    def move_basket(self, x):
        self.basket_x = max(0, min(WIDTH - self.basket_width, x))
        self.canvas.coords(
            self.basket, self.basket_x, self.basket_y,
            self.basket_x + self.basket_width,
            self.basket_y + self.basket_height,
        )

    def follow_mouse(self, event):
        if self.running:
            self.move_basket(event.x - self.basket_width // 2)

    def spawn_fruit(self):
        x = random.randint(20, WIDTH - 20)
        y = -20
        color = random.choice(FRUIT_COLORS)
        fruit_id = self.canvas.create_oval(
            x - 15, y - 15, x + 15, y + 15,
            fill=color, outline="#ffffff", width=2, tags="fruit",
        )
        self.canvas.create_line(x, y - 14, x + 3, y - 22, fill="#654321", width=3, tags="fruit")
        self.canvas.create_oval(x + 2, y - 22, x + 12, y - 17, fill="#398454", outline="", tags="fruit")
        self.fruits.append({"id": fruit_id, "x": x, "y": y, "speed": random.randint(3, 5)})

    def update_game(self):
        if not self.running:
            return

        self.spawn_counter += 1
        if self.spawn_counter >= max(18, 38 - self.score // 5):
            self.spawn_fruit()
            self.spawn_counter = 0

        basket_left = self.basket_x
        basket_right = self.basket_x + self.basket_width
        remaining = []
        for fruit in self.fruits:
            fruit["y"] += fruit["speed"] + min(self.score // 10, 5)
            x, y = fruit["x"], fruit["y"]
            self.canvas.coords(fruit["id"], x - 15, y - 15, x + 15, y + 15)
            self.canvas.move(fruit["id"] + 1, 0, fruit["speed"] + min(self.score // 10, 5))
            self.canvas.move(fruit["id"] + 2, 0, fruit["speed"] + min(self.score // 10, 5))

            caught = y + 15 >= self.basket_y and y - 15 <= self.basket_y + self.basket_height and basket_left <= x <= basket_right
            if caught:
                self.score += 1
                self.score_label.config(text=str(self.score))
                if self.score > self.best_score:
                    self.best_score = self.score
                    self.best_label.config(text=str(self.best_score))
                    try:
                        BEST_SCORE_FILE.write_text(str(self.best_score), encoding="utf-8")
                    except OSError:
                        pass
                self.canvas.delete(fruit["id"])
                self.canvas.delete(fruit["id"] + 1)
                self.canvas.delete(fruit["id"] + 2)
            elif y - 15 > HEIGHT - 30:
                self.lives -= 1
                self.lives_label.config(text=str(self.lives))
                self.canvas.delete(fruit["id"])
                self.canvas.delete(fruit["id"] + 1)
                self.canvas.delete(fruit["id"] + 2)
                if self.lives <= 0:
                    self.end_game()
                    return
            else:
                remaining.append(fruit)

        self.fruits = remaining
        self.after_id = self.root.after(30, self.update_game)

    def end_game(self):
        self.running = False
        self.after_id = None
        self.show_message("Partie terminée !", f"Score : {self.score}  |  Clique sur Recommencer")


if __name__ == "__main__":
    root = tk.Tk()
    FruitCatch(root)
    root.mainloop()
