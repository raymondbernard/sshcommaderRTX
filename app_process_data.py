import json
import os
import logging
import re

# Setup logging
logging.basicConfig(level=logging.INFO, filename='process_logs_debug.log', filemode='w',
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Define file paths
local_app_data = os.getenv('LOCALAPPDATA')
COMMAND_LOGS = os.path.join(local_app_data, "NVIDIA", "ChatWithRTX", "RAG", "trt-llm-rag-windows-main", "commands_logs.jsonl")
CHAT_LOGS = os.path.join(local_app_data, "NVIDIA", "ChatWithRTX", "RAG", "trt-llm-rag-windows-main", "chat_logs.jsonl")
CONFIG_JSON = os.path.join(local_app_data, "NVIDIA", "ChatWithRTX", "RAG", "trt-llm-rag-windows-main", "config.json")

# Load and preserve existing config
def load_existing_config():
    try:
        with open(CONFIG_JSON, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {"servers": []}

# Check and update server config
def check_and_update_server_config(existing_config, new_server):
    existing_server = next((server for server in existing_config['servers'] if server['timestamp'] == new_server['timestamp']), None)
    if existing_server:
        for field in ['address', 'username', 'password']:
            if new_server[field]:  # Only update if new_server has a non-empty value for the field
                existing_server[field] = new_server[field]
    else:
        existing_config['servers'].append(new_server)

# Process response
def process_response(response):
    pattern = r'```(.*?)```'
    matches = re.findall(pattern, response, re.DOTALL)
    return '\n'.join(matches).strip() if matches else response.split('\n', 1)[0] + '\n' if '\n' in response else response

# Process chat log
def process_chat_log():
    with open(CHAT_LOGS, 'r') as input_file, open(COMMAND_LOGS, 'w') as output_file:
        for line in input_file:
            data = json.loads(line)
            data['response'] = process_response(data['response'])
            output_file.write(json.dumps(data) + '\n')

# Create server config
def create_server_config(commands=[], timestamp=""):
    return {
        "address": "",
        "username": "",
        "password": "",
        "timestamp": timestamp,
        "config_description": "",
        "commands": commands
    }

# Process logs and avoid duplicates, including timestamps
def process_logs(COMMAND_LOGS, config):
    seen_commands = set()
    existing_config = load_existing_config()
    with open(COMMAND_LOGS, 'r') as file:
        for line in file:
            log_entry = json.loads(line)
            response = log_entry['response'].strip()
            timestamp = log_entry.get('timestamp', "")
            if response and timestamp not in seen_commands:
                commands = response.split('\n')
                server_config = create_server_config(commands, timestamp)
                check_and_update_server_config(existing_config, server_config)
            seen_commands.add(response)
    return existing_config

# Extract system message
def system_message(file_path):
    post_commands_texts = []
    with open(file_path, 'r') as file:
        for line in file:
            data = json.loads(line)
            response = data.get('response', '')
            match = re.search(r'```.*?```\s*(.+)', response, re.DOTALL)
            if match:
                post_commands_texts.append(match.group(1).strip())
    return post_commands_texts

# Update config description
def update_config_description(CONFIG_JSON, extracted_texts):
    with open(CONFIG_JSON, 'r') as file:
        config_data = json.load(file)
    text_index = 0
    for server in config_data['servers']:
        if text_index < len(extracted_texts):
            server['config_description'] = extracted_texts[text_index]
            text_index += 1
    with open(CONFIG_JSON, 'w') as file:
        json.dump(config_data, file, indent=4)

# Main Application Logic
def main():
    config = load_existing_config()  # Load existing config to preserve fields
    process_chat_log()
    updated_config = process_logs(COMMAND_LOGS, config)  # Process logs and update config with preservation

    extracted_texts = system_message(CHAT_LOGS)
    update_config_description(CONFIG_JSON, extracted_texts)

    # Save the updated config back to CONFIG_JSON
    with open(CONFIG_JSON, 'w') as outfile:
        json.dump(updated_config, outfile, indent=4)

    logging.info("Configuration processing complete.")

if __name__ == "__main__":
    main()
