import os
import sys
from DataFunction import *
import numpy as np
import io
import json
import pandas as pd
import requests


TOKEN = os.environ.get('CORONATOKEN')
BucketName = os.environ['BUCKET_NAME_CHAT_ID']
BASE_URL = "https://api.telegram.org/bot{}".format(TOKEN)


def coronabotfunction(event, context):

    data = json.loads(event["body"])
    message = str(data["message"]["text"])
    chat_id = data["message"]["chat"]["id"]

    OldChats = getListChats(BucketName)
    Messsage = OldChats['Body'].read().decode('utf-8') 
    ChatNew = chatID(str(chat_id), Messsage)
    writeListChats(BucketName , ChatNew)


    
    print(message)
    
    answer = keywordDetector(message)
    if type(answer)== str:
        data = {"text": answer.encode("utf8"), "chat_id": chat_id, "parse_mode": "markdown"}
        url = BASE_URL + "/sendMessage"
        requests.post(url, data)
    else:
        pic = ploteame(answer[0], answer[2], answer[1], answer[3])
        url = BASE_URL + "/sendPhoto"
        files = {'photo': pic}
        data ={ "chat_id": chat_id}
        requests.post(url, files = files, data = data)
    print('SALIMOS!')
    return {"statusCode": 200}

    
        

   