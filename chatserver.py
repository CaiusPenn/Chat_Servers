import threading
import socket
import sys
from datetime import datetime
import time

waiting_queue = {}
max_capacities = {}
channels = {}
kicking = []
sockets = {}
ports = {}
connection_threads = []
thread_channels = []
running = True

def read_config_file(filename):
    channels_info = []
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('channel'):
                _, channel_name, channel_port, channel_capacity = line.split()
                if not channel_name[0].isalpha():
                    sys.exit(1)               
                if int(channel_capacity) < 0:
                    sys.exit(1)
                if int(channel_port) == 0:
                    sys.exit(1)
                for channel in channels_info:
                    if channel_name in channel or channel_port in channel:
                        sys.exit(1) 
                channels_info.append((channel_name, channel_port, channel_capacity))
    if len(channels_info) < 3:
        sys.exit(1) 
    return channels_info

def setup(channel_info):
    ports[channel_info[0]] = channel_info[1]
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('localhost', int(channel_info[1])))
    sock.listen(int(channel_info[2]))
    handle_client(channel_info[0], sock, int(channel_info[2]))

    
def handle_client(channel_name, sock, max_capacity):
    channels[channel_name] = []
    max_capacities[channel_name] = max_capacity
    sockets[channel_name] = sock
    sock.settimeout(1)
    
    for client_name in channels.keys():
        waiting_queue[client_name] = []
    while running:
        valid = True
        
        try:
            conn, addr = sock.accept()
            data = conn.recv(1028)
            username = data.decode()
        except socket.timeout:
            continue

        try:
            for connections in channels[channel_name]:
                if connections[1] == username:
                    same_user = "[Server message (" + datetime.now().strftime("%H:%M:%S") + \
                            ")] Cannot connect to the " + channel_name + " channel." 
                    conn.sendall(("abort " + same_user).encode()) 
                    valid = False
            
            for connections in waiting_queue[channel_name]:
                if connections[1] == username:
                    same_user = "[Server message (" + datetime.now().strftime("%H:%M:%S") + \
                            ")] Cannot connect to the " + channel_name + " channel." 
                    conn.sendall(("abort " + same_user).encode())  
                    valid = False

            if not valid:
                continue
                    
            message = "[Server message (" + datetime.now().strftime("%H:%M:%S") + \
                ")] Welcome to the " + channel_name + " channel, " + username + ".\n"
            conn.send(message.encode())
            
            if len(channels[channel_name]) >= max_capacity:
                waiting_queue[channel_name].append((conn, username))
                waiting_message = "[Server message (" + datetime.now().strftime("%H:%M:%S") + \
                ")] You are in the waiting queue and there are " + str(len(waiting_queue[channel_name])-1) + " user(s) ahead of you."
                conn.sendall(waiting_message.encode())
                time.sleep(0.1)
                conn.sendall("in_queue".encode())
            else:
                channels[channel_name].append((conn, username))
                client_message = "[Server message (" + datetime.now().strftime("%H:%M:%S") + \
                ")] " + username + " has joined the channel."
                print("[Server message (" + datetime.now().strftime("%H:%M:%S") + \
                ")] " + username + " has joined the " + channel_name + " channel.", flush=True)
                for client in channels[channel_name]:
                    client[0].sendall(client_message.encode())
            
            t = threading.Thread(target=manage_connections, args=(channel_name, 
                                                        conn, channels, username, waiting_queue))
            t.start()
            connection_threads.append(t)
        except Exception:
            pass
    sock.close()
    
    
def client_whisper(data, channel_name, conn, channels, username):
    here = False
    whisper = data.decode()[len("/whisper "):].strip()
    receive_username, message = whisper.split(" ", 1)
    
    if receive_username != username:
        for conn_tuple in channels[channel_name]:
            if conn_tuple[1] == receive_username:
                whisper_message = "[" + username + " whispers to you: (" \
                                    + datetime.now().strftime("%H:%M:%S") + ")] " + message
                conn_tuple[0].sendall(whisper_message.encode())
                here = True

        if here == False: 
            whisper_message = "[Server message (" + datetime.now().strftime("%H:%M:%S") \
                    + ")] " + receive_username + " is not here."
            conn.sendall(whisper_message.encode())
    
        print("[" + username + " whispers to " + receive_username + ": (" \
            + datetime.now().strftime("%H:%M:%S") + ")] " + message, flush=True)
    
