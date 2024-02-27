import requests
import streamlit as st
import paramiko
import os
import json
import time
import select 
import os
import app_process_data

# Constants
CONFIG_FILE = "config.json"
TEST_FILE = "test.json"
CONFIG_AI_FILE = "config_ai.json"

# AI  = "call_openai"
## command out below if ou use call_openai 
DEFAULT_AI = "call_nvidi" 
DEFAULT_SYSTEM_MESSAGE  = "Note we are using Nvidia's cumulus Linux distribution, just describe the commands you see.   Please keep your responses short and precise."




# Path to your files
chat_log_file_path = 'chat_logs.jsonl'
config_file_path = 'config.json'

# Read chat log entries
chat_logs = []

# Read chat log entries
chat_logs = []
with open(chat_log_file_path, 'r') as file:
    for line in file:
        chat_logs.append(json.loads(line))

# Load existing configuration
with open(config_file_path, 'r') as file:
    config = json.load(file)

# Helper function to check if the timestamp is unique
def is_timestamp_unique(servers, timestamp):
    return all(server.get("timestamp", "") != timestamp for server in servers)


# Process and update configuration with chat log entries
for entry in chat_logs:
    timestamp = str(entry["timestamp"])
    if is_timestamp_unique(config["servers"], timestamp):
        new_server_config = {
            "address": "",  # Determine how to handle this
            "username": "",  # Determine how to handle this
            "password": "",  # Determine how to handle this
            "timestamp": timestamp,
            "config_description": entry["response"],
            "commands": entry["response"].split('\n')  # Adjust as necessary
        }
        # Add the new server configuration to the list of servers
        config["servers"].append(new_server_config)
    else:
        print(f"Skipping duplicate timestamp: {timestamp}")

# Save the updated configuration
with open(config_file_path, 'w') as file:
    json.dump(config, file, indent=4)

# Save the updated configuration
with open(config_file_path, 'w') as file:
    json.dump(config, file, indent=4)

# Display the logo in the first column
def display_ui():
    col1, col2 = st.columns([1, 15])
    with col1:
        st.image(os.path.join("ui", "assets", "nvidia_logo.png"), width=42)
    with col2:
        st.markdown("""
        <style>
        .font {
            font-size:30px;
        }
        </style>
        <div class="font">
            SSH Commander with RTX<br>
        </div>
        """, unsafe_allow_html=True)

# Define file paths
local_app_data = os.getenv('LOCALAPPDATA')
COMMAND_LOGS = os.path.join(local_app_data, "NVIDIA", "ChatWithRTX", "RAG", "trt-llm-rag-windows-main", "commands_logs.jsonl")
CHAT_LOGS = os.path.join(local_app_data, "NVIDIA", "ChatWithRTX", "RAG", "trt-llm-rag-windows-main", "chat_logs.jsonl")
CONFIG_JSON = os.path.join(local_app_data, "NVIDIA", "ChatWithRTX", "RAG", "trt-llm-rag-windows-main", "config.json")

def parse_chat_logs(file_path):
    chat_logs = []
    with open(file_path, 'r') as file:
        for line in file:
            try:
                chat_logs.append(json.loads(line))
            except json.JSONDecodeError:
                print("Error decoding JSON from line:", line)
    return chat_logs

chat_logs = parse_chat_logs(CHAT_LOGS)

def find_and_edit_server_config(timestamp, new_data):
    configs = safe_load_json(CONFIG_FILE, default={'servers': []})
    for server in configs['servers']:
        if server.get('timestamp') == timestamp:
            server.update(new_data)  # Update the server data with new_data
            break
    save_config(configs)  # Save the updated configs back to the file

def save_config(config_data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config_data, f, indent=4)
    st.success("Configuration saved successfully.")

def update_server_config(config, server_updates):
    updated = False
    for update in server_updates:
        # Find if the server already exists based on a unique attribute, e.g., address
        for server in config['servers']:
            if server['address'] == update['address']:
                server.update(update)  # Update existing server details
                updated = True
                break
        if not updated:
            # Add a new server configuration if not updated
            config['servers'].append(update)

def safe_load_json(filename, default=None):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except Exception as e:
        st.error(f"Failed to load {filename}: {e}")
        return default
def save_ai_config(config):
    with open(CONFIG_AI_FILE, 'w') as file:
        json.dump(config, file)

# Streamlit sidebar interface for changing AI configuration
def load_ai_config():
    try:
        with open('config_ai.json', 'r') as file:
            config = json.load(file)
            config['AI'] = config.get('AI', DEFAULT_AI)
            config['SYSTEM_MESSAGE'] = config.get('SYSTEM_MESSAGE', DEFAULT_SYSTEM_MESSAGE)
            
            return config
    except Exception as e:
        print(f"Error loading config: {e}")
        # Return default configuration if any error occurs
        return {"AI": DEFAULT_AI, "SYSTEM_MESSAGE": DEFAULT_SYSTEM_MESSAGE}


def save_ai_config(config):
    with open(CONFIG_AI_FILE, 'w') as file:
        json.dump(config, file)

