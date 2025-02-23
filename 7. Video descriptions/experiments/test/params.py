class Params:
    def __init__(
            self, fps:int=1, 
            top_k:int=20, 
            system_prompt:str="You are a helpful assistant.",
        ):

        self.fps = fps
        self.top_k = top_k
        self.system_prompt = system_prompt