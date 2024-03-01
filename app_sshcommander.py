import requests
import streamlit as st
import paramiko
import os
import json
import time
import select 
import os
import app_process_data
import os
from datetime import datetime
import sqlite3 


# Constants
TEST_FILE = "test.json"

# Assuming DATABASE_PATH is defined
DATABASE_PATH = 'path_to_your_database.db'


# AI  = "call_openai"
## command out below if ou use call_openai 
DEFAULT_AI = "call_nvidi" 
DEFAULT_SYSTEM_MESSAGE  = "Note we are using Nvidia's cumulus Linux distribution, just describe the commands you see.   Please keep your responses short and precise."
# Define file paths
local_app_data = os.getenv('LOCALAPPDATA')
DATABASE_PATH = os.path.join(local_app_data, "NVIDIA", "ChatWithRTX", "RAG", "trt-llm-rag-windows-main", "sshcommander.db")
# Define file paths
COMMAND_LOGS = os.path.join(local_app_data, "NVIDIA", "ChatWithRTX", "RAG", "trt-llm-rag-windows-main", "commands_logs.jsonl")
CHAT_LOGS = os.path.join(local_app_data, "NVIDIA", "ChatWithRTX", "RAG", "trt-llm-rag-windows-main", "chat_logs.jsonl")
CONFIG_JSON = os.path.join(local_app_data, "NVIDIA", "ChatWithRTX", "RAG", "trt-llm-rag-windows-main", "config.json")
NEW_CONFIG_JSON = os.path.join(local_app_data, "NVIDIA", "ChatWithRTX", "RAG", "trt-llm-rag-windows-main", "confignew.json")


CONFIG_FILE = CONFIG_JSON
chat_logs_file_path = CHAT_LOGS
updated_config_file_path = NEW_CONFIG_JSON
# Function to connect to the SQLite database

def load_servers_from_db(conn):
    cursor = conn.cursor()
    # Modified SQL query to include ROW_NUMBER
    cursor.execute("""
        SELECT 
            ROW_NUMBER() OVER (ORDER BY id) AS row_num,
            id,
            session_id,
            query,
            address,
            username,
            password,
            timestamp,
            config_description,
            commands
        FROM servers
    """)
    servers = cursor.fetchall()
    servers_list = []
    print("line 60 server_list = ", servers_list)

    # Refactored loop to populate servers_list with server details, including row number
    for server in servers:
        server_dict = {
            'row_num': server[0],  # Added row_num based on the adjusted query
            'id': server[1],
            'session_id': server[2],
            'query': server[3],
            'address': server[4],
            'username': server[5],
            'password': server[6],
            'timestamp': server[7],
            'config_description': server[8],
            'commands': server[9]
        }
        servers_list.append(server_dict)
    print("line 61 server_list", servers_list)
    # Update session_state with servers_list
    st.session_state['servers'] = servers_list
    st.write("After init:", st.session_state.servers)
    cursor.close()
    conn.close()
    return st.session_state

    
    


# Function to connect to the SQLite database
def connect_database(db_path):
    return sqlite3.connect(db_path)

# # Display server commands if servers exist in session_state
# if 'servers' in st.session_state:
#     for server in st.session_state['servers']:
#         st.text(server['commands'])

#         # Example usage
#         conn = connect_database(DATABASE_PATH)
#         load_servers_from_db(conn)
#             # After the loop, assign servers_list to the Streamlit session state
#         st.session_state.servers = servers_list

# # Optional: Print the servers list to the console for debugging purposes
# print(servers_list)


# def save_server_to_db(conn,server):
#     cursor = conn.cursor()
#     # Convert commands list to JSON string for storage
#     commands_json = json.dumps(server['commands'])
#     if 'id' in server:  # Update existing server
#         cursor.execute("""
#             UPDATE servers SET address = ?, username = ?, password = ?, timestamp = ?, config_description = ?, commands = ?
#             WHERE id = ?""", (server['address'], server['username'], server['password'], server['timestamp'], server['config_description'], commands_json, server['id']))
#     else:  # Insert new server
#         cursor.execute("""
#             INSERT INTO servers (address, username, password, timestamp, config_description, commands)
#             VALUES (?, ?, ?, ?, ?, ?)""", (server['address'], server['username'], server['password'], server['timestamp'], server['config_description'], commands_json))
#     conn.commit()



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


# def save_ai_config(config):
#     with open(CONFIG_AI_FILE, 'w') as file:
#         json.dump(config, file)

# # def config_ai_interface():
#     st.sidebar.title("AI Configuration")
#     config = load_json(CONFIG_AI_FILE, default={"AI": DEFAULT_AI, "SYSTEM_MESSAGE": DEFAULT_SYSTEM_MESSAGE})
#     system_message = st.sidebar.text_area("System Message", value=config.get('SYSTEM_MESSAGE', DEFAULT_SYSTEM_MESSAGE))
#     if st.sidebar.button("Save Configuration"):
#         config['SYSTEM_MESSAGE'] = system_message
#         save_json(CONFIG_AI_FILE, config)
#         st.sidebar.success("AI Configuration saved!")

