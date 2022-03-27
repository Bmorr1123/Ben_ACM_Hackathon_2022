import pygame
from pygame.display import get_window_size as size
import pygame_gui as gui
from abc import *
from connection import Connection
from snake import Snake
from server.server import ConnectionServer


WIDTH, HEIGHT = size()

GUISTATE_SWITCH = pygame.event.custom_type()


class GUIState(ABC):
    def __init__(self, theme_path="res/base_theme.json"):
        self.manager = gui.UIManager((WIDTH, HEIGHT), theme_path=theme_path, enable_live_theme_updates=True)
        self.time = 0

    def update(self, delta):
        self.time += delta
        self.manager.update(delta)
        self.tick(delta)

    def handle_events(self, events, mods):
        for event in events:
            self.manager.process_events(event)
            self.handle_event(event, mods)

    def draw_state(self, win):
        self.draw(win)
        self.manager.draw_ui(win)

    @abstractmethod
    def tick(self, delta):
        ...

    @abstractmethod
    def draw(self, win):
        ...

    @abstractmethod
    def handle_event(self, event, mods):
        ...

    @abstractmethod
    def on_quit(self):
        ...


class MenuState(GUIState):
    def __init__(self):
        super().__init__()

        self.title = gui.elements.UILabel(
            pygame.Rect(WIDTH * 0.1, HEIGHT * 0.1, WIDTH * 0.8, HEIGHT * 0.3),
            "SNEK", self.manager, object_id=gui.core.ObjectID("title", "none")
        )

        self.title.set_active_effect(gui.TEXT_EFFECT_TYPING_APPEAR, params={"time_per_letter": 1})

        self.host_button = gui.elements.UIButton(
            pygame.Rect(WIDTH * .25, HEIGHT * .4, WIDTH * .5, HEIGHT * .2),
            "Host", self.manager, object_id=gui.core.ObjectID("host", "#large_font_style")
        )

        self.join_button = gui.elements.UIButton(
            pygame.Rect(WIDTH * .25, HEIGHT * .65, WIDTH * .5, HEIGHT * .2),
            "Join", self.manager, object_id=gui.core.ObjectID("join", "#large_font_style")
        )

    def handle_event(self, event, mods):
        if event.type == gui.UI_BUTTON_PRESSED:
            button = event.ui_element
            if button == self.host_button:

                host = ConnectionServer()
                host.start()

                pygame.event.post(pygame.event.Event(
                    GUISTATE_SWITCH, state_type=GameState, ip="localhost", username="Host"
                ))
            elif button == self.join_button:
                pygame.event.post(pygame.event.Event(
                    GUISTATE_SWITCH, state_type=JoinState
                ))

    def tick(self, delta):
        ...

    def draw(self, win):
        ...

    def on_quit(self):
        ...


