import requests
import json
import random
import tensorflow as tf
import pymysql
import numpy as np

from keras.layers import *
from keras.models import *

from keras.utils import *
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences

CLIENT_ID = "Imn6eQOWGk9p8prlV9cf"
CLIENT_PW = "vymAq63_og"

url = "https://openapi.naver.com/v1/search/news.json?"
query_string = "query=" + "계약"

headers = {"X-Naver-Client-Id": CLIENT_ID, "X-Naver-Client-Secret": CLIENT_PW}

response = requests.get(url + query_string , headers=headers)
print(json.loads(response.text))
