from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math





# Button constants
BUTTON_WIDTH = 0.245
BUTTON_HEIGHT = 0.15
BUTTON_SPACING = 0.05
SCREEN_WIDTH = 2.666  # Adjusted for OpenGL coordinates (-1.333 to 1.333)
SCREEN_HEIGHT = 2.0   # Adjusted for OpenGL coordinates (-1.0 to 1.0)

# Button positions
# Button positions (adjusted to avoid overlap with score and life text)
# Button positions (adjusted to avoid overlap with helicopter)
restart_button_x = -1.333 + BUTTON_SPACING
restart_button_y = 1.0 - BUTTON_HEIGHT - BUTTON_SPACING + 0.1  # Adjusted up
pause_button_x = -BUTTON_WIDTH / 2
pause_button_y = 1.0 - BUTTON_HEIGHT - BUTTON_SPACING + 0.1  # Adjusted up
exit_button_x = 1.333 - BUTTON_WIDTH - BUTTON_SPACING
exit_button_y = 1.0 - BUTTON_HEIGHT - BUTTON_SPACING + 0.1  # Adjusted up


# Button colors
TEAL = (0.0, 0.5, 0.5)
AMBER = (1.0, 0.75, 0.0)
RED = (1.0, 0.0, 0.0)
WHITE = (1.0, 1.0, 1.0)

game_paused = False  # Add this near other global variables

# Game variables

bullets = []  # List to store active bullets
bullet_fire_timer = 0  # Timer to track firing intervals
bullet_fire_interval = 60  # Interval for firing bullets (2-3 seconds at 60 FPS)
bullet_fire_direction = 1  # 1 for straight down, -1 for random direction
lives = 3  # Number of lives the player starts with



# Rain variables
raindrops = []
num_raindrops = 100  # Adjust for density
rain_direction = 1  # Direction of the rain (1 for right, -1 for left)
is_raining = False  # Toggle for rain effect




window_width = 800
window_height = 450  
player_x = -0.8
player_y = -0.8
player_size = 0.1
player_jump_speed = 0.07
player_vertical_velocity = 0
gravity = -0.002
is_jumping = False
buildings = []
building_spawn_timer = 0
building_spawn_interval = 60  
building_speed = 0.01
game_running = True


helicopter_x = 1.0
helicopter_y = 0.7
helicopter_speed = 0.02
helicopter_width = 0.2
helicopter_height = 0.1


coins = []
coin_spawn_timer = 0
coin_spawn_interval = 50  
coin_size = 0.05
score = 0

special_coin_spawn_interval = coin_spawn_interval * 2  # Half the frequency of normal coins
special_coin_timer = 0  # Timer for special coin spawning
special_coins = []  # List to store special coins



#----------------------------------------------
import random  # Ensure you have imported this for generating random angles

class Bullet:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.size = 0.02
        self.speed = 0.02
        self.angle = angle  # Angle of bullet's trajectory

    def draw(self):
        glColor3f(1.0, 0.0, 0.0)  # Red color for the bullet
        glBegin(GL_POINTS)
        for i in range(int(self.size * 100)):
            for j in range(int(self.size * 100)):
                glVertex2f(self.x + (i / 100.0), self.y - (j / 100.0))
        glEnd()

    def update(self):
        self.x += self.speed * math.cos(math.radians(self.angle))
        self.y -= self.speed * math.sin(math.radians(self.angle))

    def is_off_screen(self):
        return self.y < -1.0 or self.x < -1.333 or self.x > 1.333  # Check screen boundaries



class AABB:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def collides_with(self, other):
        return (self.x < other.x + other.width and
                self.x + self.width > other.x and
                self.y < other.y + other.height and
                self.y + self.height > other.y)
    


# Button AABBs
restart_button_aabb = AABB(restart_button_x, restart_button_y, BUTTON_WIDTH, BUTTON_HEIGHT)
pause_button_aabb = AABB(pause_button_x, pause_button_y, BUTTON_WIDTH, BUTTON_HEIGHT)
exit_button_aabb = AABB(exit_button_x, exit_button_y, BUTTON_WIDTH, BUTTON_HEIGHT)



