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
File_log = logging.FileHandler('GetBjBus.log', 'w')
File_log.setLevel(logging.INFO)
File_log.setFormatter(formatter)

# 使用StreamHandler输出到屏幕
Terminal_log = logging.StreamHandler()
Terminal_log.setLevel(logging.INFO)
Terminal_log.setFormatter(formatter)

# 添加两个Handler
logger.addHandler(Terminal_log)
logger.addHandler(File_log)


RequestHeaders = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
    "Referer": "https://www.baidu.com"
    }
logger.info('初始化session!')
session = requests.Session()

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

    TmpData = []
    for key in DataLineDirectionStation:
        TmpData.append(key)
    Data['station'] = TmpData
    
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

    DataLineDirectionMsg = re.findall(Reg, r.json()['html'])

    for key in DataLineDirectionMsg:
        Data['time'] = key
    
    return Data

if __name__ == "__main__" :
    Data = []
    logger.info('获取所有的路线名称!')
    for LineName in GetAllBusLineName():
        logger.info('获取路线{}的方向名称!'.format(LineName))
        for LineDirection in GetAllBusLineDirection(LineName):
            TmpData = []
            TmpData.append(LineDirection)
            logger.info('获取路线{}的站点!'.format(LineDirection['LineName']))
            LineDirectionStation =  GetAllLineDirectionStation(LineDirection['Value'])
            TmpData.append(LineDirectionStation)
            logger.info('获取路线{}的时间!'.format(LineDirection['LineName']))
            LineDirectionMsg = GetAllLineDirectionMsg(LineDirection['Value'])
            TmpData.append(LineDirectionMsg)
            Data.append(TmpData)
    
    print(Data)

    with open('BjBus.json', 'w') as f:
        json.dump(Data, f)

