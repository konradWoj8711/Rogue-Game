import VARS, pygame, sys, boot, random
from interface_classes import Button

fps_clock = pygame.time.Clock()

def draw_rect(color, x, end_x, y, end_y, screen):
    end_x = end_x - x
    end_y = end_y - y
    pygame.draw.rect(screen, color, (x, y, end_x, end_y) ,0)

def random_partition(chunks, int_volume):
    results = {}
    for i in range(chunks):
        results[i] = int(round(int_volume/chunks,0))

    for i in range(chunks):
        target_chunk = random.randint(0,chunks-1)
        toss_amount = random.randint(0,results[i]-1)

        results[i] = results[i] - toss_amount
        results[target_chunk] = results[target_chunk] + toss_amount

    return results

def intervals(parts, duration):
    part_duration = duration / parts
    return [((i + 1) * part_duration) for i in range(parts)]


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

        self.blocked_area = set()
        self.player = character(world = self)

        self.terrain = self.generate_terrain()
        self.state = self.main_loop()

    def generate_terrain(self):
        grid_x, grid_y = (len(self.grid['start_x'])/4), (len(self.grid['start_y'])/4)
        total_squares = int(round((grid_x * grid_y),0))
        clusters = random.randint(7,20)

        assigned_chunks = random_partition(clusters,total_squares)

        cluster_seeds = []
        for i in range(clusters):
            x = random.randint(0,grid_x-1)
            y = random.randint(0,grid_y-1)

            cluster_seeds.append((x, y))

            for chunk in range(assigned_chunks[i]):
                last_chunk = cluster_seeds[len(cluster_seeds)-1]

                x = random.randint(-1,1)
                y = random.randint(-1,1)

                temp_x = last_chunk[0] + x
                if temp_x >= grid_x or temp_x < 0:
                    x = 0

                temp_y = last_chunk[1] + y
                if temp_y >= grid_y or temp_y < 0:
                    y = 0

                new_chunk = (last_chunk[0] + x, last_chunk[1] + y)
                if new_chunk not in cluster_seeds and new_chunk[0] >= 0 and new_chunk[1] >= 0:
                    cluster_seeds.append(new_chunk)


        #max_y = len(self.grid['start_y'])
        #sections = intervals(40, max_y)

        for  (x, y) in cluster_seeds:
            x_s, y_s= x*4, y*4
            for i in range(0,4):
                x_m, y_m= x_s+i, y_s+i

                #if x_s not in self.blocked_area:
                #    self.blocked_area[x_s] = set()

                self.blocked_area.add((x_s, y_s))
                self.blocked_area.add((x_s, y_m))

                #if x_m not in self.blocked_area:
                #    self.blocked_area[x_m] = set()

                self.blocked_area.add((x_m, y_s))
                self.blocked_area.add((x_m, y_m))


        return cluster_seeds

    def draw_terrain(self):
        for (x, y) in self.terrain:

            x, y= x*4, y*4
            max_x, max_y = x+3, y+3

            draw_rect(
                (0, 0, 0),
                self.grid['start_x'][x],
                self.grid['end_x'][max_x],
                self.grid['start_y'][y],
                self.grid['end_y'][max_y],
                self.screen
            )

    def main_loop(self):
        self.gui_container()

        while VARS.RUNNING:
            self.draw_window()
            event_decisions =  self.event_handle()

    def draw_window(self):
        self.screen.fill((100, 100, 100))
        self.draw_terrain()

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
            if self.check_fit([new_pos, self.player.position[1]], self.player.corners):
                self.player.position[0] = new_pos

        if keys[pygame.K_RIGHT]:
            new_pos = int(round((self.player.position[0] + (speed * self.tick_time)),0))
            if self.check_fit([new_pos, self.player.position[1]], self.player.corners):
                self.player.position[0] = new_pos

        if keys[pygame.K_UP]:
            new_pos =  int(round((self.player.position[1] - (speed * self.tick_time)),0))
            if self.check_fit([self.player.position[0], new_pos], self.player.corners):
                self.player.position[1] = new_pos

        if keys[pygame.K_DOWN]:
            new_pos = int(round((self.player.position[1] + (speed * self.tick_time)),0))
            if self.check_fit([self.player.position[0], new_pos], self.player.corners):
                self.player.position[1] = new_pos

        self.player.place_placer()

        pygame.display.update()
        self.tick_time = fps_clock.tick(self.refresh_rate)

    def check_fit(self, new_pos, corners):
        for (x_width, offset_x, y_width, offset_y) in corners:
            position_x = new_pos[0] - offset_x
            position_y = new_pos[1] - offset_y


            if position_x + x_width - offset_x not in self.grid['end_x']:
                return

            elif position_y + y_width - offset_y not in self.grid['end_y']:
                return

            elif position_x not in self.grid['start_x']:
                return

            elif position_y not in self.grid['start_y']:
                return


            corner_cords = []

            for x in range(position_x, position_x + x_width - offset_x):
                for y in range(position_y, position_y + y_width - offset_y):
                    if (x,y) not in corner_cords:
                        corner_cords.append((x,y))

            """
            # DISPLAYS HITBOX
            for cords in corner_cords:
                draw_rect((0,0,0),
                self.grid['start_x'][cords[0]] , self.grid['end_x'][cords[0]],
                self.grid['start_y'][cords[1]] , self.grid['end_y'][cords[1]],
                self.screen)
            """


            for cord in corner_cords:
                if cord in self.blocked_area:
                    return


        return True






class character():
    def __init__(self, world = None):
        self.world = world
        self.stats = character_stats()
        self.body_build = self.structure_player()
        self.position = [300, 150]
        self.corners = []

        self.is_placed = False

    def structure_player(self):
        body = {
        'head': (-3,5,5,10),
        'torso': (0,0,14,21),
        'arm_left': (3,-6,7,7),
        'arm_right': (-14,-6,-11,7),
        'shoulders': (3,-4,23,2),
        'leg_left': (0,-10,3,7),
        'leg_right': (-11,-10,-8,7),
        }

        return body

    def place_placer(self):
        self.corners = []
        for body_part, (offset_x, offset_y, x, y) in self.body_build.items():
            position_x = self.position[0] - offset_x
            position_y = self.position[1] - offset_y

            edge_x = position_x + x - offset_x
            edge_y = position_y + y - offset_y

            draw_rect(
                (181, 13, 43),
                self.world.grid['start_x'][position_x] , self.world.grid['end_x'][edge_x],
                self.world.grid['start_y'][position_y] , self.world.grid['end_y'][edge_y],
                self.world.screen
            )

            self.corners.append([x,  offset_x, y,  offset_y])

        if not self.is_placed:
            temp_position = (self.position[0],self.position[1])
            while not self.world.check_fit(temp_position, self.corners) and not self.is_placed:
                temp_position = (random.randint(0,len(self.world.grid['start_x'])),random.randint(0,len(self.world.grid['start_y'])))

            self.position = [temp_position[0], temp_position[1]]

class character_stats():
    def __init__(self):
        self.health = 100
        self.speed = 0.15