#---------------------------------------------


def draw_coin(x, y, radius, color):
    
    glColor3f(*color)
    glPointSize(2)  
    glBegin(GL_POINTS)
    for i in range(360):  
        angle = math.radians(i)
        x_offset = radius * math.cos(angle)
        y_offset = radius * math.sin(angle)
        glVertex2f(x + x_offset, y + y_offset)
    glEnd()

def reset_game():
    global score, lives, player_x, player_y, is_jumping, player_vertical_velocity, bullets, buildings, coins, special_coins, game_running

    # Reset score and lives
    score = 0
    lives = 3

    # Reset player position and velocity
    player_x = -0.8
    player_y = -0.8
    is_jumping = False
    player_vertical_velocity = 0

    # Clear active bullets, buildings, coins, and special coins
    bullets.clear()
    buildings.clear()
    coins.clear()
    special_coins.clear()

    # Spawn the initial building for the new round
    spawn_initial_building()

    # Ensure the game is running
    game_running = True


def mouse_callback(button, state, x, y):
    global game_running, game_paused

    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        # Convert screen coordinates to OpenGL coordinates
        gl_x = (x / window_width) * 2.666 - 1.333
        gl_y = 1.0 - (y / window_height) * 2.0

        # Check if the restart button is clicked
        if restart_button_aabb.collides_with(AABB(gl_x, gl_y, 0, 0)):
            reset_game()  # Reset the game
        # Check if the pause button is clicked
        elif pause_button_aabb.collides_with(AABB(gl_x, gl_y, 0, 0)):
            game_paused = not game_paused  # Toggle pause state
        # Check if the exit button is clicked
        elif exit_button_aabb.collides_with(AABB(gl_x, gl_y, 0, 0)):
            glutLeaveMainLoop()

        # Force the display to refresh
        glutPostRedisplay()


class Building:
    def __init__(self, x, width, height):
        self.x = x
        self.width = width
        self.height = height

    def draw(self):
        glColor3f(0.2, 0.2, 0.2)  
        glPointSize(2)  
        glBegin(GL_POINTS)  
        for i in range(int(self.width * 100)):  
            for j in range(int(self.height * 100)):  
                x = self.x + i / 100.0  
                y = -1.0 + j / 100.0  
                glVertex2f(x, y)
        glEnd()


    def update(self):
        self.x -= building_speed

    def is_off_screen(self):
        return self.x + self.width < -1.333  

def spawn_initial_building():
    global buildings, player_x, player_y
    x = player_x - 0.2  # Adjust the x position so the player starts on top
    width = 0.4  # Fixed width for the first building
    height = 0.5  # Height that ensures the player is positioned correctly
    buildings.append(Building(x, width, height))
    player_y = -1.0 + height  # Place the player on top of the first building


def raindrop():
    global raindrops
    raindrops = []
    for _ in range(num_raindrops):
        x = random.uniform(-1.333, 1.333)  # Adjusted for screen width
        y = random.uniform(-1.0, 1.0)  # Full screen height
        raindrops.append({'x': x, 'y': y})

def draw_raindrops():
    glColor3f(0.8, 0.8, 1.0)  # Light blue for raindrops
    glBegin(GL_LINES)
    for drop in raindrops:
        glVertex2f(drop['x'], drop['y'])  # Start of raindrop
        glVertex2f(drop['x'] + rain_direction * 0.002, drop['y'] - 0.05)  # End of raindrop
    glEnd()

def raindrops_effect():
    global raindrops
    for drop in raindrops:
        drop['y'] -= 0.02  # Falling speed
        drop['x'] += rain_direction * 0.001  # Drift direction
        if drop['y'] < -1.0:  # Reset raindrop to the top
            drop['y'] = random.uniform(0.0, 1.0)
            drop['x'] = random.uniform(-1.333, 1.333)


