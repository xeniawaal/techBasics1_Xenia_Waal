import os
import sys
import pygame

pygame.init()

WIDTH = 1200
HEIGHT = 800
FPS = 60
GAME_TIME_SECONDS = 180
MAX_INVENTORY_SIZE = 3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.join(BASE_DIR, "assets")

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Escape the Burning House")
clock = pygame.time.Clock()

FONT = pygame.font.SysFont("arial", 22)
SMALL_FONT = pygame.font.SysFont("arial", 17)
BIG_FONT = pygame.font.SysFont("arial", 54, bold=True)
TITLE_FONT = pygame.font.SysFont("arial", 64, bold=True)

WHITE = (255, 255, 255)
BLACK = (25, 20, 18)
CREAM = (255, 244, 220)
BROWN = (92, 55, 34)
LIGHT_BROWN = (166, 112, 72)
RED = (190, 55, 45)
GREEN = (45, 145, 75)
BLUE = (55, 110, 175)
GRAY = (90, 90, 90)


def load_image(filename, size=None):
    path = os.path.join(ASSET_DIR, filename)
    image = pygame.image.load(path).convert_alpha()
    if size is not None:
        image = pygame.transform.smoothscale(image, size)
    return image


def draw_text(text, font, color, x, y, center=False):
    image = font.render(text, True, color)
    rect = image.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    screen.blit(image, rect)
    return rect


def wrap_text(text, font, max_width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = word if current == "" else current + " " + word
        if font.size(test)[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


class Button:
    def __init__(self, rect, text, color=LIGHT_BROWN):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.color = color

    def draw(self):
        mouse = pygame.mouse.get_pos()
        color = tuple(min(255, value + 25) for value in self.color) if self.rect.collidepoint(mouse) else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, CREAM, self.rect, 2, border_radius=10)
        draw_text(self.text, FONT, WHITE, self.rect.centerx, self.rect.centery, center=True)

    def clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)


class Item:
    def __init__(self, name, rect, description, display_name=None):
        self.name = name
        self.display_name = display_name if display_name is not None else name
        self.rect = pygame.Rect(rect)
        self.description = description
        self.collected = False

    def draw_hotspot(self, is_hovered):
        # is_hovered is decided centrally by Game.get_hovered_item(), so that
        # only ONE box is ever highlighted even if several hitboxes overlap.
        if self.collected or not is_hovered:
            return
        overlay = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        overlay.fill((255, 230, 120, 85))
        screen.blit(overlay, self.rect.topleft)
        pygame.draw.rect(screen, (255, 230, 120), self.rect, 3, border_radius=6)
        label_rect = pygame.Rect(self.rect.x, max(0, self.rect.y - 28), max(110, self.rect.width), 26)
        pygame.draw.rect(screen, BLACK, label_rect, border_radius=6)
        draw_text(self.display_name.title(), SMALL_FONT, WHITE, label_rect.x + 8, label_rect.y + 4)


