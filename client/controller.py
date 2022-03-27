import pygame
from pygame import joystick
from pygame._sdl2 import controller

pygame.init()
joystick.init()
controller.init()

# Application stuff
game_name = "Snake"
display = pygame.display.Info()
max_size = min(display.current_w, display.current_h, 1000)
win = pygame.display.set_mode((max_size, max_size))
clock = pygame.time.Clock()
pygame.display.set_caption(game_name)

import gui_states

def main():
    looping = True
    states = [gui_states.MenuState()]
    current_state = 0
    while looping:
        delta = clock.tick() / 1000
        events, mods = pygame.event.get(), pygame.key.get_mods()

        for event in events:
            if event.type == pygame.QUIT:
                states[current_state].on_quit()
                looping = False
            if event.type == gui_states.GUISTATE_SWITCH:
                STATE_TYPE = event.state_type
                params = []
                if STATE_TYPE == gui_states.GameState:
                    params.append(event.ip)

                found_state = False
                # Looking for state of this type
                for i in range(len(states)):
                    if isinstance(states[i], STATE_TYPE):
                        current_state = i
                        found_state = True

                if not found_state:
                    states.append(event.state_type(*params))
                    current_state = len(states) - 1
                    print(states, current_state)

        # Manages the current state
        states[current_state].handle_events(events, mods)
        # print(delta)
        states[current_state].update(delta)

        # Drawing
        win.fill((50, 50, 50))
        states[current_state].draw_state(win)

        pygame.display.flip()

    print("Quitting application!")


if __name__ == '__main__':
    main()

pygame.display.quit()
controller.quit()
joystick.quit()

