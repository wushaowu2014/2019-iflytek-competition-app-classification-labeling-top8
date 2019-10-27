# -*- coding: utf-8 -*-
'''主要爬取应用宝上的app,对于没有爬到的app，用APP包名在手机百度上爬取：先搜索该app，默认选择第一条对应的
    app,获得该条的URL之后，然后对url进行爬取'''
import pandas as pd
import numpy as np
from lxml import etree
import requests
from bs4 import BeautifulSoup
import concurrent.futures
from tqdm import *
#options = webdriver.ChromeOptions()
#options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
#chrome_driver_binary = "chromedriver"
#driver = webdriver.Chrome(chrome_driver_binary, chrome_options=options)
base_url = r'https://android.myapp.com/myapp/detail.htm?apkName='
def download(app_name):
    #options = webdriver.ChromeOptions()
    #options.add_argument('-headless')
    #browser = webdriver.Chrome(chrome_options=options,executable_path='chromedriver')
    
    #google:
    #'https://play.google.com/store/apps/details?id=com.gravity.romg'
    head={'User-Agent':'Mozilla/5.0'}
    s=requests.Session()
    scont=s.get('https://android.myapp.com/myapp/detail.htm?apkName='+app_name[1],headers=head)
    html = etree.HTML(scont.text)
    html_data =html.xpath('//div[@class="det-app-data-info"]/text()')
    x=[0]
    x='。'.join(html_data)
    x=x.replace('\r','')
    if len(x)<3:
        x=download1(app_name)
        return x
    else:
        return x
def download1(app_name):
    #options = webdriver.ChromeOptions()
    #options.add_argument('-headless')
    #browser = webdriver.Chrome(chrome_options=options,executable_path='chromedriver')
    
    #google:
    #'https://play.google.com/store/apps/details?id=com.gravity.romg'
    #app_name=find_package(app_name)
    if str(app_name[0])=='nan':
        return 0
    else:
        app_name=find_package(app_name)
        if app_name==0:
            return 0
        else:
            
            head={'User-Agent':'Mozilla/5.0'}
            s=requests.Session()
            scont=s.get('https://mobile.baidu.com'+app_name,headers=head)
            html = etree.HTML(scont.text)
            html_data =html.xpath('//section/div/p/text()')
            x=[0]
            x='。'.join(html_data)
            x=x.replace('\r','')
            if len(x)<2:
                return 0
            else:
                return x
def find_package(package_name):
    head={'User-Agent':'Mozilla/5.0'}
    s=requests.Session()
    scont=s.get('https://mobile.baidu.com/search?w='+package_name[0],headers=head)
    soup=BeautifulSoup(scont.text,'lxml')
    zzr=soup.find_all(class_="app-base-normal normal-app base-normal--normal") #查找含有class=的
    url_list=[]
    for item in zzr:
        list_tmp=item.find_all('a')
        for a in list_tmp:
            url_list.append(a.get('href'))
    if len(url_list)>0:
        return url_list[0]
    else:
        return 0

if __name__ == "__main__":
    print('爬取训练集数据...')
    train= pd.read_csv("final_apptype_train.dat",header=None,encoding='utf8',delimiter='\t')
    train.columns=['id','conment','label']
    feats=[]
    with concurrent.futures.ProcessPoolExecutor() as executor:
        train_files=[(row['id'],row['conment']) for i,row in train.iterrows()]#list(train.conment)
        for path,res in tqdm(zip(train_files,executor.map(download,train_files))):
            feats.append(res)
    
    train['conment1']=feats
    train[['conment1','label']].to_csv('new_train.csv',index=None,encoding='utf8')
    print('训练集未爬到app的个数：',train[train.conment1==0].shape[0]) #5657
    #=========================================================================
    print('爬取测试集数据...')
    appname_package=pd.read_csv("appname_package.dat",header=None,encoding='utf8',delimiter='\t')
    appname_package.columns=['id','name','conment']
    feats=[]
    with concurrent.futures.ProcessPoolExecutor() as executor:
        train_files=[(row['name'],row['conment']) for i,row in appname_package.iterrows()]#list(train.conment)
        for path,res in tqdm(zip(train_files,executor.map(download,train_files))):
            feats.append(res)
    
    appname_package['conment1']=feats
    appname_package[['id','conment1']].to_csv('new_test.csv',index=None,encoding='utf8')
    print('测试集未爬到app的个数：',appname_package[appname_package.conment1==0].shape[0])
    
