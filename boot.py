import VARS, pygame, sys
VARS.load_settings()


def get_display_grid(display_size):
    whole_numbers = {}

    for i in range(1,50):
        width = round(display_size[0] / i, 1)
        height = round(display_size[1] / i, 1)

        square_name = str(round(width,0)) + ':' + str(round(height,0))

        if (width.is_integer() and height.is_integer()):
            whole_numbers[square_name] = {
                'start_x':{},
                'end_x':{},
                'start_y':{},
                'end_y':{}
            }

            square_no = 0
            for number in range(0,display_size[0], i):
                whole_numbers[square_name]['start_x'][square_no] = number
                whole_numbers[square_name]['end_x'][square_no] = number + i
                square_no+=1

            square_no = 0
            for number in range(0,display_size[1], i):
                whole_numbers[square_name]['start_y'][square_no] = number
                whole_numbers[square_name]['end_y'][square_no] = number + i
                square_no+=1

    return whole_numbers

def scale_fonts(display_size):
    size_requested = display_size[0] * display_size[1]

    difference = size_requested - VARS.DEFAULT_SIZE
    difference = ((difference / size_requested * 100) / 100) + 1

    results = {}
    for (font_tag, font_name, font_size) in VARS.DEFAULT_FONTS:
        size = int(round(font_size * difference,0))
        results[font_tag] = pygame.font.SysFont(font_name, size)

    return results

def blit_text(font_name, pos, colour, fonts, text, screen):
    textsurface = fonts[font_name].render(text, 1, (0, 0, 0))
    screen.blit(textsurface,(*pos,))


class MainMenu():
    def __init__(self):
        disp_size = VARS.APPROVED_RESOLUTIONS[VARS.CRT_REZ]

        self.screen = pygame.display.set_mode(disp_size)
        self.grid = get_display_grid(disp_size)['80.0:45.0']
        self.fonts = scale_fonts(disp_size)
        self.mouse_pos = None

        self.state = self.menu_loop()

    def menu_loop(self):
        self.containers()
        while VARS.RUNNING:
            self.draw_window()
            event_decisions =  self.event_handle()

            if event_decisions == 'Restart Window':
                break

            if event_decisions == 'Start Game':
                return 1

    def draw_window(self):
        self.screen.fill((255, 255, 255))

        blit_text(
            'main_titles',
            [self.grid['start_x'][37],self.grid['start_y'][1]],
            (0, 0, 0),
            self.fonts,
            'Settings',
            self.screen
        )

        self.resolution_select.draw(self.screen, self.mouse_pos)
        self.fps_selector.draw(self.screen, self.mouse_pos)
        self.apply_changes.draw(self.screen, self.mouse_pos)
        self.start_game.draw(self.screen, self.mouse_pos)

    def containers(self):
        self.rez_select = VARS.CRT_REZ
        self.fps_select = VARS.CRT_FPS

        self.resolution_select = Button(
            (87, 193, 255),
            self.grid['start_x'][4],self.grid['end_x'][24],
            self.grid['start_y'][6],self.grid['end_y'][7],
            self.fonts['button_font'],
            text ='Resolution: '+ str(VARS.APPROVED_RESOLUTIONS[self.rez_select]),
            alt_colour = (204, 235, 52)
        )

        self.fps_selector = Button(
            (87, 193, 255),
            self.grid['start_x'][4],self.grid['end_x'][24],
            self.grid['start_y'][9],self.grid['end_y'][10],
            self.fonts['button_font'],
            text ='FPS: '+ str(VARS.APPROVED_FPS_RATES[self.fps_select]),
            alt_colour = (204, 235, 52)
        )

        self.apply_changes = Button(
            (87, 193, 255),
            self.grid['start_x'][65],self.grid['end_x'][78],
            self.grid['start_y'][41],self.grid['end_y'][43],
            self.fonts['menu_titles'],
            text ='Apply Changes',
            alt_colour = (204, 235, 52)
        )

        self.start_game = Button(
            (87, 193, 255),
            self.grid['start_x'][33],self.grid['end_x'][48],
            self.grid['start_y'][40],self.grid['end_y'][43],
            self.fonts['main_titles'],
            text ='Start Game',
            alt_colour = (204, 235, 52)
        )


    def event_handle(self):
        for event in pygame.event.get():
            self.mouse_pos =  pygame.mouse.get_pos()
            if event.type == pygame.QUIT:
                VARS.RUNNING = False

            if event.type == pygame.MOUSEBUTTONUP:
                if self.apply_changes.isOver(self.mouse_pos):
                    print("APPLY CHANGES")
                    VARS.CRT_REZ = self.rez_select
                    VARS.CRT_FPS = self.fps_select
                    VARS.save_settings()
                    return 'Restart Window'

                elif self.resolution_select.isOver(self.mouse_pos):
                    self.rez_select  += 1

                    if self.rez_select > len(VARS.APPROVED_RESOLUTIONS) -1:
                        self.rez_select = 0

                    self.resolution_select.text = 'Resolution: '+ str(VARS.APPROVED_RESOLUTIONS[self.rez_select])

                elif self.fps_selector.isOver(self.mouse_pos):
                    self.fps_select  += 1

                    if self.fps_select > len(VARS.APPROVED_FPS_RATES) -1:
                        self.fps_select = 0

                    self.fps_selector.text = 'FPS: '+ str(VARS.APPROVED_FPS_RATES[self.fps_select])

                elif self.start_game.isOver(self.mouse_pos):
                    return 'Start Game'

        pygame.display.update()
        fps_clock.tick(VARS.TICK_SPEED_MENU)


def main():
    current_screen = 0

    while True:
        if current_screen == 0:
            window = MainMenu()

            if window.state:
                current_screen = window.state

        if current_screen == 1:
            window = MainGameWindow(VARS)


        if not VARS.RUNNING:
            pygame.quit()
            sys.exit()



if __name__ == '__main__':
    from main_game import MainGameWindow
    from interface_classes import Button


    pygame.init()
    fps_clock = pygame.time.Clock()

    main()

