import os
import json
import pandas as pd
import datetime
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

import classla

PATH = os.path.dirname(os.path.abspath(__file__))


# download standard models for Slovenian
classla.download('sl')
nlp = classla.Pipeline('sl', processors='tokenize,ner,pos,lemma,depparse')


# Read lemmatized 24ur data
with open(os.path.join(PATH, "data", "lemmatized_24ur_data.json"), "r") as f:
    data_24ur = json.loads(f.read())
data_24ur_df = pd.DataFrame.from_dict(data_24ur)
data_24ur_df["datetime_published"] = pd.to_datetime(data_24ur_df['datetime_published'], format='%Y-%m-%d %H:%M:%S')


# Read filtered data
with open(os.path.join(PATH, "data", "filtered_data.json"), "r") as f:
    data = json.loads(f.read())


# Find most similar article from 24ur and add it to the original article
for i in range(len(data)):
    article = data[i]

    title = article["title"]
    date = datetime.datetime.strptime(article["datetime_published"], "%Y-%m-%d %H:%M:%S")
    window_start = date - datetime.timedelta(days=3)
    window_end = date + datetime.timedelta(days=2)

    data_in_window = data_24ur_df[data_24ur_df["datetime_published"] > window_start]
    data_in_window = data_in_window[data_in_window["datetime_published"] < window_end]

    possible_title_matches = []
    possible_title_matches.append(" ".join(nlp(title).get("lemma")))
    for idx, row in data_in_window.iterrows():
        possible_title_matches.append(row["lemmatized_title"])
    
    tfidf = TfidfVectorizer().fit_transform(possible_title_matches)
    pairwise_similarity = tfidf * tfidf.T

    similarity_array = pairwise_similarity.toarray()[1:,0]
    most_similar_dict = {}
    if len(similarity_array) > 0:
        idx_max = np.argmax(similarity_array)
        most_similar_aricle = data_in_window.iloc[[idx_max]]

        most_similar_dict = {
            "title": most_similar_aricle.iloc[0]["title"],
            "url":  most_similar_aricle.iloc[0]["url"],
            "datetime_published":  most_similar_aricle.iloc[0]["datetime_published"].strftime("%Y-%m-%d %H:%M:%S"),
            "similarity_score": similarity_array[idx_max]
        }
    article["24ur"] = most_similar_dict

    if (i+1) % 100 == 0:
        print("Number of processed articles:", i+1)


# Save data to file
with open(os.path.join(PATH, "data", "data.json"), "w", encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=True)


