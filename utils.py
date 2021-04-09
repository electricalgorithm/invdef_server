import config
from time import asctime, localtime, time
from termcolor import colored


def throw(msg_type, message, conne=None):
    logfile = open(f"{config.LOGFILE_R}.log", "a")
    if msg_type == "ERROR":
        color = "red"
    elif msg_type == "INFO" or msg_type == "MSG":
        color = "grey"
    elif msg_type == "START":
        color = "green"
    elif msg_type == "STOP":
        color = "green"
    elif msg_type == "CLIENT":
        color = "cyan"
    else:
        print("Something wrong with \"throw\" function.\nCheck the code.")
        color = "magenta"

    _time = asctime(localtime(time()))
    if conne:
        print(colored(f"[{msg_type}] {message} ({conne})", color))
        logfile.write(f"[{msg_type}][{_time}] {message} ({conne}\n")
    else:
        print(colored(f"[{msg_type}] {message}", color))
        logfile.write(f"[{msg_type}][{_time}] {message}\n")

    logfile.close()


def setting_str2num(setting):
    if setting == "tempshield_status":
        return 1
    elif setting == "jammer_status":
        return 2
    elif setting == "light_status":
        return 3
    elif setting == "car_status":
        return 4
    elif setting == "direction":
        return 5
    elif setting == "direction_angle":
        return 6
    elif setting == "confirmation":
        return 7
    elif setting == "battery_percentage":
        return 8
    elif setting == "outside_temperature":
        return 9
    elif setting == "inside_temperature":
        return 10
    elif setting == "peltier_right":
        return 11
    elif setting == "peltier_left":
        return 12
    elif setting == "peltier_front":
        return 13
    elif setting == "peltier_back":
        return 14
    elif setting == "peltier_top":
        return 15
    elif setting == "!dis":
        return 16
    else:
        raise ValueError("The setting isn't a known string.")


def setting_num2str(setting):
    if setting == 1:
        return "tempshield_status"
    elif setting == 2:
        return "jammer_status"
    elif setting == 3:
        return "light_status"
    elif setting == 4:
        return "car_status"
    elif setting == 5:
        return "direction"
    elif setting == 6:
        return "direction_angle"
    elif setting == 7:
        return "confirmation"
    elif setting == 8:
        return "battery_percentage"
    elif setting == 9:
        return "outside_temperature"
    elif setting == 10:
        return "inside_temperature"
    elif setting == 11:
        return "peltier_right"
    elif setting == 12:
        return "peltier_left"
    elif setting == 13:
        return "peltier_front"
    elif setting == 14:
        return "peltier_back"
    elif setting == 15:
        return "peltier_top"
    elif setting == 16:
        return "!dis"
    else:
        raise ValueError("The setting isn't a known integer.")


def type_str2num(typey):
    if typey == "ERROR":
        return 1
    elif typey == "INFO":
        return 2
    elif typey == "START":
        return 3
    elif typey == "STOP":
        return 4
    elif typey == "CLIENT":
        return 5
    elif typey == "CONF":
        return 6
    else:
        raise ValueError("The value isn't a type string.")


def type_num2str(typey):
    if typey == 1:
        return "ERROR"
    elif typey == 2:
        return "INFO"
    elif typey == 3:
        return "START"
    elif typey == 4:
        return "STOP"
    elif typey == 5:
        return "CLIENT"
    elif typey == 6:
        return "CONF"
    else:
        raise ValueError("The value isn't a type integer.")


def message_creator(id_number, type_str, setting_str, value):
    message = str(id_number) + ":" + \
              str(type_str2num(type_str)) + ":" + \
              str(setting_str2num(setting_str)) + ":" + \
              str(value)
    return message


def message_splitter(message):
    array = message.split(":")
    array[0] = int(array[0])
    array[1] = type_num2str(int(array[1]))
    array[2] = setting_num2str(int(array[2]))

    if array[3].isnumeric():
        array[3] = int(array[3])
    elif array[3].lower() == 'true':
        array[3] = True
    elif array[3].lower() == 'false':
        array[3] = False

    return array
