import os
import json
import pandas as pd
import classla

PATH = os.path.dirname(os.path.abspath(__file__))

# download standard models for Slovenian
classla.download('sl')
nlp = classla.Pipeline('sl', processors='tokenize,ner,pos,lemma,depparse')

with open(os.path.join(PATH, "data", "24ur_url_data_parsed.json"), "r") as f:
    data_24ur = json.loads(f.read())

data_24ur_df = pd.DataFrame.from_dict(data_24ur)
lemmatized_titles = []
for idx, row in data_24ur_df.iterrows():
    lemmatized_titles.append(" ".join(nlp(row["title"]).get("lemma")))
data_24ur_df["lemmatized_title"] = lemmatized_titles

with open(os.path.join(PATH, "data", "lemmatized_24ur_data.json"), "w", encoding='utf-8') as f:
    json.dump(json.loads(data_24ur_df.to_json(orient="records")), f, ensure_ascii=True)