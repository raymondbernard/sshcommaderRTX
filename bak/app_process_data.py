import json
import logging
# import gc 
import json 
import re 


# Setup logging
logging.basicConfig(level=logging.INFO)

# MODEL_CONFIG_FILE = '.\\config\\config.json'
# PREFERANCE_CONFIG_FILE = '.\\config\\preferences.json'
# SYSTEM_MESSAGE_FILE = 'config_ai.json'
# CONFIG_JSON_FILE = 'config.json'

# def read_system_message(SYSTEM_MESSAGE_FILE):
#     try:
#         with open(SYSTEM_MESSAGE_FILE, 'r') as file:
#             data = json.load(file)
#             system_message = data.get("SYSTEM_MESSAGE", "Key not found.")
#             print(system_message)
#     except FileNotFoundError:
#         print("JSON file not found.")
#     except json.JSONDecodeError:
#         print("Error decoding JSON.")
#     except Exception as e:
#         print(f"An error occurred: {e}")
#     return system_message


# def run_once(func):
#     """Function decorator that ensures the function runs only once."""
#     result = {}

#     def wrapper(*args, **kwargs):
#         if func not in result:
#             result[func] = func(*args, **kwargs)
#         return result[func]
    
#     return wrapper


# def read_config(file_name):
#     try:
#         with open(file_name, 'r') as file:
#             return json.load(file)
#     except FileNotFoundError:
#         print(f"The file {file_name} was not found.")
#     except json.JSONDecodeError:
#         print(f"There was an error decoding the JSON from the file {file_name}.")
#     except Exception as e:
#         print(f"An unexpected error occurred: {e}")
#     return None

# def get_model_config(config, model_name=None):
#     models = config["models"]["supported"]
#     selected_model = next((model for model in models if model["name"] == model_name), models[0])
#     return {
#         "model_path": os.path.join(os.getcwd(), selected_model["metadata"]["model_path"]),
#         "engine": selected_model["metadata"]["engine"],
#         "tokenizer_path": os.path.join(os.getcwd(), selected_model["metadata"]["tokenizer_path"]),
#         "max_new_tokens": selected_model["metadata"]["max_new_tokens"],
#         "max_input_token": selected_model["metadata"]["max_input_token"],
#         "temperature": selected_model["metadata"]["temperature"]
#     }


# @run_once
# def initialize_llm():
 
#     # read model specific config
#     selected_model_name = None
#     config = read_config(MODEL_CONFIG_FILE)
#     if os.path.exists(PREFERANCE_CONFIG_FILE):
#         perf_config = read_config(PREFERANCE_CONFIG_FILE)
#         selected_model_name = perf_config.get('models', {}).get('selected')

#     model_config = get_model_config(config, selected_model_name)

#     # create trt_llm engine object
#     llm = TrtLlmAPI(
#         model_path=model_config["model_path"],
#         engine_name=model_config["engine"],
#         tokenizer_dir=model_config["tokenizer_path"],
#         temperature=model_config["temperature"],
#         max_new_tokens=model_config["max_new_tokens"],
#         context_window=model_config["max_input_token"],
#         verbose=False
#     )
#     return llm 
    

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
    input_file_path = 'C:\\Users\\RayBe\\AppData\\Local\\NVIDIA\\ChatWithRTX\\RAG\\trt-llm-rag-windows-main\\chat_logs.jsonl'
    output_file_path = 'C:\\Users\\RayBe\\AppData\\Local\\NVIDIA\\ChatWithRTX\\RAG\\trt-llm-rag-windows-main\\commands_logs.jsonl'

    # Processing each line in the file
    with open(input_file_path, 'r') as input_file, open(output_file_path, 'w') as output_file:
        for line in input_file:
            data = json.loads(line)
            # Process the response to extract the desired content
            data['response'] = process_response(data['response'])
            # Writing the modified data to the new file
            output_file.write(json.dumps(data) + '\n')

    # Setup logging
    logging.basicConfig(level=logging.DEBUG, filename='process_logs_debug.log', filemode='w',
                        format='%(asctime)s - %(levelname)s - %(message)s')

# import Commands Functions 
# Base structure for a single server configuration
def create_server_config(commands=[]):
    return {
        "address": "leaf01",
        "username": "cumulus",
        "password": "cumulus",
        "config_description": "",
        "commands": commands
    }

## Interm step setting up commands_logs.jsonl 
def process_logs(file_path):
    # Initialize the config structure with an empty servers list
    config = {
        "servers": [],
        "hostname": "worker07.air.nvidia.com",
        "port": 25374,
        "username": "ubuntu"
    }

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
    process_logs('C:\\Users\\RayBe\\AppData\\Local\\NVIDIA\\ChatWithRTX\\RAG\\trt-llm-rag-windows-main\\commands_logs.jsonl')

    # Save the updated configuration to a file
    with open('C:\\Users\\RayBe\\AppData\\Local\\NVIDIA\\ChatWithRTX\\RAG\\trt-llm-rag-windows-main\\config.json', 'w') as outfile:
        json.dump(config, outfile, indent=4)

    logging.info("Configuration has been successfully updated and saved.")
    print("Configuration processing complete. Check 'process_logs_debug.log' for details.")

config_file_path = 'C:\\Users\\RayBe\\AppData\\Local\\NVIDIA\\ChatWithRTX\\RAG\\trt-llm-rag-windows-main\\config.json'



# Define the path to your cha_logs file
file_path = 'C:\\Users\\RayBe\\AppData\\Local\\NVIDIA\\ChatWithRTX\\RAG\\trt-llm-rag-windows-main\\chat_logs.jsonl'

def parse_cha_logs(file_path):
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

def update_config_description(config_file_path, extracted_texts):
    # Load the JSON data from the config file
    with open(config_file_path, 'r') as file:
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
    with open(config_file_path, 'w') as file:
        json.dump(config_data, file, indent=4)

# Extract texts from cha_logs
extracted_texts = parse_cha_logs(file_path)




# Main Application Logic
def main():
 
    # Example usage
    # llm = initialize_llm()  # This initializes the LLM and returns the instance.
    # another_llm_instance = initialize_llm()  # This will return the same instance as before without re-initializing.


    process_chat_log()
    # Update the config.json file with extracted texts
    config_file_path = 'C:\\Users\\RayBe\\AppData\\Local\\NVIDIA\\ChatWithRTX\\RAG\\trt-llm-rag-windows-main\\config.json'
    update_config_description(config_file_path, extracted_texts)


    # system_message = read_system_message(SYSTEM_MESSAGE_FILE)
    # update_config_descriptions(CONFIG_JSON_FILE, system_message, llm)

if __name__=="__main__":
    main()

