import classla
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
import json
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from ipywidgets import IntProgress
from transformers import AutoTokenizer, AutoModelForMaskedLM
from tqdm import tqdm

nltk.download('stopwords')

# download standard models for Slovenian
classla.download('sl')
nlp = classla.Pipeline('sl', processors='tokenize,ner,pos,lemma,depparse')

stopwords = set(stopwords.words('slovene'))
punc = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''
for p in punc:
    stopwords.add(p)

with open("../../data/data.json", "r") as f:
    data = json.loads(f.read())

content = []
for article in data:
    content.append(article["title"] + " " + article["subtitle"] + " " + article["headline"])

lemma_all = []
for doc in content:
    lemma = [i for i in nlp(doc).get("lemma") if i not in stopwords]
    lemma_all.append(lemma)

with open("lemma.json", "w") as f:
    json.dump(lemma_all, f)