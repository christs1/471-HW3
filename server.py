import socket
import threading
import sys

msg_logs = []
client_list = {}

#def server_msg():

def client_thread(c_socket, addr):
    ip, port = addr
    client_id = ip, port
    
    # Store client socket in the client list
    client_list[client_id] = c_socket

    # Notify all other clients about new connections
    connect_msg = f"Client {ip} connected.\n"
    print(connect_msg.strip())
    for other_id, other_sock in client_list.items():
        if other_id != client_id:
            try:
                other_sock.sendall(connect_msg.encode('utf-8'))
            except:
                pass

    # Send existing message logs to new client
    if msg_logs:
        print("The server sent the message log to this client\n")
        msg_history = "Client received message log: \n" + "\n".join(msg_logs)
        c_socket.sendall(msg_history.encode('utf-8'))
    else:
        print("The server has no message log to send to this client")
        c_socket.sendall("No previous message history.\n".encode('utf-8'))

    # Send list of connected clients
    is_connected = "Currently connected clients:\n"
    for client in client_list:
        is_connected += f"{client[0]}:{client[1]}\n"
    c_socket.sendall(is_connected.encode('utf-8'))


    # Handle messages from the client
    while True:
        data = c_socket.recv(1024)
        if not data:
            # Notify all other clients about the disconnection
            disconnect_msg = f"Client {ip} has disconnected.\n"
            print(disconnect_msg.strip())
            for other_id, other_sock in client_list.items():
                if other_id != client_id:
                    try:
                        other_sock.sendall(disconnect_msg.encode('utf-8'))
                    except:
                        pass
            break
        message = data.decode('utf-8').strip()
        if not message:
            continue

        response = "Client sending message: " + '"' + message + '"\n'
        c_socket.sendall(response.encode('utf-8'))   

        client_msg = f"{client_id[0]}: {message}"
        print(f"Client {ip} sent: {message}")
        msg_logs.append(client_msg)

        # Broadcast the message to all other clients
        broadcast_msg = f"{ip}: {message}\n"
        for other_id, other_sock in client_list.items():
            if other_id != client_id:
                try:
                    other_sock.sendall(broadcast_msg.encode('utf-8'))
                except:
                    pass

    # Remove client from client_list after disconnect
    if client_id in client_list:
        del client_list[client_id]
    c_socket.close()

def main():
    if len(sys.argv) != 2:
        print("Usage: python server.py <port>")
        sys.exit(1)

    try:
        port = int(sys.argv[1])
    except ValueError:
        print("Error: Port muts be an integer.")
        sys.exit(1)

    server_socket = socket.socket()
    host = '127.0.0.1'
    port = 12345
    try:
        server_socket.bind((host, port))
        server_socket.listen(5)
        print(f"% echo_server {port}")
        print(f"Server is at adfdress: {host}\nServer is using port: {port}\n")

        while True:
            c_socket, client_address = server_socket.accept()
            print(f"The client at {client_address} has connected to the server")
            client_handler = threading.Thread(target=client_thread, args=(c_socket, client_address))
            client_handler.start()
    except OSError as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()