# import libraries
import math
import random
import pygame

pygame.init()

# pygame variables
screen_dimensions = (400, 750)
screen_center = (screen_dimensions[0] / 2, screen_dimensions[1] / 2)
screen_center_x = screen_center[0]
screen_center_y = screen_center[1]
screen = pygame.display.set_mode(screen_dimensions)
clock = pygame.time.Clock()

# default object values
bricks = []
block_width = screen_dimensions[0] / 8
block_height = block_width / 3
powerup_chance = 4      # out of ten
max_level_height = 24
ball_radius = 8
powerup_choices = ["extra ball", "long platform"]
default_platform_dimensions = [50, 10]
platform_speed = 5
colors = ("red", "orange", "yellow", "green", "blue", "cyan", "purple", "pink", "grey", "white")
info = ("In this game, you control a paddle which can move\n"
        "horizontally across the screen. The player must knock down\n"
        "as many bricks as possible by using the walls and/or the\n"
        "paddle to hit the ball against the bricks and eliminate them.\n"
        "If you run out of balls, you lose. However, you will\n"
        "occasionally get powerups to help you when you hit a brick\n"
        "such as getting an extra ball or having your platform\n"
        "expanded. You can pause the level by pressing \"p\". You can \n"
        "either play normal mode which will pit you against 10 levels\n"
        "of bricks with increasing difficulty, or you can play endless\n"
        "mode with randomly generating bricks and try to get as far as\n"
        "possible. You can also choose to create and play your own\n"
        "levels using the \"Level Creator\". The \"High Scores\" option\n"
        "will show the leaderboard for endless mode.")


class Ball:
    # Ball constructor
    def __init__(self, x: int | float, y: int | float, x_vel: int | float, y_vel: int | float, color: tuple = None):
        self.x = x
        self.y = y
        self.x_vel = x_vel
        self.y_vel = y_vel
        self.rect = pygame.Rect([x - ball_radius, y - ball_radius], [2 * ball_radius, 2 * ball_radius])
        if color is None:
            self.color = (255, 0, 0)
        else:
            self.color = color

    # handles the collision of the ball against a rectangle on the screen and decides how to bounce the ball.
    def handle_rect_bounce(self, rect, object_hit="brick"):

        # Sets velocity based on which side of the brick the ball has hit
        if self.x < rect.centerx:  # ball left of brick

            if self.y < rect.centery:  # ball to the top left of brick

                new_vel = get_new_vel(self, [-1, -1], rect, object_hit)

                self.x_vel, self.y_vel = new_vel[0], new_vel[1]
            else:  # ball to the bottom left of brick

                new_vel = get_new_vel(self, [-1, 1], rect, object_hit)

                self.x_vel, self.y_vel = new_vel[0], new_vel[1]
        else:  # ball right of brick

            if self.y < rect.centery:  # ball to the top right of brick

                new_vel = get_new_vel(self, [1, -1], rect, object_hit)

                self.x_vel, self.y_vel = new_vel[0], new_vel[1]
            else:  # ball to the bottom right of brick

                new_vel = get_new_vel(self, [1, 1], rect, object_hit)

                self.x_vel, self.y_vel = new_vel[0], new_vel[1]

    def set_pos(self, x, y):
        self.x = x
        self.y = y

        if self.x - ball_radius < 0:
            self.x = ball_radius
            self.x_vel *= -1
        if self.x + ball_radius > screen_dimensions[0]:
            self.x = screen_dimensions[0] - ball_radius
            self.x_vel *= -1
        if self.y - ball_radius < 0:
            self.y = ball_radius
            self.y_vel *= -1
        if self.y + ball_radius > screen_dimensions[1]:
            self.y = screen_dimensions[1] - ball_radius
            self.y_vel *= -1

        self.rect.center = [self.x, self.y]

    # updates the ball's position according to it's speed
    def update_pos(self):
        self.x += self.x_vel
        self.y += self.y_vel

        # puts the ball back on the screen and bounces it if the ball has hit a wall
        if self.x - ball_radius < 0:
            self.x = ball_radius
            self.x_vel *= -1
        if self.x + ball_radius > screen_dimensions[0]:
            self.x = screen_dimensions[0] - ball_radius
            self.x_vel *= -1
        if self.y - ball_radius < 0:
            self.y = ball_radius
            self.y_vel *= -1

        self.rect.center = [self.x, self.y]

    # draws the ball on the screen
    def draw(self, surface: pygame.Surface):
        pygame.draw.circle(surface, self.color, [self.x, self.y], ball_radius)


