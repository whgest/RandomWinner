# -*- coding: utf-8 -*-

import pygame
import pygcurse
import time, random
import pyfiglet
import pygame.mixer

class Point():
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return "[%s, %s]" % (self.x, self.y)


DIGIT_MAPS = {
    "digit_dimensions": Point(5, 5),
    "-": [
    [u' ', u' ', u' ', u' ', u' '],
    [u' ', u' ', u' ', u' ', u' '],
    [u' ', u'█', u'█', u'█', u' '],
    [u' ', u' ', u' ', u' ', u' '],
    [u' ', u' ', u' ', u' ', u' '],
    ],
    "0": [
    [u' ', u'█', u'█', u'█', u' '],
    [u'█', u' ', u' ', u' ', u'█'],
    [u'█', u' ', u'█', u' ', u'█'],
    [u'█', u' ', u' ', u' ', u'█'],
    [u' ', u'█', u'█', u'█', u' '],
    ],
    "1": [
    [u' ', u'▀', u'█', u' ', u' '],
    [u' ', u' ', u'█', u' ', u' '],
    [u' ', u' ', u'█', u' ', u' '],
    [u' ', u' ', u'█', u' ', u' '],
    [u' ', u'▄', u'█', u'▄', u' '],
    ],
    "2": [
    [u'█', u'█', u'█', u'█', u' '],
    [u' ', u' ', u' ', u' ', u'█'],
    [u' ', u'█', u'█', u'█', u' '],
    [u'█', u' ', u' ', u' ', u' '],
    [u'█', u'█', u'█', u'█', u'█'],
    ],
    "3": [
    [u'█', u'█', u'█', u'█', u' '],
    [u' ', u' ', u' ', u' ', u'█'],
    [u' ', u'█', u'█', u'█', u' '],
    [u' ', u' ', u' ', u' ', u'█'],
    [u'█', u'█', u'█', u'█', u' '],
    ],
    "4": [
    [u' ', u' ', u'█', u'█', u' '],
    [u' ', u'█', u' ', u'█', u' '],
    [u'█', u' ', u' ', u'█', u' '],
    [u'█', u'█', u'█', u'█', u'█'],
    [u' ', u' ', u' ', u'█', u' '],
    ],
    "5": [
    [u'█', u'█', u'█', u'█', u'█'],
    [u'█', u' ', u' ', u' ', u' '],
    [u'█', u'█', u'█', u'█', u' '],
    [u' ', u' ', u' ', u' ', u'█'],
    [u'█', u'█', u'█', u'█', u' '],
    ],
    "6": [
    [u' ', u'█', u'█', u'█', u' '],
    [u'█', u' ', u' ', u' ', u' '],
    [u'█', u'█', u'█', u'█', u' '],
    [u'█', u' ', u' ', u' ', u'█'],
    [u' ', u'█', u'█', u'█', u' '],
    ],
    "7": [
    [u' ', u'█', u'█', u'█', u'█'],
    [u' ', u' ', u' ', u' ', u'█'],
    [u' ', u' ', u' ', u'█', u' '],
    [u' ', u' ', u'█', u' ', u' '],
    [u' ', u' ', u'█', u' ', u' '],
    ],
    "8": [
    [u' ', u'█', u'█', u'█', u' '],
    [u'█', u' ', u' ', u' ', u'█'],
    [u' ', u'█', u'█', u'█', u' '],
    [u'█', u' ', u' ', u' ', u'█'],
    [u' ', u'█', u'█', u'█', u' '],
    ],
    "9": [
    [u' ', u'█', u'█', u'█', u' '],
    [u'█', u' ', u' ', u' ', u'█'],
    [u' ', u'█', u'█', u'█', u'█'],
    [u' ', u' ', u' ', u' ', u'█'],
    [u' ', u'█', u'█', u'█', u' '],
    ],
}



