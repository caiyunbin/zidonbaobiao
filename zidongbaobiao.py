# -*- coding: utf-8 -*-
"""
Created on Fri Aug 16 10:06:09 2019

@author: Administrator
"""



import csv
import pandas as pd
import requests
from urllib.parse import urlencode
import json
from datetime import datetime
import numpy as np


##获取详情页，需要输入两个参数
def get_one_page(page,bbsid):
    print('正在读取第:%d页'%(page))
    try:
        params = {
            'pageindex': page,
            'pagesize': '50',
            'bbs': 'c',
            'bbsid': bbsid,
            'fields': 'topicid,title,post_memberid,post_membername,postdate,ispoll,ispic,isrefine,replycount,viewcount,videoid,isvideo,videoinfo,qainfo,tags,topictype,imgs,jximgs,url,piccount,isjingxuan,issolve,liveid,livecover,topicimgs',
            'orderby': 'topicid-'
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
        }
        url = 'https://club.autohome.com.cn/frontapi/topics/getByBbsId?' + urlencode(params)
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
            return None
    except requests.exceptions:
        return None
    


##返回一个json数据,然后进行解析，并且将第二个参数放入表格做列区分
def parse_json_data(html,bbsid):
    data = json.loads(html)
    if data and 'result' in data.keys():
        result_list = data.get('result').get('list')
        for item in result_list:
            yield{
                    'bbsid':bbsid,
                    '用户ID':item.get('post_memberid'),
                    '文章标题':item.get('title'),
                    '发布者':item.get('post_membername'),
                    '发布时间':item.get('postdate')[0:10],
                    '帖子类型':item.get('topictype'),
                    '回帖数量':item.get('replycount'),
                    '具体链接':item.get('url')
                    }



##将源数据保存成CSV数据，保存在桌面
def save_to_csv(dics):
    with open('C:/Users/Administrator/Desktop/文件集合/qichezhijia.csv','a',encoding='GB18030',newline='') as csvfile:
        fieldnames = ['bbsid','用户ID','文章标题','发布者','发布时间','帖子类型','回帖数量','具体链接']
        writer = csv.DictWriter(csvfile,fieldnames=fieldnames)
        writer.writerow(dics)



##将每个月的三项指标进行计算
def get_month_data(data):
    shuliang = data.groupby('bbsid')['用户ID'].count()
    reply = data.groupby('bbsid')["回帖数量"].sum()
    jingping = data[data['帖子类型']=='精'].groupby('bbsid')['用户ID'].count()
    return (shuliang,reply,jingping)



##主程序，需要输入的参数是源数据需要保存文件的位置            
def main(path):
    for bbsid in ['2886','3959','448','526','364','3954','358','314','1007','4235']:
        for page in range(12):
            html = get_one_page(page,bbsid)
            content = parse_json_data(html,bbsid)
            for item in content:
                save_to_csv(item)
    
    data = pd.read_csv(path, sep=",",engine = "python",encoding="GB18030",header=None,names=['bbsid','用户ID','文章标题','发布者','发布时间','帖子类型','回帖数量','具体链接'])
    data.info()
    data.head()
    data['发布时间'] = pd.to_datetime(data['发布时间'])
    data['bbsid'].replace({2886:'K3',3959:'领动',448:'轩逸',526:'卡罗拉',364:'福克斯',3954:'KX5',358:'途胜',314:'CR-V',1007:'IX35',4235:'探界者'},inplace=True)
    this_month = data[(data["发布时间"]>= datetime(2019,7,1)) & (data["发布时间"]<= datetime(2019,7,31))]
    last_month = data[(data["发布时间"]>= datetime(2019,6,1)) & (data["发布时间"]<= datetime(2019,6,30))]    
    
    shuliang_1,reply_1,jingping_1 = get_month_data(this_month)
    shuliang_2,reply_2,jingping_2 = get_month_data(last_month)
    
    final = pd.concat([shuliang_1,reply_1,jingping_1,shuliang_2,reply_2,jingping_2],axis = 1)
    
    final.columns=['本月帖数','本月回帖','本月精品','上月帖数','上月回帖','上月精品']
    
    print(final)
    
    final.to_csv(path_or_buf = r"C:/Users/Administrator/Desktop/文件集合/yuebao.csv" ,
              sep=",",
              na_rep = 0,
              encoding = "GB18030" 
             )
    
    
    
###Python最终的程序，文件在这里保存在桌面    
if __name__=='__main__':
    path ='C:/Users/Administrator/Desktop/文件集合/qichezhijia.csv'
    main(path)
    