def client_switch(data, channel_name, conn, channels, username):
    switch_channel = data.decode()[len("/switch "):]
    valid = True

    if switch_channel.strip() not in channels.keys():
            channel_not_exist = "[Server message (" + datetime.now().strftime("%H:%M:%S") \
                        + ")] " + switch_channel + " does not exist."
            conn.sendall(channel_not_exist.encode())
            valid = False
    
    if valid:
        for connections in channels[switch_channel]:
            if connections[1] == username:
                invalid_switch = "[Server message (" + datetime.now().strftime("%H:%M:%S") \
                        + ")] Cannot switch to the " + switch_channel + " channel."
                conn.sendall(invalid_switch.encode())
                valid = False

        for connections in waiting_queue[switch_channel]:
            if connections[1] == username:
                invalid_switch = "[Server message (" + datetime.now().strftime("%H:%M:%S") \
                        + ")] Cannot switch to the " + switch_channel + " channel."
                conn.sendall(invalid_switch.encode())
                valid = False
        
    if valid:
        conn.sendall(("/switch " + str(ports[switch_channel.strip()])).encode())
    if not valid:
        time.sleep(0.1)
        conn.sendall("invalid_switch".encode())
     
def quit_management(channel_name, conn, channels, username, waiting_queue, command):
    global kicking
    client_index = 0
    
    if (conn,username) in waiting_queue[channel_name]:
        client_index = waiting_queue[channel_name].index((conn, username))
        waiting_queue[channel_name].remove((conn, username))
        message = "[Server message (" + datetime.now().strftime("%H:%M:%S") + \
        ")] " + username + " has left the channel."
        print(message, flush=True)

    else:
        channels[channel_name].remove((conn, username))
        if command != "/empty" and command != "/afk":
            message = "[Server message (" + datetime.now().strftime("%H:%M:%S") + \
                ")] " + username + " has left the channel."
            
            for clients in channels[channel_name]:
                clients[0].sendall(message.encode())
            if command != "/kick":
                print(message, flush=True)

        if command == "/afk":
            afk_message = "[Server message (" + datetime.now().strftime("%H:%M:%S") \
                    + ")] " + username + " went AFK."
            print(afk_message, flush=True)

            for clients in channels[channel_name]:
                if clients[0] != conn:
                    clients[0].sendall(afk_message.encode())
        
        if len(waiting_queue[channel_name]) > 0:
            next_client = waiting_queue[channel_name][0][1]
            next_client_conn = waiting_queue[channel_name][0][0]
            channels[channel_name].append(waiting_queue[channel_name].pop(0))
            client_message = "[Server message (" + datetime.now().strftime("%H:%M:%S") + \
            ")] " + next_client + " has joined the channel."
            print("[Server message (" + datetime.now().strftime("%H:%M:%S") + \
            ")] " + next_client + " has joined the " + channel_name + " channel.", flush=True)
            next_client_conn.sendall("not_in_queue".encode())
            for client in channels[channel_name]:
                    client[0].sendall(client_message.encode())

    for client in waiting_queue[channel_name]:
        if waiting_queue[channel_name].index(client) >= client_index:
            waiting_message = "[Server message (" + datetime.now().strftime("%H:%M:%S") + \
            ")] You are in the waiting queue and there are " + str(len(waiting_queue[channel_name])-1) + " user(s) ahead of you."
            client[0].sendall(waiting_message.encode())
    kicking = []
    conn.shutdown(socket.SHUT_RDWR)
    conn.close()

        
