import os
from transit.reader import unmarshal

data_mappings = {"nil": None,
                 "true": True,
                 "zero": 0,
                 "one": 1,
                 "vector_empty": []}

def make_fn(file):
    def inner_fn():
        print file
        with open(root + file) as fp:
            data = unmarshal(fp)
            fname, _ = os.path.splitext(file)
            if fname not in data_mappings:
                return
                raise Exception("No data validator for " + fname)
            if data_mappings[fname] != data:
                raise Exception("Data validation error " + str(data_mappings[fname]) + " != " + str(data))

    name = "test_"  + file.replace(".", "_")
    inner_fn.__name__ = name

    globals()[name] = inner_fn



root = "../transit/simple-examples/"
for subdir, dirs, files in os.walk(root):
    for file in files:
        if file.endswith(".json"):
            make_fn(file)

