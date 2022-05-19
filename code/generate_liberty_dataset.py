import pandas as pd
import numpy as np
import json
import re
import csv
from tqdm import tqdm
import argparse
import os

def tweet_parser(congressdir, lexicon):
    df = pd.read_csv(lexicon, sep="\t")
    #print(df.columns)
    #print(df)
    dict_data = []
    keywords = df['word']

    all_files = os.listdir(congressdir)
    #print(all_files)
    pbar = tqdm(total=len(all_files))
    num_found = 0
    for filename in all_files:
        #if not filename.endswith(".json") and not filename.startswith("tweets"):
        if not filename.endswith(".json"):
            continue
        #print("filename",filename)
        filepath = os.path.join(congressdir, filename)
        #print("filepath", filepath)
        data = json.load(open(filepath)) # list that stores a dictionary at every entry
        #print("data", data['423705782523098'])
        for tweet in data.items():
            #print ("tweet", tweet[0], tweet[1]) #ok

            if 'text' not in tweet[1]:
                continue
            text = tweet[1]['text'].lower()
            #print("text", text)
            words_that_appear = []

            for word in keywords:
                #print('word', word)
                if word in text:
                    words_that_appear.append(word)

            if len(words_that_appear) > 1:
                tweetDict = dict()
                tweetDict['id'] = tweet[0] #ad id
                tweetDict['text'] = text
                tweetDict['number of words that match'] = len(words_that_appear)
                tweetDict['which keywords match'] = words_that_appear
                dict_data.append(tweetDict)
                num_found += 1
        pbar.update(1)
    pbar.close()
    print("Tweets found: ", num_found)
    return dict_data

def convert_to_csv(dict_data, csv_file):
    csv_columns = dict_data[0].keys()
    try:
        with open(csv_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in dict_data:
                writer.writerow(data)
    except IOError:
        print("I/O error")


def main():
    #json_links = getJsonLinks("https://alexlitel.github.io/congresstweets/")
    parser = argparse.ArgumentParser()
    parser.add_argument('--congressdir', type=str, required=True) ## "data/annotated"
    parser.add_argument('--lexicon', type=str, required=True) ## "data/resources/liberty.dic"
    parser.add_argument('--outcsv', type=str, required=True) ## "data/moral/covid_moral.csv"
    args = parser.parse_args()

    dict_data = tweet_parser(args.congressdir, args.lexicon)
    convert_to_csv(dict_data, args.outcsv)
if __name__ == "__main__":
    main()
