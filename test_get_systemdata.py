import json
import re

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

# Update the config.json file with extracted texts
config_file_path = 'C:\\Users\\RayBe\\AppData\\Local\\NVIDIA\\ChatWithRTX\\RAG\\trt-llm-rag-windows-main\\config.json'
update_config_description(config_file_path, extracted_texts)
