import asyncio
import zlib
import websockets
import json
import ssl

remote = 'wss://broadcastlv.chat.bilibili.com:2245/sub'
roomid = '27539913'

data_raw = '000000{headerLen}0010000100000007000000017b22726f6f6d6964223a{roomid}7d'
data_raw = data_raw.format(headerLen=hex(27 + len(roomid))[2:],
                           roomid=''.join(map(lambda x: hex(ord(x))[2:], list(roomid))))


async def startup():
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    async with websockets.connect(remote, ssl=ssl_context) as websocket:
        await websocket.send(bytes.fromhex(data_raw))
        tasks = [asyncio.create_task(receDM(websocket)), asyncio.create_task(sendHeartBeat(websocket))]
        await asyncio.wait(tasks)

hb = '00 00 00 10 00 10 00 01  00 00 00 02 00 00 00 01'


async def sendHeartBeat(websocket):
    while True:
        await asyncio.sleep(30)
        await websocket.send(bytes.fromhex(hb))
        print('[Notice] Sent HeartBeat.')


async def receDM(websocket):
    while True:
        recv_text = await websocket.recv()

        if recv_text is None:
            recv_text = b'\x00\x00\x00\x1a\x00\x10\x00\x01\x00\x00\x00\x08\x00\x00\x00\x01{"code":0}'

        printDM(recv_text)


def printDM(data):
    packetLen = int(data[:4].hex(), 16)
    ver = int(data[6:8].hex(), 16)
    op = int(data[8:12].hex(), 16)

    if len(data) > packetLen:
        printDM(data[packetLen:])
        data = data[:packetLen]

    if ver == 2:
        data = zlib.decompress(data[16:])
        printDM(data)
        return

    if ver == 1:
        if op == 3:
            print('[RENQI]  {}'.format(int(data[16:].hex(), 16)))
        return

    if op == 5:
        try:
            jd = json.loads(data[16:].decode('utf-8', errors='ignore'))
            if jd['cmd'] == 'DANMU_MSG':
                print('[DANMU] ', jd['info'][2][1], ': ', jd['info'][1])
            elif jd['cmd'] == 'SEND_GIFT':
                print('[GIFT]', jd['data']['uname'], ' ', jd['data']['action'], ' ', jd['data']['num'], 'x',
                      jd['data']['giftName'])
            elif jd['cmd'] == 'LIVE':
                print('[Notice] LIVE Start!')
            elif jd['cmd'] == 'PREPARING':
                print('[Notice] LIVE Ended!')
            else:
                print('[OTHER] ', jd['cmd'])
        except Exception as e:
            pass


if __name__ == '__main__':
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(startup())
    except Exception as e:
        print("Error:", e)
        print("Error type:", type(e))
        print('Exiting')