class GameState(GUIState):
    def __init__(self, ip, name):
        super().__init__()

        self.connection = Connection(ip, 3369, name)

        self.f3_text = gui.elements.UILabel(
            pygame.Rect(0, 0, -1, -1),
            "???", self.manager
        )
        self.ip_text = gui.elements.UILabel(
            pygame.Rect(0, HEIGHT - 20, -1, -1),
            ip, self.manager
        )

        self.my_snake = None
        self.snakes = []
        self.apples = []

    def handle_event(self, event, mods):

        if event.type == pygame.KEYDOWN:
            key = event.key
            if self.my_snake:
                direction = -1
                if key == pygame.K_UP or key == pygame.K_w:
                    direction = 2
                elif key == pygame.K_LEFT or key == pygame.K_a:
                    direction = 1
                elif key == pygame.K_DOWN or key == pygame.K_s:
                    direction = 3
                elif key == pygame.K_RIGHT or key == pygame.K_d:
                    direction = 0
                if direction != -1:
                    self.connection.send(f"#turn {direction}")

        if event.type == pygame.KEYUP:
            key = event.key
            if key == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(
                    GUISTATE_SWITCH, state_type=MenuState
                ))

            if key == pygame.K_SPACE:
                if not self.my_snake:
                    self.connection.send("join")

    def tick(self, delta):
        self.f3_text.set_text(f"fps: {1 / delta:.2f}")
        self.receive()

    def receive(self):
        info = self.connection.receive()
        if not info:
            return
        if info[0] == "#":
            args = info[1:].split(" ")
            if args[0] == "apple":
                uuid, pos = args[1], (int(args[2]), int(args[3]))
                if pos in self.apples:
                    self.apples.remove(pos)
                for snake in self.snakes:
                    if snake.uuid == uuid:
                        snake.length += 1

            elif args[0] == "new_apple":
                pos = (int(args[1]), int(args[2]))
                if pos not in self.apples:
                    self.apples.append(pos)

            elif args[0] == "death":
                uuid = args[1]
                snek = self.find_snake(uuid)
                if snek:
                    print("MURDERED SNAKE")
                    self.snakes.remove(snek)
                    if uuid == self.my_snake.uuid:
                        self.my_snake = None

            elif args[0] == "snake":
                uuid, name, direction, pos = args[1], args[2], int(args[3]), (int(args[4]), int(args[5]))
                snek = Snake(uuid, name, pos, direction)
                for i in range(6, len(args), 2):
                    snek.body.append((int(args[i]), int(args[i + 1])))
                self.snakes.append(snek)
                if uuid == self.connection.uuid:
                    self.my_snake = snek

            elif args[0] == "turn":
                uuid, direction = args[1], int(args[2])
                print("Received Turn", direction)
                for snake in self.snakes:
                    if snake.uuid == uuid:
                        snake.direction = direction

        if info == "tick":
            for snake in self.snakes:
                snake.tick()

    def draw(self, win):
        grid_x, grid_y = WIDTH // 100, HEIGHT // 100
        for i in range(1, 100):
            pygame.draw.line(win, (0, 0, 0), (i * grid_x, 0), (i * grid_x, HEIGHT))
            pygame.draw.line(win, (0, 0, 0), (0, i * grid_y), (HEIGHT, i * grid_y))

        for pos in self.apples:
            pygame.draw.rect(win, (255, 0, 0), (pos[0] * grid_x + 1, pos[1] * grid_y + 1, grid_x - 2, grid_y - 2))

        for snake in self.snakes:
            for i, pos in enumerate(snake.body):
                color = self.connection.color if snake == self.my_snake else (100, 100, 100)
                pygame.draw.rect(win, color, (pos[0] * grid_x + 1, pos[1] * grid_y + 1, grid_x - 2, grid_y - 2))

    def find_snake(self, uuid):
        for snake in self.snakes:
            if snake.uuid == uuid:
                return snake
        return None

    def on_quit(self):
        ...


class JoinState(GUIState):
    def __init__(self):
        super().__init__()

        self.label = gui.elements.UILabel(
            pygame.Rect(WIDTH * 0.1, HEIGHT * 0.35, WIDTH * 0.2, HEIGHT * 0.1),
            "Server IP:", self.manager,
            object_id=gui.core.ObjectID("ip_label", class_id="#medium_font_style")
        )

        self.ip_field = gui.elements.UITextEntryLine(
            pygame.Rect(WIDTH * .1, HEIGHT * .45, WIDTH * .7, HEIGHT * .1),
            self.manager, object_id=gui.core.ObjectID("ip_entry", class_id="#large_font_style")
        )

        self.join_button = gui.elements.UIButton(
            pygame.Rect(WIDTH * .8, HEIGHT * .45, WIDTH * .1, HEIGHT * .1),
            "Join", self.manager, object_id=gui.core.ObjectID("join", class_id="#medium_font_style")
        )

    def handle_event(self, event, mods):
        if event.type == gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.join_button:
                ip = self.ip_field.get_text()
                if ip:
                    switch = pygame.event.Event(
                        GUISTATE_SWITCH, state_type=GameState, ip=ip, username="Help"
                    )
                    pygame.event.post(switch)
        elif event.type == pygame.KEYUP:
            key = event.key
            if key == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(
                    GUISTATE_SWITCH, state_type=MenuState
                ))

    def tick(self, delta):
        ...

    def draw(self, win):
        ...

    def on_quit(self):
        ...
