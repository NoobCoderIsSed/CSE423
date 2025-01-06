from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math




# Button constants
button_Width =0.245
button_Height = 0.15
button_space = 0.05
screen_width = 2.666  # (-1.333 to 1.333)
screen_height = 2.0   # (-1.0 to 1.0)

# Button positions

restart_button_x = -1.333 + button_space
restart_button_y = 1.0 - button_Height - button_space + 0.1  
pause_button_x = -button_Width / 2
pause_button_y = 1.0 - button_Height - button_space + 0.1  
exit_button_x = 1.333 - button_Width - button_space
exit_button_y = 1.0 - button_Height - button_space + 0.1  


# Button colors
teal = (0.0, 0.5, 0.5)
amber = (1.0, 0.75, 0.0)
red = (1.0, 0.0, 0.0)
white = (1.0, 1.0, 1.0)

game_paused = False  
btn_reset=False


invincibility_duration = 0

bullets = []  
bullet_fire_timer = 0  
bullet_fire_interval = 30  #helicopter fire
bullet_fire_direction = -1 
lives = 5
helicopter_destroyed =False


# Rain variables
raindrops = []
num_raindrops = 100  
rain_direction = 1  
is_raining =False  

coin_spawn_interval = 50
black_coins = []
black_coin_spawn_interval = coin_spawn_interval* 1  #1/3 interval
black_coin_timer = 0  


window_width = 800
window_height = 450  
player_x = -0.8
player_y = -0.8
player_size = 0.1

player_vertical_velocity = 0
gravity = -0.002
is_jumping = False
buildings = []
building_spawn_timer =0
building_spawn_interval =100

building_speed =0.01
game_running = True


helicopter_x = 1.0
helicopter_y = 0.7
helicopter_speed = 0.02
helicopter_width = 0.2
helicopter_height = 0.1


normal_jump_speed = 0.07  
inv_jump_speed = 0.081 
player_jump_speed = normal_jump_speed

coins = []
coin_spawn_timer = 0
coin_spawn_interval =50  
coin_size =0.05
score = 0
coin_spawn_interval =50
black_coins = []
black_coin_spawn_interval = coin_spawn_interval * 3  
black_coin_timer = 0
special_coin_spawn_interval = coin_spawn_interval * 2  
special_coin_timer = 0  
special_coins = [] 

invincibility_timer = 0

helicopter_lives = 4  
player_bullets = []

#----------------------------------------------
import random

class Bullet:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.size = 0.02
        self.speed =0.02
        self.angle =angle  #bullets angle

    def draw(self):
        glColor3f(1.0, 0.0, 0.0)  # Red bullet
        glBegin(GL_POINTS)
        for i in range(int(self.size * 100)):
            for j in range(int(self.size * 100)):
                glVertex2f(self.x + (i / 100.0), self.y - (j / 100.0))
        glEnd()

    def update(self):
        self.x += self.speed * math.cos(math.radians(self.angle))
        self.y -= self.speed * math.sin(math.radians(self.angle))

    def is_off_screen(self):
        return self.y < -1.0 or self.x < -1.333 or self.x > 1.333  #screen boundaries

class BlackCoin:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def draw(self):
        color = (0.0, 0.0, 0.0)  #black color coins
        draw_coin(self.x, self.y, coin_size, color)

    def update(self):
        self.x -= building_speed

    def is_off_screen(self):
        return self.x + coin_size < -1.333

    def is_collected(self):
        return (player_x + player_size > self.x-coin_size and
                player_x < self.x+coin_size and
                player_y + player_size > self.y-coin_size and
                player_y < self.y+coin_size)
    
class PlayerBullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 0.02
        self.speed = 0.04  # Speed for player's bullet

    def draw(self):
        glColor3f(0.0, 0.0, 0.0)  
        glBegin(GL_POINTS)
        for i in range(int(self.size * 100)):
            for j in range(int(self.size * 100)):
                glVertex2f(self.x + (i / 100.0), self.y + (j / 100.0))
        glEnd()

    def update(self):
        self.y += self.speed  

    def is_off_screen(self):
        return self.y > 1.0  # bullet goes out of the screen

