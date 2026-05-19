inventory = []

items_in_room = [
    {"name": "towel", "type": "protection", "description": "A wet towel helps you to breathe through smoke."},
    {"name": "key", "type": "tool", "description": "A small key for the front door."},
    {"name": "flashlight", "type": "tool", "description": "A flashlight to see through the smoke."},
    {"name": "water", "type": "tool", "description": "A bottle of water. Maybe it can weaken small flames."},
    {"name": "phone", "type": "tool", "description": "A phone to call for help."},
    {"name": "photo", "type": "memory", "description": "A family photo.. That is not useful, but it is hard to leave behind."}
]

MAX_INVENTORY_SIZE = 5

door_locked = True
fire_blocking_exit = True
called_help = False
protected_from_smoke = False


# --- Functions ---

def show_inventory():
    if len(inventory) == 0:
        print("Your inventory is empty.")
    else:
        print("You carry:")
        for item in inventory:
            print("-", item["name"])


def show_room_items():
    if len(items_in_room) == 0:
        print("There are no items left in the room.")
    else:
        print("You can see:")
        for item in items_in_room:
            print("-", item["name"])


def find_item(item_name, item_list):
    for item in item_list:
        if item["name"].lower() == item_name.lower():
            return item
    return None


def pick_up(item_name):
    item = find_item(item_name, items_in_room)

    if item is None:
        print("This item is not in the room.")
    elif len(inventory) >= MAX_INVENTORY_SIZE:
        print("Your inventory is full. You need to drop something first.")
    else:
        inventory.append(item)
        items_in_room.remove(item)
        print("You picked up the", item["name"] + ".")


def drop(item_name):
    item = find_item(item_name, inventory)

    if item is None:
        print("You do not have this item.")
    else:
        inventory.remove(item)
        items_in_room.append(item)
        print("You dropped the", item["name"] + ".")


def use(item_name):
    global door_locked
    global fire_blocking_exit
    global called_help
    global protected_from_smoke

    item = find_item(item_name, inventory)

    if item is None:
        print("You do not have this item.")
        return

    if item["name"] == "towel":
        protected_from_smoke = True
        print("You hold the wet towel over your mouth. The smoke feels less dangerous.")

    elif item["name"] == "key":
        door_locked = False
        print("You unlock the front door.")

    elif item["name"] == "water":
        fire_blocking_exit = False
        print("You pour water onto the small flames near the exit.")

    elif item["name"] == "phone":
        called_help = True
        print("You call the fire department. Help is on the way!")

    elif item["name"] == "flashlight":
        print("You turn on the flashlight. You can see the exit sign through the smoke.")

    else:
        print("You cannot really use this item right now.")


def examine(item_name):
    item = find_item(item_name, inventory)

    if item is None:
        item = find_item(item_name, items_in_room)

    if item is None:
        print("You cannot find this item.")
    else:
        print(item["description"])


def try_escape():
    if door_locked:
        print("The front door is locked. You need a key.")
    elif fire_blocking_exit:
        print("Fire blocks the exit. Maybe water could help.")
    elif not protected_from_smoke:
        print("The smoke is too thick. You should protect yourself first.")
    else:
        print("\nYou open the door and escape from the burning house!")
        if called_help:
            print("Because you called for help, the fire department arrives quickly.")
        print("You survived. Game over!")
        return True

    return False


# --- Game Loop ---

def game_loop():
    print("Welcome to Burning House Escape!")
    print("You wake up in a smoky room. Your goal is to escape the burning house.")
    print("Type 'help' for a list of commands.")

    while True:
        command = input("\n> ").strip().lower()

        match command.split():
            case ["help"]:
                print("Commands: inventory, look, pickup [item], drop [item], use [item], examine [item], escape, quit")

            case ["inventory"]:
                show_inventory()

            case ["look"]:
                show_room_items()

            case ["pickup", item_name]:
                pick_up(item_name)

            case ["drop", item_name]:
                drop(item_name)

            case ["use", item_name]:
                use(item_name)

            case ["examine", item_name]:
                examine(item_name)

            case ["escape"]:
                escaped = try_escape()
                if escaped:
                    break

            case ["quit"]:
                print("Thanks for playing!")
                break

            case _:
                print("Unknown command. Type 'help' to see available commands.")


if __name__ == "__main__":
    game_loop()