class Coin:
    def __init__(self, x, y, is_special=False):
        self.x = x
        self.y = y
        self.is_special = is_special  # Flag to indicate if it's a special coin

    def draw(self):
        if self.is_special:
            color = (0.0, 1.0, 0.0)  # Bright green for special coins
        else:
            color = (1.0, 1.0, 0.0)  # Yellow for regular coins
        draw_coin(self.x, self.y, coin_size, color)

    def update(self):
        self.x -= building_speed

    def is_off_screen(self):
        return self.x + coin_size < -1.333  

    def is_collected(self):
        return (player_x + player_size > self.x - coin_size and
                player_x < self.x + coin_size and
                player_y + player_size > self.y - coin_size and
                player_y < self.y + coin_size)


def spawn_special_coin():
    x = 1.0
    y = random.uniform(-0.6, 0.8)

    # Ensure the special coin does not overlap with the helicopter
    while helicopter_x - 0.1 <= x <= helicopter_x + helicopter_width + 0.1 and \
          helicopter_y - 0.1 <= y <= helicopter_y + helicopter_height + 0.1:
        y = random.uniform(-0.6, 0.8)  # Generate a new y-coordinate

    special_coins.append(Coin(x, y, is_special=True))  # Add the special coin

def draw_player():
    # Head dimensions
    head_size = player_size / 2

    # Body dimensions
    body_width = player_size / 3
    body_height = player_size

    # Arms dimensions
    arm_width = player_size / 5
    arm_height = player_size / 1.5

    # Legs dimensions
    leg_width = player_size / 4
    leg_height = player_size / 1.2

    # Adjust the player's position for better visibility
    offset_x = player_x + (player_size / 2) - (body_width / 2)
    offset_y = player_y + player_size / 2

    # Draw the head (circle)
    glColor3f(1.0, 0.6, 0.6)  # Light peach for skin
    glBegin(GL_POINTS)
    for i in range(int(head_size * 100)):
        for j in range(int(head_size * 100)):
            x = offset_x + (i / 100.0) - head_size / 2
            y = offset_y + player_size + (j / 100.0)
            if (x - offset_x) ** 2 + (y - (offset_y + player_size + head_size / 2)) ** 2 <= (head_size / 2) ** 2:
                glVertex2f(x, y)
    glEnd()

    # Draw the body (rectangle)
    glColor3f(0.2, 0.5, 0.8)  # Bright blue for body
    glBegin(GL_POINTS)
    for i in range(int(body_width * 100)):
        for j in range(int(body_height * 100)):
            x = offset_x + (i / 100.0)
            y = offset_y + (j / 100.0)
            glVertex2f(x, y)
    glEnd()

    # Draw the left arm (rectangle)
    glColor3f(1.0, 0.6, 0.6)  # Same skin color for arms
    glBegin(GL_POINTS)
    for i in range(int(arm_width * 100)):
        for j in range(int(arm_height * 100)):
            x = offset_x - arm_width + (i / 100.0)
            y = offset_y + (j / 100.0)
            glVertex2f(x, y)
    glEnd()

    # Draw the right arm (rectangle)
    glColor3f(1.0, 0.6, 0.6)  # Same skin color for arms
    glBegin(GL_POINTS)
    for i in range(int(arm_width * 100)):
        for j in range(int(arm_height * 100)):
            x = offset_x + body_width + (i / 100.0)
            y = offset_y + (j / 100.0)
            glVertex2f(x, y)
    glEnd()

    # Draw the left leg (rectangle)
    glColor3f(0.2, 0.8, 0.2)  # Bright green for legs
    glBegin(GL_POINTS)
    for i in range(int(leg_width * 100)):
        for j in range(int(leg_height * 100)):
            x = offset_x + (i / 100.0)
            y = offset_y - (j / 100.0)
            glVertex2f(x, y)
    glEnd()

    # Draw the right leg (rectangle)
    glColor3f(0.2, 0.8, 0.2)  # Bright green for legs
    glBegin(GL_POINTS)
    for i in range(int(leg_width * 100)):
        for j in range(int(leg_height * 100)):
            x = offset_x + body_width - leg_width + (i / 100.0)
            y = offset_y - (j / 100.0)
            glVertex2f(x, y)
    glEnd()

    # Add eyes (small circles on the head)
    eye_size = head_size / 8
    eye_y = offset_y + player_size + head_size / 3
    glColor3f(0.0, 0.0, 0.0)  # Black for eyes
    glBegin(GL_POINTS)
    for i in range(int(eye_size * 100)):
        for j in range(int(eye_size * 100)):
            x_left = offset_x - head_size / 4 + (i / 100.0)
            y_left = eye_y + (j / 100.0)
            if (x_left - (offset_x - head_size / 4)) ** 2 + (y_left - eye_y) ** 2 <= (eye_size) ** 2:
                glVertex2f(x_left, y_left)

            x_right = offset_x + head_size / 4 + (i / 100.0)
            y_right = eye_y + (j / 100.0)
            if (x_right - (offset_x + head_size / 4)) ** 2 + (y_right - eye_y) ** 2 <= (eye_size) ** 2:
                glVertex2f(x_right, y_right)
    glEnd()


    







    # Draw the body (rectangle)
    glColor3f(0.0, 0.0, 1.0)  # Blue color for body
    glBegin(GL_POINTS)
    for i in range(int(body_width * 100)):
        for j in range(int(body_height * 100)):
            x = player_x + (player_size / 4) + (i / 100.0)
            y = player_y + (j / 100.0)
            glVertex2f(x, y)
    glEnd()

    # Draw the left arm (rectangle)
    glColor3f(1.0, 0.8, 0.6)  # Skin color
    glBegin(GL_POINTS)
    for i in range(int(arm_width * 100)):
        for j in range(int(arm_height * 100)):
            x = player_x + (i / 100.0)
            y = player_y + (player_size / 2) + (j / 100.0)
            glVertex2f(x, y)
    glEnd()

    # Draw the right arm (rectangle)
    glColor3f(1.0, 0.8, 0.6)  # Skin color
    glBegin(GL_POINTS)
    for i in range(int(arm_width * 100)):
        for j in range(int(arm_height * 100)):
            x = player_x + (player_size - arm_width) + (i / 100.0)
            y = player_y + (player_size / 2) + (j / 100.0)
            glVertex2f(x, y)
    glEnd()

    # Draw the left leg (rectangle)
    glColor3f(0.0, 0.0, 0.0)  # Black color for legs
    glBegin(GL_POINTS)
    for i in range(int(leg_width * 100)):
        for j in range(int(leg_height * 100)):
            x = player_x + (player_size / 4) + (i / 100.0)
            y = player_y - (j / 100.0)
            glVertex2f(x, y)
    glEnd()

    # Draw the right leg (rectangle)
    glColor3f(0.0, 0.0, 0.0)  # Black color for legs
    glBegin(GL_POINTS)
    for i in range(int(leg_width * 100)):
        for j in range(int(leg_height * 100)):
            x = player_x + (player_size / 2) + (i / 100.0)
            y = player_y - (j / 100.0)
            glVertex2f(x, y)
    glEnd()




