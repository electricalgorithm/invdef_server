# Imports ##################################
import config
from utils import *
from gpio_function import gpio_function, gpio_reads
import socket
import threading
from time import sleep
from random import randint
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Hash import SHA256
from Crypto.Random import get_random_bytes
# ##########################################

process_list = []
AES_LENGTH = 256
DELAY_MIN = 0.1  # Delay between sending battery etc.
global IS_CLIENT_CONNECTED  # For communication between threads


# Networking Functions #####################
def receiver(conne, details):
    global process_list, IS_CLIENT_CONNECTED
    while True:
        # Data receiving
        try:
            data_recv = conne.recv(512)
            if data_recv:
                try:
                    nonce = data_recv[:16]
                    mac_tag = data_recv[16:32]
                    encrypted_message = data_recv[32:]
                    data_recv = decrypt(nonce, mac_tag, encrypted_message)
                except Exception as err:
                    throw("ERROR", err)
                    continue
                except IndexError:
                    throw("ERROR", "Data couldn't received correctly.")
        except Exception as err:
            throw("ERROR", err, f"{details[0]}")
            break

        # Checking for decryption -- and the trust.
        if not data_recv:
            continue

        # Splitting message into [ID, Type, Setting, Value]
        message = message_splitter(data_recv)

        # Disconnecting
        if message[2] == "!dis" and not message[3]:
            throw("CLIENT", f"Disconnected!", f"{details[0]}, {details[1]}")
            gpio_function("tempshield_status", "False")
            gpio_function("jammer_status", "False")
            gpio_function("light_status", "False")
            gpio_function("car_status", "False")
            conne.close()
            IS_CLIENT_CONNECTED = False
            throw("CLIENT", f"All the systems are closed!")
            break

        # Data Processing
        else:
            if message[1] == "CONF":
                throw("INFO", f"Received confirmation! ID: {message[0]} from {conne.getpeername()}")
                for item in process_list:
                    if int(message[0]) == item["conf"]:
                        threading.Thread(target=gpio_function, args=(item["setting"], item["value"])).start()
                        process_list.remove(item)

            else:
                # Calling GPIO functions. (If message is a INFO message)
                throw("INFO", f"Received! {message[2]}:{message[3]} from {conne.getpeername()}")
                gpio_function(message[2], message[3])

                # Sending confirmation
                send(conne=conne, typey="CONF", setting="confirmation", value=True, id_num=message[0])
                throw("INFO", f"Sent confirmation! ID: {message[0]}")
            continue


def send(conne, setting, value, typey="INFO", id_num=None):
    if not id_num:
        id_num = randint(11111, 99999)
    if typey == "INFO":
        process_list.append({
            "conf": int(id_num),
            "setting": setting,
            "value": value
        })

    try:
        message = message_creator(id_num, typey, setting, value)
    except ValueError:
        throw("ERROR", "The value or setting is incorrect.")
        return False

    enc_message, mactag, nonce = encrypt(message)
    message_to_send = nonce + mactag + enc_message

    # Sending message via thread
    while True:
        try:
            threading.Thread(target=conne.send, args=(message_to_send,), daemon=True).start()
        except OSError as err:
            if err.errno in [9, 32]:
                continue
        break
    return True


def encrypt(message_to_send):
    """
    A function to encrypt given data with AES_GDC method
    and using MainApp.AES_key.

    :returns encrypted message, mac tag and nonce
    :params message as string
    """
    aes_encrpytion_object = AES.new(AES_key, AES.MODE_GCM)
    encrypted_message, mac_tag = aes_encrpytion_object.encrypt_and_digest(message_to_send.encode(config.FORMAT))
    nonce = aes_encrpytion_object.nonce
    return encrypted_message, mac_tag, nonce


def decrypt(nonce, mac_tag, encrypted_message):
    """
    A function to decrypt given encrypted message with
    AES_GDG method via AES key, nonce and verifies
    with MAC tag.

    :params nonce, mac tag, encrypted message:
    :returns decrypted message: or 0 for uncorrect messages
    """
    decryptor = AES.new(AES_key, AES.MODE_GCM, nonce=nonce)
    try:
        decrypted_message_as_bytes = decryptor.decrypt_and_verify(encrypted_message, mac_tag)
    except ValueError:
        throw("ERROR", "The message is not trusted.")
        return False
    decrypted_message = decrypted_message_as_bytes.decode(config.FORMAT)
    return decrypted_message


