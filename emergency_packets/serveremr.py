import socket
import threading
import datetime
import re
import os

IP = socket.gethostbyname(socket.gethostname())
PORT = 8000
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
DISCONNECT_MSG = "!DISCONNECT"

def validate_ais_data(data):
    """
    Validates if the received data starts with '$' and contains 'EPB' or 'EMR'.
    Handles multiple AIS messages in one string.
    """
    messages = data.split('$')
    messages = [msg for msg in messages if msg]  # Remove empty strings
    for msg in messages:
        if any(word in msg for word in ['EPB', 'EMR']):
            return True
    return False

def extract_imei(data):
    """Extract a 15-digit IMEI from the received data."""
    try:
        imei = re.search(r"\b\d{15}\b", data).group(0)
        return imei
    except AttributeError:
        return None

def handle_client(conn, addr):
    """Handle communication with a connected client."""
    print(f"[NEW CONNECTION] {addr} connected.")
    connected = True

    while connected:
        try:
            msg = conn.recv(SIZE).decode(FORMAT)
            if msg == DISCONNECT_MSG:
                connected = False

            print(f"[{addr}] Received: {msg}")

            if validate_ais_data(msg):
                imei = extract_imei(msg)
                if imei:
                    logs_directory = "logs"
                    if not os.path.exists(logs_directory):
                        os.makedirs(logs_directory)

                    current_date = datetime.datetime.now().strftime("%d%m%Y")
                    filename = f"{imei}_{current_date}.csv"
                    file_path = os.path.join(logs_directory, filename)

                    current_datetime = datetime.datetime.now().strftime("%d%m%Y_%I%M%S")
                    csv_entry = f"{current_datetime},{msg}\n"

                    try:
                        with open(file_path, "a") as file:
                            file.write(csv_entry)
                        print(f"[{addr}] Validated data written to {file_path}")

                    except IOError as e:
                        print(f"[{addr}] Error writing to file: {e}")

                else:  # Handle cases where data is valid but no IMEI is found
                    with open("log.txt", "a") as file:
                        file.write(f"{msg}\n")
                    print(f"[{addr}] Validated data written to log.txt")

            else:
                with open("bad_data.txt", "a") as file:
                    file.write(f"[{addr}] Invalid data: {msg}\n")
                print(f"[{addr}] Invalid data written to bad_data.txt")

            conn.send("Data received and processed.".encode(FORMAT))  # Acknowledge

        except socket.error as e:
            print(f"[{addr}] Connection error: {e}")
            break

    conn.close()
    print(f"[CONNECTION CLOSED] {addr}")  # Indicate when a client disconnects


def main():
    """Start the server and listen for incoming connections."""
    print("[STARTING] Server is starting...")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print(f"[LISTENING] Server is listening on {IP}:{PORT}")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")


if __name__ == "__main__":
    main()