def draw_helicopter():
    # Body dimensions
    body_width = helicopter_width
    body_height = helicopter_height

    # Rotor dimensions
    rotor_length = body_width * 2
    rotor_height = body_height / 10

    # Tail dimensions
    tail_length = body_width * 0.8
    tail_height = body_height / 4

    # Draw the helicopter body (oval shape)
    glColor3f(0.8, 0.0, 0.0)  # Red for the helicopter body
    glBegin(GL_POINTS)
    for i in range(int(body_width * 100)):
        for j in range(int(body_height * 100)):
            x = helicopter_x + (i / 100.0)
            y = helicopter_y - (j / 100.0)
            if ((x - helicopter_x - body_width / 2) ** 2) / ((body_width / 2) ** 2) + \
               ((y - helicopter_y + body_height / 2) ** 2) / ((body_height / 2) ** 2) <= 1:
                glVertex2f(x, y)
    glEnd()

    # Draw the helicopter tail (rectangle)
    glColor3f(0.2, 0.2, 0.2)  # Gray for the tail
    glBegin(GL_POINTS)
    for i in range(int(tail_length * 100)):
        for j in range(int(tail_height * 100)):
            x = helicopter_x + body_width + (i / 100.0)
            y = helicopter_y - body_height / 2 + (j / 100.0)
            glVertex2f(x, y)
    glEnd()

    # Draw the rotor (horizontal line)
    glColor3f(0.0, 0.0, 0.0)  # Black for the rotor
    glBegin(GL_POINTS)
    for i in range(int(rotor_length * 100)):
        for j in range(int(rotor_height * 100)):
            x = helicopter_x + body_width / 2 - rotor_length / 2 + (i / 100.0)
            y = helicopter_y + body_height / 2 + (j / 100.0)
            glVertex2f(x, y)
    glEnd()

    # Draw the cockpit (small oval)
    cockpit_width = body_width / 2
    cockpit_height = body_height / 2.5
    glColor3f(0.0, 0.8, 1.0)  # Cyan for the cockpit
    glBegin(GL_POINTS)
    for i in range(int(cockpit_width * 100)):
        for j in range(int(cockpit_height * 100)):
            x = helicopter_x + (i / 100.0)
            y = helicopter_y - (j / 100.0)
            if ((x - helicopter_x - body_width / 4) ** 2) / ((cockpit_width / 2) ** 2) + \
               ((y - helicopter_y + body_height / 2.5) ** 2) / ((cockpit_height / 2) ** 2) <= 1:
                glVertex2f(x, y)
    glEnd()

    # Draw the tail rotor (small vertical line)
    glColor3f(0.0, 0.0, 0.0)  # Black for the tail rotor
    glBegin(GL_POINTS)
    for i in range(int(tail_height * 100)):
        for j in range(int(rotor_height * 100)):
            x = helicopter_x + body_width + tail_length + (j / 100.0)
            y = helicopter_y - body_height / 2 + tail_height / 2 - (i / 100.0)
            glVertex2f(x, y)
    glEnd()


