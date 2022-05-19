import json
import argparse
from tqdm import tqdm
from nltk.tokenize import TweetTokenizer
import re
import os
import pandas as pd

def translate(label):
    label = label.lower()
    if label.startswith('care') or label.startswith('harm'):
        return 'care/harm'
    elif label.startswith('fairness') or label.startswith('cheating'):
        return 'fairness/cheating'
    elif label.startswith('loyalty') or label.startswith('betrayal') or label.startswith('ingroup'):
        return 'loyalty/betrayal'
    elif label.startswith('authority') or label.startswith('subversion'):
        return 'authority/subversion'
    elif label.startswith('purity') or label.startswith('sanctity') or label.startswith('degradation'):
        return 'purity/degradation'
    elif label.startswith('moral'):
        return 'moral'
    else:
        print(label)
        return label

def get_mfd_keywords(filename, v2=False):
    id2mf = {}; key2mf = {}; keystar2mf = {}
    step = 0
    with open(filename) as fp:
        for line in fp:
            if line.startswith('%'):
                step += 1
                continue
            elems = line.strip().split()
            if len(elems) >= 2:
                if v2 and step > 1:
                    words = tuple(elems[:-1])
                    labels = [elems[-1]]
                else:
                    words = elems[0]
                    labels = elems[1:]
                if step == 1:
                    id2mf[words] = labels[0]
                else:
                    if isinstance(words, str) and words.endswith('*'):
                        key2mf[words[:-1]] = [translate(id2mf[x]) for x in labels]
                    else:
                        key2mf[words] = [translate(id2mf[x]) for x in labels]
                    keystar2mf[words] = [translate(id2mf[x]) for x in labels]
    #print("keystar2mf", keystar2mf)
    return id2mf, keystar2mf, key2mf


def get_sentiment_lexicon_keywords():
    positive_keys = []; negative_keys = []
    with open("/data/resources/posemo.txt") as fp:
        for line in fp:
            words = line.strip().split()
            positive_keys.append(words)
    with open("/data/resources/negemo.txt") as fp:
        for line in fp:
            words = line.strip().split()
            negative_keys.append(words)
    return positive_keys, negative_keys

def get_emotion_lexicon_keywords():
    key2emotion = {}
    with open("/data/resources/NRC-Emotion-Lexicon/NRC-Emotion-Lexicon-v0.92/NRC-Emotion-Lexicon-Wordlevel-v0.92.txt") as fp:
        for line in fp:
            word, emotion, label = line.strip().split()
            label = int(label)
            if label == 1 and emotion not in ['positive', 'negative']:
                key2emotion[word] = emotion
    return key2emotion

def build_keyword_regex(keywords):
    regex = "(?:\W|^)("
    for k in keywords:
        if k.endswith("*"):
            regex += "{}(?=\w*)".format(k[:-1])
        else:
            regex += "{}".format(k)
        regex += "|"
    regex = regex[:-1] + ")(?:\W|$)"
    return regex