def manage_connections(channel_name, conn, channels, username, waiting_queue):

    while running:
        try:
            data = conn.recv(1028)

            if data.decode() == "":                
                channels[channel_name].remove((conn, username))

                if len(waiting_queue[channel_name]) > 0:
                    next_client = waiting_queue[channel_name][0][1]
                    next_client_conn = waiting_queue[channel_name][0][0]
                    channels[channel_name].append(waiting_queue[channel_name].pop(0))
                    client_message = "[Server message (" + datetime.now().strftime("%H:%M:%S") + \
                    ")] " + next_client + " has joined the channel."
                    print("[Server message (" + datetime.now().strftime("%H:%M:%S") + \
                    ")] " + next_client + " has joined the " + channel_name + " channel.", flush=True)
                    next_client_conn.sendall("not_in_queue".encode())
                    for client in channels[channel_name]:
                            client[0].sendall(client_message.encode())
                    client_index = 0
                    for client in waiting_queue[channel_name]:
                        if waiting_queue[channel_name].index(client) >= client_index:
                            waiting_message = "[Server message (" + datetime.now().strftime("%H:%M:%S") + \
                            ")] You are in the waiting queue and there are " + str(len(waiting_queue[channel_name])-1) + " user(s) ahead of you."
                            client[0].sendall(waiting_message.encode())

                conn.shutdown(socket.SHUT_RDWR)
                conn.close()
            elif not data:
                continue

            if data.decode() == "/quit" or data.decode() == "/kick" or data.decode() == "/empty" or data.decode() == "/afk":
                command = data.decode()
                quit_management(channel_name, conn, channels, username, waiting_queue, command)
            elif data.decode()[0:8] == "/whisper":
                client_whisper(data, channel_name, conn, channels, username)

            elif data.decode()[0:7] == "/switch":
                client_switch(data, channel_name, conn, channels, username)
            
            elif data.decode() == "/list":
                for key in channels:
                    message = "[Channel] " + key + " " + str(len(channels[key])) \
                        + "/" + str(max_capacities[key]) + "/" + str(len(waiting_queue[key])) + ".\n"
                    conn.sendall(message.encode())

            elif data.decode()[0:5] == "/send":
                valid_target = False
                valid_file = True
                
                if data.decode()[5] == "0":
                    data = data.decode()[len("/send0 "):].strip()
                    target, file_path = data.split(" ", 1)
                    file_path = file_path.strip()
                    valid_file = False
                else:
                    data = data.decode()[len("/send "):].strip()
                    target, file_path = data.split(" ", 1)
                    file_path = file_path.strip()

                for clients in channels[channel_name]:
                    if target == username:
                        pass
                    
                    elif clients[1] == target:
                        valid_target = True    

                if not valid_target:
                    target_invalid = "[Server message (" + datetime.now().strftime("%H:%M:%S") \
                    + ")] " + target + " is not here.\n"
                    conn.sendall(target_invalid.encode())
                
                if not valid_file:
                    file_invalid = "[Server message (" + datetime.now().strftime("%H:%M:%S") \
                    + ")] " + file_path + " does not exist."
                    conn.sendall(file_invalid.encode())

                if not valid_target or not valid_file:
                    continue

                print("[Server message (" + datetime.now().strftime("%H:%M:%S") \
                    + ")] " + username + " sent " + file_path + " to " + target + ".", flush=True)
                
                client_msg = "[Server message (" + datetime.now().strftime("%H:%M:%S") \
                    + ")] You sent " + file_path + " to " + target + "."
                conn.sendall(client_msg.encode())
            
            elif data.decode()[0:9] == "file_data":
                data = data.decode()[len("file_data "):]
                file_name, target_content = data.split(" ", 1)
                target, content = target_content.split(" ", 1)

                for clients in channels[channel_name]:
                    if clients[1] == target:
                        clients[0].sendall(("file " + file_name + " " + content).encode())
                
            elif (conn, username) in channels[channel_name]:
                if username not in kicking:
                    print(data.decode(), flush=True)
                for client in channels[channel_name]:
                        client[0].sendall(data)
        except Exception:
            pass

