from __future__ import division
import numpy as np
from gensim.models import Word2Vec
from sklearn.manifold import TSNE
from hdbscan import HDBSCAN
from nltk import tokenize, bigrams, trigrams, everygrams, FreqDist, corpus
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import semidbm
from operator import itemgetter
from itertools import combinations
from unidecode import unidecode
from multiprocessing import process, managers
import requests
import json
import re



class card_text(object):
    def __init__(self, json_name):
        self.json_name = json_name

    def __iter__(self):
        card_list = json.load(open(self.json_name))
        for card in card_list:
            if 'text' in card:
                yield self.clean_words(card['text'])

    def clean_words(self, text):
        text = re.sub(r'(\<.\>)|(\<\/*.\>)', '', text)
        text = re.sub(r'[^(\/)a-zA-z0-9 ]', '', text)
        words = text.split()
        return [word.lower() for word in words if word not in corpus.stopwords.words('english')]
