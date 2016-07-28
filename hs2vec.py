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