# def config_ai_interface():
#     st.sidebar.title("Save Configs")
#     config = load_ai_config()
#     system_message = st.sidebar.text_area("System Message", value=config.get('SYSTEM_MESSAGE', DEFAULT_SYSTEM_MESSAGE))
#     if st.sidebar.button("Save Configuration"):
#         new_config = {
#             "AI": "na",
#             "SYSTEM_MESSAGE": system_message
#         }
#         save_ai_config(new_config)
#         st.sidebar.success("AI Configuration saved!")


# Initialize session state variables
def init_session_variables():
    if 'editing_index' not in st.session_state:
        st.session_state.editing_index = None
    if 'id' not in st.session_state:
        st.session_state.id = None
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
        server_input_form(st.session_state.servers, st.session_state.editing_index, 'server_form', "Configure your devices", save_server_to_db)


# Define the add_configuration function here
def add_configuration(server, title, description, commands):
    if 'configurations' not in server:
        server['configurations'] = []
    server['configurations'].append({
        'description': description,
        'commands': commands
    })

# Load existing configuration and tests
# def load_config():
 
        
#         st.session_state.servers = data.get("servers", [])
#         st.session_state.hostname = data.get("hostname", "")
#         st.session_state.port = data.get("port", 22)
#         st.session_state.username = data.get("username", "")
        
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

# # Save configuration 
def save_config():
    data = {
        "servers": st.session_state.servers,
        "hostname": st.session_state.hostname,
        "port": st.session_state.port,
        "username": st.session_state.username,
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f)

def save_server_to_db(servers):
    conn = connect_database(DATABASE_PATH)
    cursor = conn.cursor()
    id = 0
    for server in servers:
        if not isinstance(server, dict) or 'commands' not in server:
            print(f"Error: Invalid server data format or missing 'commands' key: {server}")
            continue
        id += 1
        print("LOOPS !!!!! == ", id )
        # Assuming 'commands' is a list and needs to be serialized
        commands_json = json.dumps(server['commands']) if isinstance(server['commands'], list) else server['commands']
        address_value = server.get('address', 'default_value_if_missing')
        username_value = server.get('username', 'default_value_if_missing')
        password_value = server.get('password', 'default_value_if_missing')
        # config_description = server.get('password', 'default_value_if_missing')
        newid = server.get('row_num')
        print("line 360 serverid == ", server.get('id',))
        print("line 361 newid row num  == ", server.get('row_num',))
        print("line 362 newid   == ", newid)
        # if not newid:
        #     newid = 1 
        # print("line 365 server id" , server['id'])
        print("line 366 newid == ", newid)
        print("line 367  commands json  id = ", id, commands_json)
    

        try:
            cursor.execute("""
                UPDATE servers SET address = ?, username = ?, password = ?, commands = ?
                WHERE id = ?""",
                (address_value, username_value, password_value, commands_json, id))
            print(f"Updated server with id {server['id']}")
        except Exception as e:
            continue
            # print(f"An error occurred while updating: {e}")


    conn.commit()
    cursor.close()


# Save tests
def save_tests():
    data = {
        "tests": st.session_state.tests,
    }
    with open(TEST_FILE, "w") as f:
        json.dump(data, f)


# Server Information Input
        
def server_input_form(servers, editing_index, key, title,  save_server_to_db):
    with st.form(key=key):
        st.subheader(title)
        editing_server = servers[editing_index] if editing_index is not None else {}
        current_timestamp = datetime.now().timestamp()

        # If editing, use the existing timestamp, otherwise generate a new one for new entries
        # current_timestamp = editing_server.get("timestamp", datetime.now().isoformat())
        print("line 417 current_timestamp", current_timestamp)
        
        address = st.text_input("Address of server/device", value=editing_server.get("address", "")).strip()
        server_username = st.text_input("Username", value=editing_server.get("username", "")).strip()
        server_password = st.text_input("Password (optional)", type="password", value=editing_server.get("password", "")).strip()

        commands = st.text_area("Commands (one per line)", value="".join(editing_server.get("commands", ""))).strip()
        save_server_to_db(servers)
        submit_button = st.form_submit_button("Save configuration")
    
    if submit_button:
        # Update session state with the new values
        st.session_state.server_address = address
        st.session_state.server_username = server_username
        st.session_state.server_password = server_password
        st.session_state.commands = commands


        # Gather server information
        server_info = {
            "address": address,
            "username": server_username,
            "password": server_password,
            "timestamp": current_timestamp,  # Use the existing or new timestamp
            "config_description": "",
            "commands": [cmd.strip() for cmd in commands.split('\n') if cmd.strip()]
        }

        # Save or update the server information
        if editing_index is not None:
            servers[editing_index] = server_info
        else:
            servers.append(server_info)
        save_server_to_db(servers)
        st.success("Server saved successfully")


def buttons():
    with st.expander("View Saved Configurations and or Edit/Delete"):
        display_servers(st.session_state.servers, 'editing_index', 'config', save_server_to_db, st.rerun)
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