def draw_rectangle(x, y, width, height, color):
    """
    Draw a rectangle using GL_POINTS at (x, y) with given width, height, and color.
    """
    glColor3f(*color)
    glBegin(GL_POINTS)
    for i in range(int(width * 100)):  # Scale to pixel-like precision
        for j in range(int(height * 100)):
            glVertex2f(x + i / 100.0, y + j / 100.0)
    glEnd()

def draw_buttons():
    # Draw restart button
    draw_rectangle(restart_button_x, restart_button_y, BUTTON_WIDTH, BUTTON_HEIGHT, TEAL)
    glColor3f(*WHITE)
    draw_text(restart_button_x + 0.01, restart_button_y + 0.02, "Restart")

    # Draw pause button
    draw_rectangle(pause_button_x, pause_button_y, BUTTON_WIDTH, BUTTON_HEIGHT, AMBER)
    glColor3f(*WHITE)
    if game_paused:
        draw_text(pause_button_x + 0.01, pause_button_y + 0.02, "Resume")
    else:
        draw_text(pause_button_x + 0.01, pause_button_y + 0.02, "Pause")

    # Draw exit button
    draw_rectangle(exit_button_x, exit_button_y, BUTTON_WIDTH, BUTTON_HEIGHT, RED)
    glColor3f(*WHITE)
    draw_text(exit_button_x + 0.01, exit_button_y + 0.02, "Exit")

def draw_text(x, y, text):
    glColor3f(1.0, 1.0, 1.0)  # White color for the text
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))


def update_player():
    global player_y, player_vertical_velocity, is_jumping
    if is_jumping:
        player_vertical_velocity += gravity
        player_y += player_vertical_velocity
        if player_y <= -0.8:  # Reset position on ground
            player_y = -0.8
            is_jumping = False
            player_vertical_velocity = 0