def server_commands():
    global running
    
    while running:
        try:
            server_input = input().strip()
        except Exception:
            continue
        
        if server_input == "/shutdown": 
            for keys in channels.keys():
                for clients in channels[keys]:
                    clients[0].sendall("/shutdown".encode())
                    clients[0].shutdown(socket.SHUT_RDWR)
                    clients[0].close()
            running = False
        
        elif (server_input[0:5] == "/kick" and len(server_input) > 5 and server_input[5] == " "):
            try:
                server_input = server_input[len("/kick "):].strip()
                kick_channel, kick_username = server_input.split(":", 1)
                if kick_channel not in channels.keys():
                    print("[Server message (" + datetime.now().strftime("%H:%M:%S") + \
                                ")] " + kick_channel + " does not exist.", flush=True)
                for conn_tuple in channels[kick_channel]:
                    if conn_tuple[1] == kick_username:
                        kicking.append(kick_username)
                        print("[Server message (" + datetime.now().strftime("%H:%M:%S") + \
                                ")] Kicked " + kick_username + ".", flush=True)
                        conn_tuple[0].sendall("/kick".encode())
                if len(kicking) == 0:
                    print("[Server message (" + datetime.now().strftime("%H:%M:%S") + \
                            ")] " + kick_username + " is not in " + kick_channel + ".", flush=True)
            except Exception:
                pass

        elif server_input[0:6] == "/empty" and len(server_input) > 6 and server_input[6] == " ":
            emptying_channel = server_input[len("/empty "):].strip() 
            empty(emptying_channel)

        elif (server_input[0:5] == "/mute" and len(server_input) > 5 and server_input[5] == " "):
            found = False
            server_input = server_input[len("/mute "):].strip()
            channel_name, username_time = server_input.split(":", 1)
            mute_username, mute_time = username_time.split(" ", 1)
            mute_time = mute_time.strip()
            try:
                int(mute_time)
            except Exception:
                print("[Server message (" + datetime.now().strftime("%H:%M:%S") + \
                        ")] Invalid mute time.", flush=True) 
                continue

            if int(mute_time) <= 0:
                print("[Server message (" + datetime.now().strftime("%H:%M:%S") + \
                        ")] Invalid mute time.", flush=True)    
                    
            elif channel_name not in channels.keys():
                print("[Server message (" + datetime.now().strftime("%H:%M:%S") + \
                                ")] " + mute_username + " is not here.", flush=True)
            else:
                for clients in channels[channel_name]:
                    if clients[1] == mute_username:
                        found = True
                        print("[Server message (" + datetime.now().strftime("%H:%M:%S") + \
                                    ")] Muted " + mute_username + " for " + mute_time + " seconds.", flush=True)
                        clients[0].sendall(("muted " + mute_time).encode())

                    
                        for clients in channels[channel_name]:
                            if clients[1] != mute_username:
                                message = "[Server message (" + datetime.now().strftime("%H:%M:%S") + \
                                    ")] " + mute_username + " has been muted for " + mute_time + " seconds."
                                clients[0].sendall(message.encode())
                if not found:
                    print("[Server message (" + datetime.now().strftime("%H:%M:%S") + \
                                ")] " + mute_username + " is not here.", flush=True)
        

def empty(emptying_channel):
    if emptying_channel not in channels.keys():
        print( "[Server message (" + datetime.now().strftime("%H:%M:%S") + \
                            ")] " + emptying_channel + " does not exist.", flush=True)
    else:
        for connections in channels[emptying_channel]:
            connections[0].sendall("/empty".encode())   
        print("[Server message (" + datetime.now().strftime("%H:%M:%S") + \
                            ")] " + emptying_channel + " has been emptied.", flush=True) 
        

                                     
def main():
    try:
        channels_info = read_config_file(sys.argv[1])     
    except:
        exit(1)

    send_thread = threading.Thread(target=server_commands, args=())
    send_thread.start()
    thread_channels.append(send_thread)
    for channel_info in channels_info:
        t = threading.Thread(target=setup, args=(channel_info,))
        thread_channels.append(t)
        t.start()

    for t in thread_channels:
        t.join()
    
    for t in connection_threads:
        t.join()
        
if __name__ == '__main__':
    main()
