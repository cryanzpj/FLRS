import datetime
import ijson,os,sys,ast
import json
import numpy as np
from collections import defaultdict

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "FLRS.settings")

import django
django.setup()

from reviews.models import Review, Paper, Author, Paper_cluster


def save_paper_from_row(row,cluster,tfidf):
    authors = row['authors'] + row["co-authors"]
    paper = Paper()
    paper.name = row['title']
    paper.recid = row["recid"]
    paper.abstract = row["abstract"]
    paper.cluster = Paper_cluster.objects.get(c_id = cluster[row['recid']])
    paper.tfidf =  ','.join(tfidf[row["recid"]].astype(str))

    if len(row["creation_date"].split("-")) == 1:
        paper.date = row["creation_date"]+ '-01-01'
    elif  len(row["creation_date"].split("-")) == 2:
        paper.date = row["creation_date"]+ '-01'
    else:
        paper.date = row["creation_date"]

    paper.save()
    for author in authors:
        if not authors:
            continue
        else:
            obj,created = Author.objects.get_or_create(name = author)
            if created:
                obj.save()
                paper.author.add(obj)
            else:
                paper.author.add(obj)
    paper.save()

def create_cluster():
    for i in range(100):
        if not Paper_cluster.objects.filter(c_id = i).exists():
            temp = Paper_cluster(c_id = i)
            temp.save()
        else:
            continue


if __name__ == "__main__":
    # file = "../hep_records.json"
    # Check number of arguments (including the command name)
    print('loading cluster info \n')
    cluster = np.load("./data/paper_cluster.npy").item()
    tfidf = np.load("./data/corpus_tfidf_pca.npy")
    ids = np.load("./data/corp_id_list.npy")
    ids = dict(zip(ids,range(ids.shape[0])))
    print('creating 100 clusters \n')
    create_cluster()

    if len(sys.argv) == 2:
        print "Reading from file " + str(sys.argv[1])

        with open(sys.argv[1]) as infile:
            line = json.loads(infile.readline())
            n = 0
            while line:
                if not line['abstract']:
                    line = json.loads(infile.readline())
                    continue
                n+=1
                save_paper_from_row(line,cluster,tfidf)
                if n % 20000 == 0:
                    print(str(n ))
                try:
                    line = json.loads(infile.readline())
                except ValueError:
                    print('Done')
                    break


        # apply save_review_from_row to each review in the data frame

        print "There are {} reviews in DB".format(Paper.objects.count())

    else:
        print "Please, provide Reviews file path"