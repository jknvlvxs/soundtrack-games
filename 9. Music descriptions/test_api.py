from ollama_deepseek_api import OllamaChat

chat = OllamaChat(1234)
res = chat.send("Hi!")
print(res)