import socket
import sys
import re
import time

# Function to determine the operation for single-input circuits
def single_input(input, output):
    return "not" if all(i != o for i, o in zip(input, output)) else "not found"

def two_input(input1, input2, output):
    and_result = ''.join(str(int(i1) & int(i2)) for i1, i2 in zip(input1, input2))
    or_result = ''.join(str(int(i1) | int(i2)) for i1, i2 in zip(input1, input2))
    xor_result = ''.join(str(int(i1) ^ int(i2)) for i1, i2 in zip(input1, input2))
    nand_result = ''.join(str(int(not (int(i1) & int(i2)))) for i1, i2 in zip(input1, input2))
    nor_result = ''.join(str(int(not (int(i1) | int(i2)))) for i1, i2 in zip(input1, input2))

    if and_result == output:
        return "and"
    elif or_result == output:
        return "or"
    elif xor_result == output:
        return "xor"
    elif nand_result == output:
        return "nand"
    elif nor_result == output:
        return "nor"
    else:
        return "unknown"

# Function to extract input/output patterns from the message
def extract_io(message):
    patterns = [
        (r"Circuit\[(\d+)\]\s*:\s*\('(\w+)',\s*'(\w+)'\)\s*->\s*\[OPERATION\]\s*->\s*\('(\w+)',\s*'(\w+)'\)\s*->\s*\[OPERATION\]\s*->\s*(\w+)",
         lambda m: (int(m.group(1)), [((m.group(2), m.group(3)), (m.group(4), m.group(5))), ((m.group(4), m.group(5)), m.group(6))])),
        # New pattern for two two-input operations
        (r"Circuit\[(\d+)\]\s*:\s*\('(\w+)',\s*'(\w+)'\)\s*->\s*\[OPERATION\]\s*->\s*\('(\w+)',\s*'(\w+)'\)\s*->\s*\[OPERATION\]\s*->\s*(\w+)",
         lambda m: (int(m.group(1)), [((m.group(2), m.group(3)), (m.group(4), m.group(5))), ((m.group(4), m.group(5)), m.group(6))])),
        # Existing patterns...
        (r"Circuit\[(\d+)\]\s*:\s*\('(\w+)',\s*'(\w+)'\)\s*->\s*\[OPERATION\]\s*->\s*(\w+)\s*->\s*\[OPERATION\]\s*->\s*(\w+)", 
         lambda m: (int(m.group(1)), [((m.group(2), m.group(3)), m.group(4)), (m.group(4), m.group(5))])),
        (r"Circuit\[(\d+)\]\s*:\s*(\w+)\s*->\s*\[OPERATION\]\s*->\s*\('(\w+)',\s*'(\w+)'\)\s*->\s*\[OPERATION\]\s*->\s*(\w+)",
         lambda m: (int(m.group(1)), [(m.group(2), (m.group(3), m.group(4))), ((m.group(3), m.group(4)), m.group(5))])),
        (r"Circuit\[(\d+)\]\s*:\s*(\w+)\s*->\s*\[OPERATION\]\s*->\s*(\w+)\s*->\s*\[OPERATION\]\s*->\s*(\w+)",
         lambda m: (int(m.group(1)), [(m.group(2), m.group(3)), (m.group(3), m.group(4))])),
        (r"Circuit\[(\d+)\]\s*:\s*(\w+)\s*->\s*\[OPERATION\]\s*->\s*\('(\w+)',\s*'(\w+)'\)\s*->\s*(\w+)",
         lambda m: (int(m.group(1)), [(m.group(2), (m.group(3), m.group(4)), m.group(5))])),
        (r"Circuit\[(\d+)\]\s*:\s*\('(\w+)',\s*'(\w+)'\)\s*->\s*\[OPERATION\]\s*->\s*(\w+)",
         lambda m: (int(m.group(1)), [((m.group(2), m.group(3)), m.group(4))])),
        (r"Circuit\[(\d+)\]\s*:\s*(\w+)\s*->\s*\[OPERATION\]\s*->\s*(\w+)",
         lambda m: (int(m.group(1)), [(m.group(2), m.group(3))]))
    ]
    
    for pattern, handler in patterns:
        match = re.search(pattern, message)
        if match:
            return handler(match)
    
    return None

# Function to connect to the server
def connect_to_server(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, int(port)))
    return s

def interact_with_server(host, port):
    circuit_number = 0

    while True:
        try:
            s = connect_to_server(host, port)

            while True:
                data = s.recv(1024).decode().strip()
                print(f"Received: {data}")

                if f"Circuit[{circuit_number}]" in data:
                    break

            while True:
                if "Circuit" in data:
                    circuit_info = extract_io(data)
                    if circuit_info is None:
                        print("Could not parse input/output. End of challenge or error.")
                        break

                    current_circuit, io = circuit_info
                    if current_circuit != circuit_number:
                        print(f"Expected Circuit[{circuit_number}], but received Circuit[{current_circuit}]")
                        circuit_number = current_circuit

                    for i, operation_io in enumerate(io):
                        if isinstance(operation_io[0], tuple) and isinstance(operation_io[1], tuple):
                            # Two consecutive two-input operations
                            input1, input2 = operation_io[0]
                            intermediate1, intermediate2 = operation_io[1][0], operation_io[1][1]
                            final_output = operation_io[1]
                            operation1 = two_input(input1, input2, intermediate1)
                            operation2 = two_input(intermediate1, intermediate2, final_output)
                            
                            print(f"Determined operation {i+1}: {operation1}")
                            s.sendall(f"{operation1}\n".encode())
                            time.sleep(0.1)
                            
                            data = s.recv(1024).decode().strip()
                            print(f"Received: {data}")
                            
                            print(f"Determined operation {i+2}: {operation2}")
                            s.sendall(f"{operation2}\n".encode())
                            time.sleep(0.1)
                        elif isinstance(operation_io[0], tuple):
                            # Single two-input operation
                            input1, input2, output = operation_io[0][0], operation_io[0][1], operation_io[1]
                            operation = two_input(input1, input2, output)
                            print(f"Determined operation {i+1}: {operation}")
                            s.sendall(f"{operation}\n".encode())
                            time.sleep(0.1)
                        else:
                            # Single-input operation
                            input, output = operation_io[0], operation_io[1]
                            operation = single_input(input, output)
                            print(f"Determined operation {i+1}: {operation}")
                            s.sendall(f"{operation}\n".encode())
                            time.sleep(0.1)

                    circuit_number += 1

                data = s.recv(1024).decode().strip()
                print(f"Received: {data}")

                if "flag" in data.lower():
                    print("Flag received!")
                    return

        except Exception as e:
            print(f"An error occurred: {e}")
            print(f"Restarting from Circuit[0]...")
            circuit_number = 0
            s.close()
            time.sleep(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <host> <port>")
        sys.exit(1)
    
    host = sys.argv[1]
    port = sys.argv[2]
    
    interact_with_server(host, port)
