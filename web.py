# -*- coding: utf-8 -*-
from flask import Response
import flask,requests
from flask import Flask,redirect
import os
import json


data={}
if os.path.isfile("config.json") == True:
    print("配置文件存在,直接读取")
    try:

        with open("config.json", "r", encoding='utf-8') as jsonFile:
            data = json.load(jsonFile)
            jsonFile.close()

        try:


            main_site = data['main_site']
            main_port= data['main_port']
            new_port = data['new_port']
            api_key  = data['api_key']
            redirects= data['redirects']
            password_key= data['password_key']
            if password_key=="True":
                password_value = data['password_value']
            replace_list = data['replace_list']


        except Exception as e:
            print(e)

    except Exception as e:
        print(e)

else:
    input("请先文件目录下配置config.json")

    with open("config.json", "a") as file:  # 只需要将之前的”w"改为“a"即可，代表追加内容
        file.close()




replace_list=[]

app = Flask(__name__)


@app.route('/', methods=['GET',"POST"])
def index():

    #return redirect("/web/index.html")
    url=flask.request.url

    return redirect(url+"web/index.html")
    #return redirect(url_for('/web/index.html'),code=302)

#http://176.113.81.126:8098/emby/videos/64292/stream.mp4?DeviceId=a8c06645-2729-4edc-ae73-09593a775031&MediaSourceId=2858a4cd04bfc490f714a625ecf7c537&Static=true&PlaySessionId=987cca26085644cd86fd2fbcd54ebc71&api_key=b82f726ac4be4817ac51294614674ebb
#http://127.0.0.1:8096/emby/videos/64292/stream.mp4?DeviceId=a8c06645-2729-4edc-ae73-09593a775031&MediaSourceId=2858a4cd04bfc490f714a625ecf7c537&Static=true&PlaySessionId=987cca26085644cd86fd2fbcd54ebc71&api_key=b82f726ac4be4817ac51294614674ebb



@app.route('/<path:path>',methods=['GET',"POST"])
def proxy(path):

    headers=dict(flask.request.headers)

    '''for key, value in headers.items():
        # recurse into nested dicts
        headers[key] = str(value).replace(domainsite, true_site)'''
    par=flask.request.query_string.decode()
    if par !="":
        url=f'{main_site}{path}?{par}'
    else:
        url=f'{main_site}{path}'

    if "stream" in url:
        MediaSourceId = flask.request.args.get('MediaSourceId')
        info_url = f"{main_site}emby/Items?Fields=Path&Ids={MediaSourceId}&api_key={api_key}"
        info_json = requests.get(url=info_url).json()

        for a in replace_list:
            index_url = str(info_json['Items'][0]['Path']).replace(a['from'], a['to'])
        print(f"处理后的直链:{index_url}")
        if redirects=="True":

            true_result=requests.get(index_url,allow_redirects=False)

            #return redirect(index_url)
            if true_result.status_code==200 and password_key=="True":
                data = {"password1": password_value}
                true_result = requests.post(index_url, allow_redirects=False, data=data)

            true_url=dict(true_result.headers)['Location']
        else:
            true_url=index_url
        #print(true_url)
        return redirect(true_url)

    elif "Download" in url and "Items" in url:
        MediaSourceId = flask.request.args.get('mediaSourceId')
        info_url = f"{main_site}emby/Items?Fields=Path&Ids={MediaSourceId}&api_key={api_key}"
        info_json = requests.get(url=info_url).json()

        for a in replace_list:
            index_url = str(info_json['Items'][0]['Path']).replace(a['from'], a['to'])
        print(f"处理后的直链:{index_url}")

        true_result=requests.get(index_url,allow_redirects=False)

        if true_result.status_code==200 and password_key=="True":
            data = {"password1": "wcy98151"}
            true_result = requests.post(index_url, allow_redirects=False, data=data)

        #return redirect(index_url)
        true_url=dict(true_result.headers)['Location']
        #print(true_url)
        return redirect(true_url)



    if flask.request.method == 'GET':
        resp = requests.get(url=url,headers=headers)

        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]
        response = Response(resp.content, resp.status_code, headers)
        return response
    elif flask.request.method == 'POST':
        data=flask.request.data

        resp = requests.post(url=url,headers=headers,data=data)


        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]
        response = Response(resp.content, resp.status_code, headers)
        return response



if __name__ == '__main__':


    app.run(host='127.0.0.1', port=new_port)