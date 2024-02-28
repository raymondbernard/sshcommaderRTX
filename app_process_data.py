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
# Create server config with a timestamp
def create_server_config(commands=[], -=""):
    return {
        "address": "",
        "username": "",
        "password": "",
        "timestamp": timestamp,  # Include the timestamp
        "config_description": "",
        "commands": commands
    }


# Process logs and avoid duplicates, including timestamps
def process_logs(COMMAND_LOGS, config):
    seen_commands = set()
    with open(COMMAND_LOGS, 'r') as file:
        for line in file:
            log_entry = json.loads(line)
            response = log_entry['response'].strip()
            timestamp = log_entry.get('timestamp', "")  # Extract the timestamp
            if response and response not in seen_commands:
                commands = response.split('\n')
                # Pass the timestamp to the server config
                server_config = create_server_config(commands, str(timestamp))
                config['servers'].append(server_config)
                seen_commands.add(response)


# Extract system message
def system_message(file_path):
    post_commands_texts = []
    with open(file_path, 'r') as file:
        for line in file:
            data = json.loads(line)
            response = data.get('response', '')
            match = re.search(r'```\n.*?\n```\n(.+)', response, re.DOTALL)
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
    config = {"servers": [], "hostname": "", "port": 25374, "username": "ubuntu"}
    process_chat_log()
    process_logs(COMMAND_LOGS, config)
    with open(CONFIG_JSON, 'w') as outfile:
        json.dump(config, outfile, indent=4)
    extracted_texts = system_message(CHAT_LOGS)
    update_config_description(CONFIG_JSON, extracted_texts)
    logging.info("Configuration processing complete.")

if __name__ == "__main__":
    main()
