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

app = Flask(__name__)

# 環境変数取得
# LINE Developersで設定されているアクセストークンとChannel Secretをを取得し、設定します。
LINE_BOT_CHANNEL_TOKEN = os.environ["LINE_BOT_CHANNEL_TOKEN"]
LINE_BOT_CHANNEL_SECRET = os.environ["LINE_BOT_CHANNEL_SECRET"]
MSBING_IMAGE_SUBSCRIPTION_KEY = os.environ["MSBING_IMAGE_SUBSCRIPTION_KEY"]

line_bot_api = LineBotApi(LINE_BOT_CHANNEL_TOKEN)
handler = WebhookHandler(LINE_BOT_CHANNEL_SECRET)
headers = {
    'Content-Type': 'multipart/form-data',
    'Ocp-Apim-Subscription-Key': MSBING_IMAGE_SUBSCRIPTION_KEY,
}

SEARCH_URL = "https://api.cognitive.microsoft.com/bing/v7.0/images/search"

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

#Bing画像検索APIを使った画像URL取得
def searching_image_by_q(url, headers, params, timeout=10):
    response = requests.get(url,
                            headers=headers,
                            params=params,
                            allow_redirects=True,
                            timeout=timeout)

def validate_response_from_image_url(image_url):
    response = requests.get(image_url)

def getImage(getMesege):
    SEARCH_TERM = getMesege
    SEARCH_URL = "https://api.cognitive.microsoft.com/bing/v7.0/images/search"
    SUBSCRIPTION_KEY = "db484ddbe7f7490ea2e6e2641c3b7a87"

    number_images_required = 1
    number_images_per_transaction = 1
    offset_count = math.floor(number_images_required / number_images_per_transaction)

    url_list = []

    headers = {
        'Content-Type': 'multipart/form-data',
        'Ocp-Apim-Subscription-Key': SUBSCRIPTION_KEY,
    }
    for offset in range(offset_count):
        params = urllib.parse.urlencode({
            'q': SEARCH_TERM,
            'count': number_images_per_transaction,
            'offset': offset * number_images_per_transaction,
            'safeSearch': "Off",
        })

        try:
            response = searching_image_by_q(SEARCH_URL, headers, params)
            response_json = response.json()
        except Exception as err:
            print("[Error No.{0}] {1}".format(err.errno,
                                              err.strerror))
        else:
            for values in response_json['value']:
                img_url = urllib.parse.unquote(values['contentUrl'])
                if img_url:
                    url_list.append(img_url)
    return img_url



## 2 ##
############################################################################################################################################################################################################################################
# LINEのメッセージの取得と返信内容の設定(オウム返し)
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
    getMessage = event.message.text;# ユーザが送信したメッセージ(event.message.text)を取得
    keyword = ['なにこれ','ヘルプ','の画像'];

    if getMessage not in keyword:
        message = getMessage + 'だあああああぁぁぁぁぁ'#通常モードはオウム返し
        replyMessageText(event, message)

    elif getMessage == 'なにこれ':#キーワードでモード変更
        message = '私はまつりちゃん．君が送った言葉の画像を返信するよ\nBing画像検索で検索して出てくる画像を適当に選んで君に送信するだけだけどね(笑)'
        replyMessageText(event, message)

    elif getMessage in 'の画像':
        message = getImage(getMessage)
        line_bot_api.reply_message(
            event.reply_token,

            imgMessage = ImageSendMessage(
                preview_image_url = message,
                original_content_url = message
            )

            #TextSendMessage(text=message) # 返信メッセージ
        )


    elif getMessage == 'ヘルプ':
        message = '「なにこれ」：このBOTの説明をするよ\n「祭り」：祭りを始めるよ\n「ヘルプ」：これ\n「今は昼だね」：セーフサーチオン\n'
        replyMessageText(event, message)





# ポート番号の設定
if __name__ == "__main__":
    #    app.run()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
