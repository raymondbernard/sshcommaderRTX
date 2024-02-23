import requests
import streamlit as st
import paramiko
import os
import json
import time
import select 
import socket
import jsonlines



# from dotenv import load_dotenv
# from openai import OpenAI

# Constants
CONFIG_FILE = "config.json"
TEST_FILE = "test.json"
CONFIG_AI_FILE = "config_ai.json"
# Modify the system message to customize the AI's configuration responses
DEFAULT_SYSTEM_MESSAGE  = "Note we are using Nvidia's cumulus Linux distribution, just describe the commands you see.   Please keep your responses short and precise."
# modify the url to your project
## Switch between nvidia or openai 

# AI  = "call_openai"
## command out below if ou use call_openai 
URL = "https://api.nvcf.nvidia.com/v2/nvcf/pexec/functions/df2bee43-fb69-42b9-9ee5-f4eabbeaf3a8" ## user for only Nvidia 
DEFAULT_AI = "call_nvidi" 


def query_chat_logs(file_path, query):
    """
    Query the chat logs JSONL file.
    
    Args:
    - file_path (str): Path to the JSONL file.
    - query (str): Query string to search for in the chat logs.
    
    Returns:
    - list of dict: List of chat log entries matching the query.
    """
    results = []
    with jsonlines.open(file_path) as reader:
        for line in reader:
            if query in line['query'] or query in line['response']:
                results.append(line)
    return results

# Example usage:
file_path = 'chat_logs.jsonl'
query = 'NVIDIA'
results = query_chat_logs(file_path, query)
for result in results:
    print(result)




def load_ai_config():
    try:
        with open('config_ai.json', 'r') as file:
            config = json.load(file)
            config['AI'] = config.get('AI', DEFAULT_AI)
            config['SYSTEM_MESSAGE'] = config.get('SYSTEM_MESSAGE', DEFAULT_SYSTEM_MESSAGE)
            if config['AI'] == "call_nvidi":
                config['URL'] = "https://api.nvcf.nvidia.com/v2/nvcf/pexec/functions/df2bee43-fb69-42b9-9ee5-f4eabbeaf3a8"
            return config
        
    except Exception as e:
        print(f"Error loading config: {e}")
        # Return default configuration if any error occurs
        return {"AI": DEFAULT_AI, "SYSTEM_MESSAGE": DEFAULT_SYSTEM_MESSAGE}

def save_ai_config(config):
    with open(CONFIG_AI_FILE, 'w') as file:
        json.dump(config, file)

# Streamlit sidebar interface for changing AI configuration


def config_ai_interface():
    st.sidebar.title("AI Configuration")
    config = load_ai_config()
    system_message = st.sidebar.text_area("System Message", value=config.get('SYSTEM_MESSAGE', DEFAULT_SYSTEM_MESSAGE))
    if st.sidebar.button("Save Configuration"):
        new_config = {
            "AI": "na",
            "SYSTEM_MESSAGE": system_message
        }
        save_ai_config(new_config)
        st.sidebar.success("AI Configuration saved!")

#App Title and Description
def display_app_header():
    st.title("SSH Commander with AI with Nvidia\Tensorrt_LLM (Local)")
    st.write("This tool helps to configure & test your servers/network devices via SSH.")

# Initialize session state variables
def init_session_variables():
    if 'hostname' not in st.session_state:
        st.session_state.hostname = ''
    if 'port' not in st.session_state:
        st.session_state.port = 22
    if 'username' not in st.session_state:
        st.session_state.username = ''
    if 'password' not in st.session_state:
        st.session_state.password = ''
    if 'key_filename_path' not in st.session_state:
        st.session_state.key_filename_path = None
    if 'servers' not in st.session_state:
        st.session_state.servers = []
    if 'editing_index' not in st.session_state:
        st.session_state.editing_index = None
    if 'tests' not in st.session_state:
        st.session_state.tests = []
    if 'editing_test_index' not in st.session_state:
        st.session_state.editing_test_index = None