def update_helicopter():
    global helicopter_x
    helicopter_x -= helicopter_speed  # Move helicopter left
    if helicopter_x + helicopter_width < -1.333:  # Reset to the right of the screen
        helicopter_x = 1.0

def fire_bullet():
    global bullets, bullet_fire_direction
    bullet_x = helicopter_x + helicopter_width / 2
    bullet_y = helicopter_y - helicopter_height / 2

    if bullet_fire_direction == 1:  # Straight down
        angle = 90  # Angle for straight down
    else:  # Random direction
        angle = random.uniform(45, 135)  # Random angle between 45 and 135 degrees

    # Alternate the direction for the next bullet
    bullet_fire_direction *= -1

    bullets.append(Bullet(bullet_x, bullet_y, angle))





def reset_game():
    global score, lives, player_x, player_y, is_jumping, player_vertical_velocity, bullets, buildings, coins, special_coins
    # Reset player position and velocity
    player_x = -0.8
    player_y = -0.8
    is_jumping = False
    player_vertical_velocity = 0
    


    # Clear active bullets, buildings, coins, and special coins
    bullets = []
    buildings = []
    coins = []
    special_coins = []

    # Spawn the initial building for the new round
    spawn_initial_building()
    







def spawn_building():
    x = 1.0
    width = random.uniform(0.1, 0.3)
    height = random.uniform(0.3, 0.6)
    buildings.append(Building(x, width, height))


def spawn_coin():
    x = 1.0
    y = random.uniform(-0.6, 0.8)

    # Ensure the coin does not overlap with the helicopter
    while helicopter_x - 0.1 <= x <= helicopter_x + helicopter_width + 0.1 and \
          helicopter_y - 0.1 <= y <= helicopter_y + helicopter_height + 0.1:
        y = random.uniform(-0.6, 0.8)  # Generate a new y-coordinate

    coins.append(Coin(x, y))



def check_collision():
    global game_running, lives, score

    # Collision with buildings
    for building in buildings:
        if (player_x + player_size > building.x and
            player_x < building.x + building.width and
            player_y < -1.0 + building.height):
            lives -= 1
            print(f"Life lost! Lives remaining: {lives}")
            if lives <= 0:
                print(f"Game Over! Final Score: {score}")
                game_running = False  # End the game
                return True
            else:
                reset_game()  # Reset game state for the next round
                return True

    # Collision with bullets
    for bullet in bullets:
        if (player_x + player_size > bullet.x and
            player_x < bullet.x + bullet.size and
            player_y + player_size > bullet.y - bullet.size and
            player_y < bullet.y):
            lives -= 1
            print(f"Life lost! Lives remaining: {lives}")
            if lives <= 0:
                print(f"Game Over! Final Score: {score}")
                game_running = False  # End the game
                return True
            else:
                reset_game()  # Reset game state for the next round
                return True

    # Collision with helicopter
    if (player_x + player_size > helicopter_x and
        player_x < helicopter_x + helicopter_width and
        player_y + player_size > helicopter_y - helicopter_height and
        player_y < helicopter_y):
        lives -= 1
        print(f"Life lost! Lives remaining: {lives}")
        if lives <= 0:
            print(f"Game Over! Final Score: {score}")
            game_running = False  # End the game
            return True
        else:
            reset_game()  # Reset game state for the next round
            return True

    return False







def update_buildings():
    global buildings
    for building in buildings:
        building.update()
    buildings = [b for b in buildings if not b.is_off_screen()]


def update_coins():
    global coins, special_coins, score

    # Update and check regular coins
    for coin in coins:
        coin.update()
    collected = [c for c in coins if c.is_collected()]
    score += len(collected)  # Add 1 point for each regular coin collected
    coins = [c for c in coins if not c.is_off_screen() and c not in collected]

    # Update and check special coins
    for special_coin in special_coins:
        special_coin.update()
    special_collected = [c for c in special_coins if c.is_collected()]
    score += len(special_collected) * 5  # Add 5 points for each special coin collected
    special_coins = [c for c in special_coins if not c.is_off_screen() and c not in special_collected]


