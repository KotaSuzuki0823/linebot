from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage,
)

import requests
import os
import urllib
import math
import json
from _datetime import datetime

app = Flask(__name__)
APPID = '';

# 環境変数取得
# アクセストークンとChannel Secretをを取得し、設定
LINE_BOT_CHANNEL_TOKEN = os.environ["LINE_BOT_CHANNEL_TOKEN"]
LINE_BOT_CHANNEL_SECRET = os.environ["LINE_BOT_CHANNEL_SECRET"]

DOCOMOAPI_CLIENT_ID = os.environ["DOCOMOAPI_CLIENT_ID"]
DOCOMOAPI_CLIENT_SECRET = os.environ["DOCOMOAPI_CLIENT_SECRET"]

DOCOMOAPI_API_KEY= os.environ["DOCOMOAPI_API_KEY"]

line_bot_api = LineBotApi(LINE_BOT_CHANNEL_TOKEN)
handler = WebhookHandler(LINE_BOT_CHANNEL_SECRET)

# リクエストクエリ
endpoint = 'https://api.apigw.smt.docomo.ne.jp/naturalChatting/v1/dialogue?APIKEY=REGISTER_KEY'
url = endpoint.replace('REGISTER_KEY', DOCOMOAPI_API_KEY)

## 1 ##
# Webhookからのリクエストをチェックします。
@app.route("/callback", methods=['POST'])
def callback():
    # リクエストヘッダーから署名検証のための値を取得します。
    signature = request.headers['X-Line-Signature']

    # リクエストボディを取得します。
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body

     # 署名を検証し、問題なければhandleに定義されている関数を呼び出す。
    try:
        handler.handle(body, signature)
        # 署名検証で失敗した場合、例外を出す。
    except InvalidSignatureError:
        abort(400)
    # handleの処理を終えればOK
    return 'OK'

#DoCoMo自然対話API
#　user registration
def register():
    r_endpoint = 'https://api.apigw.smt.docomo.ne.jp/naturalChatting/v1/registration?APIKEY=REGISTER_KEY'
    r_url = r_endpoint.replace('REGISTER_KEY', DOCOMOAPI_API_KEY)
    r_headers = {'Content-type': 'application/json'}
    pay = {
        "botId": "Chatting",
        "appKind": "Smart Phone"
    }
    r = requests.post(r_url, data=json.dumps(pay), headers=r_headers)
    appId = r.json()['appId']
    return appId

#返信
def reply(appId, utt_content):
    headers = {'Content-type': 'application/json;charset=UTF-8'}
    payload = {
        "language": "ja-JP",
        "botId": "Chatting",
        "appId": APPID,
        "voiceText": utt_content,
        "appRecvTime": "2019-05-11 22:44:22",  # 仮置き。これで動いてしまう。
        "appSendTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    # Transmission
    r = requests.post(url, data=json.dumps(payload), headers=headers)
    data = r.json()
    # rec_time = data['serverSendTime']
    response = data['systemText']['expression']

    #print("response: %s" % response)
    return response

## 2 ##
####################################################################################################################################################
# LINEのメッセージの取得と返信内容の設定
###############################################

# LINEでMessageEvent（普通のメッセージを送信された場合）が起こった場合に、
# def以下の関数を実行します。
# reply_messageの第一引数のevent.reply_tokenは、イベントの応答に用いるトークンです。
# 第二引数には、linebot.modelsに定義されている返信用のTextSendMessageオブジェクトを渡しています。
def replyMessageText(event, message):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=message)  # 返信メッセージ
    )


# ここで返信メッセージを作成
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global APPID
    if APPID is '':
        APPID = register()

    getMessage = event.message.text;# ユーザが送信したメッセージ(event.message.text)を取得
    keyword = ['なにこれ','ヘルプ','仕組み','リセット'];

    if getMessage not in keyword:
        #appId = register()
        message = reply(APPID,getMessage)
        replyMessageText(event, message)

    elif getMessage == 'なにこれ':
        message = '私はまつりちゃん．君の言葉に反応するよ！'
        replyMessageText(event, message)

    elif getMessage == '仕組み':
        message = 'メッセージの送信と受信はLINEのMessageAPIを使用しているよ！このAPIで取得した君の送信内容をDoCoMoの雑談対話APIを使って返信内容を考えてるよ！'
        replyMessageText(event, message)

    elif getMessage == 'ヘルプ':
        message = '「なにこれ」：このBOTの説明をするよ\n「ヘルプ」：これ\n'
        replyMessageText(event, message)

    elif getMessage == 'リセット':
        APPID = register()
        message = 'APPIDをリセットしました'
        replyMessageText(event, message)

# ポート番号の設定
if __name__ == "__main__":
    #    app.run()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
