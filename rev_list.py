
class RevList():
    def __init__(self):
        self.items = []
        self.len = 0 

    def append(self, item):
        self.items.append(item)
        self.len += 1

    # reverse slice starting at the end of the list
    def __getitem__(self,key):
        if isinstance(key,slice):
            if key.start < 0:
                raise ValueError("s must be >= 0")
            if key.stop > self.len:
                raise ValueError("e must be <= len")

            return self.items[-1-key.start:-1-key.stop:-1]


    def __len__(self):
        return self.len

    def __str__(self):
        return str(self.items)
