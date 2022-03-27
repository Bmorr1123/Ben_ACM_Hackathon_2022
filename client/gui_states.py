import pygame
from pygame.display import get_window_size as size
import pygame_gui as gui
from abc import *


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
                pygame.event.post(pygame.event.Event(
                    GUISTATE_SWITCH, state_type=GameState, ip="localhost"
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
    def __init__(self, ip):
        super().__init__()

        self.f3_text = gui.elements.UILabel(
            pygame.Rect(0, 0, -1, -1),
            "???", self.manager
        )
        self.ip_text = gui.elements.UILabel(
            pygame.Rect(0, HEIGHT - 20, -1, -1),
            ip, self.manager
        )

    def handle_event(self, event, mods):
        if event.type == pygame.KEYUP:
            key = event.key
            if key == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(
                    GUISTATE_SWITCH, state_type=MenuState
                ))

    def tick(self, delta):
        self.f3_text.set_text(f"fps: {1 / delta:.2f}")

    def draw(self, win):
        grid_x, grid_y = WIDTH // 100, HEIGHT // 100
        for i in range(1, 100):
            pygame.draw.line(win, (0, 0, 0), (i * grid_x, 0), (i * grid_x, HEIGHT))
            pygame.draw.line(win, (0, 0, 0), (0, i * grid_y), (HEIGHT, i * grid_y))

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
                        GUISTATE_SWITCH, state_type=GameState, ip=ip
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
