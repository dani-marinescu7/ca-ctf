import socket
import sys
import re

def decimal_to_binary(n):
    return bin(n)[2:]

def interact_with_server(host, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, int(port)))
            
            for i in range(25):
                data = s.recv(1024).decode().strip()
                print(f"Received: {data}")
                
                match = re.search(r'(\d+)\s*:', data)
                if match:
                    number = int(match.group(1))
                else:
                    print(f"Could not extract number from: {data}")
                    continue
                
                binary = decimal_to_binary(number)
                print(f"Sending: {binary}")
                
                s.sendall(f"{binary}\n".encode())
            
            final_response = s.recv(1024).decode().strip()
            print(f"Final response: {final_response}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <host> <port>")
        sys.exit(1)
    
    host = sys.argv[1]
    port = sys.argv[2]
    
    interact_with_server(host, port)