#Firing a bullet from the player
def fire_player_bullet():
    global player_bullets
    bullet_x = player_x + player_size / 2  # Center of player
    bullet_y = player_y + player_size
    player_bullets.append(PlayerBullet(bullet_x, bullet_y))


#Check the collison of the helicopter with player bullet
def update_player_bullets():
    global player_bullets, helicopter_lives, helicopter_x, helicopter_y, helicopter_width, helicopter_height, helicopter_destroyed, score

    for bullet in player_bullets:
        bullet.update()

        #collision with the helicopter
        if (bullet.x > helicopter_x and bullet.x < helicopter_x + helicopter_width and
            bullet.y > helicopter_y - helicopter_height and bullet.y < helicopter_y):
            helicopter_lives -= 1 
            print(f"Helicopter hit! Lifes remaining: {helicopter_lives}")
            player_bullets.remove(bullet)

            
            if helicopter_lives <= 0:
                create_demolishing_effect()
                helicopter_destroyed = True 
                helicopter_x = -2.0  #helicopter off the screen
                score += 50
                print("Helicopter is destroyed!")
                return

        #collision heli's tail
        tail_length = helicopter_width * 0.8
        tail_height = helicopter_height / 4
        tail_x = helicopter_x + helicopter_width
        tail_y = helicopter_y - helicopter_height / 2

        if (bullet.x > tail_x and bullet.x < tail_x + tail_length and
            bullet.y > tail_y and bullet.y < tail_y + tail_height):
            helicopter_lives -= 1 
            print(f"Helicopter tail hit! Lifes remaining: {helicopter_lives}")
            player_bullets.remove(bullet)  

            
            if helicopter_lives <= 0:
                create_demolishing_effect()
                helicopter_destroyed = True  
                helicopter_x = -2.0  
                score += 50  
                print("Helicopter is destroyed!")
                return

    
    player_bullets = [bullet for bullet in player_bullets if not bullet.is_off_screen()]

#demolishing effect for helicopter destroy
def create_demolishing_effect():
    global helicopter_x, helicopter_y, helicopter_width, helicopter_height

    #flashing color effect
    for _ in range(100):  
        glColor3f(1.0, 0.5, 0.0)  # yellow color
        glBegin(GL_POINTS)
        for _ in range(200):
            x = random.uniform(helicopter_x, helicopter_x + helicopter_width)
            y = random.uniform(helicopter_y - helicopter_height, helicopter_y)
            glVertex2f(x, y)
        glEnd()
        glFlush()

    
    helicopter_x = -2.0  # off-screen heli




class buttonsss:
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
    


#Buttons
restart_button_aabb = buttonsss(restart_button_x, restart_button_y, button_Width, button_Height)
pause_button_aabb = buttonsss(pause_button_x, pause_button_y, button_Width, button_Height)
exit_button_aabb = buttonsss(exit_button_x, exit_button_y, button_Width, button_Height)





#Direct implement of midpoint circle
def draw_coin(x, y, radius, color):
    glColor3f(*color)
    glBegin(GL_POINTS)
    
    x_center = int(x * 100)  
    y_center = int(y * 100)
    r = int(radius * 100)
    
    x = r
    y = 0
    decision_parameter = 1 - r
    
    while y <= x:
        glVertex2f((x_center + x) / 100.0, (y_center + y) / 100.0)
        glVertex2f((x_center + x) / 100.0, (y_center - y) / 100.0)
        glVertex2f((x_center - x) / 100.0, (y_center + y) / 100.0)
        glVertex2f((x_center - x) / 100.0, (y_center - y) / 100.0)
        glVertex2f((x_center + y) / 100.0, (y_center + x) / 100.0)
        glVertex2f((x_center + y) / 100.0, (y_center - x) / 100.0)
        glVertex2f((x_center - y) / 100.0, (y_center + x) / 100.0)
        glVertex2f((x_center - y) / 100.0, (y_center - x) / 100.0)
        
        y += 1
        if decision_parameter < 0:
            decision_parameter += 2 * y + 1
        else:
            x -= 1
            decision_parameter += 2 * (y - x) + 1
    
    glEnd()




