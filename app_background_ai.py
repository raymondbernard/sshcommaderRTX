import os
import time
import json
import logging
# import gc
import json 
import torch
# import ast
# import threading
from pathlib import Path
from trt_llama_api import TrtLlmAPI
# from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from collections import defaultdict
# from llama_index import ServiceContext
from faiss_vector_storage import FaissEmbeddingStorage
from ui.user_interface import MainInterface

# Setup logging
logging.basicConfig(level=logging.INFO)


app_config_file = 'config\\app_config.json'
model_config_file = 'config\\config.json'
preference_config_file = 'config\\preferences.json'

def log_response(query, response, session_id):
    print(response)

    log_entry = {
        "session_id": session_id,
        "query": query,
        "response": response,
        "timestamp": time.time()
    }
    with open("chat_logs.jsonl", "a") as log_file:
        json.dump(log_entry, log_file)
        log_file.write("\n")  # For readability in the log file


def log_completion_response(completion_response):
    print(f"Received input: {completion_response}, Type: {type(completion_response)}")  # Debug print
    try:
        # Assuming CompletionResponse has a .text attribute
        if not hasattr(completion_response, 'text'):
            raise ValueError("completion_response must have a 'text' attribute.")
        
        user_prompt_text = getattr(completion_response, 'text', None)
        if user_prompt_text is None:
            raise ValueError("The 'text' attribute could not be found.")
        
        log_entry = {
            "user_prompt": user_prompt_text,
            "timestamp": time.time()
        }
        with open("test_user_prompt.jsonl", "a") as log_file:
            json.dump(log_entry, log_file)
            log_file.write("\n")
    except Exception as e:
        print(f"Failed to log completion response: {e}")

def read_config(file_name):
    try:
        with open(file_name, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"The file {file_name} was not found.")
    except json.JSONDecodeError:
        print(f"There was an error decoding the JSON from the file {file_name}.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    return None


def get_model_config(config, model_name=None):
    models = config["models"]["supported"]
    selected_model = next((model for model in models if model["name"] == model_name), models[0])
    return {
        "model_path": os.path.join(os.getcwd(), selected_model["metadata"]["model_path"]),
        "engine": selected_model["metadata"]["engine"],
        "tokenizer_path": os.path.join(os.getcwd(), selected_model["metadata"]["tokenizer_path"]),
        "max_new_tokens": selected_model["metadata"]["max_new_tokens"],
        "max_input_token": selected_model["metadata"]["max_input_token"],
        "temperature": selected_model["metadata"]["temperature"]
    }

# read the app specific config
app_config = read_config(app_config_file)
streaming = app_config["streaming"]
similarity_top_k = app_config["similarity_top_k"]
is_chat_engine = app_config["is_chat_engine"]
embedded_model = app_config["embedded_model"]
embedded_dimension = app_config["embedded_dimension"]

# read model specific config
selected_model_name = None
selected_data_directory = None
config = read_config(model_config_file)
if os.path.exists(preference_config_file):
    perf_config = read_config(preference_config_file)
    selected_model_name = perf_config.get('models', {}).get('selected')
    selected_data_directory = perf_config.get('dataset', {}).get('path')


model_config = get_model_config(config, selected_model_name)


# create trt_llm engine object
llm = TrtLlmAPI(
    model_path=model_config["model_path"],
    engine_name=model_config["engine"],
    tokenizer_dir=model_config["tokenizer_path"],
    temperature=model_config["temperature"],
    max_new_tokens=model_config["max_new_tokens"],
    context_window=model_config["max_input_token"],
    verbose=False
)


# user_prompt = "Who is BB King?"
# completion_response = llm.complete(user_prompt)
# print({"text": completion_response.text, "status": 1} ) # Assuming success status is 1

# log_completion_response(completion_response)


def update_config_descriptions(config_file_path):
    # Load the JSON data from the file
    with open(config_file_path, 'r') as file:
        config_data = json.load(file)

    # Iterate over each server in the config
    for server in config_data["servers"]:
        # Check if config_description needs to be updated
        if  server["config_description"] == "":
            user_prompt = "Generate a description for the following commands: " + ', '.join(server["commands"])
            completion_response = llm.complete(user_prompt)
            # Adjust access method here based on the actual structure of CompletionResponse
            # if hasattr(completion_response, 'status') and completion_response.status == 1:
            server["config_description"] = completion_response.text

    # Write the updated configuration back to the config.json file
    with open(config_file_path, 'w') as file:
        json.dump(config_data, file, indent=4, ensure_ascii=False)
# Example usage
config_file_path = 'config.json'
update_config_descriptions(config_file_path)










# def chat_response(user_prompt):
#     print("line 657 user prompt ", user_prompt)

#     if not user_prompt:
#         logging.error("No user prompt provided.")
#         return None
#     try:
#         completion_response = llm.complete(user_prompt)
#         return {"text": completion_response.text, "status": 1}  # Assuming success status is 1
#     except Exception as e:
#         logging.error(f"Error during chat response generation: {e}")
#         return {"status": 0, "error_message": f"Failed to generate chat response: {e}"}

# def handle_client(conn, addr):
#     print(f"Connection from {addr} has been established.")
#     while True:
#         data = conn.recv(4096)
#         if not data:
#             break
#         received_msg = data.decode('utf-8')
#         print(f"Received from client: {received_msg}")
#         response = chat_response(received_msg)
#         print(response)
#         response_json = json.dumps(response)  # Convert the dictionary to a JSON string        
#         conn.send(json.dumps(response).encode('utf-8'))
        
# def run_server():
#     server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

#     server.bind(('localhost', 12345))
#     server.listen(5)
#     print("Server listening on localhost:12345")
#     while True:
#         conn, addr = server.accept()
#         thread = threading.Thread(target=handle_client, args=(conn, addr))
#         thread.start()
# run_server()