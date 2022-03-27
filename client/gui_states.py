import pygame
from pygame.display import get_window_size as size
import pygame_gui as gui
from abc import *


WIDTH, HEIGHT = size()

GUISTATE_SWITCH = pygame.event.custom_type()


class GUIState(ABC):
    def __init__(self):
        self.manager = gui.UIManager((WIDTH, HEIGHT))

    def update(self, delta):
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
            pygame.Rect(WIDTH * 0.1, HEIGHT * 0.1, HEIGHT * 0.8, HEIGHT * 0.3),
            "Snek", self.manager
        )

        self.play_button = gui.elements.UIButton(
            pygame.Rect(WIDTH * .25, HEIGHT * .4, WIDTH * .5, HEIGHT * .2),
            "PLAY", self.manager
        )

    def handle_event(self, event, mods):
        if event.type == gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.play_button:
                switch = pygame.event.Event(
                    GUISTATE_SWITCH, state_type=GameState
                )
                pygame.event.post(switch)

    def tick(self, delta):
        ...

    def draw(self, win):
        ...

    def on_quit(self):
        ...


class GameState(GUIState):
    def __init__(self):
        super().__init__()

        self.f3_text = gui.elements.UILabel(
            pygame.Rect(0, 0, -1, -1),
            "???", self.manager
        )

    def handle_event(self, event, mods):
        pass

    def tick(self, delta):
        self.f3_text.set_text(f"fps: {1 / delta:.2f}")

    def draw(self, win):
        grid_x, grid_y = WIDTH // 100, HEIGHT // 100
        for i in range(1, 100):
            pygame.draw.line(win, (255, 255, 255), (i * grid_x, 0), (i * grid_x, HEIGHT))
            pygame.draw.line(win, (255, 255, 255), (0, i * grid_y), (HEIGHT, i * grid_y))

    def on_quit(self):
        ...
