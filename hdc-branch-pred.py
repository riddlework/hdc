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
        #print(HDC.dist(self.decisions.get("y"),self.decisions.get("n")))

    

    # takes a list of decisions and returns a list of their representative hypervectors
    def list_to_vec(self,decision_list):
        return [self.decisions.get(decision) for decision in decision_list]
    

    # takes a list of hypervectors and returns a list of their representative decisions
    # for debugging purposes
    def vec_to_list(self,vec_list):
        return [self.decisions.wta(vec) for vec in vec_list]


    def encode_run(self,run):
        # create k-gram
        return HDC.bind_all([HDC.permute(run[i],i) for i in range(len(run))])


    # assumes that history is long enough for k-gram
    def encode_history(self,history):
        # create history vector by encoding past branch decisions
        
        # begin by replacing decisions with their representative vectors
        history_vecs = self.list_to_vec(history) 

        # create list of bound k-grams
        grams = []
        unique_runs = []
        for i in range(len(history_vecs)-self.k+1): 
            string_run = history[i:i+self.k]
            vec_run = history_vecs[i:i+self.k]

            if "".join(string_run) not in unique_runs: 
                unique_runs.append("".join(string_run))
                grams.append(self.encode_run(vec_run))

        # bundle together and return 
        return HDC.bundle(grams)


    # assumes that history is long enough for k-gram
    def make_query(self,history):
        # last k-1 items from history 
        lenh = len(history)
        query = history[lenh-self.k+1:lenh]
        #print(f"query: {query}")
        #print(f"history: {history}")
        query_vecs =  self.list_to_vec(query)
        
        lenh = len(query_vecs)
        run = self.encode_run(query_vecs[lenh-self.k+1:lenh])
        #print(lenh-self.k+1)
        #print(lenh)

        # permute by 1 to cancel out desired section
        return HDC.permute(run,1)


    def predict(self,history_hv,query_hv):
        # predict next branch outcome based on current decision vector
        return self.decisions.wta(HDC.bind(history_hv,query_hv))


def initialize(k=3):
    # initialize data 
    HDC.SIZE = 10000

    decisions = []
    with open("410185-dataset.txt","r") as csv_file:
        csv_reader = csv.DictReader(csv_file)

        num_yes = 0
        decisions = []
        for row in csv_reader:
            decisions.append(row["decision"])
            if row["decision"] == "y":
                num_yes += 1
            if len(decisions) >= 2500:
                break
        
        print(f"num_yes: {num_yes}")
        #decisions = [row["decision"] for row in csv_reader]
        
    # reverse decision array to get most recent decisions first
    decisions.reverse()

    # initialize branch predictor
    predictor = branchPredictor(k)

    # reverse decision array to get most recent decisions first
    return decisions,predictor


def test_predictor(history,predictor):

    print("======= testing predictor ======")
    correct, idx = 0, 0

    # count results
    num_correct_positives = 0
    num_correct_negatives = 0
    num_false_positives = 0
    num_false_negatives = 0
    
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

        if prediction == "y" and actual == "y":
            num_correct_positives += 1
        elif prediction == "y" and actual == "n":
            num_false_positives += 1
        elif prediction == "n" and actual == "n":
            num_correct_negatives += 1
        elif prediction == "n" and actual == "y":
            num_false_negatives += 1

        accuracy = float(correct)/idx
        pbar.set_description("accuracy=%f" % accuracy)

    print(f"num_correct_positives: {num_correct_positives}")
    print(f"num_correct_negatives: {num_correct_negatives}")
    print(f"num_false_positives: {num_false_positives}")
    print(f"num_false_negatives: {num_false_negatives}")

    print(f"ACCURACY: {accuracy}")
        

def testing(predictor):
    # y y n history
    # y y query
    # should return n

    #history = ["y","y","n"]
    #reverse_history = ["n","y","y"] 

    # make history vector
    #history_hv = predictor.encode_history(reverse_history)
    #query_hv = predictor.make_query(reverse_history)

    #history_vecs = []
    #for i in range(len(reverse_history)):
    #    history_vec = predictor.decisions.get(reverse_history[i])
    #    history_vecs.append(HDC.permute(history_vec,i))
    #    print(f"reverse_history_element: {reverse_history[i]}, i: {i}")

    #history_hv = HDC.bind_all(history_vecs)

#    query = ["y","y"]
#    query_vecs = []
#    hv_y = predictor.decisions.get("y")
#    query_vecs.append(hv_y)
#    query_vecs.append(HDC.permute(hv_y,1))
#    query_hv = HDC.bind_all(query_vecs)
#    query_hv = HDC.permute(query_hv,1)
#
    #hv_qh = HDC.bind(history_hv,query_hv)
    #print(predictor.decisions.distance(hv_qh))

    #print(f"{predictor.decisions.wta(HDC.bind(history_hv,query_hv))}")
    return


def main():
    # initialize k-gram size
    k = 3

    # initialize data
    history,predictor = initialize(k)

    # debugging/testing code
    testing(predictor)

    # test predictor
    test_predictor(history,predictor)


if __name__ == "__main__":
    main()
