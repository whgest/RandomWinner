# -*- coding: utf-8 -*-

import pygame
import pygcurse
import time, random
import pyfiglet
import pygame.mixer
import SMS_Server
import json
import string

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
    for line in f.renderText(string).replace("#", u"■").split("\n"):
        digit_map.append(list(line))
    return digit_map

class Spinner_Wheel():
    def __init__(self):
        self.random_key = ''
        self.entrants, self.numbers, self.winner, self.winner_index = self.import_numbers()
        self.grid_size = Point(80, 45)
        self.screen = pygcurse.PygcurseWindow(self.grid_size.x, self.grid_size.y, fullscreen=True)
        self.screen._autoupdate = False
        pygame.mixer.init()

        self.screen.update()
        pygame.display.set_caption("Wheel O' Winners")
        self.cell_size = (self.screen.cellheight, self.screen.cellwidth)

    def text(self, x, y, s, fgcolor="white", bgcolor="black"):
        self.screen.write(s, x=x, y=y, fgcolor=fgcolor, bgcolor=bgcolor)
        return


    def import_numbers(self):
        # with open("entrants.txt") as fin:
        #     entrants = json.load(fin)
        entrants = {}
        for i in range(50):
            random_initials = random.choice(string.uppercase) + random.choice(string.uppercase) + random.choice(string.uppercase)
            entrants[str(random.randint(1111111111, 9999999999))] = random_initials
        keys = entrants.keys()
        if len(keys) > 150:
            random.shuffle(keys)
            keys = keys[:149]


        random.seed(self.random_key)
        winner = random.choice(keys)
        winner_index = keys.index(winner)
        return entrants, keys, winner, winner_index

    #
    # def print_entrants(self):
    #     try:
    #         to_print = self.numbers[:149]
    #     except IndexError:
    #         to_print = self.numbers
    #     self.print_border(border_only=True)
    #     self.text(self.grid_size.x/2 - 4, 2, "PLAYERS:", fgcolor="yellow")
    #     col = -3
    #     for i, player in enumerate(to_print):
    #         if i % 30 == 0:
    #             col += 13
    #         self.text(col, i % 20 + 4, player, fgcolor="white")
    #     self.screen.update()
    #     #time.sleep(5)
    #     for col in range(len(self.numbers)/5):
    #         self.screen.settint(100, 150, 70, (11+col*13, 4, 1, 30))
    #         self.screen.settint(100, 150, 70, (16+col*13, 4, 1, 30))
    #     self.screen.update()
    #
    #
    #     self.text(self.grid_size.x/2 - 4, 34, "RANDOM SEED: ", fgcolor="yellow")
    #     row = 35
    #     col = 9
    #     for i, char in enumerate(self.random_seed):
    #         if i % 63 == 0:
    #             row += 1
    #             col = 9
    #         col += 1
    #         self.text(col, row, char, fgcolor="yellow")
    #
    #
    #     self.screen.update()
    #     pygcurse.waitforkeypress()

    def print_border(self, color="yellow", border_only=False, character="?"):
        self.screen.fill(character, fgcolor=color, region=(0, 0, self.grid_size.x-1, 1))
        self.screen.fill(character, fgcolor=color, region=(0, self.grid_size.y-1, self.grid_size.x-1, 1))
        self.screen.fill(character, fgcolor=color, region=(0, 0, 1, self.grid_size.y-1))
        self.screen.fill(character, fgcolor=color, region=(self.grid_size.x-1, 0, 1, self.grid_size.y))
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
            try:
                wheel_map.extend(self.map_digits(self.entrants[number][:3] + " " + number[-4:]))
            except IndexError:
                continue
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
        # pygame.mixer.music.load("gwoopie.ogg")
        # pygame.mixer.music.play()
        tick_sound = pygame.mixer.Sound("Pickup_Coin56.wav")
        wheel_win = pygame.mixer.Sound("wheel_finish.wav")
        start_time = time.time()
        center_row = self.grid_size.y/2
        current_row = 1
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
        self.print_border("yellow")
        self._print_wheel(wheel_map, current_row)
        self.screen.update()
        break_now2 = False
        while 1:
            for e in pygame.event.get():
                if e.type == pygame.KEYDOWN and e.key == 27:
                    exit()
                if e.type == pygame.KEYDOWN and e.key == 32:
                    print "spinnnnn"
                    break_now2 = True
            if break_now2:
                break

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
                tick_sound.play()
                print self.numbers[wheel_index % len(self.numbers)], i, slow_time

            if i % update_interval == 0:
                self.screen.update()

            self._print_wheel(wheel_map, current_row)

            if (total_rotation_ticks - i) > wheel_tick:
                time.sleep(slow_time)
            elif (total_rotation_ticks - i) == wheel_tick:
                time.sleep(1.5)
            else:
                pass

            current_row += 1

        tick_sound.play()

        print "WINNER:", self.winner
        #SMS_Server.notify_winner(self.winner)
        end_time = time.time()
        print "WHEEL SPUN IN:", end_time - start_time
        break_now = False
        wheel_win.play()
        while 1:
            self.screen.settint(200, 100, 50, (11, center_row - 4, self.grid_size.x-20, 8))
            self.print_border("yellow", character="*")
            self.screen.update()
            time.sleep(0.05)
            self.screen.settint(100, 150, 70, (11, center_row - 4, self.grid_size.x-20, 8))
            self.print_border("fuchsia", character="*")
            self.screen.update()
            time.sleep(0.05)
            for e in pygame.event.get():
                if e.type == pygame.KEYDOWN and e.key == 27:
                    exit()
                if e.type == pygame.KEYDOWN and e.key == 32:
                    print "spinnnnn"
                    break_now = True
            if break_now:
                break
        return


def main():
    while 1:
        print "initializing..."
        wheel = Spinner_Wheel()
        wheel_map = wheel.make_wheel()
        rotations = 50/len(wheel.entrants)
        if rotations < 1:
            rotations = 1
        wheel.spin_wheel(wheel_map, rotations=rotations)

if __name__ == "__main__":
    main()