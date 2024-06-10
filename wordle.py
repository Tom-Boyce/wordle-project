from random import randint
import time
import threading


#calls list functions
def word_list_maker():
    valid_solutions = list_from_txt("wordle-answers-alphabetical.txt")
    valid_words = list_from_txt("wordle-allowed-guesses.txt")
    valid_inputs = valid_solutions + valid_words

    return valid_solutions, valid_inputs
    

#gets data for word sets to be used in wordle games
def list_from_txt(file_path):
    valid_words = []
    with open(file_path, "r") as get_words:
        lines = get_words.readlines()
        for line in lines:
            valid_words.append((line.replace("\n", "")))

    return valid_words


#chooses what the secret word is
def goal_word_selector():
    #counter to prevent while loop running for too long
    counter = 0
    while True and counter < 1000:
        index = randint(0, len(valid_solutions))
        if index not in words_played:
            return valid_solutions[index]

    #if we are somehow unlucky enough to reach this point, the player deserves to play against a word they have already seen    
    return valid_solutions[0]


def evaluate_guess(secret, guess):
    evals = ["b"] * len(guess)
    secret_letter_counts = {}

    #greens
    for i in range(len(guess)):
        if guess[i] == secret[i]:
            evals[i] = "g"

        else:
            if secret[i] not in secret_letter_counts:
                secret_letter_counts[secret[i]] = 0
            secret_letter_counts[secret[i]] += 1


    #yellows
    for i in range(len(guess)):
        if evals[i] == "g":
            continue

        if guess[i] in secret_letter_counts and secret_letter_counts[guess[i]] > 0:
            evals[i] = "y"
            secret_letter_counts[guess[i]] -= 1


    return list(zip(guess, evals))


#lets a person play wordle
def human_play(save=False, game_type="normal"):
    global time_up
    time_up = False
    secret_word = goal_word_selector()
    guesses = 0
    sleep_time = 5

    #set upper time limit to have unlimited guesses for time attack, remove wait time between words
    upper_guess_limit = 6
    if game_type == "timed":
        upper_guess_limit = float('inf')
        sleep_time = 0

    while guesses < upper_guess_limit and not time_up:
        valid_guess = False
        while not valid_guess and not time_up:
            user_guess = input("Enter word (5 letters long): ")

            #check if time is up after user input
            if time_up:
                return 0

            if len(user_guess) != 5:
                print("\nERROR, word must be 5 letters long\n")

            elif not user_guess.isalpha():
                print("\nERROR, inputs must be letters\n")

            elif not user_guess.lower() in valid_inputs:
                print("\nERROR, input not a valid word\n")

            elif user_guess.lower() == secret_word:
                print(f"\nCongratulations! {secret_word} was the word!\nYou got it in {guesses + 1} guesses!\n")

                if save:
                    with open("tbwordlesave.txt", "a") as save_file:
                        scored_word = f"{secret_word}, {guesses + 1}\n"
                        save_file.write(scored_word)
                time.sleep(sleep_time)
                return 1
            
            else:
                valid_guess = True

        evaluation = evaluate_guess(secret_word, user_guess)
        print(evaluation)
        guesses += 1

    print(f"\nUnlucky! The correct word was {secret_word}. Better luck next time!\n")

    if save:
        with open("tbwordlesave.txt", "w") as save_file:
            save_file.write(f"{secret_word}, {guesses}\n")

    time.sleep(sleep_time)
    return 0


def machine_play():
    ...


#this code consists of some descent into madness. 2d array was definitely necessary, definitely couldnt have just used maths
def scoreboard():
    def scoreboard_print(scoreboard):
        name_max = max(len(name) for name, _ in scoreboard)
        score_max = max(len(str(score)) for _, score in scoreboard)
        title = "H I G H   S C O R E S"
        num_entries = len(scoreboard)
        combi = max(len(title) + 2, name_max + score_max + 6)

        table = [[' ' for _ in range(combi)] for _ in range(4 + num_entries)]

        for i in range(4 + num_entries):
            table[i][0] = '|'
            table[i][-1] = '|'
            table[i][combi - (score_max + 4)] = '|'

        for i in range(combi):
            table[0][i] = '='
            table[2][i] = '='
            table[-1][i] = '='

        start_title = (combi - len(title)) // 2
        for i, char in enumerate(title):
            table[1][start_title + i] = char

        for i, (name, score) in enumerate(scoreboard):
            start_name = 2
            for j, char in enumerate(name):
                table[3 + i][start_name + j] = char
            start_score = combi - score_max - 2
            for j, char in enumerate(str(score)):
                table[3 + i][start_score + j] = char

        for row in table:
            print(''.join(row))

    
    user_name = input("\nEnter your name: ")
    file_path = "wordlescoreboard.txt"

    scoreboard = []
    with open(file_path, "r") as board_file:
        for line in board_file:
            name, score = line.strip().split(", ")
            scoreboard.append((name, int(score)))

    scoreboard.append((user_name, counter))

    scoreboard.sort(reverse=True, key=lambda x: x[1])

    scoreboard_print(scoreboard)
                
    # Writing scoreboard back to file
    with open(file_path, "w") as board_file:
        for name, score in scoreboard:
            board_file.write(f"{name}, {score}\n")
            
    return
    

#clear most wordles in 3 minutes - no fails, unlimited words!
def time_play():
    global time_up
    global counter
    time_up = False
    start_time = time.time()
    time_limit = 3 * 60
    counter = 0

    def timeout():
        global time_up
        while True:
            elapsed_time = time.time() - start_time
            if elapsed_time > time_limit:
                time_up = True
                return

    timer_thread = threading.Thread(target=timeout)
    timer_thread.start()

    try:
        while not time_up:
            if not time_up:
                counter += human_play(game_type="timed")

            if time_up:
                scoreboard()
                break
            
    except KeyboardInterrupt:
        print("Interrupted by user")

    timer_thread.join()


#where stuff happens
def main():
    
    #initialising lists used throughout
    global valid_solutions, valid_inputs, words_played
    valid_solutions, valid_inputs = word_list_maker()
    words_played = []

    #lets user choose what they wish to do
    finished = False
    while finished == False:
        mode_choice = input("What would you like to do? \n    1: Play a random word \n    2: Let a computer play \n    3:Time attack \n    4:end game \nEnter Your Choice: ")

        match mode_choice:
            case "1":
                human_play()
            case "2":
                machine_play()
            case "3":
                time_play()
            case "4":
                finished = True
            case "tb":
                human_play(save = True)
            case _:
                print("\nERROR, invalid choice. Try again\n")


#calls main
if __name__ == "__main__":
    main()


'''
TO ADD:
1)GUI
2) ability to view player record
3)AI functionality
'''