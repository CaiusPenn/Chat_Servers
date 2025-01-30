#Chat Server and Client Application

##Overview
This program implements a multi-threaded chat server and client system. The chat server manages multiple channels that can be configured through a configuration file. Clients can connect to the server on a specified port that represents a channel, send messages, share files, whisper to other users, and perform various commands. The server and client communicate using TCP socket connections.

## Features
- **Multi-threaded Architecture**: The server uses separate threads for handling each client connection, enabling concurrent communication for multiple clients.
- **Channel Management**: Each channel runs on a separate socket, and users can switch between channels or quit the program at any time.
- **Whisper Command**: Clients can send private messages to specific users within a channel.
- **Client Commands**: Clients can issue commands like `/quit`, `/switch`, and `/whisper` for channel management and communication.
- **Server Commands**: The server admin can issue commands to shut down the server, kick users from channels, empty channels, and mute users.
  
## Setup and Installation

1. Clone this repository or download the project files.
2. Ensure Python 3.x is installed on your system.
3. Install any required dependencies using pip:
4. Run the server with the following command:
5. The server will read the configuration file and start listening for client connections. Each channel will be available on a different port.
6. To run the client, use:

The client will prompt for a username and allow the user to choose a channel to connect to.

## Functions

### chatserver.py

- **read_config_file(filename)**: Reads the configuration file and extracts channel information (name, port, and capacity).
- **setup(channel_info)**: Sets up a channel based on the given configuration.
- **handle_client(channel_name, sock, max_capacity)**: Manages client connections and the operations for a given channel.
- **client_whisper(data, channel_name, conn, channels, username)**: Handles the `/whisper` command to send a private message to another user in the same channel.
- **client_switch(data, channel_name, conn, channels, username)**: Allows a client to switch to a different channel.
- **quit_management(channel_name, conn, channels, username, waiting_queue, command)**: Manages client disconnections (quitting or being kicked from channels).
- **server_commands()**: Handles admin commands such as `/shutdown`, `/kick`, `/empty`, and `/mute`.
- **empty(emptying_channel)**: Sends a command to disconnect all users from the specified channel.
- **main()**: Initializes the server, reads the configuration, and sets up the channels. It also starts server command threads.

### chatclient.py

- **receive_messages(sock, username)**: Receives and processes messages from the server.
- **send_messages(sock, username)**: Sends messages to the server.
- **client_switch(port, username)**: Allows the client to switch to a new channel.
- **client_quit(sock, username, command)**: Disconnects the client from the server.
- **client_empty(sock)**: Closes the client's connection when the server empties the channel.
- **client_muted(muted_time)**: Handles the client’s muted state and its duration.
- **client_afk(sock, username)**: Kicks the client for being idle for too long.
- **main()**: Initializes the client connection, handles switching channels, and processes user commands.
