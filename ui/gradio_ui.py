import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import gradio as gr

from agents.travel_agent import create_travel_agent


def predict(message, history):
    messages = [
        {"role": turn["role"], "content": [{"text": turn["content"]}]}
        for turn in history
        if turn["role"] in ("user", "assistant")
    ]
    agent = create_travel_agent(messages=messages)
    return str(agent(message))


demo = gr.ChatInterface(predict, api_name="chat")

if __name__ == "__main__":
    demo.launch()
