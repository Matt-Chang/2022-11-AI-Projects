# import flask related
from flask import Flask, request, abort
import random
# import linebot related
from datetime import datetime
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, AudioMessage,
    LocationSendMessage, ImageSendMessage, StickerSendMessage
)

# create flask server
app = Flask(__name__)
## your linebot message API - Channel access token (from LINE Developer)
line_bot_api = LineBotApi('964GaSPPnuQIwz4Ia8LG6L5zKc31VSKgHbYIslc4VhykzwsQw9aKAH+ebUAjacd9aytNRqBCbNdTKW2xHZqQmf9Y8kTyKUpLKHi16W+x/57tp2W8tMzR3ofYIOUSZItFuPlKlqB98a3qxDfP3O0wKwdB04t89/1O/w1cDnyilFU=')
# your linebot message API - Channel secret
handler = WebhookHandler('fc19f1444ca0738ce69241569e41a6d0')
question =[["building", "item", "laundry"],["hygienic", "atmosphere", "phenomenon"],["mediocre", "enthusiasm","acquisition"], ["I'm going to tell you about a building I know quite well and I really like", "Pneumonoultramicroscopicsilicovolcanoconiosis","supercalifragilisticexpialidocious"]]
num = [0]
n = random.randint(0,2)
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)
    return 'OK'

# handle msg
import os
import speech_recognition as sr
# question = "I'm going to tell you about a building I know quite well and I really like."

def transcribe(wav_path):
    '''
    Speech to Text by Google free API
    language: en-US, zh-TW
    '''
    
    r = sr.Recognizer()
    with sr.AudioFile(wav_path) as source:
        audio = r.record(source)
    try:
        return r.recognize_google(audio, language="en-us")
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))
    return None

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    mtext = event.message.text
    if mtext == "哈囉" or mtext == "嗨":
        try:
            message =  TextSendMessage(  
                text = "您好！\n我是jacky8888老師帶你英文8888，\n輸入'開始測驗'就會出現英文單字，達到60分就可以進入下一關"
            )
            line_bot_api.reply_message(event.reply_token,message)
            
        except:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤！'))    
    if mtext == '開始測驗':
        try:
            global n
            message =  TextSendMessage(  
                text = "第一題題目是:\n{}".format(question[num[0]][n])
            )
            line_bot_api.reply_message(event.reply_token,message)
            
        except:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤！'))    
    if mtext == "挑戰題":
        try:
            message =  TextSendMessage(  
                text = "挑戰題是:\n{}".format(question[num[0]][n])
            )
            line_bot_api.reply_message(event.reply_token,message)
            
        except:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤！'))
    if mtext == "重新開始" or mtext == "0":
        num[0] = 0
        try:
            message =  TextSendMessage(  
                text = "題目已重置，請再輸入'開始測驗'")
            line_bot_api.reply_message(event.reply_token,message)
        except:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤！'))  
@handler.add(MessageEvent, message=AudioMessage)

def handle_audio(event):
    name_mp3 = 'recording.mp3'
    name_wav = 'recording.wav'
    message_content = line_bot_api.get_message_content(event.message.id)
    
    with open(name_mp3, 'wb') as fd:
        for chunk in message_content.iter_content():
            fd.write(chunk)
    
    os.system('ffmpeg -y -i ' + name_mp3 + ' ' + name_wav + ' -loglevel quiet')
    text = transcribe(name_wav)
    score = 0
    global n
    if text:
        for i in text:
            if (i and question[num[0]][n]) in question[num[0]][n]: 
                score += 1
        length = max(len(text),len(question[num[0]][n]))
        if score/length >= 0.6:
            if num[0]+2 == len(question):
                line_bot_api.reply_message(event.reply_token, 
                                       [TextSendMessage(text = "您剛剛的回答是: {}".format(text)), 
                                        TextSendMessage(text = "您的得分是: {}".format(round(100*score/length,2))),
                                       TextSendMessage(text = "恭喜您闖關成功!!!\n如果您還想挑戰請輸入'挑戰題'"),
                                        TextSendMessage(text = "如果您想重新挑戰請輸入'重新開始'或'0'")])
                num[0] += 1
            elif num[0]+1 == len(question):
                line_bot_api.reply_message(event.reply_token, 
                       [TextSendMessage(text = "您剛剛的回答是: {}".format(text)), 
                        TextSendMessage(text = "您的得分是: {}".format(round(100*score/length,2))),
                       TextSendMessage(text = "恭喜您挑戰成功!!!"),
                       TextSendMessage(text = "如果您想重新挑戰請輸入'重新開始'或'0'")])
            else:
                
                line_bot_api.reply_message(event.reply_token, 
                                           [TextSendMessage(text = "您剛剛的回答是: {}".format(text)), 
                                            TextSendMessage(text = "您的得分是: {}".format(round(100*score/length,2))),
                                           TextSendMessage(text = "恭喜您進入下一關，下一題題目是:{}".format(question[num[0]+1][n]))])
                n = random.randint(0,2)
                num[0] += 1
        else:
            line_bot_api.reply_message(event.reply_token, 
                                       [TextSendMessage(text = "您剛剛的回答是: {}".format(text)), 
                                        TextSendMessage(text = "您的得分是: {}".format(round(100*score/length,2))),
                                       TextSendMessage(text = "很抱歉，您未通過本關。請再說一次!!!"),
                                       TextSendMessage(text = "新題目為:{}".format(question[num[0]][n]))])
            n = random.randint(0,2)
        
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = "抱歉!!我沒聽懂，請重新回答"))


    print('Transcribe:', text)


# run app
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=12345)