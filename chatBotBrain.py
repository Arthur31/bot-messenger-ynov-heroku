import nltk
import numpy as np
import pandas as pd
import random
import string
import json
import markovify

EXPEDITEUR_NAME = 'Arthur Marty'


df = pd.read_csv('messenger.csv', engine='python', encoding='utf8')
df.iloc[0] = ['Temps', 'Expediteur', 'Message']  # adding a row
df.columns = df.iloc[0]
df = df.drop(df.index[0])
df['Message']=df['Message'].str.lower()# converts to lowercase
# df.head(10)

dfPerso = df[df.Expediteur == EXPEDITEUR_NAME]
dfPerso.dropna()

speeches =  list(dfPerso['Message'].str.split('\n', expand=True).stack())

model = markovify.Text(speeches, state_size=2)

chain_dict = json.loads(
    json.loads(model.to_json()).get('chain')
)

json.dump(chain_dict,
    open('./cache/pos_model.json', 'w'),
    indent=4,
    sort_keys=True
)

print(model.make_sentence_with_start("tu", tries=100))