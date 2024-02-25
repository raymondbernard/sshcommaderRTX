import json
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG, filename='process_logs_debug.log', filemode='w',
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Base structure for a single server configuration
def create_server_config(commands=[]):
    return {
        "address": "leaf01",
        "username": "cumulus",
        "password": "cumulus",
        "config_description": "Configuration details will be dynamically updated based on command logs.",
        "commands": commands
    }

# Initialize the config structure with an empty servers list
config = {
    "servers": [],
    "hostname": "worker07.air.nvidia.com",
    "port": 25374,
    "username": "ubuntu"
}

def process_logs(file_path):
    logging.info("Starting to process log file.")
    try:
        with open(file_path, 'r') as file:
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
        logging.error(f"File {file_path} not found.")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

# Process the log file
process_logs('commands_logs.jsonl')

# Save the updated configuration to a file
with open('config.json', 'w') as outfile:
    json.dump(config, outfile, indent=4)

logging.info("Configuration has been successfully updated and saved.")
print("Configuration processing complete. Check 'process_logs_debug.log' for details.")
