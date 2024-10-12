import socket
import sys
import re

def single_input(input, output):
    return "not" if all(i != o for i, o in zip(input, output)) else "not found"

def two_input(input1, input2, output):
    and_match = or_match = xor_match = True
    for i in range(len(input1)):
        i1, i2, o = int(input1[i]), int(input2[i]), int(output[i])
        and_match = and_match and (o == (i1 & i2))
        or_match = or_match and (o == (i1 | i2))
        xor_match = xor_match and (o == (i1 ^ i2))

    if and_match:
        return "and"
    elif or_match:
        return "or"
    elif xor_match:
        return "xor"
    else:
        return "unknown"
        
def extract_io(message):
    single_input_pattern = r"Circuit\[\d+\]\s*:\s*(\w+)\s*->\s*\[OPERATION\]\s*->\s*(\w+)"
    two_input_pattern = r"Circuit\[\d+\]\s*:\s*\('(\w+)',\s*'(\w+)'\)\s*->\s*\[OPERATION\]\s*->\s*(\w+)"
    
    single_match = re.search(single_input_pattern, message)
    if single_match:
        return single_match.group(1), single_match.group(2)
    
    two_match = re.search(two_input_pattern, message)
    if two_match:
        return (two_match.group(1), two_match.group(2)), two_match.group(3)
    
    return None

def interact_with_server(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, int(port)))
        
        welcome_msg = s.recv(1024).decode().strip()
        print(f"Received: {welcome_msg}")
        
        while True:
            try:
                data = s.recv(1024).decode().strip()
                print(f"Received: {data}")

                if "flag" in data.lower():
                    print("Flag received!")
                    break

                io = extract_io(data)
                if io is None:
                    print("Could not parse input/output. Might be the end of the challenge or an error.")
                    break

                if isinstance(io[0], tuple):
                    operation = two_input(io[0][0], io[0][1], io[1])
                else:
                    operation = single_input(io[0], io[1])

                print(f"Determined operation: {operation}")
                s.sendall(f"{operation}\n".encode())

            except Exception as e:
                print(f"An error occurred: {e}")
                break

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <host> <port>")
        sys.exit(1)
    
    host = sys.argv[1]
    port = sys.argv[2]
    
    interact_with_server(host, port)