import VARS, pygame, sys, boot
from interface_classes import Button

fps_clock = pygame.time.Clock()

def draw_rect(color, x, end_x, y, end_y, screen):
    end_x = end_x - x
    end_y = end_y - y
    pygame.draw.rect(screen, color, (x, y, end_x, end_y) ,0)



class MainGameWindow():

    def __init__(self, parent = None):
        VARS.load_settings()

        disp_size = VARS.APPROVED_RESOLUTIONS[VARS.CRT_REZ]

        self.refresh_rate = VARS.APPROVED_FPS_RATES[VARS.CRT_FPS]
        self.screen = pygame.display.set_mode(disp_size)
        self.grid = boot.get_display_grid(disp_size)['640.0:360.0']
        self.fonts = boot.scale_fonts(disp_size)
        self.mouse_pos = None
        self.tick_time = 0

        self.player = character(world = self)
        self.state = self.main_loop()


    def main_loop(self):
        self.gui_container()

        while VARS.RUNNING:
            self.draw_window()
            event_decisions =  self.event_handle()

    def draw_window(self):
        self.screen.fill((100, 100, 100))

    def gui_container(self):
        pass


    def event_handle(self):
        for event in pygame.event.get():
            self.mouse_pos =  pygame.mouse.get_pos()
            if event.type == pygame.QUIT:
                VARS.RUNNING = False


        keys = pygame.key.get_pressed()
        movement_keys = [keys[pygame.K_LEFT],keys[pygame.K_RIGHT],keys[pygame.K_UP],keys[pygame.K_DOWN]]

        if sum(movement_keys) > 1:
            speed = self.player.stats.speed * 0.845
        else:
            speed = self.player.stats.speed

        if keys[pygame.K_LEFT]:
            new_pos = int(round((self.player.position[0] - (speed * self.tick_time)),0))
            if check_fit([new_pos, self.player.position[1]], self.player.corners, self.grid):
                self.player.position[0] = new_pos

        if keys[pygame.K_RIGHT]:
            new_pos = int(round((self.player.position[0] + (speed * self.tick_time)),0))
            if check_fit([new_pos, self.player.position[1]], self.player.corners, self.grid):
                self.player.position[0] = new_pos

        if keys[pygame.K_UP]:
            new_pos =  int(round((self.player.position[1] - (speed * self.tick_time)),0))
            if check_fit([self.player.position[0], new_pos], self.player.corners, self.grid):
                self.player.position[1] = new_pos

        if keys[pygame.K_DOWN]:
            new_pos = int(round((self.player.position[1] + (speed * self.tick_time)),0))
            if check_fit([self.player.position[0], new_pos], self.player.corners, self.grid):
                self.player.position[1] = new_pos

        self.player.place_placer()

        pygame.display.update()
        self.tick_time = fps_clock.tick(self.refresh_rate)

def check_fit(new_pos, corners, grid):
    for (start_x, end_x, start_y, end_y) in corners:

        if new_pos[0] + end_x not in grid['end_x']:
            return

        elif new_pos[1] + end_y not in grid['end_y']:
            return

        elif new_pos[0] not in grid['start_x']:
            return

        elif new_pos[1] not in grid['start_y']:
            return

    return True






class character():
    def __init__(self, world = None):
        self.world = world
        self.stats = character_stats()
        self.body_build = self.structure_player()
        self.position = [300, 150]
        self.corners = []

    def structure_player(self):
        body = {
        'torso': (0,0,13,21),
        #'arms': (0,0,25,2)
        }

        return body

    def place_placer(self):
        self.corners = []
        for body_part, (offset_x, offset_y, x, y) in self.body_build.items():
            edge_x = self.position[0] + x
            edge_Y = self.position[1] + y

            print(self.position)
            print(edge_x,edge_Y)

            draw_rect(
                (0, 0, 0),
                self.world.grid['start_x'][self.position[0]] , self.world.grid['end_x'][self.position[0] + x],
                self.world.grid['start_y'][self.position[1]] , self.world.grid['end_y'][self.position[1] + y],
                self.world.screen
            )
            self.corners.append([self.position[0],  x, self.position[1],  y])


class character_stats():
    def __init__(self):
        self.health = 100
        self.speed = 0.15