def mouse_callback(button, state, x, y):
    global game_running,game_paused

    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        
        gl_x = (x / window_width) * 2.666 - 1.333
        gl_y = 1.0 - (y / window_height) * 2.0

        #restart button
        if restart_button_aabb.collides_with(buttonsss(gl_x, gl_y, 0, 0)):
            button_reset_game()  # Reset the game
        #pause button
        elif pause_button_aabb.collides_with(buttonsss(gl_x, gl_y, 0, 0)):
            game_paused = not game_paused  # Toggle pause state
        #exit button
        elif exit_button_aabb.collides_with(buttonsss(gl_x, gl_y, 0, 0)):
            glutLeaveMainLoop()

        
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
    x = player_x - 0.2  #player starts on top
    width = 0.4  
    height = 0.5  
    #Fixed w and h for the first building
    buildings.append(Building(x, width, height))
    player_y = -1.0 + height  #player on top of first building


def raindrop():
    global raindrops
    raindrops = []
    for _ in range(num_raindrops):
        x = random.uniform(-1.333,1.333)  
        y = random.uniform(-1.0,1.0) 
        raindrops.append({'x': x, 'y': y})

def draw_raindrops():
    glColor3f(0.8, 0.8,1.0)  # Light blue
    glBegin(GL_LINES)
    for drop in raindrops:
        glVertex2f(drop['x'], drop['y'])  # Start of rain
        glVertex2f(drop['x'] + rain_direction * 0.002, drop['y'] - 0.05)  # End of rain
    glEnd()

def raindrops_effect():
    global raindrops
    for drop in raindrops:
        drop['y'] -= 0.02  
        drop['x'] += rain_direction * 0.001  
        if drop['y'] < -1.0: 
            drop['y'] = random.uniform(0.0, 1.0)
            drop['x'] = random.uniform(-1.333, 1.333)


class Coin:
    def __init__(self, x, y, is_special=False):
        self.x = x
        self.y = y
        self.is_special = is_special  # Flag for special coin

    def draw(self):
        if self.is_special:
            color = (0.0, 1.0, 0.0)  #Green
        else:
            color = (1.0, 1.0, 0.0)  # Yellow
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
    x =1.0
    y = random.uniform(-0.6,0.8)

    #special coins don't overlap with the heli
    while helicopter_x - 0.1 <= x <= helicopter_x + helicopter_width + 0.1 and \
          helicopter_y - 0.1 <= y <= helicopter_y + helicopter_height + 0.1:
        y = random.uniform(-0.6, 0.8)

    special_coins.append(Coin(x, y, is_special=True))

