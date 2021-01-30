def save_settings():
    import csv, os

    path = os.getcwd()
    with open(path + "//Data//setting_profile.csv", mode = 'w', encoding = 'utf-8') as data:
        wrtier = csv.writer(data, delimiter=',',lineterminator = '\n')
        wrtier.writerow(['Resolution', 'FPS'])
        wrtier.writerow([CRT_REZ, CRT_FPS])

def load_settings():
    global CRT_REZ, CRT_FPS

    import csv, os
    path = os.getcwd()
    if os.path.isfile(path + "//Data//setting_profile.csv"):
        with open(path + "//Data//setting_profile.csv", mode = 'r', encoding = 'utf-8') as data:
            reader = csv.DictReader(data)
            for row in reader:
                CRT_REZ = int(row['Resolution'])
                CRT_FPS = int(row['FPS'])

                print(CRT_REZ,CRT_FPS)


"""

GLOBALS / CONSTANTS

"""

RUNNING = True

TICK_SPEED_MENU = 27

DEFAULT_SIZE = 1280 * 720
DEFAULT_FONTS = [
    ['main_titles','comicsans', 45],
    ['menu_titles','comicsans', 30],
    ['button_font','arial', 23],
]

CRT_REZ, CRT_FPS = 0, 0

APPROVED_RESOLUTIONS =[
    [1280, 720],
    [1920, 1080],
    [2560, 1440],

]

APPROVED_FPS_RATES = [
    30, 60, 90, 120, 150
]



