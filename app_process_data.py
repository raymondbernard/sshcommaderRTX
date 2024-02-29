import json
import os
import logging
import sqlite3

# Setup logging
logging.basicConfig(level=logging.INFO, filename='process_logs_debug.log', filemode='w',
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Define file paths
local_app_data = os.getenv('LOCALAPPDATA')
CHAT_LOGS = os.path.join(local_app_data, "NVIDIA", "ChatWithRTX", "RAG", "trt-llm-rag-windows-main", "chat_logs.jsonl")
DATABASE_PATH = os.path.join(local_app_data, "NVIDIA", "ChatWithRTX", "RAG", "trt-llm-rag-windows-main", "sshcommander.db")

def parse_chat_logs(chat_logs_path):
    results = []
    with open(chat_logs_path, 'r') as file:
        for line in file:
            data = json.loads(line.strip())
            session_id, query, response, timestamp = data.get('session_id', ''), data.get('query', ''), data.get('response', ''), data.get('timestamp', '')
            command, description = '', ''
            if '```' in response:
                parts = response.split('```')
                command = parts[1].strip() if len(parts) > 1 else ""
                description = parts[2].strip() if len(parts) > 2 else ""
            results.append({'session_id': session_id, 'query': query, 'command': command, 'config_description': description, 'timestamp': timestamp})
    return results

def update_configuration(chat_log_entries, db_path):
    conn = connect_database(db_path)
    cursor = conn.cursor()
    try:
        for entry in chat_log_entries:
            try:
                cursor.execute("""
                    INSERT INTO servers (session_id, query, address, username, password, timestamp, config_description, commands) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (entry['session_id'], entry['query'], '', '', '', entry['timestamp'], entry['config_description'], entry['command']))
            except Exception as e:
                logging.error("Error updating configuration for entry %s: %s", entry.get('session_id'), e)
        conn.commit()
    except Exception as e:
        logging.error("Critical error updating configurations: %s", e)
        conn.rollback()
    finally:
        conn.close()


def connect_database(db_path):
    return sqlite3.connect(db_path)

def create_tables(conn):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS servers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            query TEXT NOT NULL,
            address TEXT NOT NULL,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            timestamp REAL UNIQUE NOT NULL,
            config_description TEXT NOT NULL,
            commands TEXT 
        );
    """)
    conn.commit()

if __name__ == '__main__':
    conn = connect_database(DATABASE_PATH)
    create_tables(conn)
    conn.close()

    chat_log_entries = parse_chat_logs(CHAT_LOGS)
    update_configuration(chat_log_entries, DATABASE_PATH)
    logging.info("Configuration data has been successfully updated in the database.")
