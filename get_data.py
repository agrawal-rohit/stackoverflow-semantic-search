from google.cloud import bigquery
import ast
import glob
import re
from pathlib import Path

import astor
import pandas as pd
import spacy
from tqdm import tqdm
from nltk.tokenize import RegexpTokenizer
from sklearn.model_selection import train_test_split

# from general_utils import apply_parallel, flattenlist
from bs4 import BeautifulSoup
from textblob import TextBlob

EN = spacy.load('en_core_web_sm')
pd.set_option('display.max_colwidth', -1)
tqdm.pandas(desc="Processing:")
use_cache = False

import bq_helper
from bq_helper import BigQueryHelper
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="credentials.json"
stackOverflow = bq_helper.BigQueryHelper(active_project="bigquery-public-data",
                                   dataset_name="stackoverflow")
bq_assistant = BigQueryHelper("bigquery-public-data", "stackoverflow")
bq_assistant.list_tables()
bq_assistant.table_schema("comments")

# SELECT q.title, q.body, q.tags, c.text, SUM(c.score) FROM `bigquery-public-data.stackoverflow.posts_questions` AS q INNER JOIN `bigquery-public-data.stackoverflow.comments` AS c ON q.id = c.post_id WHERE q.tags LIKE '%python%'  GROUP BY q.id,q.title,q.body,q.tags,c.text LIMIT 10
QUERY = "SELECT q.title, q.body, q.tags FROM `bigquery-public-data.stackoverflow.posts_questions` AS q WHERE q.tags LIKE '%python%' LIMIT 10"
df = bq_assistant.query_to_pandas(QUERY)