# call Nivida api to retrieve AI from LLaMa2 code 32b 
def call_nvidia(prompt):
    config = load_ai_config()
    message = config['SYSTEM_MESSAGE'] + prompt 
    print(message)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(('localhost', 12345))
        print(f"Sending: {message}")
        sock.send(message.encode('utf-8'))
     
        # In client.py, after receiving the response
        response_data = sock.recv(4096).decode('utf-8')  # Decode response to string
        print("Getting a response from server = ", response_data)
        response = json.loads(response_data)  # Parse JSON string back into a dictionary

        complete_message = response
        # for line in response.iter_lines():
        #     if line:
        #         decoded_line = line.decode('utf-8').strip()

        #         # Check if the line is the end of data marker
        #         if decoded_line == '[DONE]':
        #             print("End of data stream.")
        #             break

        #         # Remove the "data: " prefix if present
        #         if decoded_line.startswith('data: '):
        #             decoded_line = decoded_line[6:]
        #         try:
        #             json_line = json.loads(decoded_line)
        #             for choice in json_line['choices']:
        #                 complete_message += choice['delta']['content']
        #         except json.JSONDecodeError:
        #             break 

    print(complete_message)
    return complete_message


def ssh_conn_form():
    # SSH Connection Information
    with st.expander("Add SSH Connection Information"):
        st.session_state.hostname = st.text_input("Hostname (Original Server)", st.session_state.hostname).strip(" ")
        st.session_state.port = st.number_input("Port (Original Server)", min_value=1, max_value=65535, value=st.session_state.port)
        st.session_state.username = st.text_input("Username (Original Server)", st.session_state.username).strip(" ")
        key_filename = st.file_uploader("Private Key File (Original Server)", type=['pem'])
        st.session_state.password = st.text_input("Password (Original Server, if required)", type="password", help="Leave empty if using a private key")

        # Save the uploaded private key file
    if key_filename is not None:
        st.session_state.key_filename_path = save_uploaded_file(key_filename)
    # Initialize session state for server details
    if 'server_address' not in st.session_state:
        st.session_state.server_address = ''
    if 'server_username' not in st.session_state:
        st.session_state.server_username = ''
    if 'server_password' not in st.session_state:
        st.session_state.server_password = ''
        
    # Configuration Section
    with st.expander("Setup server/device configuration section"):            
        server_input_form(st.session_state.servers, st.session_state.editing_index, 'server_form', "Configure your devices", save_config)
# Define the add_configuration function here
def add_configuration(server, title, description, commands):
    if 'configurations' not in server:
        server['configurations'] = []
    server['configurations'].append({
        'description': description,
        'commands': commands
    })

# Load existing configuration and tests
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)
            st.session_state.servers = data.get("servers", [])
            st.session_state.hostname = data.get("hostname", "")
            st.session_state.port = data.get("port", 22)
            st.session_state.username = data.get("username", "")

def load_tests():
    if os.path.exists(TEST_FILE):
        with open(TEST_FILE, "r") as f:
            data = json.load(f)
            st.session_state.tests = data.get("tests", [])

# Function to handle file upload and save it temporarily
def save_uploaded_file(uploaded_file):
    try:
        if not os.path.exists('tempDir'):
            os.makedirs('tempDir')
        with open(os.path.join("tempDir", uploaded_file.name), "wb") as f:
            f.write(uploaded_file.getbuffer())
        return os.path.join("tempDir", uploaded_file.name)
    except Exception as e:
        st.error(f"Error saving file: {e}")
        return None

# SSH Functions
def create_ssh_client(hostname, port, username, password=None, key_filename=None):
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # Automatically add the server's host key without confirmation
    try:
        if key_filename:
            if not os.path.exists(key_filename):
                st.error("Private key file not found.")
                return None
            ssh_client.connect(hostname, port=port, username=username, key_filename=key_filename, look_for_keys=False, allow_agent=False)
        elif password:
            ssh_client.connect(hostname, port=port, username=username, password=password, look_for_keys=False, allow_agent=False)
        else:
            st.error("No authentication method provided. Please provide a password or a key file.")
            return None
    except paramiko.AuthenticationException:
        st.error("Authentication failed, please verify your credentials")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
        return None
    return ssh_client

