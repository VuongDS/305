# -*- coding: utf-8 -*-
"""textclassify.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1fctwurIpWQWuyhMyK1CeBgLeqgHxnoBO

# Email Spam Detector

## Import library
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys, os, re, csv, codecs, numpy as np, pandas as pd
import tensorflow.keras
import datetime
from tensorflow.keras import backend as K
import tensorflow.keras.optimizers as Optimizer
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.callbacks import ModelCheckpoint, TensorBoard
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.layers import Dense, Input, LSTM, Embedding, Dropout, Activation, GRU
from tensorflow.keras.layers import Bidirectional, GlobalMaxPool1D
from tensorflow.keras.models import Model, load_model
# import tensorflow_addons as tfa

from tensorflow.keras import initializers, regularizers, constraints, optimizers, layers
from sklearn.metrics import confusion_matrix as CM
from sklearn.metrics import confusion_matrix, f1_score, precision_score, recall_score
import matplotlib.pyplot as plot
import seaborn as sn
import tensorflow as tf

"""## Import dataset

Business Understanding:

What is mail spam ?

Spam emails are illegal or unsolicited messages sent through to a large number of users. 

Their primary goal is to lure the user into clicking a malicious link or downloading an attachment that is harmful to the user's machine.

Why classifycation mail spam?

to protect user from malicious email

reduce user distractions when receiving unsolicited emails

Goal: 

build a usable spam classification model

The classification is based on the f1 metric, which is more than 0.9
"""

email = pd.read_csv('https://raw.githubusercontent.com/VuongDS/305/main/emails_1.csv')

"""Shape of dataset is (5728, 2).
It's conclude two column:
- 'text' contains the content of the email
- 'spam' is label of dataset
"""

from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator

"""## Cleaning the text"""

from gensim.utils import simple_preprocess

email.iloc[:, 0] = email.iloc[:, 0].apply(lambda x: ' '.join(simple_preprocess(x)))

email_spam = email[email['spam'] == 1] 
email_not_spam = email[email['spam'] == 0]

# Store word in a list:
text_contain_spam = []
for text in email_spam.text:
  text_contain_spam.append(text)


text_contain_not_spam = []
for text in email_not_spam.text:
  text_contain_not_spam.append(text)

# Conver list to a text file
text_contain_spam = ''.join(text_contain_spam)
text_contain_not_spam = ''.join(text_contain_not_spam)

"""## Creating the Bag of Words model"""

from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(email['text'], email['spam'], test_size = 0.20, random_state = 0)

X_train = pd.DataFrame(X_train)
X_test = pd.DataFrame(X_test)
y_train = pd.DataFrame(y_train)
y_test = pd.DataFrame(y_test)

from gensim.utils import simple_preprocess

X_train.iloc[:, 0] = X_train.iloc[:, 0].apply(lambda x: ' '.join(simple_preprocess(x)))
X_test.iloc[:, 0] = X_test.iloc[:, 0].apply(lambda x: ' '.join(simple_preprocess(x)))

y_train.iloc[:, 0] = y_train.iloc[:, 0].apply(lambda x: '__label__' + str(x))
y_test.iloc[:, 0] = y_test.iloc[:, 0].apply(lambda x: '__label__' + str(x))

# Create train/test dataset
X_train[['label']] = y_train
X_test[['label']] = y_test

train_dataset = X_train
test_dataset = X_test

# !pip3 -q install fasttext
import fasttext

# Convert dataset to CSV file
train_dataset[['label', 'text']].to_csv('train.txt', 
                                        index = False, 
                                        sep = ' ',
                                        header = None, 
                                        quoting = csv.QUOTE_NONE, 
                                        quotechar = "", 
                                        escapechar = " ")

test_dataset[['label', 'text']].to_csv('test.txt', 
                                        index = False, 
                                        sep = ' ',
                                        header = None, 
                                        quoting = csv.QUOTE_NONE, 
                                        quotechar = "", 
                                        escapechar = " ")

# Training the fastText classifier
model = fasttext.train_supervised('train.txt', wordNgrams = 2)

lst_predict = []
for text in test_dataset.iloc[:, 0]:
  label, pro = model.predict(text)
  lst_predict.append(list(label))
lst_predict = pd.DataFrame(lst_predict)

from sklearn.metrics import f1_score

# Evaluating performance on the entire test file
model.test('test.txt')

"""**Tuning**"""

# Training the fastText classifier
model_tune = fasttext.train_supervised(
                                'train.txt', 
                                wordNgrams = 2,
                                dim = 100,
                                lr = 0.1,
                                epoch = 10,
                                autotuneModelSize="200M",
                                autotuneDuration=1200,
                                autotunePredictions=200
                                )

# Evaluating performance on the entire test file
model_tune.test('test.txt')

lst_predict = []
for text in test_dataset.iloc[:, 0]:
  label, pro = model_tune.predict(text)
  lst_predict.append(list(label))
lst_predict = pd.DataFrame(lst_predict)

f1_score(y_test, lst_predict, average='micro')

def model_predict(*lst_predict):
  for lst in lst_predict:
    label, prob = model_tune.predict(lst)
    if list(label) == ['__label__0']:
      print('The sentence "{}" is NOT a mail spam !'.format(lst))
    else:
      print('The sentence "{}" is a mail spam !'.format(lst))
  return None
