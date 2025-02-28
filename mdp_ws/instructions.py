class Instructions:
    def __init__(self):
        self.instructions = []

    def clear(self):
        self.instructions.clear()

    def load_instructions(self, instructions_list):
        self.instructions = instructions_list

    def get_next(self):
        if self.instructions:
            return self.instructions.pop(0)
        return None


