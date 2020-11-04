import time
from typing import List
import csv
import json
from random import randint, random, uniform

import cv2
import numpy as np
from mss import mss
import pytesseract
from fuzzywuzzy import fuzz
import mouse

from clicktest import PressKey, ReleaseKey

OUTPUT = "horsies.csv"
with open("horses.json", "r") as horse_in:
    HORSIES = json.load(horse_in)
with open("known.json", "r") as known_in:
    KNOWN_FIXES = json.load(known_in)


class Horse:
    def __init__(self, name:str, odd:int):
        self.name = name
        self.odd = odd


class Race:
    def __init__(self, horses: List[Horse]):
        self.horses = horses
        self.winner = None

    def report(self, winner: str):
        winning_horse = [horse for horse in self.horses if horse.name == winner.name]
        if len(winning_horse) == 0:

            return False

        else:
            self.winner = winning_horse[0]
            outline = []
            for horse in self.horses:
                outline += [horse.name, horse.odd]
            outline += [self.winner.name, self.winner.odd]
            print(outline)
            with open(OUTPUT, mode='a') as out:
                out_writer = csv.writer(out, delimiter=',', quotechar='"')
                out_writer.writerow(outline)

            return True

    def bet(self):

        horse_odds = [horse.odd for horse in self.horses]
        sorted_odds = sorted(horse_odds)

        chosen_horse = horse_odds.index(sorted_odds[0])
        horse_picker(chosen_horse)

        if sorted_odds[1] > 2:
            increase_bet()

        place_bet()


def click():
    PressKey()
    time.sleep(0.1)
    ReleaseKey()


def img_to_text(img):
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    gray, img_bin = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    gray = cv2.bitwise_not(img_bin)
    kernel = np.ones((2, 1), np.uint8)
    img = cv2.erode(gray, kernel, iterations=1)
    img = cv2.dilate(img, kernel, iterations=1)

    out_below = pytesseract.image_to_string(img)
    return out_below


def start_to_horses(img):
    horses = [None] * 6
    for i in range(6):
        horse_img = img[290 + 122 * i:330 + 122 * i, 175:500]
        horse = img_to_text(horse_img).replace("\n", "")
        horse.upper()

        if horse not in HORSIES.keys():

            if horse in KNOWN_FIXES.keys():
                horse = KNOWN_FIXES[horse]

            else:

                best_match = 0
                best_key = None

                for key in HORSIES.keys():
                    try:
                        ratio = fuzz.ratio(horse, key)
                    except:
                        print("read failed")
                        best_key = input(horse + " should be :")
                        best_key = best_key.upper()
                        break
                    if ratio > best_match:
                        best_key = key
                        best_match = ratio
                print(best_key, type(best_key), horse, type(horse))
                KNOWN_FIXES.update({horse: best_key})
                with open("known.json", "w") as known_in:
                    json.dump(KNOWN_FIXES, known_in)
                horse = best_key

        horses[i] = Horse(horse, HORSIES[horse])

    print([horse.name for horse in horses])

    return horses


def end_to_horses(img):
    horse = img[600:660, 720:1200]
    winner = img_to_text(horse).replace("\n", "")
    winner.upper()
    if len(winner) <= 1:
        return None
    if winner not in HORSIES.keys():

        if winner in KNOWN_FIXES.keys():
            winner = KNOWN_FIXES[winner]

        else:
            best_match = 0
            best_key = None

            for key in HORSIES.keys():
                try:
                    ratio = fuzz.ratio(winner, key)
                except:
                    raise RuntimeError
                else:
                    print("read failed")
                    best_key = input(winner + " should be :")
                    best_key = best_key.upper()
                    break
                if ratio > best_match:
                    best_key = key
                    best_match = ratio

            print(best_key, type(best_key), winner, type(winner))
            KNOWN_FIXES.update({winner: best_key})
            with open("known.json", "w") as known_in:
                json.dump(KNOWN_FIXES, known_in)
            winner = best_key


    winner = Horse(winner, HORSIES[winner])

    return winner


def start_bet():
    pos_x = [3780, 4220]
    pos_y = [1040, 1115]
    mouse.move(randint(pos_x[0], pos_x[1]),
               randint(pos_y[0], pos_y[1]),
               absolute=True,
               duration=random()
               )
    time.sleep(0.3)
    click()
    time.sleep(0.3)


def horse_picker(horse_number: int):
    horse_x = [2620, 3170]
    horse_position = [[460, 560],
                      [585, 685],
                      [710, 810],
                      [835, 935],
                      [960, 1060],
                      [1085, 1185]]
    mouse.move(randint(horse_x[0], horse_x[1]),
               randint(horse_position[horse_number][0], horse_position[horse_number][1]),
               absolute=True,
               duration=random()
               )
    time.sleep(0.3)
    click()
    time.sleep(0.3)


def increase_bet():

    increase_x = randint(4060, 4095)
    increase_y = randint(670, 715)
    mouse.move(increase_x, increase_y, absolute=True, duration=random())

    for i in range(30):
        click()
        time.sleep(uniform(0.1, 0.2))


def place_bet():
    pos_x = [3540,4140]
    pos_y = [920, 1000]
    mouse.move(randint(pos_x[0], pos_x[1]),
               randint(pos_y[0], pos_y[1]),
               absolute=True,
               duration=random()
               )
    time.sleep(0.3)
    click()
    time.sleep(0.3)


def bet_again():

    pos_x = [3285, 3745]
    pos_y = [1130, 1210]
    mouse.move(randint(pos_x[0], pos_x[1]),
               randint(pos_y[0], pos_y[1]),
               absolute=True,
               duration=random()
               )
    time.sleep(0.3)
    click()
    time.sleep(0.3)


def main():
    time.sleep(5)
    reference_pixel_pos = [200,800]
    race = None
    with mss() as sct:
        mon = sct.monitors[1]
        while True:
            img = sct.grab(mon)
            img = np.array(img)
            reference_pixel = img[reference_pixel_pos[0], reference_pixel_pos[1]]

            if reference_pixel[0] == 0:
                # Betting
                #if race is None:
                    # Initial betting
                horses = start_to_horses(img)
                race = Race(horses)
                race.bet()

            elif reference_pixel[0] == 27:
                # Reference Pixel 27 racing
                pass
            elif reference_pixel[0] == 249:
                # Reference Pixel 249 Snapshot
                pass
            elif reference_pixel[0] == 243:
                # Reference Pixel 243 Photo finish
                pass
            elif reference_pixel[0] == 16:
                # Post Match
                if race is not None:
                    winner = end_to_horses(img)

                    if winner is not None and race.report(winner):
                        race = None
                        bet_again()

            elif reference_pixel[0] == 55:
                # Base Screen
                time.sleep(random())
                start_bet()

            time.sleep(1)


if __name__ == "__main__":

    main()