def refactordb():

    # Connect to your SQLite database
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()


    # Step 1: Create a temporary table to store the current data
    cursor.execute("""CREATE TEMPORARY TABLE tmp_servers AS SELECT * FROM servers;""")

    # Step 2: Drop the original 'servers' table
    cursor.execute("""DROP TABLE servers;""")

    # Step 3: Recreate the 'servers' table with the updated structure, including all specified columns
    cursor.execute("""
    CREATE TABLE "servers" (
        "id"    INTEGER PRIMARY KEY AUTOINCREMENT,
        "session_id" TEXT NOT NULL,
        "query" TEXT NOT NULL,
        "address"   TEXT NOT NULL,
        "username"  TEXT NOT NULL,
        "password"  TEXT NOT NULL,
        "timestamp" REAL NOT NULL UNIQUE,
        "config_description" TEXT NOT NULL,
        "commands"  TEXT
    );
    """)

    # Step 4: Copy data from the temporary table to the 'servers' table with new primary keys
    # Ensure all columns including 'query' are correctly listed in both the INSERT INTO and SELECT parts
    cursor.execute("""
    INSERT INTO servers (session_id, query, address, username, password, timestamp, config_description, commands)
    SELECT session_id, query, address, username, password, timestamp, config_description, commands FROM tmp_servers;
    """)

    # Step 5: Drop the temporary table
    cursor.execute("""DROP TABLE tmp_servers;""")

    # Commit changes and close connection
    conn.commit()
    conn.close()


def delete_server_from_db(server):

    server_id = server['id']  # Correctly capture the server's ID
    conn = connect_database(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM servers WHERE id = ?", (server_id,))  # Pass ID as a tuple
    conn.commit()
    cursor.close()
    conn.close()
    refactordb()

    # Filter out the deleted server from session state
    updated_servers = [s for s in st.session_state.servers if s['id'] != server_id]

    # Optionally, reassign row numbers for display purposes
    for i, server in enumerate(updated_servers, start=1):
        server['row_num'] = i  # Assign new row numbers starting from 1

    st.session_state.servers = updated_servers


def display_servers(servers, editing_index_key, section, delete_server_from_db, rerun_function):
    for i, server in enumerate(servers):
        st.write(f"Server {i+1}: {server['address']}")
        st.write(f"Username: {server['username']}")
        st.write("Commands:")
       
        st.text(server['commands'])

        with st.container():
            col1, col2, col3 = st.columns([1, 1, 1])
            edit_button = col1.button("Edit", key=f"edit_{section}_{i}")
            delete_button = col2.button("Delete", key=f"delete_{section}_{i}")
            
            # Handle edit button press
            if edit_button:
                # Safely retrieve the timestamp, providing a default if not found
                # Update the session state to indicate which server is being edited
                st.session_state[editing_index_key] = i
                
                rerun_function()  # Rerun the app to load the editing form
                st.session_state.clear()

            # Handle delete button press separately
            if delete_button:
    
                print("line 522 servers == ", server)
                print("line 523 server id = ", server['id'])
                print("line 534, = ",servers[i])
                delete_server_from_db(server)
                st.session_state.clear()

                rerun_function()
        st.write("---")


# call nvidia or openai api 
def call_ai(ai_type, commands):
    with st.spinner('Waiting for AI response...'):
        print("Calling Nvidia Local")
        
        return call_nvidia(commands)
    

# read the config.json file for markdown conversion       
def read_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# process config to markdown 
def display_servers_as_markdown(servers):
    markdown_text = ""
    print("590 servers markdown === ", servers)
    if servers and 'servers' in servers:
        for server in servers['servers']:
            # Adding server details and description
            # markdown_text += f"## Server ID: {server['id']}\n\n"
            markdown_text += f"**Session ID:** `{server['session_id']}`\n\n"
            markdown_text += f"**Query:** {server['query']}\n\n"
            markdown_text += f"**Configuration Note:**\n\n> {server['config_description']}\n\n"
            markdown_text += "**Commands:**\n\n```bash\n"
            
            # Assuming commands are stored as a single string with newline characters
            markdown_text += f"{server['commands']}\n```\n\n"
            
            markdown_text += "---\n\n"  # Separator between server configurations
    else:
        markdown_text += "No servers configured.\n"

    return markdown_text
# create a markdown of the contents of the config.json file
def markdown_file(servers):
    st.sidebar.button('Read Config', on_click=lambda: st.session_state.update({'read_config': True}))
    if 'read_config' in st.session_state and st.session_state['read_config']:
        config_file = 'config.json'
        markdown_text = display_servers_as_markdown(servers)
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

# Function to close the database connection
def close_database_connection(conn):
    conn.close()
# Main Application Logic

def main():
    # st.session_state.clear()
    conn = connect_database(DATABASE_PATH)
    init_session_variables()
    display_ui()
    # load_config()
    # config_ai_interface()
    servers = load_servers_from_db(conn)
    load_tests()
    ssh_conn_form()
    buttons()
    markdown_file(servers)
    close_database_connection(conn)
    # app_process_data.main()
    
if __name__ == "__main__":
    main()