def draw_player():
    
    # Head
    head_size = player_size / 2

    # Body
    body_width = player_size / 3
    body_height = player_size

    #Arms
    arm_width = player_size /5
    arm_height = player_size /1.5

    #Legs
    leg_width = player_size /4
    leg_height = player_size /1.2

    
    offset_x = player_x + (player_size /2) - (body_width / 2)
    offset_y = player_y + player_size /2

    #head draw
    glColor3f(1.0, 0.6, 0.6) 
    glBegin(GL_POINTS)
    for i in range(int(head_size * 100)):
        for j in range(int(head_size * 100)):
            x = offset_x + (i / 100.0) - head_size /2
            y = offset_y + player_size + (j / 100.0)
            if (x - offset_x) ** 2 + (y - (offset_y + player_size + head_size / 2)) ** 2 <= (head_size / 2) ** 2:
                glVertex2f(x, y)
    glEnd()

    # body draw
    glColor3f(0.2, 0.5, 0.8)  #blue
    glBegin(GL_POINTS)
    for i in range(int(body_width * 100)):
        for j in range(int(body_height * 100)):
            x = offset_x + (i / 100.0)
            y = offset_y + (j / 100.0)
            glVertex2f(x, y)
    glEnd()

    # Draw left arm 
    glColor3f(1.0, 0.6, 0.6)  
    glBegin(GL_POINTS)
    for i in range(int(arm_width * 100)):
        for j in range(int(arm_height * 100)):
            x = offset_x - arm_width + (i / 100.0)
            y = offset_y + (j / 100.0)
            glVertex2f(x, y)
    glEnd()

    # Draw right arm
    glColor3f(1.0, 0.6, 0.6)  
    glBegin(GL_POINTS)
    for i in range(int(arm_width * 100)):
        for j in range(int(arm_height * 100)):
            x = offset_x + body_width + (i / 100.0)
            y = offset_y + (j / 100.0)
            glVertex2f(x, y)
    glEnd()

    # Draw left le
    glColor3f(0.2, 0.8, 0.2)
    glBegin(GL_POINTS)
    for i in range(int(leg_width * 100)):
        for j in range(int(leg_height * 100)):
            x = offset_x + (i / 100.0)
            y = offset_y - (j / 100.0)
            glVertex2f(x, y)
    glEnd()

    # Draw the right leg
    glColor3f(0.2, 0.8, 0.2) 
    glBegin(GL_POINTS)
    for i in range(int(leg_width * 100)):
        for j in range(int(leg_height * 100)):
            x = offset_x + body_width - leg_width + (i / 100.0)
            y = offset_y - (j / 100.0)
            glVertex2f(x, y)
    glEnd()
    # Draw the body
    glColor3f(0.0, 0.0, 1.0)  
    glBegin(GL_POINTS)
    for i in range(int(body_width * 100)):
        for j in range(int(body_height * 100)):
            x = player_x + (player_size / 4) + (i / 100.0)
            y = player_y + (j / 100.0)
            glVertex2f(x, y)
    glEnd()

    # Draw left arm 
    glColor3f(1.0, 0.8, 0.6) 
    glBegin(GL_POINTS)
    for i in range(int(arm_width * 100)):
        for j in range(int(arm_height * 100)):
            x = player_x + (i / 100.0)
            y = player_y + (player_size / 2) + (j / 100.0)
            glVertex2f(x, y)
    glEnd()

    # Draw the right arm 
    glColor3f(1.0, 0.8, 0.6)  
    glBegin(GL_POINTS)
    for i in range(int(arm_width * 100)):
        for j in range(int(arm_height * 100)):
            x = player_x + (player_size - arm_width) + (i / 100.0)
            y = player_y + (player_size / 2) + (j / 100.0)
            glVertex2f(x, y)
    glEnd()

    # Draw the left leg 
    glColor3f(0.0, 0.0, 0.0)  
    glBegin(GL_POINTS)
    for i in range(int(leg_width * 100)):
        for j in range(int(leg_height * 100)):
            x = player_x + (player_size / 4) + (i / 100.0)
            y = player_y - (j / 100.0)
            glVertex2f(x, y)
    glEnd()

    # Draw the right leg
    glColor3f(0.0, 0.0, 0.0)
    glBegin(GL_POINTS)
    for i in range(int(leg_width * 100)):
        for j in range(int(leg_height * 100)):
            x = player_x + (player_size / 2) + (i / 100.0)
            y = player_y - (j / 100.0)
            glVertex2f(x, y)
    glEnd()




