import config
from utils import *


def gpio_function(setting, value):
    # Temperature Shield
    if setting == "tempshield_status":
        if value == "True":
            # tempshield_status = True olunca yapılacak işlemler buraya.
            throw("INFO", "Temperature shield is activated.")
        elif value == "False":
            # tempshield_status = False olunca yapılacak işlemler buraya.
            throw("INFO", "Temperature shield is inactivated.")

    # Jammer
    elif setting == "jammer_status":
        if value == "True":
            # jammer_status = True olunca yapılacak işlemler buraya.
            throw("INFO", "Jammer is activated.")
        elif value == "False":
            # jammer_status = False olunca yapılacak işlemler buraya.
            throw("INFO", "Jammer is inactivated.")

    # Lights
    elif setting == "light_status":
        if value == "True":
            # light_status = True olunca yapılacak işlemler buraya.
            throw("INFO", "Lights are activated.")
        elif value == "False":
            # light_status = False olunca yapılacak işlemler buraya.
            throw("INFO", "Lights are inactivated.")

    # Engine
    elif setting == "car_status":
        if value == "True":
            # car_status = True olunca yapılacak işlemler buraya.
            throw("INFO", "Engine is activated.")
        elif value == "False":
            # car_status = False olunca yapılacak işlemler buraya.
            throw("INFO", "Engine is inactivated.")

    # Direction
    elif setting == "direction":
        if value == "forward":
            # direction = forward olunca yapılacak işlemler buraya.
            throw("INFO", "Forward!")
        elif value == "backward":
            # direction = backward olunca yapılacak işlemler buraya.
            throw("INFO", "Backward!")
        elif value == "stop":
            # direction = stop olunca yapılacak işlemler buraya.
            throw("INFO", "Stop!")

    elif setting == "direction_angle":
        value = int(value)
        # direction açısı değişince yapılacak işlemler buraya.
        throw("INFO", f"Directon angle: {value}")