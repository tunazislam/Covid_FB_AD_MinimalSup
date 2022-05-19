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

# def parse_roles(tw_id, roles):
#     res = {}
#     # Dealing with cases where things are in spreadsheet as a list
#     roles = roles.replace('[', '').replace(']', '').replace('"', '').replace("'", '')
#     #print("roles:", roles)
#     roles = re.split(':|,', roles)
#     if len(roles) == 1 and (roles[0] == "none" or roles[0] == ""):
#         return res

#     curr_role = None
#     #print("ROLES", roles)
#     for i, r in enumerate(roles):
#         r = r.strip()
#         #print("HERE", r)
#         # Correcting some errors in the original files to be able to parse them
#         r = re.sub('Positve Actor', 'Positive Actor', r)
#         r = re.sub('Negative Tatget', 'Negative Target', r)
#         r = re.sub('Negarive Actor', 'Negative Actor', r)
#         r = re.sub('negative actor', 'Negative Actor', r)
#         r = re.sub('Negartive Actor', 'Negative Actor', r)
#         r = re.sub('Positive Avctor', 'Positive Actor', r)
#         # Parsing it
#         if r in ['Positive Actor', 'Negative Actor', 'Positive Target', 'Negative Target']:
#             if r not in res:
#                 res[r] = []
#             res[r].append(roles[i+1].strip())
#     #if tw_id == 1024:
#     #    print(res)
#     return res

def parse_dataset():
    directory = "data/annotated"
    ad_ids = []; all_ads = []; all_mfs = []; all_types = []; all_themes = []
    for filename in os.listdir(directory):
        if filename.endswith(".csv"):
            csv_file = os.path.join(directory, filename)
            with open(csv_file) as fp:
                spamreader = csv.reader(fp)
            
                for i, row in enumerate(spamreader):
                    if i == 0: #skip header
                        continue
                    ad = row[2]
                    ad_type = row[3]
                    theme = row[4]
                    moral_foundation = row[5]
                    #print(row[-1], type(row[-1]))
                    ad_id = int(row[-1].split('.')[0])
                    #print("ad_id", ad_id, type(ad_id))
                    all_mfs.append(moral_foundation)
                    all_types.append(ad_type)
                    all_themes.append(theme)
                    all_ads.append(ad)
                    ad_ids.append(ad_id)

                    # if i % 3 == 0:
                    #     #print(mfs)
                    #     #print(mf_roles)
                    #     all_tweets.append(tweet)
                    #     tweet_ids.append(tweet_id)
                    #     all_mfs.append(mfs)
                    #     all_roles.append(mf_roles)
                    #     mfs = []; mf_roles = []
    return ad_ids, all_ads, all_types, all_themes, all_mfs

# def parse_stances():
#     directory = "/data/hold_out.csv"
#     tweets = {}
#     with open(directory) as fp:
#         spamreader = csv.reader(fp)
#         for i, row in enumerate(spamreader):
#             if i == 0:
#                 continue
#             tweet = row[0]
#             tweet_id = int(row[-4])
#             comments = (row[-1], row[-2], row[-3])
#             comments = "".join(comments)
#             annotations = (int(row[1]), int(row[2]), int(row[3]))
#             tweets[tweet_id] = {'text': tweet, 'stance': annotations, 'comments': comments}
#     return tweets

# def calculate_agreement(tweet_ids, tweets, mfs, roles):
#     #tt = TweetTokenizer()
#     # Calculate MFs
#     annotation_triplets = []
#     for i, mf in enumerate(mfs):
#         for j, ann in enumerate(mf):
#             annotation_triplets.append(('coder_{}'.format(j), 'sample_{}'.format(i), ann))
#     task = AnnotationTask(distance=binary_distance)
#     task.load_array(annotation_triplets)
#     print("MF Krippendorff's-Alpha (Binary Distance)", task.alpha())

#     # Calculate Roles
#     annotation_triplets = []
#     all_characters = []
#     for i, rs in enumerate(roles):
#         #tokens = tt.tokenize(tweets[i])
#         new_tweet = tweets[i].lower()
#         tw_id = tweet_ids[i]
#         #print(new_tweet)
#         #print(tokens)

#         characters = []