class Platform:
    # Platform constructor
    def __init__(self, x, y, width, height, speed, color=(255, 255, 255)):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.rect = pygame.Rect(x, y, width, height)

    # resets the conditions of the platform to their defaults
    def reset(self):
        self.set_width(50)
        self.x = 175
        self.rect.centerx = screen_center_x

    def change_width(self, inc):
        self.rect.width += inc
        self.width += inc

    def set_width(self, w):
        self.width = w
        self.rect.width = w

    # takes the player's inputs and moves the platform accordingly
    def player_move(self, inputs):
        if inputs[pygame.K_a] or inputs[pygame.K_LEFT]:
            self.x -= platform_speed
            self.rect = self.rect.move(-platform_speed, 0)
        if inputs[pygame.K_d] or inputs[pygame.K_RIGHT]:
            self.x += platform_speed
            self.rect = self.rect.move(platform_speed, 0)

        if self.rect.right > screen_dimensions[0]:
            self.rect.right = screen_dimensions[0]
        if self.rect.left < 0:
            self.rect.left = 0

    # draws the platform on the screen
    def draw(self, surface: pygame.Surface):
        pygame.draw.rect(surface, self.color, self.rect)


# returns -1 if the parameter number is negative, 0 if it is 0, and 1 if it is positive
def normalize(num):
    if num > 0:
        return 1
    elif num < 0:
        return -1
    else:
        return 0


# takes ball and brick objects and calculates and returns the appropriate velocity for the ball.
# meant to make the ball bounce off of platforms and bricks
def get_new_vel(ball, norm_cords, rect, object_hit):
    if object_hit == "platform":
        ratio = (rect.left - ball.x) / rect.width * math.pi
        ball.x_vel = -math.cos(ratio) * 2
    norm_vel_cords = [normalize(ball.x_vel), normalize(ball.y_vel)]
    dist = 0
    for i in range(len(norm_vel_cords)):
        if norm_vel_cords[i] != norm_cords[i]:
            dist += 1
    dist_arr = [0 if norm_vel_cords[i] == norm_cords[i] else 1 for i in range(len(norm_cords))]
    match dist:
        case 0:
            if norm_cords[0] == -1:
                ball.set_pos(rect.left - ball_radius, ball.y)
            else:
                ball.set_pos(rect.right + ball_radius, ball.y)
            return [norm_vel_cords[0] * abs(ball.x_vel), ball.y_vel]
        case 1:
            if dist_arr[0] == 1:
                if norm_cords[0] == -1:
                    ball.set_pos(rect.left - ball_radius, ball.y)
                else:
                    ball.set_pos(rect.right + ball_radius, ball.y)
                return [-norm_vel_cords[0] * abs(ball.x_vel), ball.y_vel]
            else:
                if norm_cords[1] == -1:
                    ball.set_pos(ball.x, rect.top - ball_radius)
                else:
                    ball.set_pos(ball.x, rect.bottom + ball_radius)
                return [ball.x_vel, -norm_vel_cords[1] * abs(ball.y_vel)]
        case 2:
            if abs(ball.x_vel) > .1:
                m = ball.y_vel / ball.x_vel
            else:
                if norm_vel_cords[1] == 1:
                    ball.set_pos(ball.x, rect.top - ball_radius)
                    return [ball.x_vel, -abs(ball.y_vel)]
                else:
                    ball.set_pos(ball.x, rect.bottom + ball_radius)
                    return [ball.x_vel, abs(ball.y_vel)]

            match norm_vel_cords:
                case [1, 1]:
                    if m * (rect.left - ball.x) + ball.y > rect.top:
                        ball.set_pos(rect.left - ball_radius, ball.y)
                        return [-abs(ball.x_vel), ball.y_vel]
                    else:
                        ball.set_pos(ball.x, rect.top - ball_radius)
                        return [ball.x_vel, -abs(ball.y_vel)]
                case [-1, 1]:
                    if m * (rect.right - ball.x) + ball.y < rect.top:
                        ball.set_pos(ball.x, rect.top - ball_radius)
                        return [ball.x_vel, -abs(ball.y_vel)]
                    else:
                        ball.set_pos(rect.right + ball_radius, ball.y)
                        return [abs(ball.x_vel), ball.y_vel]
                case [1, -1]:
                    if m * (rect.left - ball.x) + ball.y > rect.bottom:
                        ball.set_pos(ball.x, rect.bottom + ball_radius)
                        return [ball.x_vel, abs(ball.y_vel)]
                    else:
                        ball.set_pos(rect.left - ball_radius, ball.y)
                        return [-abs(ball.x_vel), ball.y_vel]
                case [-1, -1]:
                    if m * (rect.right - ball.x) + ball.y > rect.bottom:
                        ball.set_pos(ball.x, rect.bottom + ball_radius)
                        return [ball.x_vel, abs(ball.y_vel)]
                    else:
                        ball.set_pos(rect.right + ball_radius, ball.y)
                        return [abs(ball.x_vel), ball.y_vel]