def run_commands(ssh_client, server):
    address = server['address']
    username = server['username']
    server_password = server.get('password')
    config_description = server['config_description']
    commands = server['commands']
    st.markdown(f"<h4 style='font-weight:bold;'>{config_description}</h4>", unsafe_allow_html=True)
    ssh_cmd = f"ssh -o StrictHostKeyChecking=no {username}@{address}"
    if server_password:
        ssh_cmd = f"sshpass -p {server_password} {ssh_cmd}"
    
    shell = ssh_client.invoke_shell()
    shell.setblocking(0)
    shell.send(f"{ssh_cmd}\n")

    for command in commands:
        shell.send(f"{command}\n")
        time.sleep(2)
        output = ""
        while not output.strip().endswith("$"):  # Adjust the ending prompt as per your server's command prompt
            ready, _, _ = select.select([shell], [], [], 0.5)
            if ready:
                output += shell.recv(10000).decode()  # Adjust buffer size as needed
            else:
                # Handle timeout or no data scenario
                break
        st.text(output)

    shell.send("exit\n")
    output = ""
    while not output.strip().endswith("$"):  # Adjust the ending prompt as per your server's command prompt
        ready, _, _ = select.select([shell], [], [], 0.5)
        if ready:
            output += shell.recv(10000).decode()  # Adjust buffer size as needed
        else:
            # Handle timeout or no data scenario
            break
    st.text(output)

    shell.close()

# Save configuration 
def save_config():
    data = {
        "servers": st.session_state.servers,
        "hostname": st.session_state.hostname,
        "port": st.session_state.port,
        "username": st.session_state.username,
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f)

# Save tests
def save_tests():
    data = {
        "tests": st.session_state.tests,
    }
    with open(TEST_FILE, "w") as f:
        json.dump(data, f)


# Server Information Input
def server_input_form(servers, editing_index, key, title, save_function):
    with st.form(key=key):
        st.subheader(title)
        editing_server = servers[editing_index] if editing_index is not None else {}
        address = st.text_input("Address of server/device", value=editing_server.get("address", st.session_state.server_address)).strip()
        server_username = st.text_input("Username", value=editing_server.get("username", st.session_state.server_username)).strip()
        server_password = st.text_input("Password (optional)", type="password", value=editing_server.get("password", st.session_state.server_password)).strip()
        commands = st.text_area("Commands (one per line)", value="\n".join(editing_server.get("commands", []))).strip()
        submit_button = st.form_submit_button("Save configuration")
    
    if submit_button:
        # Update session state with the new values
        st.session_state.server_address = address
        st.session_state.server_username = server_username
        st.session_state.server_password = server_password

        # Gather server information
        server_info = {
            "address": address,
            "username": server_username,
            "password": server_password,
            "config_description": "",  # Initialize as empty
            "commands": [cmd.strip() for cmd in commands.split('\n') if cmd.strip()]
        }
        config = load_ai_config()
        AI = config['AI']
        # Check for AI response
    
        ai_response = call_ai(AI, commands)
        print("AI Response:", ai_response)  # Replace with logging if appropriate
        server_info["config_description"] = ai_response
        st.text_area("AI's Configuration Description", value=ai_response, key="updated_description")

        # Save or update the server information
        if editing_index is not None:
            servers[editing_index] = server_info
            st.session_state.editing_index = None
        else:
            servers.append(server_info)
        save_function()
        st.success("Server saved successfully!")


def buttons():
    with st.expander("View Saved Configurations and or Edit/Delete"):
        display_servers(st.session_state.servers, 'editing_index', 'config', save_config, st.experimental_rerun)
    # Action Button for Configuration
    if st.button("Start Configuration"):
        with st.spinner("Configuring devices..."):
            try:
                # Create SSH client to the original server
                original_ssh_client = create_ssh_client(
                    st.session_state.hostname,
                    st.session_state.port,
                    st.session_state.username,
                    st.session_state.password,
                    st.session_state.key_filename_path
                )
                if original_ssh_client is None:
                    st.error("Failed to create SSH client to the original server.")
                    st.stop()

                # Run commands on each server through the original server
                for server in st.session_state.servers:
                    st.write(f"Configuring {server['address']} through {st.session_state.hostname}...")
                    run_commands(original_ssh_client, server)

                st.success("Configuration completed successfully!")
            except Exception as e:
                st.error(f"An error occurred: {e}")
            finally:
                if 'original_ssh_client' in locals() and original_ssh_client is not None:
                    original_ssh_client.close()