def info_repeatedly(p_conn):
    global IS_CLIENT_CONNECTED
    info_types = ["battery_percentage",
                  "outside_temperature",
                  "inside_temperature",
                  "peltier_right",
                  "peltier_left",
                  "peltier_front",
                  "peltier_back",
                  "peltier_top"
                  ]

    while True:
        if not IS_CLIENT_CONNECTED:
            break

        sleep(60 * DELAY_MIN)
        for _type in info_types:
            val = gpio_reads(_type)
            print(f"{_type}::{val}")
            send(p_conn, f"{_type}", f"{val}")
            sleep(0.5)

# ##########################################


def get_command(param):
    while True:
        cmd = input("")
        if cmd == "!cx":
            send(param, "!dis", False, typey="CLIENT")
            param.close()
            throw("CLIENT", "Connection closed!")
        elif cmd == "auch!":
            print("Command panel is working.")
        elif cmd[:4] == "exc ":
            cmd = cmd[4:].split("/")
            gpio_function(cmd[0], cmd[1])
            send(param, f"{cmd[0]}", f"{cmd[1]}")
# ##########################################


if __name__ == "__main__":
    global IS_CLIENT_CONNECTED
    _PORT = config.PORT
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    while True:
        try:
            # Binding the socket to predetermined port;
            # if port is busy, we'll check the one upper.
            connection.bind((config.SERVER_ADDR, _PORT))
            break
        except OSError as error:
            if error.errno == 98:
                _PORT += 1
                continue
            else:
                throw("ERROR", error)
    connection.listen(1)

    throw("START", f"Server is listening on {socket.gethostbyname(socket.gethostname())}:{_PORT}")

    while True:
        # Let the clients connect server
        conn, data = connection.accept()
        throw("CLIENT", "New connection established.", f"{data[0]}:{data[1]}")

        # Creating the RSA key pair
        rasp_keys = RSA.generate(2048)
        rasp_public = rasp_keys.publickey().export_key()
        # Receiving public key from the mobile client
        public_mobile = conn.recv(450)
        # Sending our (server) public key to mobile client
        conn.send(rasp_public)
        # Receiving username and password as encrypted with RSA.
        login_details = [conn.recv(256), conn.recv(256)]
        # Creating a decrypter object for RSA-PKCS1-OAEP
        decryptor_for_login = PKCS1_OAEP.new(RSA.import_key(rasp_keys.export_key()))
        # Decrypting the login details. 0: Username, 1: Password (hashed)
        login_details = [decryptor_for_login.decrypt(login_details[0]), decryptor_for_login.decrypt(login_details[1])]

        # Creating the encryptor for AES key or error message
        encryptor_for_aes = PKCS1_OAEP.new(RSA.import_key(public_mobile))

        # Checking if the user is correct
        if login_details[0].decode("utf-8") == config.USER["username"] and login_details[1] == config.USER["pass"]:
            throw("CLIENT", "Connection confirmed.", f"{data[0]}:{data[1]}")
            # Creating random AES key
            AES_key = get_random_bytes(int(AES_LENGTH / 8))
            # Saving it for cameraSender.py
            with open(".session.enc", "bw") as key_file:
                key_file.write(AES_key)
            # Encrypting the AES key with RSA protocol to send it
            encrypted_AES_key = encryptor_for_aes.encrypt(AES_key)
            # Sending encrypted AES key
            conn.send(encrypted_AES_key)
        else:
            # If user is not correct
            throw("ERROR", "Connection is not confirmed.", f"{data[0]}:{data[1]}")
            # Encrypting the false message
            encrypted_false_msg = encryptor_for_aes.encrypt("False".encode(config.FORMAT))
            # Sending the false message and closing the socket
            conn.send(encrypted_false_msg)
            conn.close()
            continue

        IS_CLIENT_CONNECTED = True

        # Opening a thread for receiver function
        receiver_t = threading.Thread(target=receiver, args=(conn, data), daemon=True)
        receiver_t.start()
        
        # Opening a thread for get_command function
        cmd_r = threading.Thread(target=get_command, args=(conn,), daemon=True)
        cmd_r.start()

        # Opening a thread for sending gpio_inputs
        threading.Thread(target=info_repeatedly, args=(conn,), daemon=True).start()
