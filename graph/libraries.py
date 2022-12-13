import re
import pandas as pd
import bs4
import requests

import spacy
from spacy import displacy
from spacy.matcher import Matcher
from spacy.tokens import Span

import networkx as nx
import nltk

import matplotlib.pyplot as plt
from tqdm import tqdm

nltk.download('punkt')
nlp = spacy.load('en_core_web_sm')
pd.set_option('display.max_colwidth', 200)