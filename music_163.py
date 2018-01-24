from Crypto.Cipher import AES
import base64
import codecs
import re
import requests
import json
import os
import csv
#url = 'http://music.163.com/weapi/v1/resource/comments/R_SO_4_418603077?csrf_token='
#headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'}
#payload = {'params':'m4QmZDHyzIAQhhgSU4m4pdBzVs9D0KaNefTTfYMLXjX66NfqfGQ/9iJD5\
#+Tq3Sx1Aou2KLe9RH8HFTZ0p1ibL+z6bBcCtnsaNrMkkogiY35UIalHK/h3UseA22iy7tk3er+xVHYWsM9/8PXLg/zXoUcKfjxh2\
#+Z036DQXQK3Bcywvn2qs/NV10BtxX654W1r',
#'encSecKey':'bbf0bcb35703f836c74b872c1e6047d63b7361ec66fa22f407bed4c140b5a5e5cbd370ab5f2dc7009ed386868c249a01dacd72be68d5d3e6789d9220f6c54c98908429ee0f3213588f08c566831f39de2985b9507eb7707f930698777a99c48f31a905785d7260d85570df1fe2bc784c268c7e69a1735b1371fd987665798591'}



def aesEncrypt(text, secKey):
    pad = 16 - len(text) % 16
    if isinstance(text, bytes):
        print("type(text) == 'bytes'")
        text = text.decode('utf-8')
    text = text + pad * chr(pad)
    encryptor = AES.new(secKey, 2, '0102030405060708')
    ciphertext = encryptor.encrypt(text)
    ciphertext = base64.b64encode(ciphertext)
    return ciphertext


def rsaEncrypt(text, pubKey, modulus):
    text = text[::-1]
    rs = int(codecs.encode(text.encode('utf-8'), 'hex_codec'), 16) ** int(pubKey, 16) % int(modulus, 16)
    return format(rs, 'x').zfill(256)

modulus = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
nonce = '0CoJUm6Qyw8W8jud'
pubKey = '010001'

def createSecretKey(size):
    return (''.join(map(lambda xx: (hex(ord(xx)) [2:]), str(os.urandom(size))))[0:16])

def get_it_comments(url):
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'}
    comment_list = []
    count = 0
    for i in range(20):
        text = {
        'username' : '',
        'password' : '',
        'rememberLogin' : 'True',
        'offset' : i * 10
        }


        text = json.dumps(text)
        secKey = createSecretKey(16)
        encText = aesEncrypt(aesEncrypt(text, nonce), secKey)
        encSecKey = rsaEncrypt(secKey, pubKey, modulus)
        payload = {
            'params' : encText,
            'encSecKey' : encSecKey
        }
        r = requests.post(url, headers = headers, data = payload)
        r.raise_for_status()
        try:
            r_dic = json.loads(r.text)
        except:
    	    print("json.loads(r.text)出错了")
    #print(r.status_code)
    #print(r.headers)
    #print(r_dic)
        comments = r_dic["comments"]
        print()
    #print('共有{0}条评论'.format(len(comments)))
        assert len(comments) == 10
        for comment in comments:
            comment_list.append([count, comment['content']])
            count += 1  
    print('已经get第{0}条评论'.format(len(comment_list)))
    return comment_list


if __name__ == '__main__':
    for comment in get_it_comments('http://music.163.com/weapi/v1/resource/comments/R_SO_4_523251118?csrf_token='):
        print(comment)