import time


def slow_print(text):
    for char in text:
        print(char, end="", flush=True)
        time.sleep(0.03)
    print()


def get_number():
    while True:
        try:
            number = int(input("Choose your magic power (1-10): "))
            if 1 <= number <= 10:
                return number
            else:
                print("Please enter a number between 1 and 10.")
        except ValueError:
            print("That is not a valid number.")


slow_print("⚡ Welcome to Harry Potter and the Chamber of Secrets! ⚡")
time.sleep(1)
slow_print("You are in Hogwarts and must destroy the serpent in the Chamber of Secrets.")
time.sleep(1)

name = input("What is your name, wizard? ")
house = input("Choose your house (gryffindor / slytherin / ravenclaw / hufflepuff): ").lower()
power = get_number()

time.sleep(1)
slow_print("You walk down into the dark chamber...")
time.sleep(1)

weapon = input("Do you use the sword or a spell? ").lower()

if weapon == "sword":
    slow_print("You take the Sword of Gryffindor!")
    time.sleep(1)

    if power >= 6:
        slow_print("You are brave enough to attack the serpent.")
        time.sleep(1)

        if house == "gryffindor":
            slow_print("Because you are in Gryffindor, your courage is even stronger!")
            time.sleep(1)
            slow_print("You destroy the serpent and save Hogwarts! 🐍⚔️")
        else:
            slow_print("You hit the serpent with the sword and destroy it! 🐍⚔️")
    else:
        slow_print("You try to fight, but your magic power is too low.")
        time.sleep(1)
        slow_print("The serpent attacks you. Game over.")
        
elif weapon == "spell":
    slow_print("You raise your wand and prepare a spell!")
    time.sleep(1)

    spell = input("Choose a spell (expelliarmus / stupefy): ").lower()

    if spell == "stupefy":
        if power >= 8:
            slow_print("Your spell is strong enough!")
            time.sleep(1)
            slow_print("The serpent is defeated and Hogwarts is safe! ✨")
        else:
            slow_print("The spell is too weak.")
            time.sleep(1)
            slow_print("The serpent survives. Game over.")
    elif spell == "expelliarmus":
        slow_print("Expelliarmus does not work well against the serpent.")
        time.sleep(1)
        slow_print("The serpent attacks you. Game over.")
    else:
        slow_print("That spell is not known.")
        time.sleep(1)
        slow_print("You lose your chance. Game over.")

else:
    slow_print("You waited too long and did nothing.")
    time.sleep(1)
    slow_print("The serpent escapes. Game over.")

slow_print("Thanks for playing!")

