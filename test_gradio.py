import gradio as gr

def greet(name):
    inputs = gr.Textbox(value="Default system message", label="System Message", placeholder="Type a system message here...", visible=True)

    return "Cosmic is cool " + name + "!", inputs

demo = gr.Interface(fn=greet, inputs="textbox", outputs="textbox")



print(demo)
if __name__ == "__main__":
    demo.launch()   