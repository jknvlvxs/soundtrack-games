from ollama_deepseek_api import OllamaChat

chat = OllamaChat(1234)
print("---------------------")
res = chat.send(
    "You will receive descriptions of gameplay videos. Your task will be to, given a video description, answer with a music description that fits the video. The video description was given by a Visual Question Answering model when asked to talk about the actions and movement of speed happening in the video. It was also asked to describe the game's environment, art style, mechanics and genre. The music description will be sent to a text-to-music model that expects a description like the following example: 'A grand orchestral arrangement with thunderous percussion, epic brass fanfares, and soaring strings, creating a cinematic atmosphere fit for a heroic battle.'",
    setup=True)
print(res)
print("---------------------")
res = chat.send("The video shows a screenshot of a video game with no apparent actions happening. The game environment is not described in the given captions, but the art style is described as pixelated. The movement speed is not mentioned in the captions. The game mechanics and genre are not specified in the captions either.")
print(res)