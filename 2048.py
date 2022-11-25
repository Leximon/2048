import random
import colorsys
import pygame
import time


def draw_rect(pos, color):
    global screen, grid_size, grid_border_size
    screen.fill(color, (int(pos[0] * (grid_size + grid_border_size) + grid_border_size),
                        int(pos[1] * (grid_size + grid_border_size) + grid_border_size),
                        grid_size,
                        grid_size))


def draw_num(pos, num):
    global screen, font, grid_size, grid_border_size
    s = str(num)
    text = font.render(s, True, (255, 255, 255))
    text_size = font.size(s)
    screen.blit(text, (
        int(pos[0] * (grid_size + grid_border_size) + grid_border_size + (grid_size - text_size[0]) / 2),
        int(pos[1] * (grid_size + grid_border_size) + grid_border_size + (grid_size - text_size[1]) / 2)
    ))


def ran_pos():
    space = get_free_space()
    return space[random.randrange(0, len(space))]


def lerp(__delta, a, b):
    return a + (b - a) * __delta


def lerp_pos(__delta, pos_a, pos_b):
    return (
        lerp(__delta, pos_a[0], pos_b[0]),
        lerp(__delta, pos_a[1], pos_b[1])
    )


def clamp(__value, __min, __max):
    return max(min(__value, __max), __min)


def clamp_pos(__value, min_pos, max_pos):
    return (
        clamp(__value[0], min_pos[0], max_pos[0]),
        clamp(__value[1], min_pos[1], max_pos[1])
    )


def get_square_at(ignore, pos):
    global squares
    for s in squares:
        if ignore is not s and not s.mark_for_removal and s.pos[0] == pos[0] and s.pos[1] == pos[1]:
            return s
    return None


def get_squares_in_order(direction):
    global field_width, field_height, squares
    new_squares = []
    if direction[0] != 0:
        for __x in range(0, field_width) if direction[0] < 0 else reversed(range(0, field_width)):
            for s in squares:
                if s.pos[0] == __x:
                    new_squares.append(s)
    else:
        for __y in range(0, field_height) if direction[1] < 0 else reversed(range(0, field_height)):
            for s in squares:
                if s.pos[1] == __y:
                    new_squares.append(s)
    return new_squares


def move_squares(direction):
    global squares, moved_timestamp
    if moved_timestamp != -1:
        square.on_move_end()
    squares.append(Square(None))
    for s in get_squares_in_order(direction):
        s.move_in_direction(direction)
    moved_timestamp = time.time()


def exceeds_field(pos):
    global field_width, field_height
    return (pos[0] < 0 or pos[1] < 0) or (pos[0] >= field_width or pos[1] >= field_height)


def get_free_space():
    global field_width
    free = []
    for __x in range(0, field_width):
        for __y in range(0, field_height):
            if get_square_at(None, (__x, __y)) is None:
                free.append((__x, __y))
    return free


class Square:
    def __init__(self, pos, value=2):
        global field_width, field_height
        self.value = value
        self.pos = pos if pos is not None else ran_pos()
        self.prev_pos = self.pos
        self.mark_for_removal = False

    def color(self):
        return tuple(int(c * 255) for c in colorsys.hsv_to_rgb(self.value / 75.31275, 0.75, 1))

    def draw(self):
        global move_transition_duration, font, squares, moved_timestamp
        if moved_timestamp > 0:
            p = (time.time() - moved_timestamp) / move_transition_duration
            pos = lerp_pos(p, self.prev_pos, self.pos)
            draw_rect(pos, self.color())
            draw_num(pos, self.value)
        else:
            draw_rect(self.pos, self.color())
            draw_num(self.pos, self.value)

    def on_move_end(self):
        if self.mark_for_removal:
            squares.remove(self)

    def set_pos(self, new_pos):
        global field_width, field_height
        new_pos2 = clamp_pos(new_pos, (0, 0), (field_width-1, field_height-1))
        if new_pos2 != self.pos:
            self.prev_pos = self.pos
            self.pos = new_pos2

    def move_in_direction(self, direction):
        if self.mark_for_removal:
            squares.remove(self)
            return
        target_pos = self.pos
        while True:
            new_target_pos = (target_pos[0] + direction[0], target_pos[1] + direction[1])
            if exceeds_field(new_target_pos):
                break
            target_square = get_square_at(self, new_target_pos)
            if target_square is not None and target_square.value != self.value:
                break
            target_pos = new_target_pos
        self.set_pos(target_pos)
        self.try_merge()

    def try_merge(self):
        global squares
        target_square = get_square_at(self, self.pos)
        if target_square is not None \
                and target_square is not self \
                and target_square.value == self.value:
            squares.append(Square(self.pos, self.value + target_square.value))
            target_square.mark_for_removal = True
            self.mark_for_removal = True


col_white = (255, 255, 255)
col_gray = (222, 222, 222)

field_size = field_width, field_height, = 5, 5
grid_size = 100
grid_border_size = 10
move_transition_duration = 0.5
size = width, height = (grid_size + grid_border_size) * field_width + grid_border_size,\
                       (grid_size + grid_border_size) * field_height + grid_border_size

squares = []
for i in range(2):
    squares.append(Square((3, i * 4)))
moved_timestamp = -1

pygame.init()
font = pygame.font.SysFont("Consolas", 40, True)
screen = pygame.display.set_mode(size)
prev_time = time.time()
while True:
    current_time = time.time()
    delta = (current_time - prev_time) * 0.01
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit(0)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                move_squares((0, -1))
            elif event.key == pygame.K_DOWN:
                move_squares((0, 1))
            elif event.key == pygame.K_LEFT:
                move_squares((-1, 0))
            elif event.key == pygame.K_RIGHT:
                move_squares((1, 0))

    screen.fill(col_gray, (0, 0, width, height))
    for x in range(0, field_width):
        for y in range(0, field_height):
            draw_rect((x, y), col_white)

    for square in squares:
        square.draw()
    if moved_timestamp != -1 and current_time - moved_timestamp > move_transition_duration:
        moved_timestamp = -1
        for square in squares:
            square.on_move_end()

    pygame.display.flip()
