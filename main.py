import pygame
import random
from enum import Enum
from collections import namedtuple
pygame.init()

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4
Point = namedtuple('Point', 'x, y')
BLOCK_SIZE = 20
font = pygame.font.SysFont('arial', 25)
PLAY_TIME = 30

# rgb colors
WHITE = (255,255,255)
RED = (200,0,0)
BLUE = (0,0,255)
BLUE1 = (0,100,255)
BLACK = (0,0,0)

class SnakeGame:
    def __init__(self, w=640, h=480):

        self.w = w
        self.h = h
        # Init Display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Snake')
        # Init second display
        self.second_display = pygame.Surface((self.w, self.h))  # the size of your rect
        self.second_display.set_alpha(20)  # alpha level
        self.second_display.fill((0, 0, 0))  # this fills the entire surface

        self.clock = pygame.time.Clock()
        # Init game state
        self.direction = Direction.RIGHT
        self.head = Point(self.w/2, self.h/2)
        self.snake = [self.head,
                       Point(self.head.x-BLOCK_SIZE, self.head.y),
                       Point(self.head.x-(2*BLOCK_SIZE), self.head.y)]
        self.score = 0
        self.level = 1
        self.food = None
        self._place_food()
        self.start_time = pygame.time.get_ticks()  # reset the start time



    def _init_time(self):
        # Calculate how much time is left by subtracting the current time
        # from the start time, and then this value from the maximum allowed time (30 seconds).
        # As these times are stored in milliseconds, we then
        # divide by 1000 to convert to seconds, and convert the result to an integer
        # value so that only whole seconds are shown.
        self.time_left = pygame.time.get_ticks() - self.start_time  # find out how much time has passed since the start of the game
        self.time_left = self.time_left / 1000  # Convert this time from milliseconds to seconds
        self.time_left = PLAY_TIME - self.time_left  # Find out how much time is remaining by subtracting total time from time thats passed
        self.time_left = int(self.time_left)  # Convert this value to an integer
        self.draw_timer(0, 25, self.time_left)  # Once we have calculated how much time is left, draw the timer

    def _place_food(self):
        x = random.randint(0, (self.w-BLOCK_SIZE )//BLOCK_SIZE)*BLOCK_SIZE
        y = random.randint(0, (self.h - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        self.food = Point(x, y)
        if self.food in self.snake:
            self._place_food()

    """def _place_big_food(self):
        x = random.randint(0, (self.w - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        y = random.randint(0, (self.h - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        self.food = Point(x, y)
        if self.food in self.snake:
            self._place_big_food()"""

    def play_step(self):
        # Collect user input
        game_over = False
        self._init_time()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT or event.key == pygame.K_a and self.direction != Direction.RIGHT:
                    self.direction = Direction.LEFT
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d and self.direction != Direction.LEFT:
                    self.direction = Direction.RIGHT
                elif event.key == pygame.K_UP or event.key == pygame.K_w and self.direction != Direction.DOWN:
                    self.direction = Direction.UP
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s and self.direction != Direction.UP:
                    self.direction = Direction.DOWN

        # 2. move
        self._move(self.direction)
        self.snake.insert(0, self.head) # update the head
        # 3. check if game over
        if self._is_collision("modern"):
            game_over = True
            #self.draw_game_over("g", "g")
            return game_over, self.score
        # 4. replace new food or just move
        if self.head == self.food:
            self.score += 1
            self.start_time += 2000
            self._place_food()
        else:
            self.snake.pop()
        # 5. update ui
        self._update_ui()
        # 6. change Level and speed
        if self.score <= 5:
            self.level = 1
            self.clock.tick(10)
        elif self.score > 5:
            self.level = 2
            self.clock.tick(12)
        elif self.score > 13:
            self.level = 3
            self.clock.tick(15)
        elif self.score > 20:
            self.level = 4
            self.clock.tick(18)
        elif self.score > 40:
            self.level = 5
            self.clock.tick(23)
        elif self.score > 80:
            self.level = 6
            self.clock.tick(30)
        elif self.score > 150:
            self.level = 2
            self.clock.tick(36)
        # 7. return game over and score if time is over
        if self.time_left <= 0:
            # If the time is up, set the boolean game_ended to True
            # so we can display the correct game over screen
            game_over = True
            self.draw_game_over("g", "g")
        return game_over, self.score

    def _is_collision(self, mode):
        mode = mode
        # hits boundary
        if mode == 'classic':
            if self.head.x > self.w - BLOCK_SIZE or self.head.x < 0 or self.head.y > self.h - BLOCK_SIZE or self.head.y < 0:
                return True

        elif mode == 'modern':
            # hits right boundary
            if self.head.x >= self.w and self.direction == Direction.RIGHT:
                self.head = Point(self.head.x-self.w-BLOCK_SIZE, self.head.y)
            # hits left boundary
            if self.head.x < 0 and self.direction == Direction.LEFT:
                self.head = Point(self.head.x+self.w+BLOCK_SIZE, self.head.y)
            # hits top boundary
            if self.head.y < 0 and self.direction == Direction.UP:
                self.head = Point(self.head.x, self.head.y+self.h+BLOCK_SIZE)
            # hits bottom boundary
            if self.head.y > self.h - BLOCK_SIZE and self.direction == Direction.DOWN:
                self.head = Point(self.head.x, self.head.y-self.h-BLOCK_SIZE)

        # hits itself
        if self.head in self.snake[1:]:
            return True

        return False


    def _update_ui(self):
        self.display.fill(BLACK)
        self.draw_timer(0, 25, self.time_left)

        for pt in self.snake:
            pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.display, BLUE, pygame.Rect(pt.x+4, pt.y+4, 12, 12))


#### Draw borders / another way: https://stackoverflow.com/questions/61765229/snake-game-in-pygame-borders
        line_number_w = self.w / BLOCK_SIZE
        line_number_h = self.h / BLOCK_SIZE

        w_lines = {
            '0': [(0, 0), (0, 480)],
            '1': [(5, 0), (20, 480)],
        }
        h_lines = {
            '0': [(0, 0), (0, 480)],
            '1': [(5, 0), (20, 480)],
        }

        for i in range(int(line_number_w)):
            w_lines[f'{i}'] = [(i*20, 20*i), (0, 480)]

        for i in range(int(line_number_h)):
            h_lines[f'{i}'] = [(640, 0), (i*20, i*20)]

        for i in range(int(line_number_w)):
            for element in w_lines[str(i)]:
                value_1 = str(element)
                a, b = value_1.split(' ')
                a, b = zip(*w_lines[str(i)])
                pygame.draw.line(self.second_display, WHITE, a, b, width=1)

        for i in range(int(line_number_h)):
            for element in h_lines[str(i)]:
                value_1 = str(element)
                a, b = value_1.split(' ')
                a, b = zip(*h_lines[str(i)])
                pygame.draw.line(self.second_display, WHITE, a, b, width=1)

####
        pygame.draw.rect(self.display, RED,  pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))

        # Draw Score and Speed text
        text_score = font.render('Score: ' + str(self.score), True, WHITE)
        text_lvl = font.render('Level: ' + str(self.level), True, WHITE)
        self.display.blit(text_score, [0, 0])
        self.display.blit(text_lvl, [90, 0])

        self.display.blit(self.second_display, (0, 0))  # (0,0) are the top-left coordinates
        pygame.display.flip()

    def _move(self, direction):
        x = self.head.x
        y = self.head.y
        if direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif direction == Direction.UP:
            y -= BLOCK_SIZE

        self.head = Point(x, y)

    def draw_timer(self, x, y, time_left):
        font2 = pygame.font.Font(None, 36)  # Choose the font for the text
        text = font2.render("Time Left = " + str(time_left), 1, WHITE)  # Create the text
        self.display.blit(text, (x, y))  # Draw the text on the screen

    def draw_game_over(self, message_1, message_2):
        pygame.draw.rect(self.display, WHITE, (150, 200, 400, 100), 0)  # Draw a white box for the text to sit in

        #font = pygame.font.Font(None, 36)  # Choose the font for the text
        text = font.render(message_1, 1, BLACK)  # Create the text for "GAME OVER"
        self.display.blit(text, (170, 220))  # Draw the text on the screen
        text = font.render(message_2, 1, BLACK)  # Create the text for "You hit the other player"
        self.display.blit(text, (170, 260))  # Draw the text on the screen

        #font = pygame.font.Font(None, 28)  # Make the font a bit smaller for this bit
        text = font.render("Press P to play again. Press E to exit the game.", 1,
                            WHITE)  # Create text for instructions on what to do now
        self.display.blit(text, (100, 350))  # Draw the text on the screen

if __name__ =='__main__':
    game = SnakeGame()

    # Game Loop
    while True:
        game_over, score = game.play_step()
        if game_over == True:
            break

    print('Final score: ' + str(score))
        #break if game over

    pygame.quit()


    """## TO do list:
    1. Dodac BigFood
    2. Zrobic Menu glowne i opcje wyboru trundosci(czas, predkosc)
    3. Zrobic menu game over
    4. Dodac opcje multiplayer czyli dwoch graczy nie moze sie ze soba zderzyc, albo
    gracz ma mini plansze drugiego gracza w mini mapie i widzi jego punkty, ten gracz ktory
    zdobedzie wiecej wygrywa, a roznica w punktach daje wiecej kasy wirtualnej za ktora
    mozna kupic ulepszenia, skorki.
    5. DOdac AI"""