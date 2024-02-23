import socket
import json 


def send_message(message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(('localhost', 12345))
        print(f"Sending: {message}")
        sock.send(message.encode('utf-8'))
     
        # In client.py, after receiving the response
        response_data = sock.recv(4096).decode('utf-8')  # Decode response to string
        print("Getting a response from server = ", response_data)
        response = json.loads(response_data)  # Parse JSON string back into a dictionary

        
if __name__ == "__main__":
    send_message("who is cosmicray007?")
    # send_message("I need to setup a switch's port using the nv commands for a  16 port switch please provide all the commands I will need to configure all the ports example : nv set interface swp1s0 ip address 10.1.1.1/31 etc")
    # send_message('''I need to prepare mistral for use for tensorrt llm .   
    #                 I am perparing an instruct model for minstral 7b , the enginee directory is mistral7b_engine , the tokens are in mistral7b_tok, the wieghts are in mistral7b_w.
    #               I would like to quantize the model to use int quant for the wieghts.  please provide me with the build.py args to create my engine.
    #              ''')