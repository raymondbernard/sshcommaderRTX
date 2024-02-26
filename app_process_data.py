import json
import os 
import logging
# import gc 
import json 
import re 


# Setup logging
logging.basicConfig(level=logging.INFO)

# import commands     
local_app_data = os.getenv('LOCALAPPDATA')

# Append the specific path to it
COMMAND_LOGS = os.path.join(local_app_data, "NVIDIA", "ChatWithRTX", "RAG", "trt-llm-rag-windows-main", "commands_logs.jsonl")
    
# Append the specific path to it
CHAT_LOGS = os.path.join(local_app_data, "NVIDIA", "ChatWithRTX", "RAG", "trt-llm-rag-windows-main", "chat_logs.jsonl")

# Append the specific path to it
CONFIG_JSON= os.path.join(local_app_data, "NVIDIA", "ChatWithRTX", "RAG", "trt-llm-rag-windows-main", "config.json")


# Append the specific path to it
CONFIG_AI= os.path.join(local_app_data, "NVIDIA", "ChatWithRTX", "RAG", "trt-llm-rag-windows-main", "config_ai.json")



## Extract Chat_logs to prepare them to import commands function 
def process_response(response):
    # First, try to extract content within triple backticks
    pattern = r'```(.*?)```'
    matches = re.findall(pattern, response, re.DOTALL)
    if matches:
        # If found, join all matches. Assumes you want all extracted commands concatenated.
        return '\n'.join(matches).strip()
    else:
        # If not found, handle the edge case with newline characters
        # Keep everything up to and including the first newline
        split_response = response.split('\n', 1)
        if len(split_response) > 1:
            # Return up to and including the first newline
            return split_response[0] + '\n'
        else:
            # If there's no newline, return the entire response
            return response

def process_chat_log():
    # File paths

    # Processing each line in the file
    with open(CHAT_LOGS, 'r') as input_file, open(COMMAND_LOGS, 'w') as output_file:
        for line in input_file:
            data = json.loads(line)
            # Process the response to extract the desired content
            data['response'] = process_response(data['response'])
            # Writing the modified data to the new file
            output_file.write(json.dumps(data) + '\n')

    # Setup logging
    logging.basicConfig(level=logging.DEBUG,
                        filename='process_logs_debug.log',
                        filemode='w',
                        format='%(asctime)s - %(levelname)s - %(message)s')

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



def system_message(file_path):
    # This list will hold all extracted texts following the triple backticks
    post_commands_texts = []

    with open(file_path, 'r') as file:
        for line in file:
            try:
                # Parse the JSON object from each line
                data = json.loads(line)
                
                # Extract the response field
                response = data.get('response', '')
                
                # Use a regular expression to find the text after the triple backticks
                match = re.search(r'```\n.*?\n```\n(.+)', response, re.DOTALL)
                if match:
                    # Extract the text after the triple backticks
                    post_command_text = match.group(1).strip()
                    post_commands_texts.append(post_command_text)
            except json.JSONDecodeError:
                print("Error decoding JSON from line:", line)
                continue
    
    return post_commands_texts

def update_config_description(CONFIG_JSON, extracted_texts):
    # Load the JSON data from the config file
    with open(CONFIG_JSON, 'r') as file:
        config_data = json.load(file)

    # Initialize an index to iterate through the extracted_texts list
    text_index = 0
    
    # Ensure there are extracted texts to use for updates
    if not extracted_texts:
        print("No extracted texts available for updates.")
        return
    
    # Iterate over the servers in the config
    for server in config_data['servers']:
        # Check if config_description is empty and an extracted text is available
        if not server['config_description'] and text_index < len(extracted_texts):
            server['config_description'] = extracted_texts[text_index]
            text_index += 1  # Move to the next extracted text for the next server

    # Write the updated JSON data back to the file
    with open(CONFIG_JSON, 'w') as file:
        json.dump(config_data, file, indent=4)



# Main Application Logic
def main():
    # Define the path to your cha_logs file
    file_path = CHAT_LOGS
    process_chat_log()

    process_logs(COMMAND_LOGS)

    # Save the updated configuration to a file
    with open('config.json', 'w') as outfile:
        json.dump(config, outfile, indent=4)

    logging.info("Configuration has been successfully updated and saved.")
    print("Configuration processing complete. Check 'process_logs_debug.log' for details.")
    # Extract texts from cha_logs
    extracted_texts = system_message(file_path)

    # Update the config.json file with extracted texts
    update_config_description(CONFIG_JSON, extracted_texts)


if __name__=="__main__":
    main()

