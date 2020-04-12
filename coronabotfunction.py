import os
import sys
from DataFunction import *
import numpy as np
import io
import json
import pandas as pd
import requests


TOKEN = os.environ.get('CORONATOKEN')

BASE_URL = "https://api.telegram.org/bot{}".format(TOKEN)

print('FUNCION!')
def coronabotfunction(event, context):

    data = json.loads(event["body"])
    message = str(data["message"]["text"])
    chat_id = data["message"]["chat"]["id"]
    chatID( chat_id)
    

    
    print(message)
    
    answer = keywordDetector(message)
    if type(answer)== str:
        data = {"text": answer.encode("utf8"), "chat_id": chat_id}
        url = BASE_URL + "/sendMessage"
        requests.post(url, data)
    else:
        pic = ploteame(answer[0], answer[2], answer[1])
        url = BASE_URL + "/sendPhoto"
        files = {'photo': pic}
        data ={ "chat_id": chat_id}
        requests.post(url, files = files, data = data)
    return {"statusCode": 200}

    
        

   