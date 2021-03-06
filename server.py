 
#Python libraries that we need to import for our bot
import random
from flask import Flask, request
from pymessenger.bot import Bot

import nltk
import numpy as np
import pandas as pd
import random
import string
import json
import markovify


model = ''

EXPEDITEUR_NAME = 'Arthur Marty'

def trainModel():
    global model
    print("Loading datas ...")
    df = pd.read_csv('messages.csv', engine='python', encoding='utf8')
    df.iloc[0] = ['Temps', 'Expediteur', 'Message']
    df.columns = df.iloc[0]
    df = df.drop(df.index[0])
    df['Message']=df['Message'].str.lower()# converts to lowercase

    dfPerso = df[df.Expediteur == EXPEDITEUR_NAME]
    dfPerso.dropna()

    speeches =  list(dfPerso['Message'].str.split('\n', expand=True).stack())

    print("Training model ...")

    model = markovify.Text(speeches, state_size=2)

    print("Model create")

app = Flask(__name__)
ACCESS_TOKEN = 'EAAF0eiSwXmcBALGN3wE5GahuwPK2YUsFJDVs9WiOzTsvkp5HZCyjiiZAoLgpcN2hT2oRUZBMlROOxVasqeZBGsBgxlUvpyndOZChY7gzajYPf1IP2AvrDZBOZCfJ40Yi7aYGMkIvEsk73qOahL1mg7lHOkH6QeCBH8ZA4Dmu8gaddQZDZD'
VERIFY_TOKEN = 'bwB6HMSZ8RPf3RiuDhi015UN96VX7gpkCpoCTCHdazEhR3o8bQuRHz0N+uGlKuYQEq/'
bot = Bot(ACCESS_TOKEN)


# trainModel()
@app.route("/model", methods=['GET'])
def makeModel():
    trainModel()
    return "Model Done"

#We will receive messages that Facebook sends our bot at this endpoint 
@app.route("/", methods=['GET', 'POST'])
def receive_message():
    if request.method == 'GET':
        """Before allowing people to message your bot, Facebook has implemented a verify token
        that confirms all requests that your bot receives came from Facebook.""" 
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)
    #if the request was not get, it must be POST and we can just proceed with sending a message back to user
    else:
        # get whatever message a user sent the bot
       output = request.get_json()
       for event in output['entry']:
          messaging = event['messaging']
          for message in messaging:
            if message.get('message'):
                #Facebook Messenger ID for user so we know where to send response back to
                recipient_id = message['sender']['id']
                if message['message'].get('text'):
                    response_sent_text = get_message()
                    send_message(recipient_id, response_sent_text)
                #if user sends us a GIF, photo,video, or any other non-text item
                if message['message'].get('attachments'):
                    response_sent_nontext = get_message()
                    send_message(recipient_id, response_sent_nontext)
    return "Message Processed"


def verify_fb_token(token_sent):
    #take token sent by facebook and verify it matches the verify token you sent
    #if they match, allow the request, else return an error 
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'


#chooses a random message to send to the user
def get_message():
    try:
        return model.make_sentence_with_start("tu", tries=100)
    except AttributeError:
        pass
        print('managing errors model')
        # trainModel()
        return "Mon model n'est pas bien entrainé, je le reentraine et je reviens"
    

#uses PyMessenger to send response to user
def send_message(recipient_id, response):
    #sends user the text message provided via input response parameter
    bot.send_text_message(recipient_id, response)
    return "success"

if __name__ == "__main__":
    # trainModel()
    app.run()
