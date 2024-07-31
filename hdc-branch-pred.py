from hdc import *
from rev_list import *
import csv
import tqdm
import matplotlib.pyplot as plt
from enum import Enum

class encodingType(Enum):
    RUNNING_BUNDLE = "RB"
    BASELINE = "BL" 

class branchPredictor:
    
    def __init__(self,history,k=3):
        # initialize size of k-grams
        self.k = k
        
        # initialize atomics -- decisions 
        self.decisions = HDCodebook()
        self.decisions.add("0")
        self.decisions.add("1")

        # initialize 

        # initialize vector stores
        self.history = history
        self.history_vecs = self.list_to_vec(history)
        self.grams = []
        self.unthr_grams = np.zeros(HDC.SIZE)
        self.num_grams = 0

        self.encoding_type = encodingType.RUNNING_BUNDLE
        
    # convert list of decisions to list of representative vectors
    def list_to_vec(self,decision_list):
        return np.array([self.decisions.get(str(decision)) for decision in decision_list])
    

    # create gram out of given list of decision vectors 
    def encode_run(self,decision_vecs):
        return HDC.bind_all([HDC.permute(decision_vecs[i],i) for i in range(len(decision_vecs))])

    
    def encode_history(self,i):
        if self.encoding_type == encodingType.RUNNING_BUNDLE:
            return self.encode_history_running_bundle(i)
        else:
            return self.encode_history_baseline(i)


    # assumes that history is long enough for k-gram
    # create history vector by encoding past branch decisions
    def encode_history_running_bundle(self,i):
        # get vectors of current k-gram
        run = self.history_vecs[i-self.k:i]

        # encode run by binding
        run = self.encode_run(run)

        # add current gram to unthresholded grams
        self.unthr_grams += run

        # must keep track of number of grams thus far processed
        self.num_grams += 1

        # return thresholded run
        return (self.unthr_grams > (self.num_grams / 2)).astype(int)
        
        
    # calculates entire sum every time
    def encode_history_baseline(self,i):
        # create list of bound k-grams
        grams = []
        for j in range(i-self.k+1):
            run = self.history_vecs[j:j+self.k]
            grams.append(self.encode_run(run))

        # bundle together and return 
        return HDC.bundle(grams)


    # assumes that history is long enough for k-gram
    # create query vector from last k-1 items from memory
    def make_query(self,i):

        # retrieve last k-1 items from history
        query_vecs = self.history_vecs[i-self.k+1:i]

        # encode run
        run = self.encode_run(query_vecs)

        # permute by 1 to cancel out desired section
        return HDC.permute(run,1)


    # predict next branch outcome based on current decision vector
    def predict(self,history_hv,query_hv):
        return int(self.decisions.wta(HDC.bind(history_hv,query_hv)))

    # test predictor
    def test(self,plot=True):

        if plot == True: 
            print("======= testing predictor ======")

        # initialize parameters
        correct = 0
        accuracies = []

        for i in (pbar := tqdm.tqdm(range(len(self.history)))):

            # if history is not long enough for k-gram, make random prediction
            if i < self.k:
                rand_num = np.random.rand()
                if rand_num < 0.5:
                    prediction = 1 
                else:
                    prediction = 0 

            # otherwise, make prediction based on history
            else:
                # make history and query vectors
                history_hv = self.encode_history(i)  
                query_hv = self.make_query(i)
                
                # generate prediction and compare to actual 
                prediction = self.predict(history_hv,query_hv)

            # update accuracy using actual decision
            actual = self.history[i]

            if prediction == actual:
                correct += 1

            accuracy = float(correct) / (i+1)
            accuracies.append(accuracy)
            pbar.set_description("accuracy=%f" % accuracy)

        # plot accuracies 
        if plot == True:
            make_plot(self,func=0,accuracies=accuracies)

            # print final accuracy
            print(f"ACCURACY: {accuracy}")

        else:
            return accuracies



def initialize(k=3):
    # initialize data 
    HDC.SIZE = 10000

    # initialize decisions
    decisions = []
    with open("./data/traces/410185-dataset.txt","r") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        #decisions = [row["decision"] for row in csv_reader]

        for row in csv_reader:
            decisions.append(int(row["decision"]))
            
    # convert into numpy list
    decisions = np.array(decisions)

    # reverse decisions array to get most recent decisions first
    decisions = np.flip(decisions)

    # initialize branch predictor
    predictor = branchPredictor(decisions,k=k)

    return predictor


# test different k-gram sizes
def test_k_gram_sizes(predictor,k_vals=[i for i in range(3,10)]):

    print("======= testing k-gram sizes ======")

    all_accuracies = {} 
    for val in k_vals:
        
        print(f"======= testing predictor k={val} ======")
        predictor.k = val
        all_accuracies[val] = predictor.test(plot=False)

    # print each final accuracy
    for k,accuracies in all_accuracies.items():
        print(f"k={k} accuracy={accuracies[-1]}")

    # plot accuracies
    make_plot(predictor,func=1,all_accuracies=all_accuracies)
        

# generate plot based on data 
def make_plot(predictor,func=0,accuracies=[],all_accuracies={}):
    
    # one-line plot
    if func == 0:
        plt.plot(np.arange(len(accuracies)),accuracies,color="blue", linewidth=2.5)

    # multi-line plot
    elif func == 1:
        # get colormaps
        color = plt.get_cmap("plasma")
        
        # plot accuracies
        for k,accuracies in all_accuracies.items():
            plt.plot(np.arange(len(accuracies)),accuracies,label=f"k={k}",color=color( (k-3) / len(all_accuracies) ))

        # show labels
        plt.legend()

    # modify axis objects
    ax = plt.gca()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_xlim(0, ax.get_xlim()[1])

    # modify plot aesthetics 
    plt.title("Branch Prediction Accuracy")
    plt.xlabel("Number of Decisions")
    plt.ylabel("Accuracy")
    plt.grid(color='black', alpha=0.1)
    
    # save plot
    plt.savefig(f"accuracy_plot_{predictor.encoding_type.value}.png")

    # show plot
    plt.show()


def main():
    # initialize k-gram size
    k = 3

    # initialize data
    predictor = initialize(k)
    
    # test different k-gram sizes
    # test_k_gram_sizes(predictor)

    # test predictor
    predictor.test()

    # debugg/testing simple code 
    # debug_testing()


if __name__ == "__main__":
    main()