def load_json(filename, default=None):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except Exception as e:
        st.error(f"Failed to load {filename}: {e}")
        return default

def save_json(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)
    st.success("Configuration saved successfully.")



def config_ai_interface():
    st.sidebar.title("AI Configuration")
    config = load_json(CONFIG_AI_FILE, default={"AI": DEFAULT_AI, "SYSTEM_MESSAGE": DEFAULT_SYSTEM_MESSAGE})
    system_message = st.sidebar.text_area("System Message", value=config.get('SYSTEM_MESSAGE', DEFAULT_SYSTEM_MESSAGE))
    if st.sidebar.button("Save Configuration"):
        config['SYSTEM_MESSAGE'] = system_message
        save_json(CONFIG_AI_FILE, config)
        st.sidebar.success("AI Configuration saved!")

def config_ai_interface():
    st.sidebar.title("Save Configs")
    config = load_ai_config()
    system_message = st.sidebar.text_area("System Message", value=config.get('SYSTEM_MESSAGE', DEFAULT_SYSTEM_MESSAGE))
    if st.sidebar.button("Save Configuration"):
        new_config = {
            "AI": "na",
            "SYSTEM_MESSAGE": system_message
        }
        save_ai_config(new_config)
        st.sidebar.success("AI Configuration saved!")


# Initialize session state variables
def init_session_variables():
    if 'editing_index' not in st.session_state:
        st.session_state.editing_index = None
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
    if 'timestamp' not in st.session_state:
        st.session_state.timestamp = ''
    if 'editing_index' not in st.session_state:
        st.session_state.editing_index = None
    if 'tests' not in st.session_state:
        st.session_state.tests = []
    if 'editing_test_index' not in st.session_state:
        st.session_state.editing_test_index = None


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
        commands = st.text_area("Commands (one perline)", value="\n".join(editing_server.get("commands", []))).strip()
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


        # Save or update the server information
        if editing_index is not None:
            servers[editing_index] = server_info
            ## Rewirte out to Chat_log
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

def delete_chat_log_entry_by_timestamp(target_timestamp):
    updated_entries = []
    target_timestamp = float(target_timestamp)  # Convert target timestamp to float for comparison
    with open('chat_logs.jsonl', 'r') as file:
        for line in file:
            try:
                entry = json.loads(line)
                if entry.get('timestamp', 0.0) != target_timestamp:
                    updated_entries.append(line)
            except json.JSONDecodeError:
                continue  # Skip lines that can't be decoded
    with open('chat_logs.jsonl', 'w') as file:
        file.writelines(updated_entries)
def display_servers(servers, editing_index_key, section, save_function, rerun_function):
    for i, server in enumerate(servers):
        st.write(f"Server {i+1}: {server['address']}")
        st.write(f"Username: {server['username']}")
        st.write("Commands:")
        for command in server['commands']:
            st.text(command)
        with st.container():
            col1, col2, col3 = st.columns([1, 1, 1])
            edit_button = col1.button("Edit", key=f"edit_{section}_{i}")
            delete_button = col2.button("Delete", key=f"delete_{section}_{i}")
            
            # Handle edit button press
            if edit_button:
                # Safely retrieve the timestamp, providing a default if not found
                current_editing_timestamp = server.get('timestamp', None)
                # Update the session state to indicate which server is being edited
                st.session_state[editing_index_key] = i
                st.session_state['current_editing_timestamp'] = current_editing_timestamp
                
                rerun_function()  # Rerun the app to load the editing form
            
            # Handle delete button press separately
            if delete_button:
                delete_chat_log_entry_by_timestamp(server.get('timestamp', None))
                save_function()
                rerun_function()
        st.write("---")


def edit_entry_form():
    if 'current_editing_timestamp' in st.session_state and st.session_state['current_editing_timestamp']:
        with open('chat_logs.jsonl', 'r') as file:
            for line in file:
                entry = json.loads(line)
                if entry.get('timestamp') == st.session_state['current_editing_timestamp']:
                    # Populate the form with this entry's data for editing
                    address = st.text_input("Address", value=entry.get('address', ''))
                    # Continue for other fields...
                    if st.form_submit_button("Save Edited Entry"):
                        # Call function to save the edited entry
                        save_edited_entry(entry)
                        st.success("Entry updated successfully!")
                        del st.session_state['current_editing_timestamp']  # Clear the editing state
                        break

def save_edited_entry(edited_entry):
    updated_entries = []
    with open('chat_logs.jsonl', 'r') as file:
        for line in file:
            entry = json.loads(line)
            if entry.get('timestamp') != edited_entry.get('timestamp'):
                updated_entries.append(line)
            else:
                updated_entries.append(json.dumps(edited_entry) + '\n')
    
    with open('chat_logs.jsonl', 'w') as file:
        file.writelines(updated_entries)


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
    init_session_variables()
    display_ui()
    load_config()
    config_ai_interface()
    load_tests()
    ssh_conn_form()
    buttons()
    test_form()
    markdown_file()

    app_process_data.main()

if __name__ == "__main__":
    main()
