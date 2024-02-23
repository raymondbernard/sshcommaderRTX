import json

# Function to reformat the response field based on certain criteria
def reformat_response(data):
    # Check if the response contains commands and reformat if necessary
    # This is just an example based on your provided output. You might need to adjust the logic.
    if "nv set interface" in data['response']:
        # Split the response into lines, strip each line, and join back with newline characters
        commands = data['response'].split('\n')
        commands = [cmd.strip() for cmd in commands if cmd.strip()]  # Remove empty lines and strip
        data['response'] = '\n'.join(commands)
    elif "important about" in data['query']:  # Example condition to modify or clear the response
        data['response'] = ""  # Clear the response or modify as needed

    return data

# Path to the original and new JSONL files
input_path = 'chat_logs.jsonl'
output_path = 'modified_logs.jsonl'

# Open the original JSONL file for reading and the new JSONL file for writing
with open(input_path, 'r') as input_file, open(output_path, 'w') as output_file:
    # Process each line in the original JSONL file
    for line in input_file:
        data = json.loads(line)  # Load JSON data from the line
        modified_data = reformat_response(data)  # Reformat the response field
        output_file.write(json.dumps(modified_data) + '\n')  # Write the modified data to the new JSONL file
