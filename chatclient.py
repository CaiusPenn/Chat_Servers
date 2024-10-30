import socket
import sys
import threading
from datetime import datetime
import time
from pathlib import Path

muted = False
start_time = None
mute_end_time = None
last_msg_time = None
connected = True

receive_thread = None
send_thread = None
check_afk_thread = None
switching = False
port = None
in_queue = False


def receive_messages(sock, username):
    global connected
    global port
    global switching

    while connected:
        global muted
        global start_time
        global muted_time
        global mute_end_time
        global in_queue
        try:
            data = sock.recv(1024)
            if not data:
                continue
            
            if data.decode() == "/shutdown":
                connected = False
                sock.shutdown(socket.SHUT_RDWR)
                sock.close()

            elif data.decode() == "in_queue":
                in_queue = True

            elif data.decode() == "not_in_queue":
                in_queue = False
            
            elif data.decode() == "/kick":
                client_quit(sock, username, data.decode())
                
            elif data.decode() == "/empty":
                client_empty(sock)
            elif data.decode()[0:5] == "muted":
                muted = True
                start_time = time.time()
                muted_time = int(data.decode()[len("muted "):])
                print("[Server message (" + datetime.now().strftime("%H:%M:%S") + \
                                    ")] You have been muted for " + str(muted_time) + " seconds.", flush=True)
                mute_end_time = time.time() + muted_time
                mute_thread = threading.Thread(target=client_muted, args=(muted_time, ))
                mute_thread.daemon = True
                mute_thread.start()

            elif "/switch" in data.decode():
                client_quit(sock, username, "/switch")
                port = data.decode()[len("/switch "):]
                switching = True
                break
            
            elif "invalid_switch" == data.decode():
                send_thread = threading.Thread(target=send_messages, args=(sock, username))
                send_thread.daemon = True
                send_thread.start()

            elif "abort" == data.decode()[0:5]:
                print(data.decode()[len("abort "):], flush=True)
                sock.shutdown(socket.SHUT_RDWR)
                sock.close()
                connected = False

            elif "file" == data.decode()[0:4]:
                rec_data =  data.decode()[len("file "):]
                file_name, file_content = rec_data.split(" ", 1)
                file_content = file_content.encode()
                
                file_path = "./" + file_name
                with open(file_path, "wb") as file:
                    try:
                        file.write(file_content)
                    except Exception as e:
                        pass
                file.close()
                
            else:
                print(data.decode().strip(), flush=True)
            
        except Exception as e:
           pass

def send_messages(sock, username):
    global connected
    global last_msg_time
    while connected:
        try:
            client_input = input().strip()
            last_msg_time = time.time()
        
            if (client_input == "/quit"):
                client_quit(sock, username, client_input)
            
            elif (client_input[0:8] == "/whisper" and len(client_input) > 8 and client_input[8] == " "):
                if not muted:
                    sock.sendall(client_input.encode())
                else:
                    print("[Server message (" + datetime.now().strftime("%H:%M:%S") \
                    + ")] You are still muted for " + str(round(mute_end_time - time.time())) + " seconds.", flush=True)

            elif client_input == "/list":
                sock.sendall(client_input.encode())

            elif client_input[0:7] == "/switch" and len(client_input) > 7 and client_input[7] == " ":
                sock.sendall(client_input.encode())
                break

            elif client_input[0:5] == "/send" and len(client_input) > 5 and client_input[5] == " ":
                data = client_input[len("/send "):].strip()
                target, file_path = data.split(" ", 1)
                file_path = file_path.strip()
                path = Path(file_path)
                
                if not path.is_file():
                    sock.sendall(("/send0 " + target + " " + file_path).encode())

                else:
                    sock.sendall(client_input.encode())
                    with open(file_path, 'rb') as f:
                        file_content = f.read()
                    file_name = file_path[file_path.rfind('/') + 1:]
                    server = "file_data " + file_name + " " + target + " "
                    sock.sendall(server.encode() + file_content)
                    f.close()

            else:  
                if not muted:    
                    message = "[" + username + " (" + datetime.now().strftime("%H:%M:%S") + ")] " + client_input
                    sock.sendall(message.encode())
                else:
                    
                    print("[Server message (" + datetime.now().strftime("%H:%M:%S") \
                    + ")] You are still muted for " + str(round(mute_end_time - time.time())) + " seconds.", flush=True)
    
        except Exception as e:
            pass

def client_switch(port, username):
    global last_msg_time
    global connected
    global receive_thread
    global send_thread
    global switching
    global check_afk_thread
    global in_queue
    switching = False
    in_queue = False

    server_address = ('localhost', port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(server_address)
    connected = True

    last_msg_time = time.time()
    sock.sendall(username.encode())
    
    receive_thread = threading.Thread(target=receive_messages, args=(sock, username))
    receive_thread.daemon = True
    receive_thread.start()

    send_thread = threading.Thread(target=send_messages, args=(sock, username))
    send_thread.daemon = True
    send_thread.start()

    check_afk_thread = threading.Thread(target=client_afk, args=(sock, username))
    check_afk_thread.daemon = True
    check_afk_thread.start()

    
def client_quit(sock, username, command):
    global connected
    if command == "/quit" or command == "/kick":
        connected = False
    else:
        command = "/quit"
    
    sock.sendall((command).encode())
    sock.shutdown(socket.SHUT_RDWR)
    sock.close()

def client_empty(sock):
    global connected
    connected = False
    sock.sendall(("/empty").encode())
    sock.shutdown(socket.SHUT_RDWR)
    sock.close()

def client_muted(muted_time):
    global muted
    global last_msg_time
    last_msg_time += muted_time
    while True:
        if (time.time() - start_time) >= muted_time:
            break
    muted = False

def client_afk(sock, username):
    global switching
    global connected
    global in_queue 
    while connected:
        if (time.time() - last_msg_time) >= 100 and not in_queue:
            connected = False
            sock.sendall(("/afk").encode())
            sock.shutdown(socket.SHUT_RDWR)
            sock.close()
            break
        elif switching:
            break
    

def main():
    global last_msg_time
    global send_thread
    global receive_thread
    global port
    global switching
    global connected

    try:
        server_address = ('localhost', int(sys.argv[1]))
        username = sys.argv[2] 
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(server_address)
    except Exception as e:
        exit(1)

    last_msg_time = time.time()
    sock.sendall(username.encode())

    receive_thread = threading.Thread(target=receive_messages, args=(sock, username))
    receive_thread.daemon = True
    receive_thread.start()

    send_thread = threading.Thread(target=send_messages, args=(sock, username))
    send_thread.daemon = True
    send_thread.start()

    check_afk_thread = threading.Thread(target=client_afk, args=(sock, username))
    check_afk_thread.daemon = True
    check_afk_thread.start()

    try:
        while connected:
            if switching:
                client_switch(int(port), username)
    except KeyboardInterrupt:
        pass
        
        
    
if __name__ == '__main__':
    main()
