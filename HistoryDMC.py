import requests

baseurl = 'https://api.live.bilibili.com/xlive/web-room/v1/dM/gethistory'
# 要获取的弹幕的直播间号
roomid = 545068
# 请求头
headers = {
    'Host': 'api.live.bilibili.com',
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.48"
}
# 传递的参数
data = {
    'roomid': roomid,
    'csrf_token': '',
    'csrf': '',
    'visit_id': '',
}


def getDANMU():
    req = requests.post(url=baseurl, headers=headers, data=data)
    html = req.json()
    code = html['code']

    if req.status_code == 200 and code == 0:
        for dic in html['data']['room']:
            name = dic['nickname']
            timeline = dic['timeline'].split(' ')[-1]
            text = dic['text']
            # msg = timeline + '' + name + ':' + text + '\n'
            msg = timeline + ' ' + name + ':' + text
            print(msg)


if __name__ == '__main__':
    # roomid = input('请输入房间号:')
    getDANMU()
