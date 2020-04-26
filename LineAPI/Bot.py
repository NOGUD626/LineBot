from flask import Blueprint, request, abort,current_app,render_template
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
import requests
import json
import os
from LineAPI import MessageFunction as CPS_MessageAPI

line_token = os.environ.get('LineBotApi')
line_bot_api = LineBotApi(line_token)

LineWebhook = os.environ.get('LineWebhook')
handler = WebhookHandler(LineWebhook)

# 認証用
cilent_id = os.environ.get('cilent_id')
client_secret = os.environ.get('client_secret')
# SlackOutCommingURL
SlackOutCommingURL = os.environ.get('SlackOutCommingURL')

myselfURL = os.environ.get('myselfURL')
# import sys
#
# sys.path.append('../')

app1 = Blueprint('app1', __name__)

# Line認証用のエンドポイント
@app1.route("/callbackLogin", methods=["GET", "POST"])
def callbackLogin():
    try:
        code = request.args.get('code')
        state = request.args.get('state')
    except KeyError:
        print("Error")

    uri_access_token = "https://api.line.me/oauth2/v2.1/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data_params = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": "{0}/LineBot-API/callbackLogin".format(myselfURL),
        "client_id": cilent_id,
        "client_secret": client_secret
    }

    # トークンを取得するためにリクエストを送る
    response_post = requests.post(uri_access_token, headers=headers, data=data_params)
    # 今回は"id_token"のみを使用する
    access_token = json.loads(response_post.text)['access_token']
    # アクセストークンを使いユーザー情報を取得
    headers = {'Authorization': 'Bearer {}'.format(access_token)}
    response_get = requests.get('https://api.line.me/v2/profile', headers=headers)

    displayName = response_get.json()["displayName"]
    userId = response_get.json()["userId"]

    # Slack外であれば(転送通知をチャンネルに転送)
    if not (state == "Line11107b"):
        WEB_HOOK_URL = SlackOutCommingURL
        requests.post(WEB_HOOK_URL, data=json.dumps({
            'text': u'LINE REGIST:{0}:{1}'.format(state,userId),  # 通知内容
            'username': u'Line登録の情報通知',  # ユーザー名
            'icon_emoji': u':line:',  # アイコン
            'link_names': 1,  # 名前をリンク化
         }))
    return render_template('index.html',state=state,displayName=displayName)

#LineBot-API/callback
@app1.route("/callback", methods=["GET", "POST"])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    # logger = current_app.logger
    # logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# メッセージが来たときのハンドラー
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # コマンドがある場合何かしらの機能を発動
    CPS_MessageAPI.MessageFunctionDetaction(event)
