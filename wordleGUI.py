import tkinter as tk
import string
from random import randint
import time
import tkinter.simpledialog as simpledialog

def word_list_maker():
    valid_solutions = list_from_txt("wordle-answers-alphabetical.txt")
    valid_words = list_from_txt("wordle-allowed-guesses.txt")
    valid_inputs = valid_solutions + valid_words
    return valid_solutions, valid_inputs

def list_from_txt(file_path):
    with open(file_path, "r") as get_words:
        return [line.strip() for line in get_words]

def goal_word_selector():
    while True:
        index = randint(0, len(valid_solutions) - 1)
        if index not in words_played:
            words_played.append(index)
            return valid_solutions[index]

def evaluate_guess(secret, guess):
    evals = ["b"] * len(guess)
    secret_letter_counts = {}

    for i in range(len(guess)):
        if guess[i] == secret[i]:
            evals[i] = "g"
        else:
            if secret[i] not in secret_letter_counts:
                secret_letter_counts[secret[i]] = 0
            secret_letter_counts[secret[i]] += 1

    for i in range(len(guess)):
        if evals[i] == "g":
            continue
        if guess[i] in secret_letter_counts and secret_letter_counts[guess[i]] > 0:
            evals[i] = "y"
            secret_letter_counts[guess[i]] -= 1

    return list(zip(guess, evals))

def human_play_tk():
    global secret_word, guesses, current_input, start_time
    secret_word = goal_word_selector()
    guesses = 0
    current_input = ""
    start_time = time.time()
    update_labels()
    reset_guess_labels()
    reset_button_colors()
    result_label.config(text="")

def check_word_tk():
    global current_input, guesses, secret_word, score
    if len(current_input) != 5:
        return

    if current_input.lower() == secret_word:
        score += 1
        result_label.config(text=f"Congratulations! {secret_word.upper()} was the word!\nYou got it in {guesses + 1} guesses!")
        window.update_idletasks()
        time.sleep(2)
        human_play_tk()
        return

    if current_input.lower() not in valid_inputs:
        result_label.config(text="Invalid word!")
        return

    evaluation = evaluate_guess(secret_word, current_input.lower())
    update_guess_labels(evaluation)
    guesses += 1
    current_input = ""
    update_labels()

    if guesses >= 6:
        result_label.config(text=f"Unlucky! The correct word was {secret_word.upper()}. Moving on to the next word.")
        window.update_idletasks()
        time.sleep(2)
        human_play_tk()
        return


def letter_click(letter):
    global current_input
    if len(current_input) < 5:
        current_input += letter
        update_labels()

def delete_letter():
    global current_input
    if current_input:
        current_input = current_input[:-1]
        update_labels()

def update_labels():
    for i in range(5):
        if i < len(current_input):
            letter_labels[i].config(text=current_input[i])
        else:
            letter_labels[i].config(text="")

def update_guess_labels(evaluation):
    button_colors = {letter: None for letter in string.ascii_uppercase}
    for letter, eval in evaluation:
        if eval == "g":
            button_colors[letter.upper()] = "green"
        elif eval == "y" and button_colors[letter.upper()] != "green":
            button_colors[letter.upper()] = "yellow"
    
    for letter, color in button_colors.items():
        if color:
            letter_buttons[letter].config(bg=color)
    
    for i, (letter, eval) in enumerate(evaluation):
        guess_labels[guesses][i].config(text=letter.upper(), bg=color_map[eval])


def reset_guess_labels():
    for row in guess_labels:
        for label in row:
            label.config(text="", bg="white")

def reset_button_colors():
    for button in letter_buttons.values():
        button.config(bg="SystemButtonFace")  # Reset to default button color

def time_attack_mode():
    human_play_tk()
    window.after(180000, time_attack_end)  # 3 minutes (180,000 milliseconds)

def time_attack_end():
    window.withdraw()  # Hide the main window
    player_name = simpledialog.askstring("Time Attack Mode", "Time's up! Enter your name for the scoreboard:")
    if player_name:
        with open("wordlescoreboard.txt", "a") as scoreboard_file:
            scoreboard_file.write(f"{player_name}, {score}\n")
    window.destroy()

color_map = {
    "g": "green",
    "y": "yellow",
    "b": "gray"
}

valid_solutions, valid_inputs = word_list_maker()
words_played = []

window = tk.Tk()
window.title("Wordle")
window.geometry("720x1500")

current_input = ""
guesses = 0
global score
score = 0
secret_word = ""
start_time = 0

# Create labels for the letters
letter_labels = []
for i in range(5):
    lbl = tk.Label(window, text="", borderwidth=2, relief="solid", width=10, height=3)
    lbl.grid(row=0, column=i)
    letter_labels.append(lbl)

# Create labels for each guess (6 rows, 5 columns)
guess_labels = []
for row in range(6):
    guess_row = []
    for col in range(5):
        lbl = tk.Label(window, text="", borderwidth=2, relief="solid", width=10, height=3)
        lbl.grid(row=row + 1, column=col)
        guess_row.append(lbl)
    guess_labels.append(guess_row)

# Create buttons for each letter in the alphabet
letter_buttons = {}
lower = list(string.ascii_uppercase)
curr_row = 8
curr_col = 0
for letter in lower:
    choice = lambda x=letter: letter_click(x)
    btn = tk.Button(window, text=letter, command=choice, width=10, height=7)
    btn.grid(row=curr_row, column=curr_col)
    letter_buttons[letter] = btn
    curr_col += 1
    if curr_col == 9:
        curr_col = 0
        curr_row += 1

tk.Button(window, text="Delete", command=delete_letter, width=10, height=3).grid(row=curr_row, column=curr_col)
tk.Button(window, text="Submit", command=check_word_tk, width=10, height=3).grid(row=curr_row + 1, column=curr_col // 2)

result_label = tk.Label(window, text="", width=50, height=3)
result_label.grid(row=curr_row + 2, column=0, columnspan=9)

tk.Button(window, text="Start New Game", command=human_play_tk, width=50, height=3).grid(row=curr_row + 3, column=0, columnspan=9)
tk.Button(window, text="Start Timed Game", command=time_attack_mode, width=50, height=3).grid(row=curr_row + 4, column=0, columnspan=9)

human_play_tk()
window.mainloop()