# Takes the coordinates of the platform and decides whether to spawn a powerup using the random module. "long platform"
# will increase the platform width, and "extra "ball" will spawn another ball at the platforms location
def spawn_powerup(x_pos, y_pos, speed):
    # determines whether to spawn powerup
    if random.randint(0, 10) > 10 - powerup_chance:

        # randomly chooses which powerup from "powerup_choices" to spawn
        choice = random.choice(powerup_choices)
        if choice == "extra ball":
            # adds a ball to the game at the platform's position
            balls.append(Ball(x_pos, y_pos - platform.height / 2 - ball_radius, 0, -speed))
        if choice == "long platform":

            # increases the platform width
            platform.rect.width += 5
            platform.width += 5

            # if the platform width has increased beyond half of the screen's width, the platform's width is set to half
            # the screen width
            if platform.width > screen_dimensions[0] / 2:
                platform.set_width(screen_dimensions[0] / 2)


# adds a score to the "Endless-High-Scores" file and organizes the file with the top ten scores from highest to lowest
def add_high_score(added_score: int):
    scores_file = open("Endless-High-Scores", "r")

    # puts the scores in the "Endless-High-Scores" in the "scores" array
    scores = []
    for line in scores_file:
        string = ""
        for char in line:
            if char in "1234567890":
                string += char
        if string != "":
            scores.append(int(string))

    # adds the "added_score" to the "scores" array
    if added_score >= 0:
        scores.append(added_score)

    # organizes the array with the scores going from highest on the left to lowest on the right
    scores.sort()
    scores.reverse()

    # isolates the top ten scores from the "scores" array
    if len(scores) <= 10:
        top_ten_scores = scores
    else:
        top_ten_scores = scores[:10]

    scores_file.close()

    # re-writes the reorganized high scores in the "Endless-High-Scores" file
    scores_file = open("Endless-High-Scores", "w")
    for number in top_ten_scores:
        scores_file.write(str(number) + "\n")
    scores_file.close()

    return scores


# spawns the bricks associated with each level normal or custom and adds the rect objects and colors to the "bricks"
# array
def level_spawn_bricks(round_num, is_custom):
    # determines whether the level is custom or normal and gets the text from the file
    if is_custom:
        inter = "Custom"
    else:
        inter = ""
    string = get_file_text("Maps/" + inter + "Level-" + str(round_num))

    # turns the text received from the level file into an array of the corresponding descriptive characters
    brick_arr = tuple(char for char in string if char != "\n")

    # fills the "res" array with each existing brick and its associated color
    res = []
    row = 0
    for i, index in enumerate(brick_arr):
        if index != "e":
            index = int(index)
            color = colors[index]
            res.append((pygame.Rect([i % 8 * block_width + 1, row * block_height + 1],
                                    [block_width - 2, block_height - 2]), color))
        if (i + 1) % 8 == 0:
            row += 1

    return res