def draw_helicopter():
    # Body
    body_width = helicopter_width
    body_height = helicopter_height

    # Rotor
    rotor_length = body_width * 2
    rotor_height = body_height / 10

    # Tail
    tail_length = body_width * 0.8
    tail_height = body_height / 4

    # Draw helicopter body
    glColor3f(0.8, 0.0, 0.0)  # Red
    glBegin(GL_POINTS)
    for i in range(int(body_width * 100)):
        for j in range(int(body_height * 100)):
            x = helicopter_x + (i / 100.0)
            y = helicopter_y - (j / 100.0)
            if ((x - helicopter_x - body_width / 2) ** 2) / ((body_width / 2) ** 2) + \
               ((y - helicopter_y + body_height / 2) ** 2) / ((body_height / 2) ** 2) <= 1:
                glVertex2f(x, y)
    glEnd()

    # Draw the helicopter tail
    glColor3f(0.2, 0.2, 0.2)  # Gray 
    glBegin(GL_POINTS)
    for i in range(int(tail_length * 100)):
        for j in range(int(tail_height * 100)):
            x = helicopter_x + body_width + (i / 100.0)
            y = helicopter_y - body_height / 2 + (j / 100.0)
            glVertex2f(x, y)
    glEnd()

    #horizontal line as rotor
    glColor3f(0.0, 0.0, 0.0)  # Black
    glBegin(GL_POINTS)
    for i in range(int(rotor_length * 100)):
        for j in range(int(rotor_height * 100)):
            x = helicopter_x + body_width / 2 - rotor_length / 2 + (i / 100.0)
            y = helicopter_y + body_height / 2 + (j / 100.0)
            glVertex2f(x, y)
    glEnd()

    #small oval
    cockpit_width = body_width /2
    cockpit_height = body_height /2.5
    glColor3f(0.0, 0.8, 1.0)  # Cyan
    glBegin(GL_POINTS)
    for i in range(int(cockpit_width * 100)):
        for j in range(int(cockpit_height * 100)):
            x = helicopter_x + (i / 100.0)
            y = helicopter_y - (j / 100.0)
            if ((x - helicopter_x - body_width / 4) ** 2) / ((cockpit_width / 2) ** 2) + \
               ((y - helicopter_y + body_height / 2.5) ** 2) / ((cockpit_height / 2) ** 2) <= 1:
                glVertex2f(x, y)
    glEnd()

    # Draw small vertical line
    glColor3f(0.0, 0.0, 0.0)  # Black
    glBegin(GL_POINTS)
    for i in range(int(tail_height *100)):
        for j in range(int(rotor_height *100)):
            x = helicopter_x + body_width + tail_length + (j/100.0)
            y = helicopter_y - body_height / 2 + tail_height / 2 - (i /100.0)
            glVertex2f(x, y)
    glEnd()


def draw_rectangle(x, y, width, height, color):
    glColor3f(*color)
    glBegin(GL_POINTS)
    for i in range(int(width * 100)):  # Scale to pixel
        for j in range(int(height *100)):
            glVertex2f(x +i /100.0, y +j /100.0)
    glEnd()

def draw_buttons():
    # Draw restart button
    draw_rectangle(restart_button_x, restart_button_y, button_Width, button_Height, teal)
    glColor3f(*white)
    draw_text(restart_button_x +0.01, restart_button_y +  0.02, "Restart")

    # Draw pause button
    draw_rectangle(pause_button_x, pause_button_y, button_Width, button_Height, amber)
    glColor3f(*white)
    if game_paused:
        draw_text(pause_button_x + 0.01, pause_button_y +0.02, "Resume")
    else:
        draw_text(pause_button_x +0.01, pause_button_y +0.02, "Pause")

    # Draw exit button
    draw_rectangle(exit_button_x, exit_button_y, button_Width, button_Height, red)
    glColor3f(*white)
    draw_text(exit_button_x +0.01, exit_button_y +0.02, "Exit")

def draw_text(x, y, text):
    glColor3f(1.0, 1.0, 1.0)  # White
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))


def update_player():
    global player_y,player_vertical_velocity,is_jumping
    if is_jumping:
        player_vertical_velocity += gravity
        player_y += player_vertical_velocity
        if player_y <= -0.8:  # Reset position on ground
            player_y = -0.8
            is_jumping =  False
            player_vertical_velocity =0


def update_helicopter():
    global helicopter_x, helicopter_destroyed
    if not helicopter_destroyed: 
        helicopter_x -= helicopter_speed  # Move helicopter left
        if helicopter_x + helicopter_width < -1.333:  # Reset right of the screen
            helicopter_x = 1.0

def fire_bullet():
    global bullets, bullet_fire_direction
    bullet_x = helicopter_x + helicopter_width / 2
    bullet_y = helicopter_y - helicopter_height / 2

    if bullet_fire_direction == 1:  
        angle = 90  #straight down shoot 
    else: 
        angle = random.uniform(45, 135)  #angle between 45 and 135 degrees

    # Alternate the direction for the next bullet
    bullet_fire_direction *= -1

    bullets.append(Bullet(bullet_x, bullet_y, angle))


