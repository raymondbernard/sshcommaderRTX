import json
import os
import logging
import re
import sqlite3 

# Setup logging
logging.basicConfig(level=logging.INFO, filename='process_logs_debug.log', filemode='w',
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Define file paths
local_app_data = os.getenv('LOCALAPPDATA')
COMMAND_LOGS = os.path.join(local_app_data, "NVIDIA", "ChatWithRTX", "RAG", "trt-llm-rag-windows-main", "commands_logs.jsonl")
CHAT_LOGS = os.path.join(local_app_data, "NVIDIA", "ChatWithRTX", "RAG", "trt-llm-rag-windows-main", "chat_logs.jsonl")
CONFIG_JSON = os.path.join(local_app_data, "NVIDIA", "ChatWithRTX", "RAG", "trt-llm-rag-windows-main", "config.json")
NEW_CONFIG_JSON = os.path.join(local_app_data, "NVIDIA", "ChatWithRTX", "RAG", "trt-llm-rag-windows-main", "confignew.json")
DATABASE_PATH = os.path.join(local_app_data, "NVIDIA", "ChatWithRTX", "RAG", "trt-llm-rag-windows-main", "sshcommander.db")


config_file_path = CONFIG_JSON
chat_logs_file_path = CHAT_LOGS
updated_config_file_path = NEW_CONFIG_JSON

# Function to read the existing configuration from a file
def read_config(config_file_path):
    with open(config_file_path, 'r') as file:
        return json.load(file)

# Function to read chat logs from a JSON Lines file
def read_chat_logs(chat_logs_file_path):
    chat_log_entries = []
    with open(chat_logs_file_path, 'r') as file:
        for line in file:
            chat_log_entries.append(json.loads(line))
    return chat_log_entries

# Helper function to extract command and system message from the response field
def extract_command_and_description(response):
    parts = response.split('```')
    command = parts[1] if len(parts) > 1 else ""
    description = parts[0].strip() if len(parts) > 0 else ""
    return command, description

# Function to update or append new entries to the configuration based on chat logs
def update_configuration(existing_config, chat_log_entries):
    updated_servers = existing_config['servers']
    for entry in chat_log_entries:
        command, description = extract_command_and_description(entry['response'])
        timestamp = entry['timestamp']
        
        # Check if this entry already exists in the configuration
        exists = False
        for server in updated_servers:
            if server['timestamp'] == timestamp and command in server['commands']:
                exists = True
                break
        
        # If the entry does not exist, append it
        if not exists:
            updated_servers.append({
                'address': '',  # Assuming address, username, and password details are not provided
                'username': '',
                'password': '',
                'timestamp': timestamp,
                'config_description': description,
                'commands': [command]
            })
    existing_config['servers'] = updated_servers
    return existing_config


# Function to save the updated configuration to a file
def save_updated_config(updated_config, updated_config_file_path):
    with open(updated_config_file_path, 'w') as file:
        json.dump(updated_config, file, indent=4)


# Function to connect to the SQLite database
def connect_database(db_path):
    return sqlite3.connect(db_path)

# Function to create the servers table
def create_tables(conn):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS servers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            address TEXT NOT NULL,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            timestamp REAL UNIQUE NOT NULL,
            config_description TEXT NOT NULL,
            commands TEXT 
        );
    """)
    conn.commit()

# Function to insert or update server configurations in the database
def insert_or_update_server_db(conn, server):
    cursor = conn.cursor()
    # Check if a server with this timestamp already exists
    cursor.execute("SELECT id FROM servers WHERE timestamp = ?", (server['timestamp'],))
    server_id = cursor.fetchone()
    if server_id:
        # Server exists, update it (if needed)
        server_id = server_id[0]
    else:
        # Insert new server
        cursor.execute("""
            INSERT INTO servers (address, username, password, timestamp, config_description, commands) 
            VALUES (?, ?, ?, ?, ?, ?)
            """, (server['address'], server['username'], server['password'], server['timestamp'], server['config_description'], json.dumps(server['commands'])))
        server_id = cursor.lastrowid
    conn.commit()
    return server_id

# Function to close the database connection
def close_database_connection(conn):
    conn.close()


if __name__ == '__main__':

    # Paths to the existing configuration and chat logs files

    # Execute the functions to read, update, and save the configuration
    existing_config = read_config(config_file_path)
    chat_log_entries = read_chat_logs(chat_logs_file_path)
    updated_config = update_configuration(existing_config, chat_log_entries)
    save_updated_config(updated_config, updated_config_file_path)
    conn = connect_database(DATABASE_PATH)
    create_tables(conn)
    
    # Assuming existing_config and chat_log_entries are obtained as before
    existing_config = read_config(CONFIG_JSON)  # Ensure this path is correct
    chat_log_entries = read_chat_logs(CHAT_LOGS)  # Ensure this path is correct
    
    # Update or insert server configurations in the database
    for server in existing_config['servers']:
        insert_or_update_server_db(conn, server)
    
    close_database_connection(conn)
    logging.info("Configuration data has been successfully updated in the database.")