#         for j, ann in enumerate(rs):
#             # create set of judgments
#             for key in ann:
#                 for value in ann[key]:
#                     #print(value.lower())
#                     if key == 'Positive Actor':
#                         new_tweet = re.sub(r'(?<=\W){}(?=(\W|$))'.format(value.lower()), '1'*len(value), new_tweet)
#                         new_tweet = re.sub(r'(?<=^){}(?=(\W|$))'.format(value.lower()), '1'*len(value), new_tweet)
#                     elif key == 'Negative Actor':
#                         #print('-------')
#                         #print(new_tweet)
#                         #print("VAL:", value.lower())
#                         #print(tw_id)
#                         #print('-------')
#                         new_tweet = re.sub(r'(?<=\W){}(?=(\W|$))'.format(value.lower()), '2'*len(value), new_tweet)
#                         new_tweet = re.sub(r'(?<=^){}(?=(\W|$))'.format(value.lower()), '2'*len(value), new_tweet)
#                     elif key == 'Positive Target':
#                         new_tweet = re.sub(r'(?<=\W){}(?=(\W|$))'.format(value.lower()), '3'*len(value), new_tweet)
#                         new_tweet = re.sub(r'(?<=^){}(?=(\W|$))'.format(value.lower()), '3'*len(value), new_tweet)
#                     elif key == 'Negative Target':
#                         new_tweet = re.sub(r'(?<=\W){}(?=(\W|$))'.format(value.lower()), '4'*len(value), new_tweet)
#                         new_tweet = re.sub(r'(?<=^){}(?=(\W|$))'.format(value.lower()), '4'*len(value), new_tweet)

#             characters.append(new_tweet)
#             for k, character in enumerate(new_tweet):
#                 if character not in ['1', '2', '3', '4']:
#                     # outside case, use 0
#                     annotation_triplets.append(('coder_{}'.format(j), 'sample_{0}_{1}'.format(i, k), '0'))
#                 else:
#                     annotation_triplets.append(('coder_{}'.format(j), 'sample_{0}_{1}'.format(i, k), character))
#         #exit()
#         all_characters.append(characters)

#     #print(annotation_triplets)
#     task = AnnotationTask(distance=binary_distance)
#     task.load_array(annotation_triplets)
#     print("Roles Krippendorff's-Alpha (Char-based, binary distance)", task.alpha())


#     annotation_triplets = []
#     for i, elem in enumerate(all_characters):
#         for k, (c1, c2, c3) in enumerate(zip(elem[0], elem[1], elem[2])):
#             if (c1 not in ['1', '2', '3', '4'] and\
#                c2 not in ['1', '2', '3', '4'] and\
#                c3 not in ['1', '2', '3', '4']):

#                 continue

#             else:
#                 c1_new = c1; c2_new = c2; c3_new = c3
#                 if c1 not in ['1', '2', '3', '4']:
#                     c1_new = '0'
#                 if c2 not in ['1', '2', '3', '4']:
#                     c2_new = '0'
#                 if c3 not in ['1', '2', '3', '4']:
#                     c3_new = '0'

#                 annotation_triplets.append(('coder_0', 'sample_{0}_{1}'.format(i, k), c1))
#                 annotation_triplets.append(('coder_1', 'sample_{0}_{1}'.format(i, k), c2))
#                 annotation_triplets.append(('coder_2', 'sample_{0}_{1}'.format(i, k), c3))

#     task = AnnotationTask(distance=binary_distance)
#     task.load_array(annotation_triplets)
#     print("Roles Krippendorff's-Alpha (Char-based, binary distance -- Removing spans where all three anns DON'T mark this character (ALL OUTSIDE))", task.alpha())

# def calculate_stance_agreement(tweet_stances):
#     annotation_triplets = []
#     for i, tw in enumerate(tweet_stances):
#         for j, ann in enumerate(tweet_stances[tw]['stance']):
#             annotation_triplets.append(('coder_{}'.format(j), 'sample_{}'.format(tw), ann))
#     task = AnnotationTask(distance=binary_distance)
#     task.load_array(annotation_triplets)
#     print("Stance Krippendorff's-Alpha (Binary Distance)", task.alpha())

# def get_role_entities(role_type, annotations):
#     ret = []
#     for ann in annotations:
#         if role_type in ann:
#             ret += ann[role_type]
#     return ret

# def get_majority_mf(mf, res):
#     counter = Counter(mf)
#     elems = counter.most_common(1)
#     (label, count) = elems[0]
#     if count > 1:
#         res.append(label)
#     else:
#         res.append(None)
#     return res

