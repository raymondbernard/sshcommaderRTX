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
CHAT_LOGS = os.path.join(local_app_data, "NVIDIA", "ChatWithRTX", "RAG", "trt-llm-rag-windows-main", "chat_logs.jsonl")
DATABASE_PATH = os.path.join(local_app_data, "NVIDIA", "ChatWithRTX", "RAG", "trt-llm-rag-windows-main", "sshcommander.db")
chat_logs_file_path = CHAT_LOGS


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
    description = parts[2].strip() if len(parts) > 0 else ""
    
    return command, description

# Function to update or append new entries to the configuration based on chat logs
def update_configuration(chat_log_entries):
    conn = connect_database(DATABASE_PATH)
    for entry in chat_log_entries:
        command, description = extract_command_and_description(entry['response'])
        timestamp = entry['timestamp']
        # Check if a server with this timestamp already exists
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO servers (address, username, password, timestamp, config_description, commands) 
            VALUES (?, ?, ?, ?, ?, ?)
            """, ('', '', '', timestamp, description, command))
        conn.commit()
    return 
        

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

def close_database_connection(conn):
    conn.close()

if __name__ == '__main__':
    chat_log_entries = read_chat_logs(chat_logs_file_path)
    updated_config = update_configuration(chat_log_entries)
    print("read chatlogs = ", chat_log_entries)
    print(" update config", updated_config)
    conn = connect_database(DATABASE_PATH)
    create_tables(conn)
    close_database_connection(conn)
    logging.info("Configuration data has been successfully updated in the database.")