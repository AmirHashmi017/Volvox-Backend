import pyautogui
import pyperclip
import time
import Nova_music

# -------------------------------
# Global Variables
# -------------------------------
name_web: str = ""
like_w: str = ""


# -------------------------------
# Utility Functions
# -------------------------------
def log_action(action: str):
    pass


# -------------------------------
# Mouse Control Functions
# -------------------------------
def desktop_fun():
    try:
        pyautogui.click(1891 ,21)
        time.sleep(1)
        log_action("Desktop activated")
    except:
        pass


def min_fun():
    try:
        pyautogui.click(1780,19)
        time.sleep(1)
        log_action("Window minimized")
    except :
        pass


def pau_play_fun():
    try:
        pyautogui.click(641, 485)
        time.sleep(1)
        log_action("Play/Pause toggled")
    except :
        pass


def mute_fun():
    try:
        pyautogui.click(369,821)
        time.sleep(2)
        log_action("Mute/Unmute toggled")
    except :
        pass


def fullscreen_fun():
    try:
        pyautogui.click(1173, 818)
        time.sleep(1)
        log_action("Fullscreen activated")
    except :
        pass


def exit_the_full_screen_fun():
    try:
        pyautogui.click(1858, 1046)
        time.sleep(1)
        log_action("Exited fullscreen")
    except :
        pass


# -------------------------------
# Tab and Web Control
# -------------------------------
def w_filter(word):
    return word in like_w


def check_web_point():
    global like_w

    tab_positions = {
        0: (148, 20),
        1: (464, 22),
        2: (757, 25),
        3: (1071, 21),
        4: (1385, 18),
    }

    for idx, (x, y) in tab_positions.items():
        try:

            pyautogui.click(x, y)
            time.sleep(1.2)


            pyautogui.click(581, 78)
            time.sleep(0.8)


            pyautogui.hotkey('ctrl', 'a')
            pyautogui.hotkey('ctrl', 'c')
            time.sleep(0.8)


            like_w = pyperclip.paste()


            temp_list = list(filter(w_filter, Nova_music.list_web))
            if temp_list:
                found_site = temp_list[0]


                if found_site == name_web:
                    pyautogui.hotkey('ctrl', 'w')
                    log_action("Tab closed successfully")
                    time.sleep(1.2)
                    return
        except :
            pass



def cliking():
    log_action("Tab checking initiated")
    check_web_point()
