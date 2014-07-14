# -*- coding: utf-8 -*-

import pygame
import pygcurse
import time, random
import pyfiglet
import pygame.mixer
import string
import SMS_Server
import pickle

class Point():
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return "[%s, %s]" % (self.x, self.y)


DIGIT_DIMENSIONS = Point(5, 7)

def char_to_font(string):
    f = pyfiglet.Figlet(font='5x7')
    digit_map = []
    for line in f.renderText(string).replace("#", u"█").replace("/", u"█").replace("\\", u"█").replace("o", u"█").replace("-", u"█").replace("O", u"█").replace("0", u"█").split("\n"):
        digit_map.append(list(line))
    return digit_map

class Spinner_Wheel():
    def __init__(self):
        self.random_key = ''
        self.numbers, self.winner, self.winner_index = self.import_numbers()
        self.grid_size = Point(80, 45)
        self.screen = pygcurse.PygcurseWindow(self.grid_size.x, self.grid_size.y, fullscreen=False)
        self.screen._autoupdate = False
        pygame.mixer.init()

        self.screen.update()
        pygame.display.set_caption("Wheel O' Winners")
        self.cell_size = (self.screen.cellheight, self.screen.cellwidth)

    def text(self, x, y, s, fgcolor="white", bgcolor="black"):
        self.screen.write(s, x=x, y=y, fgcolor=fgcolor, bgcolor=bgcolor)
        return


    def import_numbers(self):
        with open("entrants.txt") as fin:
            entrants = pickle.load(fin)
        keys = entrants.keys()
        numbers = []
        for number in keys:
            numbers.append(number[-3:])
        for i in range(50):
            random_initials = random.choice(string.uppercase) + random.choice(string.uppercase) + random.choice(string.uppercase)
            numbers.append(random_initials + " " + str(random.randint(1111, 9999)))
        self.random_seed = self.determine_seed(numbers)
        random.seed(self.random_key)
        random.shuffle(numbers)
        winner = random.choice(numbers)
        winner_index = numbers.index(winner)
        return numbers, winner, winner_index

    def determine_seed(self, numbers):
        seed = ''
        for number in numbers:
            seed += number[1]
            seed += number[5]
        print "SEED:", seed
        return seed

    def print_entrants(self):
        try:
            to_print = self.numbers[:149]
        except IndexError:
            to_print = self.numbers
        self.print_border(border_only=True)
        self.text(self.grid_size.x/2 - 4, 2, "PLAYERS:", fgcolor="yellow")
        col = -3
        for i, player in enumerate(to_print):
            if i % 30 == 0:
                col += 13
            self.text(col, i % 20 + 4, player, fgcolor="white")
        self.screen.update()
        #time.sleep(5)
        for col in range(len(self.numbers)/5):
            self.screen.settint(100, 150, 70, (11+col*13, 4, 1, 30))
            self.screen.settint(100, 150, 70, (16+col*13, 4, 1, 30))
        self.screen.update()


        self.text(self.grid_size.x/2 - 4, 34, "RANDOM SEED: ", fgcolor="yellow")
        row = 35
        col = 9
        for i, char in enumerate(self.random_seed):
            if i % 63 == 0:
                row += 1
                col = 9
            col += 1
            self.text(col, row, char, fgcolor="yellow")


        self.screen.update()
        pygcurse.waitforkeypress()

    def print_border(self, color="yellow", border_only=False):
        self.screen.fill('?', fgcolor=color, region=(0, 0, self.grid_size.x-1, 1))
        self.screen.fill('?', fgcolor=color, region=(0, self.grid_size.y-1, self.grid_size.x-1, 1))
        self.screen.fill('?', fgcolor=color, region=(0, 0, 1, self.grid_size.y-1))
        self.screen.fill('?', fgcolor=color, region=(self.grid_size.x-1, 0, 1, self.grid_size.y))
        if not border_only:
            self.text(3, self.grid_size.y/2, ">>>>>", fgcolor=color)
            self.text(21, 2, "PLAYER:" + (" "*23) + "NUMBER:", fgcolor=color)


    def map_digits(self, digits):
        result = []
        for row in range(DIGIT_DIMENSIONS.y):
            result.append([])
        for digit in digits:
            #digit_map = DIGIT_MAPS[digit]
            digit_map = char_to_font(digit)
            for i, row in enumerate(digit_map):
                try:
                    result[i].extend(digit_map[i])
                    result[i].extend([" "])
                except IndexError:
                    pass

        result.append(list(" "*(self.grid_size.x-25)))
        return result

    def make_wheel(self):
        wheel_map = []
        y = 0
        for number in self.numbers:
            wheel_map.extend(self.map_digits(number))
            y += DIGIT_DIMENSIONS.y + 1
        return wheel_map

    def _print_wheel(self, wheel_map, start_row):
        center_row = self.grid_size.y/2
        step = 510/self.grid_size.y
        for row in range(self.grid_size.y-4):
            line = (start_row+row) % len(wheel_map)
            row_color = 250 - step * abs(center_row-row)
            self.text(15, row+3, ''.join(wheel_map[line]), fgcolor=(row_color, row_color, row_color, 0))

    def spin_wheel(self, wheel_map, rotations=1):
        start_time = time.time()
        center_row = self.grid_size.y/2
        current_row = 0
        wheel_index = 0
        wheel_tick = (DIGIT_DIMENSIONS.y) + 1
        ticks_per_rotation = len(self.numbers) * wheel_tick
        ticks_to_winner = (self.winner_index-2) * wheel_tick
        total_rotation_ticks = (ticks_per_rotation * rotations) + ticks_to_winner

        update_interval = 7
        slow_time = 0
        start_slowing = False
        print total_rotation_ticks
        slow_time_delta = 0.004
        for i in range(total_rotation_ticks):


            if i % (total_rotation_ticks/6) == 0 and update_interval > 2:
                update_interval -= 1
                print "SLOW DOWN!", update_interval

            if total_rotation_ticks - i <= 80 and not start_slowing:
                start_slowing = True

            if start_slowing:
                slow_time += slow_time_delta


            if i % (wheel_tick * 2) == 0:
                self.print_border("yellow")
            elif i % wheel_tick == 0:
                self.print_border("fuchsia")

            if i % wheel_tick == 0:
                wheel_index += 1
                #tick_sound.play()
                print self.numbers[wheel_index % len(self.numbers)], i, slow_time

            if i % update_interval == 0:
                self.screen.update()

            self._print_wheel(wheel_map, current_row)
            time.sleep(slow_time)

            current_row += 1


        print "WINNER:", self.winner
        SMS_Server.notify_winner(self.winner)
        end_time = time.time()
        print "WHEEL SPUN IN:", end_time - start_time

        while 1:
            self.screen.settint(200, 100, 50, (11, center_row - 3, self.grid_size.x-20, 8))
            self.screen.update()
            time.sleep(0.05)
            self.screen.settint(100, 150, 70, (11, center_row - 3, self.grid_size.x-20, 8))
            self.screen.update()
            time.sleep(0.05)

if __name__ == "__main__":
    wheel = Spinner_Wheel()
    #wheel.print_entrants()
    wheel_map = wheel.make_wheel()
    wheel.spin_wheel(wheel_map, rotations=1)