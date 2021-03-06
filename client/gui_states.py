import pygame
from pygame.display import get_window_size as size
import pygame_gui as gui
from pygame import Vector2
from abc import *
from client.snake import Snake
from pygame._sdl2 import controller as con
import client.connection
from random import randint, random


WIDTH, HEIGHT = size()

HAIL_SERVER = pygame.event.custom_type()
GUISTATE_SWITCH = pygame.event.custom_type()


class GUIState(ABC):
    def __init__(self, theme_path="client/res/base_theme.json"):
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
            pygame.Rect(WIDTH * 0.1, HEIGHT * 0.1, WIDTH * 0.8, HEIGHT * 0.2),
            "SNEK", self.manager, object_id=gui.core.ObjectID("title", "none")
        )

        self.title.set_active_effect(gui.TEXT_EFFECT_TYPING_APPEAR, params={"time_per_letter": 1})

        self.host_button = gui.elements.UIButton(
            pygame.Rect(WIDTH * .25, HEIGHT * .5, WIDTH * .5, HEIGHT * .1),
            "Host", self.manager, object_id=gui.core.ObjectID("host", "#large_font_style")
        )

        self.join_button = gui.elements.UIButton(
            pygame.Rect(WIDTH * .25, HEIGHT * .6, WIDTH * .5, HEIGHT * .1),
            "Join", self.manager, object_id=gui.core.ObjectID("join", "#large_font_style")
        )

        self.settings_button = gui.elements.UIButton(
            pygame.Rect(WIDTH * .25, HEIGHT * .7, WIDTH * .5, HEIGHT * .1),
            "Settings", self.manager, object_id=gui.core.ObjectID("settings", "#large_font_style"), visible=False
        )

        self.exit_button = gui.elements.UIButton(
            pygame.Rect(WIDTH * .25, HEIGHT * .7, WIDTH * .5, HEIGHT * .1),
            "Exit", self.manager, object_id=gui.core.ObjectID("exit", "#large_font_style")
        )

    def handle_event(self, event, mods):
        if event.type == gui.UI_BUTTON_PRESSED:
            button = event.ui_element
            if button == self.host_button:
                pygame.event.post(pygame.event.Event(
                    HAIL_SERVER
                ))

                pygame.event.post(pygame.event.Event(
                    GUISTATE_SWITCH, state_type=GameState, ip=client.connection.Connection.LOCALHOST, username="Host"
                ))
            elif button == self.join_button:
                pygame.event.post(pygame.event.Event(
                    GUISTATE_SWITCH, state_type=JoinState
                ))
            elif button == self.settings_button:
                pygame.event.post(pygame.event.Event(
                    GUISTATE_SWITCH, state_type=ColorState
                ))
            elif button == self.exit_button:
                pygame.event.post(pygame.event.Event(pygame.QUIT))

    def tick(self, delta):
        ...

    def draw(self, win):
        ...

    def on_quit(self):
        ...


