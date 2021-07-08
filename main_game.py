import VARS
import boot
import pygame
import random
import path_finding

fps_clock = pygame.time.Clock()


def draw_rect(color, x, end_x, y, end_y, screen):
    end_x = end_x - x
    end_y = end_y - y
    pygame.draw.rect(screen, color, (x, y, end_x, end_y), 0)


def random_partition(chunks, int_volume):
    results = {}
    for i in range(chunks):
        results[i] = int(round(int_volume / chunks, 0))

    for i in range(chunks):
        target_chunk = random.randint(0, chunks - 1)
        toss_amount = random.randint(0, results[i] - 1)

        results[i] = results[i] - toss_amount
        results[target_chunk] = results[target_chunk] + toss_amount

    return results


def intervals(parts, duration):
    part_duration = duration / parts
    return [((i + 1) * part_duration) for i in range(parts)]



def make_level_map(x, y, blocked):
    map_plan = []
    for vertical in range(x):
        plan_line = []
        for horizontal in range(y):
            if (vertical, horizontal) in blocked:
                plan_line.append(1)
            else:
                plan_line.append(0)
        map_plan.append(plan_line)

    return map_plan

class MainGameWindow():

    def __init__(self, parent=None):
        VARS.load_settings()
        display_size = VARS.APPROVED_RESOLUTIONS[VARS.CRT_REZ]

        self.refresh_rate = VARS.APPROVED_FPS_RATES[VARS.CRT_FPS]
        self.screen = pygame.display.set_mode(display_size)
        self.grid = boot.get_display_grid(display_size)['640.0:360.0']
        self.fonts = boot.scale_fonts(display_size)
        self.mouse_pos = None
        self.tick_time = 0
        self.level = None

        self.player = Character(world=self)
        self.state = None
        self.load_level(100)

    def load_level(self, level_rage):
        for current_level in range(1, level_rage):
            self.level = current_level
            self.blocked_area = set()
            self.terrain = self.generate_terrain()
            self.current_placements = {}
            self.enemies = {}

            self.path_grapth = make_level_map(int(len(self.grid['start_x'])), int(len(self.grid['start_y'])), self.blocked_area)

            for i in range(1):
                self.enemies[i] = Enemy(i, world=self)

            self.state = self.main_loop()
            if self.state: break

    def generate_terrain(self):
        grid_x, grid_y = (len(self.grid['start_x']) / 4), (len(self.grid['start_y']) / 4)
        total_squares = int(round((grid_x * grid_y), 0))
        clusters = random.randint(7, 20)

        assigned_chunks = random_partition(clusters, total_squares)

        cluster_seeds = []
        for i in range(clusters):
            x = random.randint(0, grid_x - 1)
            y = random.randint(0, grid_y - 1)

            cluster_seeds.append((x, y))

            for chunk in range(assigned_chunks[i]):
                last_chunk = cluster_seeds[len(cluster_seeds) - 1]

                x = random.randint(-1, 1)
                y = random.randint(-1, 1)

                temp_x = last_chunk[0] + x
                if temp_x >= grid_x or temp_x < 0:
                    x = 0

                temp_y = last_chunk[1] + y
                if temp_y >= grid_y or temp_y < 0:
                    y = 0

                new_chunk = (last_chunk[0] + x, last_chunk[1] + y)
                if new_chunk not in cluster_seeds and new_chunk[0] >= 0 and new_chunk[1] >= 0:
                    cluster_seeds.append(new_chunk)

        # max_y = len(self.grid['start_y'])
        # sections = intervals(40, max_y)

        for (x, y) in cluster_seeds:
            x_s, y_s = x * 4, y * 4
            for i in range(0, 4):
                x_m, y_m = x_s + i, y_s + i

                # if x_s not in self.blocked_area:
                #    self.blocked_area[x_s] = set()

                self.blocked_area.add((x_s, y_s))
                self.blocked_area.add((x_s, y_m))

                # if x_m not in self.blocked_area:
                #    self.blocked_area[x_m] = set()

                self.blocked_area.add((x_m, y_s))
                self.blocked_area.add((x_m, y_m))

        return cluster_seeds

    def draw_terrain(self):
        for (x, y) in self.terrain:
            x, y = x * 4, y * 4
            max_x, max_y = x + 3, y + 3

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
            event_decisions = self.event_handle()

        if not VARS.RUNNING: return -1

    def draw_window(self):
        self.screen.fill((100, 100, 100))
        self.draw_terrain()

        boot.blit_text(
            'main_titles',
            [self.grid['start_x'][10], self.grid['start_y'][340]],
            (255, 255, 255),
            self.fonts,
            'Stage ' + str(self.level),
            self.screen
        )

    def gui_container(self):
        pass

    def event_handle(self):
        for event in pygame.event.get():
            self.mouse_pos = pygame.mouse.get_pos()
            if event.type == pygame.QUIT:
                VARS.RUNNING = False

        keys = pygame.key.get_pressed()
        movement_keys = [keys[pygame.K_LEFT], keys[pygame.K_RIGHT], keys[pygame.K_UP], keys[pygame.K_DOWN]]

        if sum(movement_keys) > 1:
            speed = self.player.stats.speed * 0.845
        else:
            speed = self.player.stats.speed

        if keys[pygame.K_LEFT]:
            new_pos = int(round((self.player.position[0] - (speed * self.tick_time)), 0))
            if self.check_fit([new_pos, self.player.position[1]], self.player.corners, 'player'):
                self.player.position[0] = new_pos

        if keys[pygame.K_RIGHT]:
            new_pos = int(round((self.player.position[0] + (speed * self.tick_time)), 0))
            if self.check_fit([new_pos, self.player.position[1]], self.player.corners, 'player'):
                self.player.position[0] = new_pos

        if keys[pygame.K_UP]:
            new_pos = int(round((self.player.position[1] - (speed * self.tick_time)), 0))
            if self.check_fit([self.player.position[0], new_pos], self.player.corners, 'player'):
                self.player.position[1] = new_pos

        if keys[pygame.K_DOWN]:
            new_pos = int(round((self.player.position[1] + (speed * self.tick_time)), 0))
            if self.check_fit([self.player.position[0], new_pos], self.player.corners, 'player'):
                self.player.position[1] = new_pos

        for enemy_tag, enemy_class in self.enemies.items():
            enemy_class.find_path(self.player.position, self.tick_time)
            enemy_class.place_enemy()

        self.player.place_player()

        pygame.display.update()
        self.tick_time = fps_clock.tick(self.refresh_rate)

    def check_fit(self, new_pos, corners, object_type):
        temp_coordinates = set()

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
                    if (x, y) not in corner_cords:
                        corner_cords.append((x, y))
                        temp_coordinates.add((x, y))

            """
            # DISPLAYS HITBOX
            for cords in corner_cords:
                draw_rect((0,0,0),
                self.grid['start_x'][cords[0]] , self.grid['end_x'][cords[0]],
                self.grid['start_y'][cords[1]] , self.grid['end_y'][cords[1]],
                self.screen)
            """
            avoidance = set()
            for block_id, occupation in self.current_placements.items():
                if block_id == 'player': continue
                if block_id != object_type:
                    avoidance.update(occupation)

            for cord in corner_cords:
                if cord in self.blocked_area:
                    return

                elif cord in avoidance:
                    return

        self.current_placements[object_type] = temp_coordinates

        return True

    def get_free_cords(self):
        all_cords = set()
        w, h = len(self.grid['start_x']), len(self.grid['start_y'])
        for x in range(w):
            for y in range(h):
                all_cords.add((x, y))

        free_cords = []
        for cord in all_cords:
            if cord not in self.blocked_area:
                free_cords.append(cord)

        return all_cords

