import socket
import threading
import datetime
import re
import os

# Server configuration
IP = socket.gethostbyname(socket.gethostname())
PORT = 5566 
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
DISCONNECT_MSG = "!DISCONNECT"
    
def validate_ais_data(data):
    """Validates data in the format $LGN,....* or $LGN,....*<digits> 
       (without checksum calculation)."""

    if not isinstance(data, str):
        print("Data is not a string")
        return False

    if not data.startswith("$"):
        print("Data does not start with '$'")
        return False

    pattern = r"^\$(.*?)\*(\d*)?$"  # Same regex as before

    match = re.match(pattern, data)

    if match:
        checksum_part = match.group(2)  # The digits after * (if any)

        if checksum_part != "": #Check if there are any characters after *
            if not checksum_part.isdigit(): #If there are characters, check if they are digits
                print("Invalid checksum format. Checksum should contains only digits")
                return False

        return True  # Valid data (passes basic format check)
    else:
        print("Invalid data format")
        return False   

# Function to extract IMEI number from data
def extract_imei(data):
    """Extract a 15-digit IMEI from the received data."""
    try:
        imei = re.search(r"\b\d{15}\b", data).group(0)
        return imei
    except AttributeError:
        return None

# Function to handle client connections
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
                    # Ensure logs directory exists
                    logs_directory = "logs"
                    if not os.path.exists(logs_directory):
                        os.makedirs(logs_directory)  # Create logs/ folder if missing

                    # Create log filename
                    current_date = datetime.datetime.now().strftime("%d%m%Y")
                    filename = f"{imei}_{current_date}.csv"
                    file_path = os.path.join(logs_directory, filename)

                    # Prepare log entry
                    current_datetime = datetime.datetime.now().strftime("%d%m%Y_%I%M%S")
                    csv_entry = f"{current_datetime},{msg}\n"

                    try:
                        # Append data to CSV file
                        with open(file_path, "a") as file:
                            file.write(csv_entry)
                        print(f"[{addr}] Validated data written to {file_path}")

                    except IOError as e:
                        print(f"[{addr}] Error writing to file: {e}")
                else:
                    with open("log.txt", "a") as file:
                        file.write(f"{msg}\n")
                    print(f"[{addr}] Validated data written to log.txt")
            else:
                with open("bad_data.txt", "a") as file:
                    file.write(f"[{addr}] Invalid data: {msg}\n")
                print(f"[{addr}] Invalid data written to bad_data.txt")

            # Send acknowledgment to client
            conn.send("Data received and processed.".encode(FORMAT))
        except socket.error as e:
            print(f"[{addr}] Connection error: {e}")
            break

    conn.close()

# Main server function
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

# Start the server
if __name__ == "__main__":
    main()