class GameState(GUIState):
    def __init__(self, ip, name):
        super().__init__()

        self.connection = client.connection.Connection(ip, 3369, name)

        inputs = [con.Controller(index) for index in range(con.get_count())]

        self.f3_text = gui.elements.UILabel(
            pygame.Rect(0, 0, -1, -1),
            "???", self.manager, visible=False
        )

        # self.ip_text = gui.elements.UILabel(
        #     pygame.Rect(0, HEIGHT - 20, -1, -1),
        #     ip, self.manager
        # )

        # self.leaderboard = gui.elements.UIPanel(
        #     pygame.Rect(WIDTH * .7, 0, WIDTH * .3, HEIGHT * .2), 1, manager=self.manager,
        #     object_id=gui.core.ObjectID("leaderboard", "leaderboard")
        # )
        #
        # self.lb_title = gui.elements.UILabel(
        #     pygame.Rect(0, 0, WIDTH *.3, -1), "Leaderboard:", self.manager, container=self.leaderboard,
        #     object_id=gui.core.ObjectID(name, "#small_font_style")
        # )

        self.names = {}
        self.labels = {}

        self.my_snake = None
        self.snakes = []
        self.apples = []

        self.input_buffer = []
        self.particles = []

    def handle_event(self, event, mods):

        if event.type == pygame.KEYDOWN:
            key = event.key
            if self.my_snake:
                direction = -1
                if key == pygame.K_LEFT or key == pygame.K_a:
                    direction = 0
                elif key == pygame.K_DOWN or key == pygame.K_s:
                    direction = 1
                elif key == pygame.K_RIGHT or key == pygame.K_d:
                    direction = 2
                elif key == pygame.K_UP or key == pygame.K_w:
                    direction = 3

                cmp = self.my_snake.direction
                if self.input_buffer:
                    cmp = self.input_buffer[-1]

                if direction != -1 and direction % 2 != cmp % 2:
                    self.input_buffer.append(direction)

        elif event.type == pygame.CONTROLLERBUTTONDOWN:
            print(event)
            button = event.button
            if self.my_snake:
                direction = -1
                if button == pygame.CONTROLLER_BUTTON_DPAD_LEFT:
                    direction = 0
                elif button == pygame.CONTROLLER_BUTTON_DPAD_DOWN:
                    direction = 1
                elif button == pygame.CONTROLLER_BUTTON_DPAD_RIGHT:
                    direction = 2
                elif button == pygame.CONTROLLER_BUTTON_DPAD_UP:
                    direction = 3

                cmp = self.my_snake.direction
                if self.input_buffer:
                    cmp = self.input_buffer[-1]

                if direction != -1 and direction % 2 != cmp % 2:
                    self.input_buffer.append(direction)

            if button == pygame.CONTROLLER_BUTTON_A:
                if not self.my_snake:
                    self.connection.send("join")

        elif event.type == pygame.KEYUP:
            key = event.key
            if key == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(
                    GUISTATE_SWITCH, state_type=MenuState
                ))

            if key == pygame.K_SPACE:
                if not self.my_snake:
                    self.connection.send("join")

            if key == pygame.K_F3:
                self.f3_text.visible = not self.f3_text.visible

    def tick(self, delta):
        if delta:
            self.f3_text.set_text(f"fps: {1 / delta:.2f}")

        i = 0
        while i < len(self.particles):
            particle = self.particles[i]
            particle[0] += particle[1] * delta
            particle[-2] = particle[-2] * (1 - delta)
            if particle[-2] <= 3:
                self.particles.pop(i)
            else:
                i += 1

        self.receive()

    def receive(self):
        grid_x, grid_y = WIDTH // 100, HEIGHT // 100
        while info := self.connection.receive():
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
                    while snek := self.find_snake(uuid):
                        print("MURDERED SNAKE")

                        for i in range(50):
                            color = (randint(255 // 2, 255), randint(0, 100), 0)
                            self.particles.append([Vector2(snek.body[-1][0] * grid_x, snek.body[-1][1] * grid_y),
                                                   Vector2(random() - .5, random() - .5).normalize() * randint(20, 50),
                                                   randint(5, 35), color])

                        self.snakes.remove(snek)
                        if self.my_snake:
                            if uuid == self.my_snake.uuid:
                                self.my_snake = None

                elif args[0] == "snake":
                    print("CREATING SNAKE")
                    self.add_snake(args)

                elif args[0] == "turn":
                    uuid, direction = args[1], int(args[2])
                    for snake in self.snakes:
                        if snake.uuid == uuid:
                            snake.direction = direction

            if info == "tick":
                if len(self.input_buffer):
                    self.connection.send(f"#turn {self.input_buffer.pop(0)}")

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
            for i, pos in enumerate(reversed(snake.body)):
                pygame.draw.rect(win, snake.colors[i % len(snake.colors)], (pos[0] * grid_x + 1, pos[1] * grid_y + 1, grid_x - 2, grid_y - 2))

        for particle in self.particles:
            pygame.draw.rect(win, particle[-1], (particle[0].x, particle[0].y, particle[-2], particle[-2]))

    def find_snake(self, uuid):
        for snake in self.snakes:
            if snake.uuid == uuid:
                return snake
        return None

    def add_snake(self, args):
        print(f"Snake Args: {args}")
        uuid, name, direction, length, count = args[1], args[2], int(args[3]), int(args[4]), int(args[5])

        args = args[6:]

        colors = []
        for i in range(count):
            colors.append([int(args.pop(0)) for i in range(3)])

        body = []
        while len(args) > 1:
            body.append([int(args.pop(0)) for i in range(2)])

        snek = Snake(uuid, name, body[-1], direction)
        snek.length = length
        snek.colors = colors

        if uuid == self.connection.uuid:
            self.my_snake = snek

        self.snakes.append(snek)
        print(f"Created snake \"{snek.name}\" with uuid {snek.uuid}")

    def on_quit(self):
        self.connection.connection.close()


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

class ColorState(GUIState):
    def __init__(self):
        super().__init__()

        self.title = gui.elements.UILabel(
            pygame.Rect(WIDTH * 0.1, HEIGHT * 0.1, WIDTH * 0.8, HEIGHT * 0.3),
            "Color", self.manager, object_id=gui.core.ObjectID("title", "none")
        )

        self.title.set_active_effect(gui.TEXT_EFFECT_TYPING_APPEAR, params={"time_per_letter": 1})

        self.color1 = gui.elements.UITextEntryLine(
            pygame.Rect(WIDTH * .1, HEIGHT * .4, WIDTH * .2, HEIGHT * .05),
            self.manager, object_id=gui.core.ObjectID("ip_entry", class_id="#medium_font_style")
        )

        self.title = gui.elements.UILabel(
            pygame.Rect(WIDTH * .4, HEIGHT * .35, WIDTH * .2, HEIGHT * .05),
            "(Optional)", self.manager, object_id=gui.core.ObjectID("host", "#small_font_style")
        )

        self.color2 = gui.elements.UITextEntryLine(
            pygame.Rect(WIDTH * .4, HEIGHT * .4, WIDTH * .2, HEIGHT * .05),
            self.manager, object_id=gui.core.ObjectID("ip_entry", class_id="#medium_font_style")
        )

        self.title = gui.elements.UILabel(
            pygame.Rect(WIDTH * .7, HEIGHT * .35, WIDTH * .2, HEIGHT * .05),
            "(Optional)", self.manager, object_id=gui.core.ObjectID("host", "#small_font_style")
        )

        self.color3 = gui.elements.UITextEntryLine(
            pygame.Rect(WIDTH * .7, HEIGHT * .4, WIDTH * .2, HEIGHT * .05),
            self.manager, object_id=gui.core.ObjectID("ip_entry", class_id="#medium_font_style")
        )

        self.back_button = gui.elements.UIButton(
            pygame.Rect(WIDTH * .25, HEIGHT * .65, WIDTH * .5, HEIGHT * .2),
            "Back", self.manager, object_id=gui.core.ObjectID("join", "#large_font_style")
        )

    def handle_event(self, event, mods):
        if event.type == gui.UI_BUTTON_PRESSED:
            button = event.ui_element
            if button == self.color1:
               self.color1picker.show()
            elif button == self.color2:
                pass
            elif button == self.color3:
                pass
            elif button == self.back_button:
                pygame.event.post(pygame.event.Event(
                    GUISTATE_SWITCH, state_type=MenuState
                ))

        if event.type == gui.UI_COLOUR_PICKER_COLOUR_PICKED:
            self.color1.colours["normal_bg"] = event.colour

    def tick(self, delta):
        ...

    def draw(self, win):
        ...

    def on_quit(self):
        ...