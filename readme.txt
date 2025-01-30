# Chat Server and Client Application

## Overview
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

### chatclient.py
