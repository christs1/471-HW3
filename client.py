import socket
import threading
import sys

def get_msg_log(c_socket):
    while True:
        try:
            data = c_socket.recv(1024)
            if not data:
                print("\nServer closed the connection.\n")
                break
            response = data.decode('utf-8')
            print(f"{response}")
        except OSError:
            break

def main():
    if len(sys.argv) != 3:
        print("Usage: python client.py <host> <port>")
        sys.exit(1)
    host = sys.argv[1]
    
    try:
        port = int(sys.argv[2]) # Get port from command-line argument and convert to int
    except ValueError:
        print("Error: Port must be an integer.")
        sys.exit(1)

    c_socket = socket.socket()
    try: 
        c_socket.connect((host, port))
        print(f"% echo_client {host} {port}")
        print("Client is connected to the server.")

        data = c_socket.recv(1024)
        response = data.decode('utf-8').strip()
        if "No previous message history" in response:
            print("No prior message log from the server.")
            print("No other clients connected to the server.")
        else:
            print(response)

        receive_thread = threading.Thread(target=get_msg_log, args=(c_socket,))
        receive_thread.daemon = True
        receive_thread.start()

        while True:
            message = input("Enter message to send to server: ")
            if message.lower() == 'quit':
                break
            c_socket.sendall(message.encode('utf-8'))
    except ConnectionRefusedError:
        print(f"Could not connect to server at {host}:{port}.")
    finally:
        print("Disconnecting...")
        c_socket.close()

if __name__ == "__main__":
    main()