def button_reset_game():
    global btn_reset,score, lives,player_x,player_y, is_jumping, black_coin_timer, player_vertical_velocity, bullets, buildings, coins, special_coins, black_coins, helicopter_lives,helicopter_destroyed
    # Reset player position and velocity
    btn_reset =True
    score =0
    lives =5
    player_x = -0.8
    player_y = -0.8
    is_jumping =False
    player_vertical_velocity =0

    # Reset helicopter
    helicopter_lives = 4
    helicopter_destroyed = False
    helicopter_x = 1.0

    #Clear this arrys
    bullets = []
    buildings = []
    coins = []
    special_coins = []
    black_coins = []
    black_coin_timer = 0

    #new round
    spawn_initial_building()


def reset_game():
    global btn_reset,score, lives, player_x, player_y, is_jumping,black_coin_timer, player_vertical_velocity, bullets, buildings, coins, special_coins,black_coins
    
    player_x = -0.8
    player_y = -0.8
    is_jumping = False
    player_vertical_velocity = 0
    btn_reset=False

    bullets = []
    buildings = []
    coins = []
    special_coins = []
    black_coins=[]
    black_coin_timer = 0

    
    spawn_initial_building()
    

def spawn_building():
    x = 1.0
    width = random.uniform(0.2, 0.4) ###buildings width
    height = random.uniform(0.3, 0.6)
    buildings.append(Building(x, width, height))


def spawn_coin():
    global coin_spawn_timer, black_coin_timer

    #regular coins
    if coin_spawn_timer == 0:
        x = 1.0
        y = random.uniform(-0.6, 0.8)
        coins.append(Coin(x, y))
    coin_spawn_timer = (coin_spawn_timer + 1) % coin_spawn_interval

    #black coins
    if black_coin_timer == 0:
        x = 1.0
        y = random.uniform(-0.6, 0.8)
        black_coins.append(BlackCoin(x, y))
    black_coin_timer = (black_coin_timer + 1) % black_coin_spawn_interval



def check_collision():
    global game_running, lives, score,invincibility_duration,player_jump_speed,gravity
    if invincibility_duration > 0:
        invincibility_duration -= 1
        player_jump_speed = inv_jump_speed
        
        return False
    else:
        player_jump_speed = normal_jump_speed
        # gravity = NORMAL_GRAVITY

    #Collision with buildings
    for building in buildings:
        if (player_x + player_size > building.x and
            player_x < building.x + building.width and
            player_y < -1.0 + building.height):
            lives -= 1
            print(f"Life lost! Lifes remaining: {lives}")
            if lives <= 0:
                print(f"Game Over! Final Score: {score}")
                game_running = False  
                return True
            else:
                reset_game()  # Reset game
                return True

    # Collision with bullets
    for bullet in bullets:
        if (player_x + player_size > bullet.x and
            player_x < bullet.x + bullet.size and
            player_y + player_size > bullet.y - bullet.size and
            player_y < bullet.y):
            lives -= 1
            print(f"Life lost! Lifes remaining: {lives}")
            if lives <= 0:
                print(f"Game Over! Final Score: {score}")
                game_running = False  
                return True
            else:
                reset_game()  # Reset game 
                return True

    # Collision with helicopter
    if (player_x + player_size > helicopter_x and
        player_x < helicopter_x + helicopter_width and
        player_y + player_size > helicopter_y - helicopter_height and
        player_y < helicopter_y):
        lives -= 1
        print(f"Life lost! Lifes remaining: {lives}")
        if lives <= 0:
            print(f"Game Over! Final Score: {score}")
            game_running = False  
            return True
        else:
            reset_game()  # Reset game
            return True

    return False


def update_buildings():
    global buildings
    for building in buildings:
        building.update()
    buildings = [b for b in buildings if not b.is_off_screen()]


def update_coins():
    global coins, special_coins, black_coins, score, invincibility_duration, invincibility_timer

    # Update regular coins
    for coin in coins:
        coin.update()
    collected = [c for c in coins if c.is_collected()]
    score += len(collected)  # 1 point for regular coin
    coins = [c for c in coins if not c.is_off_screen() and c not in collected]

    # Update special coins
    for special_coin in special_coins:
        special_coin.update()
    special_collected = [c for c in special_coins if c.is_collected()]
    score += len(special_collected) * 5  # 5 points for each special coin
    special_coins = [c for c in special_coins if not c.is_off_screen() and c not in special_collected]

    
    for black_coin in black_coins:
        black_coin.update()
    black_collected = [c for c in black_coins if c.is_collected()]
    invincibility_duration += len(black_collected) * 5 * 60  #5 seconds
    invincibility_timer = invincibility_duration  # Set the invincibility timer
    black_coins = [c for c in black_coins if not c.is_off_screen() and c not in black_collected]


