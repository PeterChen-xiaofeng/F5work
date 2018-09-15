import urllib.request
from bs4 import BeautifulSoup
import time
import requests
import json
from urllib import request
from sys import argv
import logging
import logging
import re

logger = logging.getLogger('sensor')
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s: - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s: - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename='%ssensor.txt' % (time.strftime("%d-%m-%Y")),
    level=logging.INFO)
streamhandler = logging.StreamHandler()
streamhandler.setLevel(logging.DEBUG)
streamhandler.setFormatter(formatter)
logger.addHandler(streamhandler)


def request_ding(result, Warning=False, isAtAll=False):
    ding_url = 'https://oapi.dingtalk.com/robot/send?access_token=8cbb188ce7bee55b95291c815fa870264ce02208ec4bd6f8ee94b7c38638dbc2'
    atMobiles = None
    if Warning:
        atMobiles = 18819254603
        logger.warning('%s' % result)
    content = ''
    for i in result:
        content += i + ' '
    data = {
        "msgtype": "text",
        "text": {
            "content": content
        },
        "at": {
            "atMobiles": [
                atMobiles
            ],
            "isAtAll": isAtAll
        }
    }
    # 设置编码格式
    json_data = json.dumps(data).encode(encoding='utf-8')
    header_encoding = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko', "Content-Type": "application/json"}
    try:
        req = request.Request(url=ding_url, data=json_data,
                          headers=header_encoding)
        res = request.urlopen(req)
        res = res.read()
        logger.info(res)
    except Exception :
        logger.warning(Exception)
        request_ding(result,Warning,isAtAll)
    


url = 'http://weixin.lvkedu.com/lvkedu-weixin/getDeviceManage.action?result=VPPI3FkdMOYAv5IHIwWQZlIeIF7PyZwuBx158RVGOuw%3D'
temperature = [0, 0, 0, 0]
temp_warning = [0, 0, 0, 0]
elec_warning = [0, 0, 0, 0]
while(True):
    response = urllib.request.urlopen(url)
    
    logger.info('Inquery begin .             %s.'%time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
    try:
        html = response.read()
        soup = BeautifulSoup(html, 'lxml')
    except :
        logger.warning('Sorry, connection failed.But we will try it again again and again.Dont be said.')
        time.sleep(60*10)
        continue
    request_ding([time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))])   
    sensor_list = ['月亮湾', '海格堡', '第一金碧', '广州办公室', '000100GP', '000100Jm']
    sensor_dict = {'月亮湾': 'div_000100JT_state', '海格堡': 'div_000100Ib_state', '第一金碧': 'div_000100gD_state',
                   '广州办公室': 'div_000100S5_state', '000100GP': 'div_000100GP_state', '000100Jm': 'div_000100Jm_state'}

    i = 0
    for sensor in sensor_list[0:4]:
        sensor = sensor_dict[sensor]
        html = soup.find(id=sensor)
        content = html.get_text().strip().split()
        logger.info(content[0:5] + content[8:10])
        # 获取conten中传感器的温度
        temp = float(re.findall(r"\d+\.?\d*", content[3])[0])
        # 当发现传感器温度发生变化时，向钉钉发送传感器信息
        if temp != temperature[i]:
            temperature[i] = temp
            request_ding(content[0:5] + content[8:10])
        # 温度超过正常范围时进行报警，并在钉钉艾特所有人
        if temperature[i] < 0 or temperature[i] > 10:
            if temp_warning[i] == 0:
                request_ding(['Temperature warning : sensor %s ' %
                             content[0], str(content[2:5]), str(content[8:10])], Warning=True, isAtAll=False)
            temp_warning[i] += 1
            if temp_warning[i] == 3:
                temp_warning[i] = 0
        else:
            temp_warning[i] = 0
        # 电量过低时报警，并在钉钉艾特电量管理人
        if float(content[1][0:4]) <= 20:
            if elec_warning[i] == 0 :
                request_ding(['Electrict warning : the sensor %s need to be recharged' %
                         content[0], content[1]], Warning=True, isAtAll=False)
            elec_warning[i] += 1
            if elec_warning[i] == 3:
                elec_warning[i] = 0
        else:
            elec_warning[i] = 0
        i += 1
        time.sleep(2)
    logger.info('Inquery end.\n')
    
    # 等待十分钟
    time.sleep(60*10)
    # 测试
    # time.sleep(2)
