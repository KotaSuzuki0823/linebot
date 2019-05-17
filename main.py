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
import os

import requests
import os
import urllib
import math
import hashlib
import _sha256

app = Flask(__name__)

# 環境変数取得
# LINE Developersで設定されているアクセストークンとChannel Secretをを取得し、設定します。
LINE_BOT_CHANNEL_TOKEN = os.environ["LINE_BOT_CHANNEL_TOKEN"]
LINE_BOT_CHANNEL_SECRET = os.environ["LINE_BOT_CHANNEL_SECRET"]
MSBING_IMAGE_SUBSCRIPTION_KEY= os.environ["MSBING_IMAGE_SUBSCRIPTION_KEY"]

line_bot_api = LineBotApi(LINE_BOT_CHANNEL_TOKEN)
handler = WebhookHandler(LINE_BOT_CHANNEL_SECRET)

#モードフラグ
#通常時：0，お祭り待機状態：1　お祭り状態：２
flag = 0
safeSerchFlag = "ON"

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


## 2 ##
############################################################################################################################################################################################################################################
# LINEのメッセージの取得と返信内容の設定(オウム返し)
###############################################

# LINEでMessageEvent（普通のメッセージを送信された場合）が起こった場合に、
# def以下の関数を実行します。
# reply_messageの第一引数のevent.reply_tokenは、イベントの応答に用いるトークンです。
# 第二引数には、linebot.modelsに定義されている返信用のTextSendMessageオブジェクトを渡しています。

# ここで返信メッセージを作成
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    getMesege = event.message.text;# ユーザが送信したメッセージ(event.message.text)を取得
    keyword = ['なにこれ','祭り','ヘルプ','今は昼だよね','真夜中のカーニバル']

    if getMesege = not in keyword:
        if flag == 0:
            message = getMesege + 'だあああああぁぁぁぁぁ'#通常モードはオウム返し
        elif flag == 1:
            flag = 2
            SEARCH_TERM = getMesege

    elif getMesege == 'なにこれ':#キーワードでモード変更
        message = '私はまつりちゃん．お祭り大好き！「お祭り」と打つとお祭りを始めるよ！私が何のお祭りやるか聞くから，やりたいお祭りを打ってね！\nお祭りって言っても，ただBing画像検索で検索して出てくる画像を適当に選んで君に送信するだけだけどね(笑)'

    elif getMesege == '祭り':
        message = 'なんの祭り????'
        flag = 1

    elif getMesege == 'ヘルプ':
        message = '「なにこれ」：このBOTの説明をするよ\n「祭り」：祭りを始めるよ\n「ヘルプ」：これ\n「今は昼だね」：セーフサーチオン\n'

    elif getMesege == '今は昼だよね':
        message = 'セーフサーチONだね'
        safeSerchFlag = "ON"

    elif getMesege == '真夜中のカーニバル':
        message = 'セーフサーチOFFにしたよ'
        safeSerchFlag = "OFF"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=message)#返信メッセージ
    )


# ポート番号の設定
if __name__ == "__main__":
    #    app.run()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
