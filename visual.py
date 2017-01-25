import json
import numpy as np
from collections import  defaultdict

cluster = np.load("./data/paper_cluster.npy").item()
kwd = json.load(open("./data/std_keyword.txt"))

temp = np.array(filter(lambda x: x[1],kwd.items()),dtype= object)

res = defaultdict(list)
tree = defaultdict(list)
for i in temp:
    for j in i[1]:
        if ":" in j:
            res[int(i[0])].append(j)
            # tree.append([j.split(":")[0],j.split(":")[1]])

            tree[j.split(":")[0]].append(j.split(":")[1])











