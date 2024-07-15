from torchvision.datasets import MNIST 
from torch.utils.data import Subset
import tqdm
import torch.utils
from hdc import *
import itertools 
import PIL
import math

MAX = 26

class MNISTClassifier:

    def __init__(self):
        self.classifier = HDItemMem()
        self.values = HDCodebook()
        self.images = {}

    def encode_pixel(self, i, j, v):
        v_str = str(v) 
        if not self.values.has(v_str):
            self.values.add(v_str)
        v_hv = self.values.get(v_str)

        # encode position via permutation
        # MAX is the width
        return HDC.permute(v_hv, (i*MAX+j))

    def encode_image(self,image):
        pixel_hvs = []
        for i,j in itertools.product(range(MAX),range(MAX)):
            v = image.getpixel((i,j))
            pixel_hvs.append(self.encode_pixel(i,j,v))
        return HDC.bundle(pixel_hvs)

    def decode_pixel(self, image_hypervec, i, j):
        return int(self.values.wta(HDC.permute(image_hypervec,-(i*MAX+j))))
        
    def decode_image(self, image_hypervec):
        im = PIL.Image.new(mode="1", size=(MAX, MAX))
        for i,j in list(itertools.product(range(MAX),range(MAX))):
            v = self.decode_pixel(image_hypervec,i,j)
            im.putpixel((i,j),v)
        return im

    def train(self,train_data):
        # encode and sort all images by label
        for image,label in tqdm.tqdm(list(train_data)):
            if label not in self.images:
                self.images[label] = []
            self.images[label].append(self.encode_image(image))
        
        # bundle each image set together and add to classifier
        for label,image_set in self.images.items():
            self.classifier.add(label,HDC.bundle(image_set))

    def classify(self,image):
        image_hv = self.encode_image(image)
        label = self.classifier.wta(image_hv)
        dist = HDC.dist(image_hv,self.classifier.get(label))
        return label,dist

    def build_gen_model(self,train_data):
        self.gen_model = {}
        
        # sort images by label
        for image,label in tqdm.tqdm(list(train_data)):
            if label not in self.gen_model:
                self.gen_model[label] = []
            self.gen_model[label].append(self.encode_image(image))

        # create probability vectors for each label
        for label,image_hvs in self.gen_model.items():
            self.gen_model[label] = np.sum(image_hvs,axis=0)/len(image_hvs)

    def generate(self, cat, trials=100):
        gen_hv = self.gen_model[cat]
        samples = [(gen_hv > np.random.rand(len(gen_hv))).astype(int) for i in range(trials)]
        return self.decode_image(HDC.bundle(samples))

def initialize(N=1000):
    alldata = MNIST(root='data', train=True, download=True)
    dataset = list(map(lambda datum: (datum[0].convert("1"), datum[1]),  \
                Subset(alldata, range(N))))

    train_data, test_data = torch.utils.data.random_split(dataset, [0.6,0.4])
    HDC.SIZE = 10000
    classifier = MNISTClassifier()
    return train_data, test_data, classifier

def test_encoding():
    train_data, test_data, classifier = initialize()
    image0,_ = train_data[0]
    hv_image0 = classifier.encode_image(image0)
    result = classifier.decode_image(hv_image0)
    image0.save("sample0.png")
    result.save("sample0_rec.png")


def test_classifier():
    train_data, test_data, classifier = initialize(2000)

    print("======= training classifier =====")
    classifier.train(train_data)

    print("======= testing classifier =====")
    correct, count = 0, 0
    for image, category in (pbar := tqdm.tqdm(test_data)):
        cat, dist = classifier.classify(image)
        if cat == category:
            correct += 1
        count += 1
        
        pbar.set_description("accuracy=%f" % (float(correct)/count))
    
    print("ACCURACY: %f" % (float(correct)/count))

def test_generative_model():
    train_data, test_data, classifier = initialize(1000)
    print("======= building generative model =====")
    classifier.build_gen_model(train_data)

    print("======= generate images =====")
    while True:
        cat = random.randint(0,9)
        img = classifier.generate(cat)
        print("generated image for class %d" % cat)
        img.save("generated.png")
        input("press any key to generate new image..")


if __name__ == '__main__':
    test_encoding()
    test_classifier()
    test_generative_model()
