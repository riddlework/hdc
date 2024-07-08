import string
import random
import operator as op
import numpy as np
import tqdm
import matplotlib.pyplot as plt

from functools import reduce

class HDC:
    SIZE = 10000

    @classmethod
    def rand_vec(cls):
        return np.random.choice([0,1],cls.SIZE)
    
    @classmethod
    def dist(cls,x1,x2):
        return op.truediv(np.sum(x1 != x2), cls.SIZE)
    
    @classmethod
    def bind(cls,x1,x2):
        return np.bitwise_xor(x1,x2)

    @classmethod
    def bind_all(cls, xs):
        return reduce(bind,xs)

    @classmethod
    def bundle(cls,xs):
        # if entry = thr, entry = 0 always
        return (np.sum(xs,axis=0) > (len(xs)/2)).astype(int)
          
    @classmethod
    def permute(cls,x,i):
        return np.roll(x,i)
    

class HDItemMem:

    def __init__(self,name=None) -> None:
        self.name = name
        self.item_mem = {}

    def add(self,key,hv):
        assert(not hv is None)
        self.item_mem[key] = hv
    
    def get(self,key):
        return self.item_mem[key]

    def has(self,key):
        return key in self.item_mem

    def distance(self,query):
        return {key: HDC.dist(val,query) for key,val in self.item_mem.items()}

    def all_keys(self):
        return list(self.item_mem.keys())

    def all_hvs(self):
        return list(self.item_mem.values())

    def wta(self,query):
        dists = self.distance(query)
        return min(dists, key=dists.get)
    
    def matches(self,query, thr=0.49):
        dists = self.distance(query)
        return {key: val for key,val in dists.items() if val <= thr}
        

# a codebook is simply an item memory that always creates a random hypervector
# when a key is added.
class HDCodebook(HDItemMem):

    def __init__(self,name=None):
        HDItemMem.__init__(self,name)

    def add(self,key):
        self.item_mem[key] = HDC.rand_vec()

    

def make_letter_hvs():
    letter_cb = HDCodebook()
    for letter in string.ascii_letters:
        letter_cb.add(letter)
    return letter_cb
    
def make_word(letter_cb, word):
    letter_hvs = [letter_cb.get(letter) for letter in word]
    return HDC.bundle([HDC.permute(letter_hvs[i],i) for i in range(len(word))])
    
def monte_carlo(fxn,trials):
    results = list(map(lambda i: fxn(), tqdm.tqdm(range(trials))))
    return results

def plot_dist_distributions(key1, dist1, key2, dist2):
    plt.hist(dist1,  
            alpha=0.75, 
            label=key1) 
    
    plt.hist(dist2, 
            alpha=0.75, 
            label=key2) 
    
    plt.legend(loc='upper right') 
    plt.title('Distance distribution for Two Words') 
    plt.show()
    plt.clf()

def study_distributions():
    def gen_codebook_and_words(w1,w2,prob_error=0.0):
        cb = make_letter_hvs()
        w1_hv = make_word(cb,w1)
        w2_hv = make_word(cb,w2)
        return HDC.dist(w1_hv,w2_hv)


    trials = 1000
    d1 = monte_carlo(lambda: gen_codebook_and_words("fox","box"), trials)
    d2 = monte_carlo(lambda: gen_codebook_and_words("fox","car"), trials)
    plot_dist_distributions("box",d1,"car",d2)

    perr = 0.10
    d1 = monte_carlo(lambda: gen_codebook_and_words("fox","box", prob_error=perr), trials)
    d2 = monte_carlo(lambda: gen_codebook_and_words("fox","car", prob_error=perr), trials)
    plot_dist_distributions("box",d1,"car",d2)


if __name__ == '__main__':
    HDC.SIZE = 10000

    letter_cb = make_letter_hvs()
    hv1 = make_word(letter_cb,"fox")
    hv2 = make_word(letter_cb,"box")
    hv3 = make_word(letter_cb,"xfo")
    hv4 = make_word(letter_cb,"care")

    print(HDC.dist(hv1, hv2))
    print(HDC.dist(hv1, hv3))
    print(HDC.dist(hv1, hv4))

    study_distributions()




