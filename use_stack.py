
import numpy as np

class Deque():
    def __init__(self):
        self.items = []
        self.size = 0
        
    # add an item to the top of the deque 
    def push(self,item):
        self.items.append(item)
        self.size += 1

    def enqueue(self,item):
        self.items.insert(0,item)
        self.size += 1

    # remove an item from the top of the stack
    def pop(self):
        if self.items == None:
            raise Exception("Stack is empty")
        self.size -= 1
        return self.items.pop()

    # remove an item from the front of the queue
    def dequeue(self):
        if self.items == None:
            raise Exception("Queue is empty")
        self.size -= 1
        return self.items.pop(0)

    def __len__(self):
        return self.size





def main():
    k = 3
    arr = 
    arr = [i for i in range(10)]
    deque = Deque()

    grams = []
    for i in range(len(arr)):
        deque.push(arr[i])

        # create gram
        if len(deque) == k:
            gram = []
            for i in range(k):

                # pop from the top
                item = deque.pop()
                grams.append(str(f"p_{i}({item})"))

                # re-add to the end
                deque.enqueue(item)

        elif len(deque) > k:




        


        

        


if __name__ == '__main__':
    main()