# def get_majority_role(tw_id, tw, elems, res):
#     substr = {}
#     for elem in elems:
#         found = 0
#         substr_elems = [sub for sub in substr]
#         for sub in substr_elems:
#             if (sub == elem) or (sub in elem):
#                 substr[sub] += 1
#                 found = 1
#             elif elem in sub:
#                 substr[sub] += 1
#                 substr[elem] = substr[sub]
#                 del substr[sub]
#                 found = 1
#         if not found:
#             substr[elem] = 1
#     curr_res = [elem for elem in substr if substr[elem] > 1]
#     res.append(curr_res)

#     '''
#     if tw_id == 1024:
#         print("elems", elems)
#         print("substr", substr)
#         print('-----')
#     '''
#     return res

# def get_majority_vote(tweet_ids, tweets, mfs, roles):
#     res_ids = []; res_tweets = []; res_mfs = []
#     res_pos_actors = []; res_neg_actors = []
#     res_pos_targets = []; res_neg_targets = []
#     for i, (tw_id, tw, mf, _roles) in enumerate(zip(tweet_ids, tweets, mfs, roles)):
#         pos_actors = get_role_entities('Positive Actor', _roles)
#         neg_actors = get_role_entities('Negative Actor', _roles)
#         pos_targets = get_role_entities('Positive Target', _roles)
#         neg_targets = get_role_entities('Negative Target', _roles)

#         res_mfs = get_majority_mf(mf, res_mfs)
#         res_pos_actors = get_majority_role(tw_id, tw, pos_actors, res_pos_actors)
#         res_neg_actors = get_majority_role(tw_id, tw, neg_actors, res_neg_actors)
#         res_pos_targets = get_majority_role(tw_id, tw, pos_targets, res_pos_targets)
#         res_neg_targets = get_majority_role(tw_id, tw, neg_targets, res_neg_targets)

#         res_tweets.append(tweets[i])
#         res_ids.append(tweet_ids[i])

#     return res_ids, res_tweets, res_mfs, res_pos_actors, res_neg_actors, res_pos_targets, res_neg_targets

# def get_stance_majority_vote(tweet_stances):
#     for tw in tweet_stances:
#         stance_counter = Counter(tweet_stances[tw]['stance'])
#         (label, count) = stance_counter.most_common(1)[0]
#         if count > 1:
#             tweet_stances[tw]['majority'] = label
#         else:
#             tweet_stances[tw]['majority'] = None
#     return tweet_stances

def main(args):
    ad_ids, ads, typs, thms, mfs = parse_dataset()
    print("# ads", len(ads), len(ad_ids), len(mfs), len(typs), len(thms))
    #calculate_agreement(ad_ids, ads, mfs)

    # tweet_ids, tweets, mfs, pos_actors, neg_actors,\
    #         pos_targets, neg_targets = get_majority_vote(tweet_ids, tweets, mfs, roles)
    # print("# tweets", len(tweets), "# 3-way disagreement mfs", mfs.count(None))

    # tweet_stances = parse_stances()
    # print("# tweets", len(tweet_stances))
    # calculate_stance_agreement(tweet_stances)
    # tweet_stances = get_stance_majority_vote(tweet_stances)

    # print('# tweets', len(tweet_stances), "# 3-way disagreement stances", len([tw for tw in tweet_stances if tweet_stances[tw]['majority'] is None]))

    dataset = {}
    labels = []; stances = []; mf_stance_count = {}
    for i, (ad_id, ad, typ, thm,  mf) in enumerate(zip(ad_ids, ads, typs, thms, mfs)):
        #print(i)
        if mf is not None:
            mf = mf.strip().lower()
        if typ is not None:
            typ = typ.strip().lower()
        if thm is not None:
            thm = thm.strip().lower()
        dataset[ad_id] = {'typ': typ, 'thm': thm, 'mf': mf, 'text': ad }
        
    print("Total", len(dataset))
    
    random.shuffle(ad_ids)

    folds = {}
    for n, i in enumerate(range(0, len(ad_ids), 150)):
        folds[n] = ad_ids[i:i+150]

    with open("data/annotated/covid_annotated_ads.json", "w") as fp:
        json.dump(dataset, fp)
    with open('data/annotated/covid_annotated_folds.json', 'w') as fp:
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