# returns an array of randomly generated bricks
def random_spawn_bricks():
    res = []

    # determines how many layers of bricks there will be
    num_layers = random.randint(1, max_level_height)

    # places bricks from left to right and top to bottom
    for layer in range(num_layers * 8):
        color = random.randint(-3, 9)

        # if the "color" index is negative, no brick is added at the current location
        if color >= 0:
            res.append((pygame.Rect([layer % 8 * block_width + 1, layer // 8 * block_height + 1],
                                    [block_width - 2, block_height - 2]), colors[color]))

    return res


# displays a string on the screen. for every "\n" in the "msg", the display will display teh rest of the text on the
# next line.
def render_message(surface: pygame.surface, msg: str, position: [int, int], font_size: int):
    # fills the "splits" array with each chunk of text in between "\n" characters
    splits = []
    temp = 0
    for i, char in enumerate(msg):
        if char == "\n":
            splits.append(msg[temp:i])
            temp = i + 1
    splits.append(msg[temp:])

    # renders each chunk of text on its own line
    for i, split in enumerate(splits):
        font = pygame.font.Font(None, font_size)
        title = font.render(split, True, (255, 255, 255))
        title_rect = title.get_rect()
        title_rect.center = (position[0], position[1] + i * font_size)
        surface.blit(title, title_rect.topleft)


# renders an image from the "path" parameter on the screen and scales it according to the scale "parameter"
def render_image(surface: pygame.surface, path: str, position: [int, int], scale: [int, int]):
    img = pygame.image.load(path).convert()
    img = pygame.transform.scale(img, scale)
    surface.blit(img, (position[0] - scale[0] / 2, position[1] - scale[1] / 2))
    return img


# returns all the text in the file specified in a single string
def get_file_text(file_path: str):
    file = open(file_path, "r")
    res = ""
    for line in file:
        res += line
    file.close()
    return res


# returns a 2D array of the brick info associated with each brick space for the file given
def get_edit_brick_placeholders(custom_file_num: int):
    file_text = get_file_text(f"Maps/CustomLevel-{custom_file_num}")
    chars = [char for char in file_text if char != "\n"]
    res = [[chars[j * 8 + i] for j in range(max_level_height)] for i in range(8)]
    return res


# gets an array of all bricks and their colors to render on the screen when the user is editing a level
def get_render_bricks(placeholders):
    res = []
    for y in range(max_level_height):
        for x in range(8):
            if placeholders[x][y] != "e":
                res.append((pygame.Rect(x * block_width + 1, y * block_height + 1, block_width - 2, block_height - 2),
                            int(placeholders[x][y])))
    return res


def loop_music(path: str):
    pygame.mixer.music.unload()
    pygame.mixer.music.load(path)
    pygame.mixer.music.play(-1)


# entity info
#########################################################
ball_speed = 6
balls = [Ball(0, 0, 0, 0), ]
platform = Platform(175, screen_dimensions[1] * 15 / 16,
                    default_platform_dimensions[0], default_platform_dimensions[1],
                    platform_speed)
edit_brick_placeholders = [["e" for i in range(max_level_height)] for j in range(8)]
render_bricks = []
#########################################################

# score and round information
#########################################################
current_round = 1
score = 0
total_score = 0
max_round_score = current_round * 8
current_color = 0
#########################################################

# sounds
#########################################################
brick_impact = pygame.mixer.Sound("SoundFiles/brick-impact.wav")
platform_impact = pygame.mixer.Sound("SoundFiles/platform-impact.wav")
win = pygame.mixer.Sound("SoundFiles/win.wav")
#########################################################

# game state booleans to determine what chunk of code to run
loop_music("SoundFiles/menu-background.wav")
game_state = "title"
endless = False
custom = False
selecting_level_to_edit = False
high_score = False
can_click = True

while game_state != "off":
    clicked = False
    if pygame.mouse.get_pressed(3)[0]:
        if can_click:
            clicked = True
            can_click = False
    else:
        can_click = True
        clicked = False

    mouse_pos = pygame.mouse.get_pos()
    keys = pygame.key.get_pressed()
    screen.fill((0, 0, 0))

    # quits the game when the user pressed the "X" button or the escape key
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_state = "off"
    if keys[pygame.K_ESCAPE]:
        game_state = "off"

    # events if a game has started
    match game_state:
        case "level creator":
            # displays intermediate screen where the user can decide which custom level to edit
            if selecting_level_to_edit:
                render_message(screen, "Choose a level to edit (1-10) by\npressing the number keys.",
                               (screen_center_x, screen_center_y - 0), 32)

                exit_level_creator_rect = render_image(screen, "assets/Exit.png",
                                                       (screen_center_x, 600), (200, 50)).get_rect()
                exit_level_creator_rect.center = (screen_center_x, 600)

                if exit_level_creator_rect.collidepoint(mouse_pos) and clicked:
                    game_state = "title"

                # When the user presses a number key, begins editing the custom level associated with it
                #########################################################
                if keys[pygame.K_1]:
                    selecting_level_to_edit = False
                    editing_level = 1
                    edit_brick_placeholders = get_edit_brick_placeholders(1)
                    render_bricks = get_render_bricks(edit_brick_placeholders)
                if keys[pygame.K_2]:
                    selecting_level_to_edit = False
                    editing_level = 2
                    edit_brick_placeholders = get_edit_brick_placeholders(2)
                    render_bricks = get_render_bricks(edit_brick_placeholders)
                if keys[pygame.K_3]:
                    selecting_level_to_edit = False
                    editing_level = 3
                    edit_brick_placeholders = get_edit_brick_placeholders(3)
                    render_bricks = get_render_bricks(edit_brick_placeholders)
                if keys[pygame.K_4]:
                    selecting_level_to_edit = False
                    editing_level = 4
                    edit_brick_placeholders = get_edit_brick_placeholders(4)
                    render_bricks = get_render_bricks(edit_brick_placeholders)
                if keys[pygame.K_5]:
                    selecting_level_to_edit = False
                    editing_level = 5
                    edit_brick_placeholders = get_edit_brick_placeholders(5)
                    render_bricks = get_render_bricks(edit_brick_placeholders)
                if keys[pygame.K_6]:
                    selecting_level_to_edit = False
                    editing_level = 6
                    edit_brick_placeholders = get_edit_brick_placeholders(6)
                    render_bricks = get_render_bricks(edit_brick_placeholders)
                if keys[pygame.K_7]:
                    selecting_level_to_edit = False
                    editing_level = 7
                    edit_brick_placeholders = get_edit_brick_placeholders(7)
                    render_bricks = get_render_bricks(edit_brick_placeholders)
                if keys[pygame.K_8]:
                    selecting_level_to_edit = False
                    editing_level = 8
                    edit_brick_placeholders = get_edit_brick_placeholders(8)
                    render_bricks = get_render_bricks(edit_brick_placeholders)
                if keys[pygame.K_9]:
                    selecting_level_to_edit = False
                    editing_level = 9
                    edit_brick_placeholders = get_edit_brick_placeholders(9)
                    render_bricks = get_render_bricks(edit_brick_placeholders)
                if keys[pygame.K_0]:
                    selecting_level_to_edit = False
                    editing_level = 10
                    edit_brick_placeholders = get_edit_brick_placeholders(10)
                    render_bricks = get_render_bricks(edit_brick_placeholders)
                #########################################################

            else:
                # establishes the lowest y level at which bricks can be placed
                y_limit = block_height * max_level_height

                # displays information for how to edit the level
                #########################################################
                pygame.draw.line(screen, "red", (0, y_limit),
                                 (screen_dimensions[0], y_limit), 1)
                render_message(screen, f"Editing Level {editing_level}",
                               (screen_center_x, y_limit + 20), 32)
                render_message(screen, "Press the number keys to change the color.",
                               (screen_center_x, y_limit + 50), 20)
                render_message(screen, "Press \"S\" to save level.",
                               (screen_center_x, y_limit + 70), 20)
                render_message(screen, "Press \"E\" to erase.",
                               (screen_center_x, y_limit + 90), 20)
                render_message(screen, "Press \"C\" to clear screen.",
                               (screen_center_x, y_limit + 110), 20)
                render_message(screen, "Press \"Enter\" to go back without saving.",
                               (screen_center_x, y_limit + 130), 20)
                render_message(screen, "Use the mouse to place bricks of the current color above the\nred line.",
                               (screen_center_x, y_limit + 150), 20)
                render_message(screen, "Current color: ",
                               (screen_center_x - 30, screen_dimensions[1] - 110), 20)
                #########################################################

                # displays the current color or eraser depending on what the user is using
                if current_color != "e":
                    pygame.draw.rect(screen, colors[current_color], [240, 630, 25, 25])
                else:
                    render_image(screen, "assets/Eraser.png", (245, 635), (25, 25))

                # invisible rectangle on the area where bricks can be placed
                place_rect = pygame.Rect(0, 0, block_width * 8, block_height * max_level_height)

                # changes the working color if the user pressed a number key
                #########################################################
                if keys[pygame.K_1]:
                    current_color = 0
                if keys[pygame.K_2]:
                    current_color = 1
                if keys[pygame.K_3]:
                    current_color = 2
                if keys[pygame.K_4]:
                    current_color = 3
                if keys[pygame.K_5]:
                    current_color = 4
                if keys[pygame.K_6]:
                    current_color = 5
                if keys[pygame.K_7]:
                    current_color = 6
                if keys[pygame.K_8]:
                    current_color = 7
                if keys[pygame.K_9]:
                    current_color = 8
                if keys[pygame.K_0]:
                    current_color = 9
                #########################################################

                # switches to eraser mode if the user presses "e"
                if keys[pygame.K_e]:
                    current_color = "e"

                # clears screen if user presses "c"a
                if keys[pygame.K_c]:
                    render_bricks = []
                    edit_brick_placeholders = [["e" for i in range(max_level_height)] for j in range(8)]

                # returns to level edit selection without saving if the user presses "Enter"
                if keys[pygame.K_RETURN]:
                    selecting_level_to_edit = True

                # saves the level the user has created if the user presses "s"
                if keys[pygame.K_s]:
                    selecting_level_to_edit = True
                    level_file = open(f"Maps/CustomLevel-{editing_level}", "w")
                    to_write = ""
                    for y in range(max_level_height):
                        for x in range(8):
                            to_write += str(edit_brick_placeholders[x][y])
                        to_write += "\n"
                    level_file.write(to_write)
                    level_file.close()
                    edit_brick_placeholders = [["e" for i in range(max_level_height)] for j in range(8)]
                    render_bricks = []

                # if the user has clicked within the placement area, a brick is created with the current color at the
                # location of the click
                if pygame.mouse.get_pressed(3)[0] and place_rect.collidepoint(mouse_pos):
                    x = int(mouse_pos[0] // block_width)
                    y = int(mouse_pos[1] // block_height)

                    edit_brick_placeholders[x][y] = current_color
                    render_bricks.append((pygame.Rect(x * block_width + 1, y * block_height + 1,
                                                      block_width - 2, block_height - 2), current_color))

                # displays the bricks that have been placed
                for brick in render_bricks:
                    if brick[1] == "e":
                        pygame.draw.rect(screen, "black", brick[0])
                    else:
                        pygame.draw.rect(screen, colors[brick[1]], brick[0])

        case "round running":
            if keys[pygame.K_p]:
                game_state = "paused"

            # updates ball and platform positions, handles collisions, and draws objects on screen
            #########################################################
            platform.player_move(keys)
            for ball in balls:
                ball.update_pos()
                if ball.rect.colliderect(platform.rect):
                    platform_impact.play()
                    ball.handle_rect_bounce(platform.rect, "platform")
                collided = False
                for brick in bricks:
                    if brick[0].colliderect(ball.rect):
                        brick_impact.play()
                        collided = True
                        spawn_powerup(platform.rect.centerx, platform.rect.centery, ball_speed)
                        ball.handle_rect_bounce(brick[0])
                        if brick in bricks:
                            bricks.remove(brick)
                            score += 1
                            total_score += 1
                    if collided:
                        break
                    else:
                        pygame.draw.rect(screen, brick[1], brick[0])
                if ball.y > screen_dimensions[1]:
                    balls.remove(ball)
                else:
                    ball.draw(screen)
            platform.draw(screen)
            #########################################################

            # progresses level
            #########################################################
            if score >= max_round_score:
                platform.reset()
                score = 0
                current_round += 1
                game_state = "pre round"

                balls = [balls[0]]
                if current_round > 10:
                    win.play()
                    game_state = "win screen"
                    pygame.mixer.music.unload()
                else:
                    if endless:
                        bricks = random_spawn_bricks()
                        max_round_score = len(bricks)
                    elif not custom:
                        max_round_score += 8
                        bricks = level_spawn_bricks(current_round, custom)
                    else:
                        bricks = level_spawn_bricks(current_round, custom)
                        max_round_score = len(bricks)
            #########################################################

            # player loses game if there are no more balls
            if len(balls) == 0:
                if endless:
                    scores = add_high_score(total_score)
                    if total_score in scores:
                        high_score = True
                    else:
                        high_score = False
                game_state = "lose screen"

            # displays score
            render_message(screen, f"Score: {total_score}", (100, screen_dimensions[1] - 15), 32)

        case "pre round":   # allows the user to move the platform and launch the ball to start the round
            render_message(screen, "Press \"Space\" to to launch ball.", (screen_center_x, screen_center_y + 45), 32)
            render_message(screen, f"Score: {total_score}", (100, screen_dimensions[1] - 15), 32)

            platform.player_move(keys)

            balls[0].x = platform.rect.centerx
            balls[0].y = platform.rect.top - ball_radius

            # launches the ball when the user presses space
            if keys[pygame.K_SPACE]:
                game_state = "round running"
                balls[0].x_vel = 0
                balls[0].y_vel = -ball_speed

            platform.draw(screen)
            balls[0].draw(screen)
            for brick in bricks:
                pygame.draw.rect(screen, brick[1], brick[0])

        case "level select":
            # displays buttons and positions rect objects to detect when the buttons are clicked
            #########################################################
            render_message(screen, "Select a mode", (screen_center_x, 100), 64)
            custom_levels_rect = render_image(screen, "assets/Custom-Levels.png",
                                              (screen_center_x, screen_center_y + 50), (200, 50)).get_rect()
            custom_levels_rect.center = (screen_center_x, screen_center_y + 50)

            normal_levels_rect = render_image(screen, "assets/Normal-Levels.png",
                                              (screen_center_x, screen_center_y - 50), (200, 50)).get_rect()
            normal_levels_rect.center = (screen_center_x, screen_center_y - 50)

            exit_level_select_rect = render_image(screen, "assets/Exit.png",
                                              (screen_center_x, 600), (200, 50)).get_rect()
            exit_level_select_rect.center = (screen_center_x, 600)
            #########################################################

            # switches the game state based on which (if any) button the user presses
            #########################################################
            if exit_level_select_rect.collidepoint(mouse_pos) and clicked:
                game_state = "title"
            if custom_levels_rect.collidepoint(mouse_pos) and clicked:
                loop_music("SoundFiles/level-background.mp3")
                game_state = "pre round"
                custom = True
                bricks = level_spawn_bricks(current_round, custom)
                max_round_score = len(bricks)
            if normal_levels_rect.collidepoint(mouse_pos) and clicked:
                loop_music("SoundFiles/level-background.mp3")
                game_state = "pre round"
                custom = False
                bricks = level_spawn_bricks(current_round, custom)
            #########################################################

        case "paused":
            platform.draw(screen)
            for ball in balls:
                ball.draw(screen)
            for brick in bricks:
                pygame.draw.rect(screen, brick[1], brick[0])

            render_message(screen, "Press \"Enter\" to unpause.", (screen_center_x, screen_center_y - 15), 32)
            render_message(screen, "Press \"Space\" to go to title", (screen_center_x, screen_center_y + 15), 32)
            render_message(screen, f"Score: {total_score}", (100, screen_dimensions[1] - 15), 32)

            if keys[pygame.K_RETURN]:
                game_state = "round running"
            if keys[pygame.K_SPACE]:
                balls = [balls[0]]
                game_state = "title"
                loop_music("SoundFiles/menu-background.wav")
                platform.reset()

        case "title":  # events if the player is on the title screen

            # renders buttons and images and positions rect objects to detect when a button is pressed
            #########################################################
            render_image(screen, "assets/title-screen.png", (screen_center_x + 70, screen_center_y + 110),
                         screen_dimensions)
            play_levels_rect = render_image(screen, "assets/Play-Levels.png",
                                            (screen_center_x, screen_center_y - 120), (200, 50)).get_rect()
            play_levels_rect.center = (screen_center_x, screen_center_y - 120)

            play_endless_rect = render_image(screen, "assets/Play-Endless.png",
                                             (screen_center_x, screen_center_y - 50), (200, 50)).get_rect()
            play_endless_rect.center = (screen_center_x, screen_center_y - 50)

            level_creator_rect = render_image(screen, "assets/Level-Creator.png",
                                              (screen_center_x, screen_center_y + 20), (200, 50)).get_rect()
            level_creator_rect.center = (screen_center_x, screen_center_y + 20)

            high_scores_rect = render_image(screen, "assets/High-Scores.png",
                                            (screen_center_x, screen_center_y + 90), (200, 50)).get_rect()
            high_scores_rect.center = (screen_center_x, screen_center_y + 90)

            info_rect = render_image(screen, "assets/Info.png",
                                     (screen_center_x, screen_center_y + 160), (200, 50)).get_rect()
            info_rect.center = (screen_center_x, screen_center_y + 160)

            quit_rect = render_image(screen, "assets/Quit.png", (screen_center_x, screen_center_y + 230),
                                     (200, 50)).get_rect()
            quit_rect.center = (screen_center_x, screen_center_y + 230)
            #########################################################

            render_message(screen, "Atari Breakout", [screen_center_x, 100], 64)

            # Detects if the player has hit any of the buttons and if so, switches the game state
            #########################################################
            if play_levels_rect.collidepoint(mouse_pos) and clicked:
                game_state = "level select"
                score = 0
                total_score = 0
                current_round = 1
                endless = False
            if play_endless_rect.collidepoint(mouse_pos) and clicked:
                loop_music("SoundFiles/level-background.mp3")
                game_state = "pre round"
                bricks = random_spawn_bricks()
                score = 0
                total_score = 0
                current_round = 1
                max_round_score = len(bricks)
                endless = True
            if high_scores_rect.collidepoint(mouse_pos) and clicked:
                game_state = "leaderboard"
            if info_rect.collidepoint(mouse_pos) and clicked:
                game_state = "info"
            if quit_rect.collidepoint(mouse_pos) and clicked:
                game_state = "off"
            if level_creator_rect.collidepoint(mouse_pos) and clicked:
                game_state = "level creator"
                selecting_level_to_edit = True
            #########################################################

        case "win screen" | "lose screen":
            exit_game_end_rect = render_image(screen, "assets/Exit.png",
                                              (screen_center_x, 600), (200, 50)).get_rect()
            exit_game_end_rect.center = (screen_center_x, 600)

            if exit_game_end_rect.collidepoint(mouse_pos) and clicked:
                platform.reset()
                loop_music("SoundFiles/menu-background.wav")
                game_state = "title"
                balls = [Ball(0, 0, 0, 0), ]

            if endless:
                render_message(screen, "GAME OVER", screen_center, 64)
                if high_score:
                    render_message(screen, f"High score of {total_score}!", (screen_center[0], screen_center[1] + 60), 64)
            else:
                render_message(screen, f"YOU {game_state[:4].upper()}", screen_center, 64)

        case "leaderboard":
            # gets scores from the "Endless-High_Scores" file and displays them on the screen
            #########################################################
            scores = add_high_score(-1)
            message = ""
            for i, num in enumerate(scores):
                message += f"{i + 1}:        {num}\n"
            message = message[:len(message) - 1]
            render_message(screen, "High Scores:", (screen_center_x, 100), 64)
            render_message(screen, message, (screen_center_x, screen_center_y - 150), 32)
            #########################################################

            exit_leaderboard_rect = render_image(screen, "assets/Exit.png",
                                              (screen_center_x, 600), (200, 50)).get_rect()
            exit_leaderboard_rect.center = (screen_center_x, 600)

            if exit_leaderboard_rect.collidepoint(mouse_pos) and clicked:
                game_state = "title"

        case "info":
            render_message(screen, "How to play.", (screen_center_x, 100), 64)
            render_message(screen, info,(screen_center_x, 160), 20)

            exit_info_rect = render_image(screen, "assets/Exit.png",
                                          (screen_center_x, 600), (200, 50)).get_rect()
            exit_info_rect.center = (screen_center_x, 600)

            if exit_info_rect.collidepoint(mouse_pos) and clicked:
                game_state = "title"

    pygame.display.flip()
    dt = clock.tick(60)
