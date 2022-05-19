import argparse
import csv
import os
import re
import nltk
from nltk.metrics.agreement import AnnotationTask
from nltk.metrics import binary_distance, masi_distance
from nltk.tokenize import TweetTokenizer
from collections import Counter
import json
import random
import sys
csv.field_size_limit(sys.maxsize) # to prevent the error _csv.Error: field larger than field limit

def parse_dataset():
    directory = "data/unlabelled"
    ad_ids = []; all_ads = []
    for filename in os.listdir(directory):
        if filename.endswith(".csv"):
            csv_file = os.path.join(directory, filename)
            with open(csv_file) as fp:
                spamreader = csv.reader(fp)
                
                for i, row in enumerate(spamreader):
                    if i == 0: #skip header
                        continue
                    ad = row[3] # ad_creative_body
                    #print("ad", ad)
                    #print(row[14], type(row[14])) # ad id
                    ad_id = int(row[14])
                    #print("ad_id", ad_id, type(ad_id))
                    
                    all_ads.append(ad)
                    ad_ids.append(ad_id)

    return ad_ids, all_ads


def main(args):
    ad_ids, ads = parse_dataset()
    print("# ads", len(ads), len(ad_ids))
    
    dataset = {}
    
    for i, (ad_id, ad) in enumerate(zip(ad_ids, ads)):
        #print(i)
        
        dataset[ad_id] = { 'text': ad }
        
    print("Total", len(dataset))
    
    random.shuffle(ad_ids)

    folds = {}
    for n, i in enumerate(range(0, len(ad_ids), 150)):
        folds[n] = ad_ids[i:i+150]

    with open("data/unlabelled/covid_all_ads.json", "w") as fp:
        json.dump(dataset, fp)
    with open('data/unlabelled/covid_all_folds.json', 'w') as fp:
        json.dump(folds, fp)

    # print("Stance per MF")
    # for mf in mf_stance_count:
    #     print(mf, mf_stance_count[mf])

    # print('Stances with comments', has_comment)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    random.seed(42)
    main(args)