class BaseStats():
    def __init__(self, speed=0.15):
        self.health = 100
        self.speed = speed


class Character():
    def __init__(self, world=None):
        self.world = world
        self.stats = BaseStats()
        self.body_build = self.structure_player()
        self.position = [300, 150]
        self.corners = []

        self.is_placed = False

    def structure_player(self):
        body = {
            'head': (-3, 5, 5, 10),
            'torso': (0, 0, 14, 21),
            'arm_left': (3, -6, 7, 7),
            'arm_right': (-14, -6, -11, 7),
            'shoulders': (3, -4, 23, 2),
            'leg_left': (0, -10, 3, 7),
            'leg_right': (-11, -10, -8, 7),
        }

        return body

    def place_player(self):
        self.corners = []
        for body_part, (offset_x, offset_y, x, y) in self.body_build.items():
            position_x = self.position[0] - offset_x
            position_y = self.position[1] - offset_y

            edge_x = position_x + x - offset_x
            edge_y = position_y + y - offset_y

            draw_rect(
                (62, 176, 106),
                self.world.grid['start_x'][position_x], self.world.grid['end_x'][edge_x],
                self.world.grid['start_y'][position_y], self.world.grid['end_y'][edge_y],
                self.world.screen
            )

            self.corners.append([x, offset_x, y, offset_y])

        if not self.is_placed:
            temp_position = (self.position[0], self.position[1])
            while not self.world.check_fit(temp_position, self.corners, 'player') and not self.is_placed:
                temp_position = (
                random.randint(0, len(self.world.grid['start_x'])), random.randint(0, len(self.world.grid['start_y'])))

            self.is_placed = True
            self.position = [temp_position[0], temp_position[1]]


