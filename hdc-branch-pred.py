from hdc import *
import csv
import tqdm
import matplotlib.pyplot as plt
from pprint import pprint

class branchPredictor:
    
    def __init__(self,k):
        # initialize size of k-grams
        self.k = k
        
        # initialize atomics -- decisions 
        self.decisions = HDCodebook()
        self.decisions.add("y")
        self.decisions.add("n")
    

    # takes a list of decisions and returns a list of their representative hypervectors
    def list_to_vec(self,decision_list):
        return [self.decisions.get(decision) for decision in decision_list]
    

    # create gram out of given list of decision vectors 
    def encode_run(self,decision_vecs):
        return HDC.bind_all([HDC.permute(decision_vecs[i],i) for i in range(len(decision_vecs))])


    # assumes that history is long enough for k-gram
    # create history vector by encoding past branch decisions
    def encode_history(self,history):
        
        # retrieve list of representative hypervectors
        history_vecs = self.list_to_vec(history) 

        # create list of bound k-grams
        grams = []
        for i in range(len(history_vecs)-self.k+1): 
            run = history_vecs[i:i+self.k]
            grams.append(self.encode_run(run))

        # bundle together and return 
        return HDC.bundle(grams)


    # assumes that history is long enough for k-gram
    # create query vector from last k-1 items from memory
    def make_query(self,history):

        # retrieve last k-1 items from history
        query = history[len(history)-self.k+1:len(history)]

        # convert to hypervectors
        query_vecs =  self.list_to_vec(query)

        # encode run
        run = self.encode_run(query_vecs)

        # permute by 1 to cancel out desired section
        return HDC.permute(run,1)


    # predict next branch outcome based on current decision vector
    def predict(self,history_hv,query_hv):
        return self.decisions.wta(HDC.bind(history_hv,query_hv))


def initialize(k=3):
    # initialize data 
    HDC.SIZE = 10000

    decisions = []
    with open("410185-dataset.txt","r") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        #decisions = [row["decision"] for row in csv_reader]

        decisions = []
        for row in csv_reader:
            decisions.append(row["decision"])
            
            # restrict amount of computation
            if len(decisions) >= 2500:
                break

    # reverse decision array to get most recent decisions first
    # TODO: re-implement so that reversal is not necessary
    decisions.reverse()

    # initialize branch predictor
    predictor = branchPredictor(k)

    # reverse decision array to get most recent decisions first
    return decisions,predictor


def test_predictor(history,predictor):

    print("======= testing predictor ======")
    correct, idx = 0, 0

    for item in (pbar := tqdm.tqdm(history)):

        # if history is not long enough for k-gram, make random prediction
        if idx < predictor.k:
            rand_num = np.random.rand()
            if rand_num < 0.5:
                prediction = "y"
            else:
                prediction = "n"

        # otherwise, make prediction based on history
        else:
            # make history and query vectors
            history_hv = predictor.encode_history(history[:idx])  
            query_hv = predictor.make_query(history[:idx])
            
            # generate prediction and compare to actual 
            prediction = predictor.predict(history_hv,query_hv)
         
        # update accuracy using actual decision
        actual = history[idx]

        if prediction == actual:
            correct += 1
        idx += 1

        accuracy = float(correct)/idx
        pbar.set_description("accuracy=%f" % accuracy)

    print(f"ACCURACY: {accuracy}")
        

def debug_testing(predictor):
    # assume k=3
    # y y n history
    # y y query
    # should return n

    history = ["y","y","n"]
    # reverse history to get most recent decisions first
    reverse_history = history[::-1] 

    # create history vector manually
    history_vecs = []
    for i in range(len(reverse_history)):
        history_vec = predictor.decisions.get(reverse_history[i])
        history_vecs.append(HDC.permute(history_vec,i))

    history_hv = HDC.bind_all(history_vecs)

    # create query vector manually
    query_vecs = []
    for i in range(1,len(reverse_history)):
        query_vecs.append(HDC.permute(predictor.decisions.get(reverse_history[i]),i))

    query_hv = HDC.bind_all(query_vecs)
        

    # make vectors using class methods
    #history_hv = predictor.encode_history(reverse_history)
    #query_hv = predictor.make_query(reverse_history)

    # get prediction result
    print(f"{predictor.decisions.wta(HDC.bind(history_hv,query_hv))}")
    return


def main():
    # initialize k-gram size
    k = 3

    # initialize data
    history,predictor = initialize(k)

    # test predictor
   # test_predictor(history,predictor)

    # debugg/testing simple code 
    # debug_testing(predictor)


if __name__ == "__main__":
    main()