def update_bullets():
    global bullets
    for bullet in bullets:
        bullet.update()
    bullets = [bullet for bullet in bullets if not bullet.is_off_screen()]



def display():
    global game_running, score, is_raining, game_paused, helicopter_lives, helicopter_destroyed
    glClear(GL_COLOR_BUFFER_BIT)

    if game_running:
        if not game_paused:
            update_player()
            draw_player()

            if not helicopter_destroyed:  # draw the helicopter if it is not already destroyed
                update_helicopter()
                draw_helicopter()

            for bullet in bullets:
                bullet.draw()

            update_buildings()
            for building in buildings:
                building.draw()
            update_coins()
            for coin in coins:
                coin.draw()

            for special_coin in special_coins:
                special_coin.draw()

            if is_raining:
                draw_raindrops()
                raindrops_effect()
            for black_coin in black_coins:
                black_coin.draw()

            
            update_player_bullets()
            for bullet in player_bullets:
                bullet.draw()

        # Display the helicopter's lives
        if helicopter_destroyed:
            draw_text(-1.2, 0.7, "Helicopter is destroyed!")
        else:
            draw_text(-1.2, 0.7, f"Helicopter LIFE: {helicopter_lives}")

        draw_text(-1.2, 0.8, f"Score: {score}  LIFE: {lives}")
        if invincibility_duration > 0 and btn_reset == False:
            draw_text(-1.2, 0.6, f"Invincible: {invincibility_timer // 60}")

        draw_buttons()

        if game_paused:
            draw_text(-0.2, 0.0, "Paused")

        if check_collision():
            print(f"Final Score: {score}")
            return
    else:
        draw_text(-0.3, 0.0, "Game Over")

    glFlush()

def timer(value):
    global building_spawn_timer, coin_spawn_timer, bullet_fire_timer, special_coin_timer,invincibility_timer

    if game_running and not game_paused:  
        
        if building_spawn_timer == 0:
            spawn_building()
        building_spawn_timer = (building_spawn_timer + 1) % building_spawn_interval

        if invincibility_timer > 0:
            invincibility_timer -= 1

        
        if coin_spawn_timer == 0:
            spawn_coin()
        coin_spawn_timer = (coin_spawn_timer + 1) % coin_spawn_interval

        
        if special_coin_timer == 0:
            spawn_special_coin()
        special_coin_timer = (special_coin_timer + 1) % special_coin_spawn_interval

        
        if bullet_fire_timer == 0:
            fire_bullet()
        bullet_fire_timer = (bullet_fire_timer + 1) % bullet_fire_interval

        
        update_bullets()  

    glutPostRedisplay()
    glutTimerFunc(16, timer, 0)  #60 FPS




def keyboard(key, x, y):
    global is_jumping, player_vertical_velocity, is_raining

    if key == b' ' and not is_jumping: 
        is_jumping = True
        player_vertical_velocity = player_jump_speed

    if key == b'R' or key == b'r':  
        is_raining = not is_raining
        if is_raining:
            raindrop()  
            glClearColor(0.0, 0.0, 0.5, 1.0)  # Deep blue
        else:
            glClearColor(0.53, 0.81, 0.98, 1.0)  

    if key == b'f' or key == b'F':  # fire a bullet
        fire_player_bullet() 

    




def init():
    glClearColor(0.53, 0.81, 0.98, 1.0)  #blue 
    gluOrtho2D(-1.333, 1.333, -1.0, 1.0)


# Main code execution
glutInit()
glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
glutInitWindowSize(window_width, window_height)
glutInitContextVersion(2, 1)
glutInitContextProfile(GLUT_COMPATIBILITY_PROFILE)
glutCreateWindow(b"BRACU RUNNER")
glutDisplayFunc(display)
glutKeyboardFunc(keyboard)
glutMouseFunc(mouse_callback)
glutTimerFunc(16, timer, 0)
init()
glutMainLoop()