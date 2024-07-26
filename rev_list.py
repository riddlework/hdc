
class RevList():
    def __init__(self):
        self.items = []
        self.len = 0 

    def append(self, item):
        self.items.append(item)
        self.len += 1

    # reverse slice starting at the end of the list
    def __getitem__(self,key):

        # slicing
        if isinstance(key,slice):
            start = key.start
            stop = key.stop
            step = key.step
           
            # error checking
            if start is None:
                start = -1
            elif start < 0:
                raise ValueError("start must be >= 0")

            if stop is None:
                stop = -self.len
            elif stop > self.len:
                raise ValueError("stop must be <= len")

            if step is None:
                step = -1

            return self.items[-1-start:-1-stop:step]

        # indexing
        elif isinstance(key,int):
            if key < 0 or key >= self.len:
                raise ValueError("index out of range")
            return self.items[-1-key]


    def __len__(self):
        return self.len

    def __str__(self):
        return str(self.items)
