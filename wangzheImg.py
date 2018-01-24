import requests
import json
import os
import sys
from urllib import parse
url = "http://pvp.qq.com/web201605/wallpaper.shtml"

workList_url = "http://apps.game.qq.com/cgi-bin/ams/module/ishow/V1.0/query/workList_inc.cgi"
saveFolder = "image"
imageSizeName = [None, None, '1024x768', '1280x720', '1280x1024', '1440x900', '1920x1080', '1920x1200', '1920x1440']

def getlist(page_id):
    global workList_url
    worklist_params = {
        "activityId":"2735",
        "sVerifyCode":"ABCD",
        "sDataType":"JSON",
        "iListNum":"20",
        "totalpage":"0",
        "page":page_id,
        "iOrder":"0",
        "iSortNumClose":"1",
        "jsoncallback":"jQuery17108075817401233616_1516795572695",
        "iAMSActivityId":"51991",
        "_everyRead":"true",
        "iTypeId":"2",
        "iFlowId":"267733",
        "iActId":"2735",
        "iModuleId":"2735",
        "_":"1516795642089"
    }
    result = requests.get(workList_url, params = worklist_params)
    worklist_raw = result.text
    worklist_json = worklist_raw[worklist_raw.find('(') + 1:len(worklist_raw) - 2]
    worklist = json.loads(parse.unquote(worklist_json))
    return worklist


def downloadImage(url, path):
    try:
        image_data = requests.get(url,timeout = 15)
    except Exception as e:
        print("图片下载出错，%s,%s" % (e, url))
        return False
    with open(path, 'wb') as f:
        f.write(image_data.content)
    return True

def download_list(list):
    global imageSizeName
    makedir(saveFolder)
    for item in list['List']:
        makedir(saveFolder, item['sProdName'])
        print("创建文件夹%s" % item['sProdName'])
        for i in range(2,9):
            node_name = 'sProdImgNo_' + str(i)
            image_rawurl = item[node_name]
            image_url = image_rawurl[:len(image_rawurl) - 3] + '0'
            
            image_savepath = os.path.join(sys.path[0], saveFolder, item['sProdName'],
                                          item['sProdName'] + '_' + imageSizeName[i] + '.jpg')
            if downloadImage(image_url, image_savepath):
                print('成功下载图片：%s, 尺寸：%s' % (item['sProdName'], imageSizeName[i]))
def makedir(*dirname):
    dirpath = os.path.join(sys.path[0], *dirname)
    if not os.path.exists(dirpath):
        os.mkdir(dirpath)

if __name__ == '__main__':
    for i in range (1,12):
        list = getlist(i)
        download_list(list)