class Game:
    def __init__(self):
        self.background = load_image("living_room.png", (WIDTH, HEIGHT))
        self.fire_frames = [
            load_image("fire_1.png", (145, 105)),
            load_image("fire_2.png", (155, 115)),
            load_image("fire_3.png", (165, 120)),
            load_image("fire_4.png", (175, 125)),
        ]

        # Coordinates re-measured directly from the actual living_room.png background
        # (1200 x 800 canvas) so hitboxes now line up with the artwork and no longer
        # overlap each other more than necessary.
        self.items = [
            Item("gasoline", (20, 250, 120, 100), "A can of gasoline. Using it in a fire is extremely dangerous."),
            Item("water", (30, 365, 115, 90), "Two bottles of water. Water can be combined with the towel."),
            Item("candle", (30, 465, 105, 95), "Candles are dangerous in a burning room."),
            Item("towel", (20, 575, 130, 120), "A dry towel. Combine it with water to protect yourself from smoke."),
            Item("book", (300, 635, 130, 55), "A book. It is not useful for escaping."),
            Item("coffee", (455, 600, 80, 80), "A cup of coffee. It does not help in this emergency."),
            Item("plant", (10, 40, 140, 200), "A houseplant. Nice, but not useful for escaping."),
            Item("curtain", (170, 40, 445, 550), "A long curtain. It could possibly be turned into a rope."),
            Item("picture frame", (700, 205, 205, 180), "A picture frame. It is a memory, but it does not help you escape."),
            Item("umbrella", (735, 410, 85, 195), "A sturdy umbrella. It might help you reach or break the window."),
            Item("wrong key", (795, 415, 25, 45), "A small metal key. You do not know whether it fits the door.", "key"),
            Item("key", (823, 415, 28, 45), "A small metal key. You do not know whether it fits the door.", "key"),
        ]

        self.start_button = Button((WIDTH // 2 - 110, HEIGHT // 2 + 55, 220, 60), "START", GREEN)
        self.pick_button = Button((865, 690, 135, 48), "PICK UP", BLUE)
        self.use_button = Button((1015, 690, 135, 48), "USE", GREEN)
        self.drop_button = Button((865, 748, 135, 42), "LET GO", GRAY)
        self.combine_button = Button((1015, 748, 135, 42), "COMBINE", LIGHT_BROWN)
        self.retry_button = Button((WIDTH // 2 - 185, HEIGHT // 2 + 95, 370, 65), "TRY AGAIN", BLUE)

        self.highscore = None
        self.reset()

    def reset(self):
        for item in self.items:
            item.collected = False

        self.state = "start"
        self.inventory = []
        self.selected_room_item = None
        self.selected_inventory = []
        self.message = "Click an object to inspect it."
        self.start_ticks = 0
        self.finish_time = None
        self.fire_frame_index = 0
        self.last_fire_change = 0
        self.wet_towel_created = False
        self.rope_created = False

    def start_game(self):
        self.state = "playing"
        self.start_ticks = pygame.time.get_ticks()
        self.message = "Find a safe route out of the burning house."

    def remaining_seconds(self):
        if self.state != "playing":
            return GAME_TIME_SECONDS
        elapsed = (pygame.time.get_ticks() - self.start_ticks) // 1000
        return max(0, GAME_TIME_SECONDS - elapsed)

    def elapsed_seconds(self):
        return (pygame.time.get_ticks() - self.start_ticks) // 1000

    def format_time(self, seconds):
        return f"{seconds // 60:02d}:{seconds % 60:02d}"

    def item_by_name(self, name):
        for item in self.items:
            if item.name == name:
                return item
        return None

    def display_name_for(self, name):
        if name in ("key", "wrong key"):
            return "key"
        return name

    def has_item(self, name):
        return name in self.inventory

    def add_item(self, name):
        if len(self.inventory) >= MAX_INVENTORY_SIZE:
            self.message = "Your inventory is full. Let go of an item first."
            return

        item = self.item_by_name(name)
        if item is not None and not item.collected:
            item.collected = True
            self.inventory.append(name)
            self.message = f"You picked up the {self.display_name_for(name)}."
            self.selected_room_item = None

    def drop_item(self):
        if len(self.selected_inventory) != 1:
            self.message = "Select exactly one inventory item to let go."
            return

        name = self.selected_inventory[0]
        if name in ("wet towel", "rope"):
            self.inventory.remove(name)
            self.message = f"You let go of the {self.display_name_for(name)}. It cannot be picked up again."
        else:
            self.inventory.remove(name)
            item = self.item_by_name(name)
            if item is not None:
                item.collected = False
            self.message = f"You let go of the {self.display_name_for(name)}."

        self.selected_inventory = []

    def combine_items(self):
        if len(self.selected_inventory) != 2:
            self.message = "Select exactly two inventory items to combine."
            return

        pair = set(self.selected_inventory)

        if pair == {"water", "towel"}:
            self.inventory.remove("water")
            self.inventory.remove("towel")
            self.inventory.append("wet towel")
            self.wet_towel_created = True
            self.message = "You soaked the towel with water. You can now breathe through the smoke."

        elif pair == {"umbrella", "curtain"}:
            self.inventory.remove("umbrella")
            self.inventory.remove("curtain")
            self.inventory.append("rope")
            self.rope_created = True
            self.message = "You tied the curtain to the umbrella and made an improvised escape rope."

        elif pair == {"gasoline", "candle"}:
            self.game_over("The gasoline ignites. The flames spread instantly.")

        elif pair == {"book", "candle"}:
            self.game_over("The book catches fire and the room fills with smoke.")

        elif pair == {"water", "plant"}:
            self.message = "You watered the plant. It looks better, but it does not help you escape."

        elif pair == {"coffee", "book"}:
            self.message = "You spilled coffee on the book. Nothing useful happens."

        else:
            self.message = "These items cannot be combined in a useful way."

        self.selected_inventory = []

    def use_item(self):
        if len(self.selected_inventory) != 1:
            self.message = "Select exactly one inventory item to use."
            return

        name = self.selected_inventory[0]

        if name == "gasoline":
            self.game_over("You pour gasoline near the fire. The whole room bursts into flames.")

        elif name == "candle":
            if self.has_item("curtain"):
                self.game_over("The candle touches the curtain. It catches fire immediately.")
            else:
                self.message = "Lighting a candle in a burning house is a terrible idea."

        elif name == "wrong key":
            self.message = "Sorry, that was the wrong key. Look for another escape route before the fire gets worse."

        elif name == "key":
            if self.has_item("wet towel"):
                self.win("You protect yourself from the smoke, unlock the door and escape safely!")
            else:
                self.message = "The key fits, but the smoke at the door is too thick. You need protection."

        elif name == "wet towel":
            if self.has_item("key"):
                self.win("With the wet towel over your mouth, you unlock the door and escape!")
            else:
                self.message = "The wet towel protects you from smoke, but the door is still locked."

        elif name == "umbrella":
            self.win("You use the umbrella to break the window and climb outside!")

        elif name == "rope":
            self.win("You attach the improvised rope to the window and climb to safety!")

        elif name == "water":
            self.message = "The water weakens a small flame, but it is not enough to clear an escape route."

        elif name == "towel":
            self.message = "The dry towel does not protect you. Combine it with water."

        elif name == "curtain":
            self.message = "The curtain is too long to carry safely. Combine it with the umbrella."

        elif name == "picture frame":
            self.message = "You save the picture frame, but it does not help you escape."

        elif name == "coffee":
            self.message = "You drink the coffee. You feel awake, but the house is still burning."

        elif name == "book":
            self.message = "You open the book. This is not the time to read."

        elif name == "plant":
            self.message = "The plant cannot help you escape."

        self.selected_inventory = []

    def win(self, message):
        self.finish_time = self.elapsed_seconds()
        self.state = "won"
        self.message = message
        if self.highscore is None or self.finish_time < self.highscore:
            self.highscore = self.finish_time

    def game_over(self, message):
        self.state = "lost"
        self.message = message

    def get_hovered_item(self):
        """Return the single item that should count as 'hovered' right now.

        Several hitboxes can overlap (e.g. curtain is a large background area).
        Instead of letting every overlapping item react at once, only the
        smallest (= most specific) one under the mouse wins. Used for both
        the hover highlight and click handling, so what you see highlighted
        is always exactly what a click would select.
        """
        mouse = pygame.mouse.get_pos()
        candidates = [item for item in self.items if not item.collected and item.rect.collidepoint(mouse)]
        if not candidates:
            return None
        return min(candidates, key=lambda item: item.rect.width * item.rect.height)

    def handle_room_click(self, pos):
        hovered = self.get_hovered_item()
        if hovered is None:
            return
        self.selected_room_item = hovered.name
        self.selected_inventory = []
        self.message = hovered.description

    def handle_inventory_click(self, pos):
        start_x = 26
        slot_width = 250
        y = 690

        for index, name in enumerate(self.inventory):
            rect = pygame.Rect(start_x + index * slot_width, y, 225, 82)
            if rect.collidepoint(pos):
                if name in self.selected_inventory:
                    self.selected_inventory.remove(name)
                else:
                    if len(self.selected_inventory) < 2:
                        self.selected_inventory.append(name)
                    else:
                        self.message = "You can select a maximum of two items."
                self.selected_room_item = None
                return

    def update(self):
        if self.state == "playing":
            if self.remaining_seconds() <= 0:
                self.game_over("Time is up. The fire became too strong before you escaped.")

            now = pygame.time.get_ticks()
            if now - self.last_fire_change > 140:
                self.fire_frame_index = (self.fire_frame_index + 1) % len(self.fire_frames)
                self.last_fire_change = now

    def draw_background_and_fire(self):
        screen.blit(self.background, (0, 0))

        frame = self.fire_frames[self.fire_frame_index]

        # Several animated fires in different sizes make the room look more realistic.
        screen.blit(frame, (180, 500))
        screen.blit(pygame.transform.smoothscale(frame, (125, 95)), (540, 430))
        screen.blit(pygame.transform.smoothscale(frame, (150, 110)), (925, 520))
        screen.blit(pygame.transform.smoothscale(frame, (95, 75)), (350, 525))
        screen.blit(pygame.transform.smoothscale(frame, (110, 85)), (690, 475))
        screen.blit(pygame.transform.smoothscale(frame, (85, 68)), (1020, 390))
        screen.blit(pygame.transform.smoothscale(frame, (100, 78)), (80, 500))
        screen.blit(pygame.transform.smoothscale(frame, (90, 72)), (790, 560))

    def draw_timer(self):
        rect = pygame.Rect(1015, 20, 160, 58)
        pygame.draw.rect(screen, BLACK, rect, border_radius=12)
        pygame.draw.rect(screen, CREAM, rect, 2, border_radius=12)
        draw_text(self.format_time(self.remaining_seconds()), BIG_FONT, WHITE, rect.centerx, rect.centery, center=True)

    def draw_message_box(self):
        # Sits at the top of the screen (instead of y=600) so it never covers
        # towel / book / coffee in the lower part of the room.
        rect = pygame.Rect(20, 20, 820, 72)
        surface = pygame.Surface(rect.size, pygame.SRCALPHA)
        surface.fill((20, 15, 12, 220))
        screen.blit(surface, rect.topleft)
        pygame.draw.rect(screen, CREAM, rect, 2, border_radius=10)

        lines = wrap_text(self.message, SMALL_FONT, rect.width - 24)
        for i, line in enumerate(lines[:3]):
            draw_text(line, SMALL_FONT, WHITE, rect.x + 12, rect.y + 10 + i * 20)

    def draw_inventory(self):
        panel = pygame.Rect(0, 680, 850, 120)
        pygame.draw.rect(screen, (35, 25, 20), panel)
        draw_text("INVENTORY — maximum 3 items", SMALL_FONT, CREAM, 25, 682)

        start_x = 26
        slot_width = 250
        y = 710

        for index in range(MAX_INVENTORY_SIZE):
            rect = pygame.Rect(start_x + index * slot_width, y, 225, 68)
            selected = index < len(self.inventory) and self.inventory[index] in self.selected_inventory
            color = (105, 82, 50) if not selected else (155, 110, 45)
            pygame.draw.rect(screen, color, rect, border_radius=10)
            pygame.draw.rect(screen, CREAM, rect, 2, border_radius=10)

            if index < len(self.inventory):
                draw_text(self.display_name_for(self.inventory[index]).title(), FONT, WHITE, rect.centerx, rect.centery, center=True)
            else:
                draw_text("Empty", SMALL_FONT, (185, 175, 160), rect.centerx, rect.centery, center=True)

    def draw_item_panel(self):
        panel = pygame.Rect(850, 600, 350, 200)
        pygame.draw.rect(screen, (30, 22, 18), panel)
        pygame.draw.line(screen, CREAM, (850, 600), (850, 800), 2)

        if self.selected_room_item:
            draw_text(self.display_name_for(self.selected_room_item).title(), FONT, CREAM, 875, 620)
            self.pick_button.draw()
        elif self.selected_inventory:
            names = " + ".join(self.display_name_for(name).title() for name in self.selected_inventory)
            lines = wrap_text(names, SMALL_FONT, 300)
            for i, line in enumerate(lines[:2]):
                draw_text(line, SMALL_FONT, CREAM, 875, 615 + i * 20)
            self.use_button.draw()
            self.drop_button.draw()
            self.combine_button.draw()
        else:
            draw_text("Select an object or inventory item.", SMALL_FONT, CREAM, 875, 625)

    def draw_start_screen(self):
        self.draw_background_and_fire()
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((15, 10, 8, 135))
        screen.blit(overlay, (0, 0))

        box = pygame.Rect(WIDTH // 2 - 360, HEIGHT // 2 - 150, 720, 310)
        pygame.draw.rect(screen, (38, 25, 20), box, border_radius=18)
        pygame.draw.rect(screen, CREAM, box, 3, border_radius=18)
        draw_text("ESCAPE THE", TITLE_FONT, WHITE, WIDTH // 2, HEIGHT // 2 - 85, center=True)
        draw_text("BURNING HOUSE", TITLE_FONT, (255, 155, 70), WIDTH // 2, HEIGHT // 2 - 20, center=True)
        draw_text("You have 3 minutes. Choose carefully.", FONT, CREAM, WIDTH // 2, HEIGHT // 2 + 35, center=True)
        self.start_button.draw()

    def draw_playing(self):
        self.draw_background_and_fire()

        hovered = self.get_hovered_item()
        for item in self.items:
            item.draw_hotspot(item is hovered)

        self.draw_timer()
        self.draw_message_box()
        self.draw_inventory()
        self.draw_item_panel()

    def draw_end_screen(self):
        self.draw_background_and_fire()
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((15, 10, 8, 190))
        screen.blit(overlay, (0, 0))

        box = pygame.Rect(WIDTH // 2 - 390, HEIGHT // 2 - 190, 780, 390)
        pygame.draw.rect(screen, (35, 24, 20), box, border_radius=18)
        pygame.draw.rect(screen, CREAM, box, 3, border_radius=18)

        if self.state == "won":
            draw_text("CONGRATULATIONS!", BIG_FONT, GREEN, WIDTH // 2, HEIGHT // 2 - 115, center=True)
            draw_text(f"You escaped in {self.format_time(self.finish_time)}.", FONT, WHITE, WIDTH // 2, HEIGHT // 2 - 50, center=True)

            if self.highscore is not None:
                draw_text(f"Highscore: {self.format_time(self.highscore)}", FONT, CREAM, WIDTH // 2, HEIGHT // 2 - 10, center=True)

            self.retry_button.text = "TRY TO BEAT YOUR HIGHSCORE"
        else:
            draw_text("GAME OVER", BIG_FONT, RED, WIDTH // 2, HEIGHT // 2 - 115, center=True)
            self.retry_button.text = "TRY AGAIN"

        lines = wrap_text(self.message, FONT, 650)
        for i, line in enumerate(lines[:3]):
            draw_text(line, FONT, WHITE, WIDTH // 2, HEIGHT // 2 + 35 + i * 28, center=True)

        self.retry_button.draw()

    def draw(self):
        if self.state == "start":
            self.draw_start_screen()
        elif self.state == "playing":
            self.draw_playing()
        else:
            self.draw_end_screen()

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if self.state == "start":
            if self.start_button.clicked(event):
                self.start_game()
            return

        if self.state in ("won", "lost"):
            if self.retry_button.clicked(event):
                old_highscore = self.highscore
                self.reset()
                self.highscore = old_highscore
                self.start_game()
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.handle_inventory_click(event.pos)
            self.handle_room_click(event.pos)

        if self.pick_button.clicked(event) and self.selected_room_item:
            self.add_item(self.selected_room_item)

        if self.use_button.clicked(event):
            self.use_item()

        if self.drop_button.clicked(event):
            self.drop_item()

        if self.combine_button.clicked(event):
            self.combine_items()


def main():
    game = Game()
    running = True

    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            game.handle_event(event)

        game.update()
        game.draw()
        pygame.display.flip()


if __name__ == "__main__":
    main()
