import app_sshtensortt  # This imports the module you created

# Assuming you want to call the `chatbot` function with some parameters
query = "how do I configure a 16 port nvidia switch?"
chat_history = []
session_id = "12345"

# Since `chatbot` is a generator function, you need to iterate over its result
for response in app_sshtensortt.chatbot(query, chat_history, session_id):
    print(response)