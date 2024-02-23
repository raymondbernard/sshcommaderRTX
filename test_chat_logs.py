import jsonlines

def query_chat_logs(file_path):
    """
    Query the chat logs JSONL file.
    
    Args:
    - file_path (str): Path to the JSONL file.
    - query (str): Query string to search for in the chat logs.
    
    Returns:
    - list of dict: List of chat log entries matching the query.
    """
    results = []
    with jsonlines.open(file_path) as reader:
        for line in reader:
            print(line["response"])

          
            results.append(line)
    return results


if __name__ == "__main__":
    # Example usage:
    file_path = 'chat_logs.jsonl'
  
    query_chat_logs(file_path)
  
