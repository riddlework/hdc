import csv
import tqdm

class Predictor():
    def __init__(self):
        self.state_book = {}

    # input a "branch instruction"
    # output bool :- True for T and False for NT
    def predict(self, pc):
        # add pc to codebook
        if pc not in self.state_book:
            # different initializations may affect accuracy?
            self.state_book[pc] = 0

        pc_state = self.state_book[pc] 

        if pc_state == 0:
            # strong NT state
            return False
        if pc_state == 1:
            # weak NT state
            # must change state here
            return False
        if pc_state == 2:
            # weak T state
            # must change state here
            return True
        if pc_state == 3:
            # strong T state
            return True


    # given the codebook state of a pc and the actual result of the branch,
    # update the state within the codebook
    def change_state(self,pc,branch_result):
        pc_state = self.state_book[pc]

        if pc_state == 0 and branch_result == True:
            pc_state += 1
        elif pc_state == 1 or pc_state == 2:
            if branch_result == True:
                pc_state += 1
            else:
                pc_state -= 1
        elif branch_result == False:
            pc_state -= 1

        self.state_book[pc] = pc_state


def initialize():
    with open("traces.txt", "r") as csv_file:
        csv_reader = csv.reader(csv_file)
        trace = [(row[0], bool(int(row[1]))) for row in csv_reader]

    with open("copy.txt","w") as copy_file:
        for decision in trace:
            copy_file.write(f"{decision[0]},{int(decision[1])}\n")

    return trace


def test_predictor(trace,predictor):

    correct = 0
    
    for i in (pbar := tqdm.tqdm(range(len(trace)))):
        
        cur_pc = trace[i][0]
        cur_actual = trace[i][1]
        cur_pred = predictor.predict(cur_pc) 

        predictor.change_state(cur_pc,cur_actual)

        if cur_actual == cur_pred:
            correct += 1

        accuracy = float(correct) / (i+1)
        accuracy_pcent = accuracy * 100
        accuracy_str = str((float(f"{accuracy_pcent:0.4f}")))
        pbar.set_description("accuracy=" + accuracy_str)

    print(f"ACCURACY={accuracy_str}")


def main():
    trace = initialize()
    predictor = Predictor()
    test_predictor(trace, predictor)

if __name__ == "__main__":
    main()
        