class Spinner_Wheel():
    def __init__(self):
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
        #TODO: Import/read file
        numbers = []
        for i in range(10):
            numbers.append(str(random.randint(111, 999)) + "-" + str(random.randint(1111, 9999)))
        random.shuffle(numbers)
        winner = random.choice(numbers)
        winner_index = numbers.index(winner)
        return numbers, winner, winner_index

    def print_border(self, color="yellow"):
        self.screen.fill('?', fgcolor=color, region=(0, 0, self.grid_size.x-1, 1))
        self.screen.fill('?', fgcolor=color, region=(0, self.grid_size.y-1, self.grid_size.x-1, 1))
        self.screen.fill('?', fgcolor=color, region=(0, 0, 1, self.grid_size.y-1))
        self.screen.fill('?', fgcolor=color, region=(self.grid_size.x-1, 0, 1, self.grid_size.y))
        self.text(3, self.grid_size.y/2, ">>>>>", fgcolor=color)


    def map_digits(self, digits):
        result = []
        for row in range(DIGIT_MAPS["digit_dimensions"].y):
            result.append([])
        for digit in digits:
            digit_map = DIGIT_MAPS[digit]
            for i, row in enumerate(digit_map):
                result[i].extend(digit_map[i])
                result[i].extend([" "])
        result.append(list(" "*(self.grid_size.x-25)))
        return result

    def make_wheel(self):
        wheel_map = []
        y = 0
        for number in self.numbers:
            wheel_map.extend(self.map_digits(number))
            y += DIGIT_MAPS["digit_dimensions"].y + 1
        return wheel_map

    def _print_wheel(self, wheel_map, start_row):
        center_row = self.grid_size.y/2
        step = 510/self.grid_size.y
        for row in range(self.grid_size.y-3):
            line = (start_row+row) % len(wheel_map)
            row_color = 250 - step * abs(center_row-row)
            self.text(15, row+1, ''.join(wheel_map[line]), fgcolor=(row_color, row_color, row_color, 0))

    def spin_wheel(self, wheel_map, rotations=1, speed=0, slow_speed=.002):
        # pygame.mixer.music.load("gwoopie.ogg")
        # pygame.mixer.music.play()
        tick_sound = pygame.mixer.Sound("wheel_tick.wav")
        current_row = 0
        wheel_index = 2
        wheel_tick = (DIGIT_MAPS["digit_dimensions"].y) + 1
        ticks_per_rotation = len(self.numbers) * wheel_tick
        total_rotation_ticks = ticks_per_rotation * rotations

        for i in range(total_rotation_ticks):

            if i % (wheel_tick * 2) == 0:
                self.print_border("yellow")
            elif i % wheel_tick == 0:
                self.print_border("fuchsia")

            if i % wheel_tick == 0:
                wheel_index += 1
                tick_sound.play()
                print self.numbers[wheel_index % len(self.numbers)], i

            self._print_wheel(wheel_map, current_row)
            self.screen.update()
            time.sleep(speed)
            current_row += 1

        ticks_to_winner = wheel_tick * (self.winner_index-3)
        slow_wheel_ticks = ticks_per_rotation + ticks_to_winner

        for i in range(slow_wheel_ticks):

            if i % (wheel_tick * 2) == 0:
                self.print_border("yellow")
            elif i % wheel_tick == 0:
                self.print_border("fuchsia")

            if i % wheel_tick == 0:
                wheel_index += 1
                tick_sound.play()
                print self.numbers[wheel_index % len(self.numbers)], i

            self._print_wheel(wheel_map, current_row)
            self.screen.update()
            time.sleep(slow_speed * i)  # better slowing equation here?
            current_row += 1

        print "WINNER:", self.winner
        pygcurse.waitforkeypress()





if __name__ == "__main__":
    wheel = Spinner_Wheel()
    wheel_map = wheel.make_wheel()
    wheel.spin_wheel(wheel_map, rotations=1)