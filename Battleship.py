import sys
import random
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QGridLayout, QLabel, QMessageBox,
    QVBoxLayout, QDialog, QDialogButtonBox, QHBoxLayout
)
from PyQt6.QtCore import Qt, QTimer
from functools import partial

GRID_SIZE = 5

class StartDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Start Game")
        self.setFixedSize(300, 200)
        self.setModal(True)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        label = QLabel("🎯 Welcome to Battleship Game!")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        layout.addWidget(label)

        start_button = QPushButton("Start Game")
        start_button.setFixedSize(120, 40)
        start_button.setStyleSheet("font-size: 14px; font-weight: bold;")
        start_button.clicked.connect(self.accept)
        layout.addWidget(start_button, alignment=Qt.AlignmentFlag.AlignCenter)

        instructions_button = QPushButton("Instructions")
        instructions_button.setFixedSize(120, 35)
        instructions_button.setStyleSheet("font-size: 13px;")
        instructions_button.clicked.connect(self.show_instructions)
        layout.addWidget(instructions_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

    def show_instructions(self):
        instructions = (
            "📜 How to Play:\n\n"
            "1. Place 3 ships on your board (blue tiles).\n"
            "2. Click on the computer's board to shoot.\n"
            "3. You have 20 seconds for each turn.\n"
            "4. Hit: Red tile with 'X'. Miss: Gray tile with 'O'.\n"
            "5. First to sink all 3 opponent ships wins!\n"
            "6. If you don’t move in time, the computer takes a turn."
        )
        QMessageBox.information(self, "Game Instructions", instructions)

class BattleshipGame(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.time_left = 20
        self.user_moved = False
        self.game_started = False
        self.show_start_dialog()

    def initUI(self):
        self.setWindowTitle("Battleship Game")
        self.setGeometry(100, 100, 600, 400)
        self.layout = QGridLayout()
        
        self.status_label = QLabel("Click Start to Begin!", self)
        self.layout.addWidget(self.status_label, 0, 0, 1, GRID_SIZE * 2)
        
        self.timer_label = QLabel("Time Left: 20s", self)
        self.layout.addWidget(self.timer_label, 1, 0, 1, GRID_SIZE * 2)
        
        self.user_board_label = QLabel("User Board", self)
        self.layout.addWidget(self.user_board_label, 2, 0, 1, GRID_SIZE)
        
        self.computer_board_label = QLabel("Computer Board", self)
        self.layout.addWidget(self.computer_board_label, 2, GRID_SIZE + 1, 1, GRID_SIZE)
        
        self.user_buttons = [[QPushButton() for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.computer_buttons = [[QPushButton() for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                self.user_buttons[i][j].setFixedSize(50, 50)
                self.user_buttons[i][j].clicked.connect(partial(self.place_user_ship, i, j))
                self.user_buttons[i][j].setEnabled(False)
                self.layout.addWidget(self.user_buttons[i][j], i + 3, j)
                
                self.computer_buttons[i][j].setFixedSize(50, 50)
                self.computer_buttons[i][j].clicked.connect(partial(self.user_turn, i, j))
                self.computer_buttons[i][j].setEnabled(False)
                self.layout.addWidget(self.computer_buttons[i][j], i + 3, j + GRID_SIZE + 1)
    
        self.setLayout(self.layout)
        self.user_ships = set()
        self.computer_ships = set()
        self.user_shots = set()
        self.computer_shots = set()
    
    def show_start_dialog(self):
        dialog = StartDialog()
        if dialog.exec():
            self.status_label.setText("Place Your Ships!")
            for i in range(GRID_SIZE):
                for j in range(GRID_SIZE):
                    self.user_buttons[i][j].setEnabled(True)
            self.game_started = True
    
    def place_user_ship(self, x, y):
        if not self.game_started:
            return

        if len(self.user_ships) < 3 and (x, y) not in self.user_ships:
            self.user_ships.add((x, y))
            self.user_buttons[x][y].setStyleSheet("background-color: blue; color: white; font-weight: bold;")
        if len(self.user_ships) == 3:
            self.start_game()
    
    def start_game(self):
        self.status_label.setText("Your Turn!")
        self.computer_ships = set(random.sample([(i, j) for i in range(GRID_SIZE) for j in range(GRID_SIZE)], 3))
        for row in self.computer_buttons:
            for button in row:
                button.setEnabled(True)
        self.reset_timer()
    
    def update_timer(self):
        if self.time_left > 0:
            self.time_left -= 1
            self.timer_label.setText(f"Time Left: {self.time_left}s")
        else:
            self.timer.stop()
            if not self.user_moved:
                QMessageBox.information(self, "Time's Up", "You took too long! It's now the computer's turn.")
                self.status_label.setText("Computer's Turn!")
                self.computer_turn()
    
    def reset_timer(self):
        self.time_left = 20
        self.timer_label.setText(f"Time Left: {self.time_left}s")
        self.timer.start(1000)
        self.user_moved = False
    
    def user_turn(self, x, y):
        if (x, y) in self.user_shots:
            return
        
        self.user_shots.add((x, y))
        self.user_moved = True
        self.status_label.setText("Computer's Turn!")
        
        if (x, y) in self.computer_ships:
            self.computer_buttons[x][y].setText("X")
            self.computer_buttons[x][y].setStyleSheet("background-color: red; color: white; font-weight: bold;")
            self.computer_ships.remove((x, y))
        else:
            self.computer_buttons[x][y].setText("O")
            self.computer_buttons[x][y].setStyleSheet("background-color: gray; color: black;")
        
        if not self.computer_ships:
            self.timer.stop()
            self.game_over_popup("🎉 You Win!")
        else:
            QTimer.singleShot(1000, self.computer_turn)
    
    def computer_turn(self):
        while True:
            x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
            if (x, y) not in self.computer_shots:
                self.computer_shots.add((x, y))
                break

        if (x, y) in self.user_ships and self.user_buttons[x][y].text() == "":
            self.user_buttons[x][y].setText("X")
            self.user_buttons[x][y].setStyleSheet("background-color: red; color: white; font-weight: bold;")
        elif self.user_buttons[x][y].text() == "":
            self.user_buttons[x][y].setText("O")
            self.user_buttons[x][y].setStyleSheet("background-color: gray; color: black;")
        
        if self.computer_shots.issuperset(self.user_ships):
            self.timer.stop()
            self.game_over_popup("💻 Computer Wins!")
        else:
            self.status_label.setText("Your Turn!")
            self.reset_timer()
    
    def game_over_popup(self, message):
        dialog = QDialog(self)
        dialog.setWindowTitle("Game Over!")
        dialog.setFixedSize(300, 150)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        label = QLabel(message)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        layout.addWidget(label)

        button_layout = QHBoxLayout()

        play_again_button = QPushButton("Play Again")
        play_again_button.setFixedSize(100, 35)
        play_again_button.clicked.connect(lambda: (dialog.accept(), self.reset_game()))

        exit_button = QPushButton("Exit")
        exit_button.setFixedSize(100, 35)
        exit_button.clicked.connect(lambda: (dialog.accept(), self.close()))

        button_layout.addWidget(play_again_button)
        button_layout.addWidget(exit_button)
        layout.addLayout(button_layout)

        dialog.setLayout(layout)
        dialog.exec()

    def reset_game(self):
        self.user_ships.clear()
        self.computer_ships.clear()
        self.user_shots.clear()
        self.computer_shots.clear()
        self.status_label.setText("Place Your Ships")
        self.timer_label.setText("Time Left: 20s")
        self.timer.stop()
        self.user_moved = False
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                self.user_buttons[i][j].setText("")
                self.user_buttons[i][j].setStyleSheet("")
                self.user_buttons[i][j].setEnabled(True)
                self.computer_buttons[i][j].setText("")
                self.computer_buttons[i][j].setStyleSheet("")
                self.computer_buttons[i][j].setEnabled(False)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    game = BattleshipGame()
    game.show()
    sys.exit(app.exec())
