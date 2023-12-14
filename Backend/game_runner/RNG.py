# AUTHOR: JASPER WANG
# DATE: 24 FEB 2022
# GOAL: RNG FOR MY GAME

import random

def get_rolls(num_of_dices, max_value):
    result = []
    for i in range(num_of_dices):
        result.append(random.randint(1, max_value))
    result.sort(reverse=True)
    return result

def get_stars():
    return random.choices([1, 2, 3], weights=(30, 40, 30), k=1)[0]

def get_alliance_code():
    code = random.choices([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], weights=(10, 10, 10, 10, 10, 10, 10, 10, 10, 10), k=5)
    passcode = ""
    for digit in code:
        passcode += str(digit)
    return passcode

def get_insignias(player_number):
    choices = ["visual_assets/INSIGNIAS/insignia1.png", "visual_assets/INSIGNIAS/insignia2.png",
        "visual_assets/INSIGNIAS/insignia3.png", "visual_assets/INSIGNIAS/insignia4.png",
        "visual_assets/INSIGNIAS/insignia5.png", "visual_assets/INSIGNIAS/insignia6.png",
        "visual_assets/INSIGNIAS/insignia7.png", "visual_assets/INSIGNIAS/insignia8.png",
        "visual_assets/INSIGNIAS/insignia9.png", "visual_assets/INSIGNIAS/insignia10.png",
        "visual_assets/INSIGNIAS/insignia11.png", "visual_assets/INSIGNIAS/insignia12.png",
        "visual_assets/INSIGNIAS/insignia13.png", "visual_assets/INSIGNIAS/insignia14.png",
        "visual_assets/INSIGNIAS/insignia15.png", "visual_assets/INSIGNIAS/insignia16.png",
        "visual_assets/INSIGNIAS/insignia17.png", "visual_assets/INSIGNIAS/insignia18.png",
        "visual_assets/INSIGNIAS/insignia19.png", "visual_assets/INSIGNIAS/insignia20.png",
        "visual_assets/INSIGNIAS/insignia21.png", "visual_assets/INSIGNIAS/insignia22.png",
        "visual_assets/INSIGNIAS/insignia23.png"]
    random.shuffle(choices)
    return choices[0:player_number]

def get_capitals(player_number):

    choices = [
        "visual_assets/CAPITALS/capital1.png",
        "visual_assets/CAPITALS/capital2.png",
        "visual_assets/CAPITALS/capital3.png",
        "visual_assets/CAPITALS/capital4.png",
        "visual_assets/CAPITALS/capital5.png",
        "visual_assets/CAPITALS/capital6.png",
        "visual_assets/CAPITALS/capital7.png",
        "visual_assets/CAPITALS/capital8.png",
        "visual_assets/CAPITALS/capital9.png",
        "visual_assets/CAPITALS/capital10.png",
        "visual_assets/CAPITALS/capital11.png",
        "visual_assets/CAPITALS/capital12.png",
        "visual_assets/CAPITALS/capital13.png",
        "visual_assets/CAPITALS/capital14.png",
        "visual_assets/CAPITALS/capital15.png",
        "visual_assets/CAPITALS/capital16.png",
        "visual_assets/CAPITALS/capital17.png"
    ]

    random.shuffle(choices)
    return choices[0:player_number]

def get_ps(choices):
    random.shuffle(choices)
    return choices[0:1][0]

