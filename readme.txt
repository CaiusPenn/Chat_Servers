BRIEF HIGH LEVEL DESCRIPTION:
The program is a chat server that has a number of channels that are set with a config file. A chat client can
connect to the chat server on a desired port which represents one of the channels. Once a connection is made, the 
client can chat to other clients in the same server as well as eecute various commands. Some of these include
sending messages, sending files, listing connected users, and whispering to specific users. The client communicates 
with the server using a TCP socket connection and sends/receives messages in bytes. The program is multi-threaded, 
with separate threads running for sending and receiving messages to and from the server. The user can switch to a 
different server or quit the program anytime.

The server handles each client connection on a separate thread to ensure concurrent functionality of all clients.
Each channel is on a seperate socket, e.g. 3 channels means 3 sockets. Overall the program allows communications
to other clients through a socket run by a server.

FUNCTIONS:
chatserver.py

def read_config_file(filename):
    """
    Reads a configuration file and extracts channel information. The configuration file should contain
    information about channels, including their name, port, and capacity, with each channel on a separate line.

    Args:
    filename (str): The name of the configuration file to read.

    Returns:
    list: A list of tuples containing channel information, where each tuple contains the name, port,
    and capacity of a channel.

    Raises:
    SystemExit: If the configuration file does not contain valid channel information, the function
    raises a SystemExit exception with an exit code of 1.
    """

def setup(channel_info):
    """ 
    Sets up a channel using the given channel information.

    Args:
    channel_info (tuple): A tuple containing the name, port, and capacity of the channel.

    Returns:
    None

    Raises:
    ValueError: If the channel name is already in use or the port is already occupied, the function
    raises a ValueError exception.
    """
   
def handle_client(channel_name, sock, max_capacity):
    """
    This function handles client connections and channel management for the server.

    Args:

    channel_name (str): The name of the channel the client wants to connect to.
    sock (socket): The server socket for listening to client connections.
    max_capacity (int): The maximum number of clients allowed in the channel.
 
    The function runs indefinitely until the running variable is set to False.
    """

def client_whisper(data, channel_name, conn, channels, username):
    """
    This function handles the /whisper command for the client. The command allows the user to send a private message to
    another user in the same channel. The function extracts the recipient username and message from the input data
    string, and then sends the message to the recipient if they are in the channel. If the recipient is not in the
    channel, a message is sent back to the sender indicating that the recipient is not present. The function also prints
    the whisper message to stdout.
    
    :param data: the input data string containing the /whisper command and message
    :param channel_name: the name of the channel that the user is in
    :param conn: the socket connection object for the user
    :param channels: the dictionary object containing the list of socket connections for each channel
    :param username: the username of the user who sent the whisper message
    """

def client_switch(data, channel_name, conn, channels, username):
    """
    Switches the client's connection to a different channel.

    Args:
    data (bytes): The data received from the client.
    channel_name (str): The name of the current channel.
    conn (socket): The client's socket connection.
    channels (dict): A dictionary containing all of the channels and their associated socket connections.
    username (str): The client's username.
    """

def quit_management(channel_name, conn, channels, username, waiting_queue, command):
    """
    Handles the management of quitting a channel for a client. This includes server kicking or emptying the channel.

    Args:
    channel_name (str): The name of the channel the client is quitting.
    conn (socket): The client's socket connection.
    channels (dict): A dictionary containing all of the active channels and their connections.
    username (str): The username of the client quitting the channel.
    waiting_queue (dict): A dictionary containing all of the waiting clients for each channel.
    command (str): The command used to quit the channel ("/quit", "/kick", or "/empty").
    """

def manage_connections(channel_name, conn, channels, username, waiting_queue):
    """
    Manages the connections of clients to the server and handles their input.

    Args:
    channel_name (str): The name of the channel.
    conn (socket): The connection object to a client.
    channels (dict): A dictionary containing the clients connected to each channel.
    username (str): The username of the client.
    waiting_queue (dict): A dictionary containing the clients who are waiting to join a channel.
    """

def server_commands():
    """"
    This function handles the server commands that can be inputted by the admin user in the chat server. 
    The available commands are "/shutdown" to shut down the server, 
    "/kick <channel>:<username>" to kick a user out of a channel, 
    "/empty <channel>" to empty a channel, and 
    "/mute <channel>:<username> <time>" to mute a user in a channel for a specified amount of time.
    """

def empty(emptying_channel):
    """
    Sends a command to all clients in the specified channel to end their connection to the socket.

    Args:
        emptying_channel (str): The name of the channel to be emptied.
    """

def main():
    """
    The main() function is the entry point of the program. 
    It reads the configuration file using the provided command-line argument, and starts a send_thread to handle server commands. 
    It then sets up a thread for each channel specified in the configuration file using the setup() function. 
    After starting all the channel threads, the main thread waits for them to finish using join(). 
    It then waits for all the connection threads to finish.
    """

chatclient.py
def receive_messages(sock, username):
   """
   Receives messages from the server and processes them accordingly.

   Args:
   sock (socket): The socket object.
   username (str): The username of the connected client.

   Globals:
   connected (bool): Flag indicating if the client is connected.
   port (str): The port number being used.
   switching (bool): Flag indicating if the client is in the process of switching channels.
   muted (bool): Flag indicating if the client is muted.
   start_time (float): The time when the mute started.
   muted_time (int): The duration of the mute.
   mute_end_time (float): The time when the mute will end.
   """

def send_messages(sock, username):
   """
   Sends messages from the client to the server.

   Args:
   sock (socket.socket): The socket communicating with the server.
   username (str): The username of the client.
   """

def client_switch(port, username):
    """
    This handles the client switching to a different channel, closing the current threads and 
    starting new ones connected on the new socket.

    Args:
    port (int): The port number to connect to.
    username (str): The username of the client.
    """

def client_quit(sock, username, command):
    """
    Called when the client is quitting from its current channel, being kicked, channel is emptied or shutdown

    Args:
    sock: a socket object representing the client's connection to the server
    username: a string representing the username of the client
    command: a string representing the command that triggered the client's exit 
    """

def client_empty(sock):
    """
    Closes the connection when the server calls empty

    Args:
    sock: a socket object representing the client's connection to the server
    """

def client_muted(muted_time):
    """
    In this function while the client is muted

    Args:
    muted_time: time the client is muted for
    """

def client_afk(sock, username):
    """
    Kicks the client for being afk, (time since last message is >= 100 seconds

    Args:
    sock: a socket object representing the client's connection to the server
    username (str): The username of the client.
    """

def main():
    """
    Initialises the client connection to the desired channel on the server, creating required threads.
    Waits for threads to finish at .join() statements
    Has a loop to handle client switching to new channel
    """

TESTING:
I tested my code as I went, manually ensuring that the functionality behaved as described on the task sheet.
This meant using print statements and running a server and creating clients within my vscode terminals to ensure
client connection/functionality worked with the server connection and functionality.

Once I implemented all functionality described on the assignment spec, I copied my files into moss using filezilla 
including the given tests. I than ran every test individually fixing any errors that occurred while testing.
