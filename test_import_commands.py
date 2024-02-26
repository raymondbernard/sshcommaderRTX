import json
import logging
import os 
# Setup logging
logging.basicConfig(level=logging.DEBUG, filename='process_logs_debug.log', filemode='w',
                    format='%(asctime)s - %(levelname)s - %(message)s')

import os

# Access the %LOCALAPPDATA% environment variable directly
local_app_data = os.getenv('LOCALAPPDATA')

# Append the specific path to it
COMMAND_LOGS = os.path.join(local_app_data, "NVIDIA", "ChatWithRTX", "RAG", "trt-llm-rag-windows-main", "commands_logs.jsonl")

print(f"The path to COMMAND_LOGS is: {COMMAND_LOGS}")


# Base structure for a single server configuration
def create_server_config(commands=[]):
    return {
        "address": "leaf01",
        "username": "cumulus",
        "password": "cumulus",
        "config_description": "",
        "commands": commands
    }

# Initialize the config structure with an empty servers list
config = {
    "servers": [],
    "hostname": "worker07.air.nvidia.com",
    "port": 25374,
    "username": "ubuntu"
}

def process_logs(COMMAND_LOGS):
    logging.info("Starting to process log file.")
    try:
        with open(COMMAND_LOGS, 'r') as file:
            for line in file:
                try:
                    log_entry = json.loads(line)
                    response = log_entry['response'].strip()
                    if response:
                        # Split commands separated by newlines into individual commands
                        commands = response.split('\n')
                        # Create a new server configuration for each line and add the commands
                        server_config = create_server_config(commands)
                        config['servers'].append(server_config)
                        logging.debug(f"Added server config with commands: {commands}")
                    else:
                        logging.debug("Empty response skipped.")
                except json.JSONDecodeError as e:
                    logging.error(f"Error decoding JSON from line: {e}")
    except FileNotFoundError:
        logging.error(f"File {COMMAND_LOGS} not found.")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

# Process the log filr
process_logs(COMMAND_LOGS)

# Save the updated configuration to a file
with open('config.json', 'w') as outfile:
    json.dump(config, outfile, indent=4)

logging.info("Configuration has been successfully updated and saved.")
print("Configuration processing complete. Check 'process_logs_debug.log' for details.")
