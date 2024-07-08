from hdc import *
import csv


class HDDatabase:

    def __init__(self):
        self.db = HDItemMem("db")
        raise Exception("other instantiations here")

        
    def encode_string(self,value):
        raise Exception("translate a string to a hypervector") 
        
    def decode_string(self,hypervec):
        raise Exception("translate a hypervector to a string") 


    def encode_row(self, fields):
        raise Exception("translate a dictionary of field-value pairs to a hypervector") 
        
    def decode_row(self, hypervec):
        raise Exception("reconstruct a dictionary of field-value pairs from a hypervector.") 

    def add_row(self, primary_key, fields):
        row_hv = self.encode_row(fields)
        self.db.add(primary_key, row_hv)

    def get_row(self,key):
        raise Exception("retrieve a dictonary of field-value pairs from a hypervector row")

    def get_value(self,key, field):
        raise Exception("given a primary key and a field, get the value assigned to the field")
        
    def get_matches(self, field_value_dict, threshold=0.4):
        raise Exception("get database entries that contain provided dictionary of field-value pairs")
        

    def get_analogy(self, target_key, other_key, target_value):
        raise Exception("analogy query")

def load_json():
    data = {}
    with open("digimon.csv","r") as csvf:
        csvReader = csv.DictReader(csvf)
        for rows in csvReader:
            key = rows['Digimon']
            data[key] = rows


    return data

def build_database(data):
    HDC.SIZE = 10000
    db = HDDatabase()

    for key, fields in data.items():
        db.add_row(key,fields)

    return db

def summarize_result(data,result, summary_fn):
    print("---- # matches = %d ----" % len(list(result.keys())))
    for digi, distance in result.items():
        print("%f] %s: %s" % (distance, digi, summary_fn(data[digi])))


def digimon_basic_queries(data,db):
    
    print("===== virus-plant query =====")
    thr = 0.40
    digis = db.get_matches({"Type":"Virus", "Attribute":"Plant"}, threshold=thr)
    summarize_result(data,digis, lambda row: "true match" if row["Type"] == "Virus" and row["Attribute"] == "Plant" else "false positive")

    print("===== champion query =====")
    thr = 0.40
    digis = db.get_matches({"Stage":"Champion"}, threshold=thr)
    summarize_result(data,digis, lambda row: "true match" if row["Stage"] == "Champion" else "false positive")


def digimon_test_encoding(data,db):
    strn = "tester"
    hv_test = db.encode_string(strn)
    rec_strn = db.decode_string(hv_test)
    print("original=%s" % strn)
    print("recovered=%s" % rec_strn)
    print("---")

    row = data["Wormmon"]
    hvect = db.encode_row(row)
    rec_row = db.decode_row(hvect)
    print("original=%s" % str(row))
    print("recovered=%s" % str(row))
    print("---")



def digimon_value_queries(data,db):
    value = db.get_value("Lotosmon", "Stage")
    print("Lotosmon.Stage = %s" % value)
    
    targ_row = db.get_row("Lotosmon")
    print("Lotosmon" + str(targ_row))


def analogy_query(data, db):
    # Lotosmon is to Data as Crusadermon is to <what field>

    targ_row = db.get_row("Lotosmon")
    other_row = db.get_row("Crusadermon")
    print("Lotosmon has a a field with a Data value, what is the equivalent value in Crusadermon's entry")
    value, dist 
    
    = db.get_analogy(target_key="Lotosmon", other_key="Crusadermon", target_value="Data")
    print("Lotosmon" + str(targ_row))
    print("Crusadermon" + str(other_row))
    print("------")
    print("value: %s (dist=%f)" % (value,dist))
    print("expected result: Virus, the type of Crusadermon")
    print("")


def __main__():
    data = load_json()
    db = build_database(data)
    digimon_basic_queries(data,db)
    digimon_value_queries(data,db)
    digimon_test_encoding(data, db)
    analogy_query(data,db)