def main(args):
    if args.moral:
        _, keystar2mf, key2mf = get_mfd_keywords('data/resources/moral_foundation_dictionary.txt')
    if args.moral2:
        _, keystar2mf2, key2mf2 = get_mfd_keywords('data/resources/mfd2.0.dic', v2=True)
    if args.sentiment:
        positive_keys, negative_keys = get_sentiment_lexicon_keywords()
    if args.emotion:
        key2emotion = get_emotion_lexicon_keywords()

    tt = TweetTokenizer()
    for filename in os.listdir(args.ad_dir):
        #if not filename.endswith(".json") and not filename.startswith("tweets"):
        if not filename.endswith(".json"):
            continue
        #print("filename", filename)
        # name, _ = filename.split('.')
        # _, _, month = name.split('_')

        filename = os.path.join(args.ad_dir, filename)
        #print("filename", filename)
        ads = json.load(open(filename))
        print("ads", len(ads))
        pbar = tqdm(total=len(ads))
        results = []
        num_found = 0
        df = pd.read_csv("data/resources/liberty.dic", sep="\t")
        keywords = df['word'] 
        
            
        #for ad_i, a in enumerate(ads):
        for ad in ads.items():
            #print(a.keys())
            text = ad[1]['text']
            #print("text", text)
            text_lower = text.lower()
            tweet_tokens = tt.tokenize(text_lower)
            result = {'text': text, 'text_lower': text_lower, 'tokens': tweet_tokens, 'labels': [], 'keys': {}}
            words_that_appear = []
            for word in keywords:
                #print('word', word)
                if word in text_lower:
                    words_that_appear.append(word)
            #print("1st ", words_that_appear)

            for i, tok in enumerate(tweet_tokens):
                #print("tok", tok)
                # Find moral things
                #pick_moral_key = []
                if args.moral:
                    for moral_key in keystar2mf:
                        #print("moral_key", moral_key) #safe*, peace*, compassion*
                        if (moral_key.endswith('*') and tok.startswith(moral_key[:-1])) or tok == moral_key:
                            #pick_moral_key.append(moral_key)


                            if 'moral' not in result['keys']:
                                result['keys']['moral'] = []
                                result['keys']['moral_foundation'] = {}
                                result['labels'].append('moral')
                            if len(words_that_appear) <= 2:
                                labels = keystar2mf[moral_key]
                                #print("labels", labels) #['care/harm']['loyalty/betrayal']

                                for label in labels:
                                    #print("label", label) #loyalty/betrayal, authority/subversion
                                    if 'mf_'+label not in result['labels']:
                                        result['labels'].append("mf_"+label)
                                    if label not in result['keys']['moral_foundation']:
                                        result['keys']['moral_foundation'][label] = []
                                    result['keys']['moral_foundation'][label].append(moral_key)
                                #print("result['keys']['moral']",result['keys']['moral'])
                                result['keys']['moral'].append(moral_key)
                                #print("result", result)
                                #print(result['keys']['moral_foundation'][label], len(result['keys']['moral_foundation'][label])
                                #print("before", result['keys']['moral_foundation'], len(result['keys']['moral_foundation']), type(result['keys']['moral_foundation']))
                                k1, v1 = max((len(v), k, v) for k, v in result['keys']['moral_foundation'].items())[1:]
                                #print(k1, v1)

                                result['keys']['moral_foundation'].clear()
                                result['keys']['moral_foundation'][k1] = v1
                                # for k, v in result['keys']['moral_foundation'].items():
                                #     result['keys']['moral_foundation'][k1] = result['keys']['moral_foundation'].pop(k)
                                #print("result", result)
                                #print("after",result['keys']['moral_foundation'], len(result['keys']['moral_foundation']))

                           
            if len(words_that_appear) > 2:
                       
                labels = ['liberty/oppression']
                for label in labels:
                    if "mf_liberty/oppression" not in result['labels']:
                        result['labels'].append("mf_liberty/oppression")
                    if label not in result['keys']['moral_foundation']:
                        result['keys']['moral_foundation'][label] = []
                    result['keys']['moral_foundation'][label] = words_that_appear
                    
                num_found += 1               
                #print("words_that_appear", words_that_appear)
                result['keys']['moral'] = words_that_appear
                #print("result", result)               
                    


            
            results.append(result)
            pbar.update(1)

            #if tw_i == 100:
            #    break
            #break
        pbar.close()
        results_json = {'covid_vaccine_dataset': results}
        #print("Writing month {}".format(month))
        with open("data/unlabelled/embedding_covid_all_ads_moral.json", "w") as fp:
            json.dump(results_json, fp)
        
        print("Tweets found: ", num_found)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--moral', default=False, action='store_true')
    parser.add_argument('--moral2', default=False, action='store_true')
    parser.add_argument('--sentiment', default=False, action='store_true')
    parser.add_argument('--ad_dir', type=str, required=True) ##data/unlabelled
    parser.add_argument('--emotion', default=False, action='store_true')
    
    args = parser.parse_args()
    main(args)