def update_bullets():
    global bullets
    for bullet in bullets:
        bullet.update()
    bullets = [bullet for bullet in bullets if not bullet.is_off_screen()]



def display():
    global game_running, score, is_raining, game_paused
    glClear(GL_COLOR_BUFFER_BIT)

    if game_running:
        if not game_paused:
            # Draw and update player
            update_player()
            draw_player()

            # Draw and update helicopter
            update_helicopter()
            draw_helicopter()

            # Draw and update bullets
            for bullet in bullets:
                bullet.draw()

            # Draw and update buildings
            update_buildings()
            for building in buildings:
                building.draw()

            # Draw and update regular coins
            update_coins()
            for coin in coins:
                coin.draw()

            # Draw special coins
            for special_coin in special_coins:
                special_coin.draw()

            # Draw rain if raining
            if is_raining:
                draw_raindrops()
                raindrops_effect()

        # Display the score and lives
        draw_text(-1.2, 0.8, f"Score: {score}  LIFE: {lives}")  # Ensure this uses the global `score` and `lives`

        # Draw buttons
        draw_buttons()

        # Display "Paused" message if the game is paused
        if game_paused:
            draw_text(-0.2, 0.0, "Paused")

        # Check for collision
        if check_collision():
            print(f"Final Score: {score}")
            return
    else:
        # Display "Game Over" message
        draw_text(-0.3, 0.0, "Game Over")

    glFlush()






def timer(value):
    global building_spawn_timer, coin_spawn_timer, bullet_fire_timer, special_coin_timer

    if game_running and not game_paused:  # Only update if the game is not paused
        # Spawn buildings at intervals
        if building_spawn_timer == 0:
            spawn_building()
        building_spawn_timer = (building_spawn_timer + 1) % building_spawn_interval

        # Spawn coins at intervals
        if coin_spawn_timer == 0:
            spawn_coin()
        coin_spawn_timer = (coin_spawn_timer + 1) % coin_spawn_interval

        # Spawn special coins at intervals
        if special_coin_timer == 0:
            spawn_special_coin()
        special_coin_timer = (special_coin_timer + 1) % special_coin_spawn_interval

        # Fire bullets at intervals
        if bullet_fire_timer == 0:
            fire_bullet()
        bullet_fire_timer = (bullet_fire_timer + 1) % bullet_fire_interval

        # Update and redisplay
        update_bullets()  # Update bullets

    glutPostRedisplay()
    glutTimerFunc(16, timer, 0)  # ~60 FPS




def keyboard(key, x, y):
    global is_jumping, player_vertical_velocity, is_raining

    if key == b' ' and not is_jumping:  # Jump
        is_jumping = True
        player_vertical_velocity = player_jump_speed

    if key == b'R' or key == b'r':  # Toggle rain
        is_raining = not is_raining
        if is_raining:
            raindrop()  # Initialize raindrops
            glClearColor(0.0, 0.0, 0.5, 1.0)  # Deep blue background
        else:
            glClearColor(0.53, 0.81, 0.98, 1.0)  # Reset to sky blue background

    




def init():
    glClearColor(0.53, 0.81, 0.98, 1.0)  # Sky blue background
    gluOrtho2D(-1.333, 1.333, -1.0, 1.0)


# Main code execution
glutInit()
glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
glutInitWindowSize(window_width, window_height)
glutInitContextVersion(2, 1)
glutInitContextProfile(GLUT_COMPATIBILITY_PROFILE)
glutCreateWindow(b"Jumping Game with Coins and Helicopter")
glutDisplayFunc(display)
glutKeyboardFunc(keyboard)
glutMouseFunc(mouse_callback)
glutTimerFunc(16, timer, 0)
init()
glutMainLoop()