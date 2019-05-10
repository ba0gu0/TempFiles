#!/usr/bin/env python3.7
#!coding=utf-8

__doc__ = '''
    * 获取北京公交官网上所有的公交信息
    * 使用python3运行
    * 结果保存为json格式数据
'''
import requests
import re
import json
import logging

logger = logging.getLogger()  # 不加名称设置root logger
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s',datefmt = '%Y-%m-%d %H:%M:%S'
)
# 使用FileHandler输出到文件
# File_log = logging.FileHandler('GetBjBus.log', 'w')
# File_log.setLevel(logging.INFO)
# File_log.setFormatter(formatter)

# 使用StreamHandler输出到屏幕
Terminal_log = logging.StreamHandler()
Terminal_log.setLevel(logging.INFO)
Terminal_log.setFormatter(formatter)

# 添加两个Handler
logger.addHandler(Terminal_log)
# logger.addHandler(File_log)


RequestHeaders = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
    "Referer": "https://www.baidu.com"
    }
logger.info('初始化session!')
session = requests.Session()

Amap_Key = '高德api key'

def GetAllBusLineName():
    Data = []

    url="https://www.bjbus.com/home/index.php"

    logger.info('发送一个http请求,地址{}'.format(url))
    r = session.get(
        url=url,
        headers=RequestHeaders
        )
    r.encoding = r.apparent_encoding

    RegLight = r'<a href="javascript:;">(.*?)</a>'
    RegDark = r'<a href="javascript:;" data-lid="\d+">(.*?)</a>'

    DataLight = re.findall(RegLight, r.text)
    DataDark = re.findall(RegDark, r.text)

    Data.extend(DataLight)
    Data.extend(DataDark)

    return Data


def GetAllBusLineDirection(LineName):
    Data = []

    url="https://www.bjbus.com/home/ajax_rtbus_data.php?act=getLineDirOption&selBLine={}".format(LineName)

    logger.info('发送一个http请求,地址{}'.format(url))
    r = session.get(
        url=url,
        headers=RequestHeaders
        )
    r.encoding = r.apparent_encoding

    Reg = r'</option><option value="(.*?)">((.*?)\((.*?)-(.*?)\))'

    DataDirection = re.findall(Reg, r.text)
    
    for key in DataDirection:
        TmpData = {}
        if key[0] :
            TmpData['LineName'] = key[1]
            TmpData['Value'] = key[0]
            TmpData['StartStation'] = key[3]
            TmpData['EndStation'] = key[4]
            Data.append(TmpData)
        
    return Data


def GetAllLineDirectionStation(LineDirectionValue):
    Data = {}

    url='https://www.bjbus.com/home/ajax_rtbus_data.php?act=getDirStationOption&selBLine=a&selBDir={}'.format(LineDirectionValue)

    logger.info('发送一个http请求,地址{}'.format(url))
    r = session.get(
        url=url
    )

    r.encoding = r.apparent_encoding


    Reg = r'<option value="\d+">(.*?)</option>'

    DataLineDirectionStation = re.findall(Reg, r.text)

    TmpData = {}
    i = 0
    for key in DataLineDirectionStation:
        TmpData[i] = key
        i += 1

    Data['Stations'] = TmpData
    if TmpData:
        Data['MidStation'] = TmpData[len(TmpData)//2]
    
    return Data


def GetAllLineDirectionMsg(LineDirectionValue):
    Data = {}

    url='https://www.bjbus.com/home/ajax_rtbus_data.php?act=busTime&selBLine=a&selBStop=1&selBDir={}'.format(LineDirectionValue)

    logger.info('发送一个http请求,地址{}'.format(url))
    r = session.get(
        url=url
    )

    r.encoding = r.apparent_encoding


    Reg = r'<p>.*?&nbsp;(.*?)&nbsp;'
    try:
        DataLineDirectionMsg = re.findall(Reg, r.json()['html'])
        for key in DataLineDirectionMsg:
            Data['time'] = key
    except Exception as e : 
        Data['time'] = ''

    return Data


def ResolveError(LineData):

    LineName = LineData['LineName']
    StartStation = LineData['StartStation']
    EndStation = LineData['EndStation']

    Reg = r'^(.*?)\((.*?)-(.*?)\)$'
    SearchResult = re.search(Reg, LineName)
    if SearchResult:
        SearchLineName = SearchResult.group(1)
    else:
        return False

    url = 'https://restapi.amap.com/v3/bus/linename?s=rsv3&city=010&citylimit=true&extensions=all&output=json&city=010&offset=2&key={}&keywords={}路'.format(Amap_Key, SearchLineName)

    logger.info('发送一个http请求,地址{}'.format(url))

    r = session.get(
        url = url
        )
    r.encoding = r.apparent_encoding

    AmapData = r.json()
    for busline in AmapData['buslines']:
        if busline['start_stop'] == StartStation or busline['end_stop'] == EndStation:
            LineData['StartStation'] = busline['start_stop']
            LineData['EndStation'] = busline['end_stop']
            LineData['LineName'] = busline['name']

    return LineData


if __name__ == "__main__" :
    logger.info('获取所有的路线名称!')
    file = open('BjBus.json', 'w')

    for LineName in GetAllBusLineName():
        logger.info('获取路线{}的方向名称!'.format(LineName))
        for LineDirection in GetAllBusLineDirection(LineName):
            Data = {}
            Data.update(LineDirection)

            logger.info('获取路线{}的站点!'.format(LineDirection['LineName']))
            LineDirectionStation =  GetAllLineDirectionStation(LineDirection['Value'])

            Data.update(LineDirectionStation)
            logger.info('获取路线{}的时间!'.format(LineDirection['LineName']))
            LineDirectionMsg = GetAllLineDirectionMsg(LineDirection['Value'])

            Data.update(LineDirectionMsg)
            Data = ResolveError(Data)

            print(Data)

            json.dump(Data, file)
            file.write('\n')
        
    file.close()

