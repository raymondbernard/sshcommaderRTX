import json
import re

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

# File paths
input_file_path = 'chat_logs.jsonl'
output_file_path = 'commands_logs.jsonl'

# Processing each line in the file
with open(input_file_path, 'r') as input_file, open(output_file_path, 'w') as output_file:
    for line in input_file:
        data = json.loads(line)
        # Process the response to extract the desired content
        data['response'] = process_response(data['response'])
        # Writing the modified data to the new file
        output_file.write(json.dumps(data) + '\n')
