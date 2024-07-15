from hdc import *
import csv
import tqdm
from pprint import pprint

class branchPredictor:
    
    def __init__(self,k):
        # initialize size of k-grams
        self.k = k
        
        # initialize atomics -- decisions 
        self.decisions = HDCodebook()
        self.decisions.add("y")
        self.decisions.add("n")
    
    def make_history_vecs(self,history):
        return [self.decisions.get(decision) for decision in history]


    def encode_run(self,run):
        # create k-gram
        return HDC.bind_all([HDC.permute(run[i],i) for i in range(len(run))])


    # assumes that history is long enough for k-gram
    def encode_history(self,history):
        # create history vector by encoding past branch decisions
        
        # begin by replacing decisions with their representative vectors
        history_vecs = self.make_history_vecs(history) 

        # create list of bound k-grams
        grams = []
        for i in range(len(history_vecs)-self.k+1):
            grams.append(self.encode_run(history_vecs[i:i+self.k]))

        # bundle together and return 
        return HDC.bundle(grams)


    # assumes that history is long enough for k-gram
    def make_query(self,history):
        # last k-1 items from history
        
        history_vecs = self.make_history_vecs(history)
        
        lenh = len(history_vecs)
        run = self.encode_run(history_vecs[lenh-self.k:lenh])

        # permute by 1 to cancel out desired section
        return HDC.permute(run,1)


    def predict(self,history_hv,query_hv):
        # predict next branch outcome based on current decision vector
        return self.decisions.wta(HDC.bind(history_hv,query_hv))


def initialize(k=3):
    # initialize data 
    HDC.SIZE = 10000

    decisions = []
    with open("dataset.txt","r") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        decisions = [row["decision"] for row in csv_reader]
        
    # reverse decision array to get most recent decisions first
    decisions.reverse()

    # initialize branch predictor
    predictor = branchPredictor(k)

    # reverse decision array to get most recent decisions first
    return decisions,predictor


def test_predictor(history,predictor):

    print("======= testing predictor ======")
    correct, idx = 0, 0
    
    for item in (pbar := tqdm.tqdm(history)):

        # initialize history/query vectors
        history_hv = HDC.rand_vec()
        query_hv = HDC.rand_vec()

        # if history is long enough, encode history and make query
        if idx >= predictor.k:
            history_hv = predictor.encode_history(history[:idx])  
            query_hv = predictor.make_query(history[:idx])

        # generate prediction and compare to actual 
        prediction = predictor.predict(history_hv,query_hv)
        actual = history[idx]

        if prediction == actual:
            correct += 1
        idx += 1

        accuracy = float(correct)/idx
        pbar.set_description("accuracy=%f" % accuracy)

    print(f"ACCURACY: {accuracy}")
        

def main():
    # initialize k-gram size
    k = 3

    # initialize data
    history,predictor = initialize(k)

    # test predictor
    test_predictor(history,predictor)


    #history = ["NT","T","T","NT","T","NT","NT"]
    #predictor = branchPredictor(3)

    #test_predictor(history,predictor)



if __name__ == "__main__":
    main()