class Enemy():
    def __init__(self, enemy_id, world=None):
        self.move_order = []
        self.world = world
        self.stats = BaseStats(speed=0.01)
        self.body_build = self.structure_enemy()
        self.position = [300, 150]
        self.corners = []
        self.enemy_id = enemy_id

        self.is_placed = False

    def structure_enemy(self, enemy_type=None):
        body = {
            'torso': (0, 0, 10, 10),

        }

        return body

    def place_enemy(self):
        self.corners = []
        for body_part, (offset_x, offset_y, x, y) in self.body_build.items():
            position_x = self.position[0] - offset_x
            position_y = self.position[1] - offset_y

            edge_x = position_x + x - offset_x
            edge_y = position_y + y - offset_y

            draw_rect(
                (181, 13, 43),
                self.world.grid['start_x'][position_x], self.world.grid['end_x'][edge_x],
                self.world.grid['start_y'][position_y], self.world.grid['end_y'][edge_y],
                self.world.screen
            )

            self.corners.append([x, offset_x, y, offset_y])

        if not self.is_placed:
            temp_position = (self.position[0], self.position[1])
            while not self.world.check_fit(temp_position, self.corners, self.enemy_id) and not self.is_placed:
                temp_position = (random.randint(0, len(self.world.grid['start_x'])), random.randint(0, len(self.world.grid['start_y'])))

            self.is_placed = True
            self.position = [temp_position[0], temp_position[1]]

    def find_path(self, target, tick_time):
        starting_point = (int(round(self.position[0], 0)), int(round(self.position[1], 0)))
        target = (int(round(target[0], 0)), int(round(target[1], 0)))

        print(starting_point, target)
        if len(self.move_order) <=1:
            self.move_order = path_finding.astar(self.world.path_grapth, starting_point, target)

        if len(self.move_order) >1:
            for i in self.move_order:
                draw_rect(
                    (62, 176, 106),
                    self.world.grid['start_x'][i[0]], self.world.grid['end_x'][i[0]],
                    self.world.grid['start_y'][i[1]], self.world.grid['end_y'][i[1]],
                    self.world.screen
                )

            if len(self.move_order) > 1:
                new_pos = [self.move_order[1][0], self.move_order[1][1]]

                if starting_point[0] != self.move_order[1][0]:
                    new_pos[0] = new_pos[0]+ (int(round(self.stats.speed * tick_time)))

                if starting_point[1] != self.move_order[1][1]:
                    new_pos[1] = new_pos[1]+ (int(round(self.stats.speed * tick_time)))

                self.position = new_pos
                del self.move_order[0]

        #print(self.world.free_terrain )
        """
        tried_positions = set()
        while temp_coordinates != target:

            neighbouring_squares = []
            move_rank, move_dict = [], {}

            for i in range(-1, 2):
                if i == 0 : continue
                neighbouring_squares.append([temp_coordinates[0] + i, temp_coordinates[1]])
                neighbouring_squares.append([temp_coordinates[0], temp_coordinates[1] + i])

            for possible_position in neighbouring_squares:
                x_away = target[0] - possible_position[0]
                y_away = target[1] - possible_position[1]
                if x_away < 0:
                    x_away = x_away * -1

                if y_away < 0:
                    y_away = y_away * -1

                move_rank.append(x_away+y_away)
                move_dict[x_away+y_away] = possible_position

            illegal = 0
            move_rank.sort()
            for move in move_rank:
                new_position = move_dict[move]
                if self.world.check_fit(new_position, self.corners, self.enemy_id) and str(new_position) not in tried_positions:
                    tried_positions.add(str(new_position))
                    temp_coordinates = new_position
                    move_order.append(new_position)
                    break

            if move < 100:
                break

        print(move_order)
        self.position = temp_coordinates


        temp_pos = self.position.copy()
        for direction in moves:
            if direction in ['left', 'right']:
                if direction == 'left':
                    temp_pos[0] = int(round((self.position[0] - distance), 0))

                elif direction == 'right':
                    temp_pos[0] = int(round((self.position[0] + distance), 0))

                if self.world.check_fit(temp_pos, self.corners, self.enemy_id):
                    self.position = temp_pos

            elif direction in ['up', 'down']:
                if direction == 'up':
                    temp_pos[1] = int(round((self.position[1] - distance), 0))

                elif direction == 'down':
                    temp_pos[1] = int(round((self.position[1] + distance), 0))

                if self.world.check_fit(temp_pos, self.corners, self.enemy_id):
                    self.position = temp_pos


        """