# Display added servers
def display_servers(servers, editing_index_key, section, delete_function, rerun_function):
    for i, server in enumerate(servers):
        st.write(f"Server {i+1}: {server['address']}")
        st.write(f"Username: {server['username']}")
        st.write("Commands:")
        for command in server['commands']:
            st.text(command)
        with st.container():
            col1, col2 = st.columns([1, 1])
            edit_button = col1.button("Edit", key=f"edit_{section}_{i}")
            delete_button = col2.button("Delete", key=f"delete_{section}_{i}")

        if edit_button:
            st.session_state[editing_index_key] = i
            rerun_function()

        if delete_button:
            del servers[i]
            delete_function()
            rerun_function()
        st.write("---")

# call nvidia or openai api 
def call_ai(ai_type, commands):
    with st.spinner('Waiting for AI response...'):
        print("Calling Nvidia Local")
        return call_nvidia(commands)
    

def test_form():
    # Testing Section
    with st.expander("Setup Testing"):

        server_input_form(st.session_state.tests, st.session_state.editing_test_index, 'test_form', "Configure a Test", save_tests)
    with st.expander("View saved Tests and or  Edit / Delete"):
        display_servers(st.session_state.tests, 'editing_test_index', 'test', save_tests, st.experimental_rerun)
        
    # Action Button for Testing
    if st.button("Start Testing"):
        with st.spinner("Testing devices..."):
            try:
                # Create SSH client to the original server
                original_ssh_client = create_ssh_client(st.session_state.hostname, st.session_state.port, st.session_state.username, st.session_state.password, st.session_state.key_filename_path)

                if original_ssh_client is None:
                    st.error("Failed to create SSH client to the original server.")
                    st.stop()
                # Run commands on each server through the original server
                for test in st.session_state.tests:
                    st.write(f"Testing {test['address']} through {st.session_state.hostname}...")
                    run_commands(original_ssh_client, test)
                st.success("Testing completed successfully!")
            except Exception as e:
                st.error(f"An error occurred: {e}")
            finally:
                if 'original_ssh_client' in locals() and original_ssh_client is not None:
                    original_ssh_client.close()

# read the config.json file for markdown conversion       
def read_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# process config to markdown 
def display_servers_as_markdown(servers):
    markdown_text = ""
    if servers:
        for server in servers['servers']:  # Assuming 'servers' is the top-level key
            markdown_text += f"### Device Address: {server['address']}\n"
            markdown_text += f"**Username:** {server['username']}\n"
            # markdown_text += f"**Password:** {server['password']}\n"
            markdown_text += f"\n**Description:**\n{server['config_description']}\n\n"
            markdown_text += "**Commands:**\n"
            for command in server['commands']:
                markdown_text += f"- {command}\n"
            markdown_text += "\n---\n\n"  # Separator between servers
        return markdown_text
    elif servers == None: 
        st.write("please configure your devices and servers")

# create a markdown of the contents of the config.json file
def markdown_file():
    st.sidebar.button('Read Config', on_click=lambda: st.session_state.update({'read_config': True}))
    if 'read_config' in st.session_state and st.session_state['read_config']:
        config_file = 'config.json'
        if os.path.exists(config_file):
            config_data = read_json(config_file)
            markdown_text = display_servers_as_markdown(config_data)
            st.markdown(markdown_text)

            # Generate a download button for the markdown content
            st.sidebar.download_button(
                label="Download Markdown",
                data=markdown_text,
                file_name="server_config.md",
                mime="text/markdown"
            )
        else:
            st.error(f"Please configure your devices first. Before you read the config, since the File {config_file} was not yet created.")

# Main Application Logic
def main():
    display_app_header()
    init_session_variables()
    load_config()
    load_ai_config()
    config_ai_interface()
    load_tests()
    ssh_conn_form()
    buttons()
    test_form()
    markdown_file()

if __name__ == "__main__":
    main()
