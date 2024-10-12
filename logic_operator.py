import socket
import sys

def single_input(input, output):
    for i in range(len(input)):
        if input[i] != output[i]:
            return "not"
        else:
            return "not found"


def two_input(input1, input2, output):
    for i in range(len(input1)):
        if int(output[i]) == (int(input1[i]) & int(input2[i])):
            return "and"
        elif int(output[i]) == (int(input1[i]) | int(input2[i])):
            return "or"
        else:
            return "xor"

# def interact_with_server(host, port):
#     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#         s.connect((host, int(port)))
        
#         while True:
#             # Receive data
#             # Parse data
#             # Determine operation
#             # Send answer
#             # Check for termination condition
#             pass

# if __name__ == "__main__":
#     if len(sys.argv) != 3:
#         print("Usage: python script.py <host> <port>")
#         sys.exit(1)
    
#     host = sys.argv[1]
#     port = sys.argv[2]
    
#     interact_with_server(host, port)