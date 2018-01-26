from Crypto.Cipher import AES
import base64
import codecs
import re
import requests
import json
import os
import pynlpir
import mysql.connector
#url = 'http://music.163.com/weapi/v1/resource/comments/R_SO_4_418603077?csrf_token='
#headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'}
#payload = {'params':'m4QmZDHyzIAQhhgSU4m4pdBzVs9D0KaNefTTfYMLXjX66NfqfGQ/9iJD5\
#+Tq3Sx1Aou2KLe9RH8HFTZ0p1ibL+z6bBcCtnsaNrMkkogiY35UIalHK/h3UseA22iy7tk3er+xVHYWsM9/8PXLg/zXoUcKfjxh2\
#+Z036DQXQK3Bcywvn2qs/NV10BtxX654W1r',
#'encSecKey':'bbf0bcb35703f836c74b872c1e6047d63b7361ec66fa22f407bed4c140b5a5e5cbd370ab5f2dc7009ed386868c249a01dacd72be68d5d3e6789d9220f6c54c98908429ee0f3213588f08c566831f39de2985b9507eb7707f930698777a99c48f31a905785d7260d85570df1fe2bc784c268c7e69a1735b1371fd987665798591'}


#对网易云AES加密进行解密
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
    for i in range(10):
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

#分析词语
def parse_words(s):
    pynlpir.open()
    key_words = pynlpir.get_key_words(s, weighted = True)
    pynlpir.close()
    return key_words

dic_keywords = {}
def dic2str(dicc):
    lst = []
    for key in dicc:
        lst.append((key,dicc[key]))
    return lst
sorted(dic2str(dic_keywords), key = lambda x:-x[1])
for comment in get_it_comments('http://music.163.com/weapi/v1/resource/comments/R_SO_4_523251118?csrf_token='):
    print(comment)
    key_words = parse_words(comment[1])
    for key_word in key_words:
        print(key_word[0], '\t', key_word[1])
        dic_keywords.update({key_word[0]:dic_keywords.get(key_word[0],0) + key_word[1]})
    print(list(sorted(dic2str(dic_keywords),key=lambda x:x[1])))

def get_and_save_top_keywords(songid):
	dic_keywords = {}
	url = 'http://music.163.com/weapi/v1/resource/comments/R_SO_4_' + songid + '?csrf_token='
	comments_lst = get_it_comments(url)
	assert comments_lst, 'comments_lst is Null'
	print('爬取部分已经完成')
	for i,comment in comments_lst:
		# print(comment)#[0, '一听就着了迷']
		try:
			save_comment(i,comment,songid)
		except Exception as e:
			print("comment保存失败：", i,comment)
			print(e)
		else:
			print("comment保存成功：",i, comment)
		# 保存的同时当场解析
		try:
			key_words = parse_words(comment)
			for key_word in key_words:
				# print(key_word[0], '\t', key_word[1])#雷子 	 6.6
				dic_keywords.update({key_word[0]: dic_keywords.get(key_word[0], 0) + key_word[1]})
		except Exception as e:
			print('comment解析失败：',i,comment)
			print(e)
		else:
			print("comment解析成功:",i,comment)
		finally:
			print()
	print('所有评论的解析与保存已完成')
	print(sorted(dic2str(dic_keywords)))
	top_keywords = list(sorted(dic2str(dic_keywords), key=lambda x: -x[1]))[:10]
	print('下面开始保存top_keywords到数据库')
	try:
		save_to_keywords(songid, top_keywords)
	except Exception as e:
		print("top_keywords保存失败:", top_keywords)
		print(e)
	else:
		print("top_keywords保存成功:", top_keywords)
	return top_keywords


def init_tables():
	conn = mysql.connector.connect(user='root', password='1234', use_unicode=True)
	# 通常我们在连接MySQL时传入use_unicode=True，让MySQL的DB-API始终返回Unicode
	cursor = conn.cursor()
	# 如果是第二次运行，先把第一次的结果删掉
	cursor.execute('drop database if exists ' + '163music')
	cursor.execute('create database if not exists ' + '163music')
	cursor.execute(
		'create table if not exists 163music.comments(top_id varchar(10) primary key, comment varchar(200),songid varchar(20))')
	cursor.execute(
		'create table if not exists 163music.keywords(top_id varchar(10) primary key, keyword varchar(10),weight varchar(20),songid varchar(20))')
	conn.commit()
	cursor.close()


def save_comment(i,comment,songid):
	#print(comment_lst,songid)#97 [97, '谢谢'] 447926067
	# 后面再加，如果有其他songid，insert；如果是一个songid第二次运行，update
	conn = mysql.connector.connect(user='root', password='1234', use_unicode=True)
	# 通常我们在连接MySQL时传入use_unicode=True，让MySQL的DB-API始终返回Unicode
	cursor = conn.cursor()
	#去掉非法字符，否则入库报错
	comment=comment.encode('gbk','ignore').decode('gbk')
	cursor.execute('insert into 163music.comments(top_id,comment,songid) values (%s,%s,%s) ',
				   [i,comment,songid])
	conn.commit()
	cursor.close()


def save_to_keywords(songid, top_keywords):
	conn = mysql.connector.connect(user='root', password='1234', use_unicode=True)
	# 通常我们在连接MySQL时传入use_unicode=True，让MySQL的DB-API始终返回Unicode
	cursor = conn.cursor()
	for i, keyword in enumerate(top_keywords):
		cursor.execute('insert into 163music.keywords(top_id, keyword,weight,songid) values (%s, %s,%s, %s)',
					   [i, keyword[0], keyword[1], songid])
	conn.commit()
	cursor.close()


if __name__ == '__main__':
	# 在数据库中新建两张表，comments和keywords
	print("下面载数据库中新建两张表")
	init_tables()
	print("下面开始主流程")
	songid = '523251118'

	top_keywords = get_and_save_top_keywords(songid)
	assert top_keywords, 'top_keywords is Null'
	for i, top_keyword in enumerate(top_keywords):
		print('top{0}\t{1}\t{2}'.format(i, top_keyword[0], top_keyword[1]))    



