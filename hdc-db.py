from hdc import *
import csv


class HDDatabase:

    def __init__(self):
        self.db = HDItemMem("db")
        self.atomics = HDCodebook("atomics")
        self.fields = []

    def encode_string(self,value):
        if not self.atomics.has(value):
            self.atomics.add(value)
        return self.atomics.get(value)
        
    def decode_string(self,hypervec):
        return self.atomics.wta(hypervec)

    def encode_row(self, fields):
        hvs = []
        for field,val in fields.items():
            # collect all fields in an arrayu
            if field not in self.fields:
                self.fields.append(field)

            field_hv = self.encode_string(field)
            val_hv = self.encode_string(val)

            hvs.append(HDC.bind(field_hv,val_hv))
        return HDC.bundle(hvs)
        
    def decode_row(self, hv):
        fields = {}
        for field in self.fields:
            # perform hdc ops to get hv closest to desired val
            val_hv = HDC.bind(self.atomics.get(field),hv)
            fields[field] = self.decode_string(val_hv)
        return fields

    def add_row(self, primary_key, fields):
        row_hv = self.encode_row(fields)
        self.db.add(primary_key, row_hv)

    def get_row(self,key):
        return self.decode_row(self.db.get(key))

    def get_value(self,key, field):
        return self.decode_row(self.db.get(key))[field]
        
    def get_matches(self, field_value_dict, thr=0.36):
        return self.db.matches(self.encode_row(field_value_dict),thr)
        
    def get_analogy(self, target_key, other_key, target_value):
        target_field = self.atomics.wta(HDC.bind(self.db.get(other_key), self.atomics.get(target_value)))
        return self.get_value(target_key,target_field)


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
    thr = 0.36
    digis = db.get_matches({"Type":"Virus", "Attribute":"Plant"}, thr=thr)
    summarize_result(data,digis, lambda row: "true match" if row["Type"] == "Virus" and row["Attribute"] == "Plant" else "false positive")

    print("===== champion query =====")
    thr = 0.40
    digis = db.get_matches({"Stage":"Champion"}, thr=thr)
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
    value = db.get_analogy(target_key="Lotosmon", other_key="Crusadermon", target_value="Data")
    print("Lotosmon" + str(targ_row))
    print("Crusadermon" + str(other_row))
    print("------")
    print("value: %s" % value)
    print("expected result: Virus, the type of Crusadermon")
    print("")


def __main__():
    data = load_json()
    db = build_database(data)
    digimon_basic_queries(data,db)
    digimon_value_queries(data,db)
    digimon_test_encoding(data, db)
    #analogy_query(data,db)

if __name__ == "__main__":
    __main__()
