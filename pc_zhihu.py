# -*-coding=utf-8-*-
__author__ = 'Rocky'
import requests
import re
import numpy as np
from pandas import DataFrame
import pandas as pd
from bs4 import BeautifulSoup
import os
from lxml import etree
import codecs
import getContent
import pdfkit
import instapaperlib as ins
import account_ins

class zhihu:
    def __init__(self, url, classify, pc):
        self.__url = url
        self.__classify = classify
        self.__getContent = getContent.saveToFile('zhihu')
        if pc:
            self.__getUrls()
        else:
            self.df = pd.read_excel(r'D:/pythonResouce/' + self.__classify + '.xls')
        #print(self.df)
        self.ins = ins.Instapaper(account_ins.userName, account_ins.password)

    def isSave(self, filename):
        return self.__getContent.isDownloaded(filename)

    def save(self, filename, text):
        self.__getContent.save(filename, text)

    def save_Urls(self):
        urlHead = 'https://www.zhihu.com'
        texts = ['{title} {urlHead}{url}\r\n'.format(urlHead=urlHead, url=self.urls[i], title=self.questions[i])
                    for i in range(len(self.urls)) ]
        print(texts)
        for text in texts:
            self.__getContent.save(self.__classify + '汇总', text)

    def getAnswers(self):
        urlHead = 'https://www.zhihu.com'
        for url in self.urls:
            self.__getAnswer(urlHead+url)

    def __getAnswer(self, url):
        #这个功能已经实现
        global text_content

        agent = '537.36 (KHTML, like Gecko) Chrome'

        #agent = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
        headers = {'Host': 'www.zhihu.com',
                   'Referer': 'https://www.zhihu.com',
                   'User-Agent': agent}

        try:
            html = requests.get(url, headers=headers)
            html.encoding = 'utf-8'
            selector = etree.HTML(html.content)
        except:
            return
        #print(html.text)
        title=selector.xpath('//h1[@class="QuestionHeader-title"]/text()')[0]
        #title = selector.xpath('//*[@id="root"]/div/main/div/div[1]/div[2]/div[1]/div[1]/h1/text()')

        filename_old = title.strip()
        filename = self.__classify + '_' + re.sub('[\/:*?"<>|]', '-', filename_old)
        # 用来保存内容的文件名，因为文件名不能有一些特殊符号，所以使用正则表达式过滤掉
        print(filename)
        self.save(filename, title)

        self.save(filename, "\r\n\r\n----Link %s -----\r\n"  %url)
        self.save(filename, "\r\n\r\n--------------------Detail----------------------\r\n\r\n")
        # 获取问题的补充内容
        content=selector.xpath('//span[@class="RichText"]')
        for i in content:
            #print(i)
            text_content=i.xpath("string(.)")
            self.save(filename,text_content)
        #print(text_content)
        self.save(filename, "\r\n\r\n--------------------Answer----------------------\r\n\r\n")

        answers = selector.xpath('//span[@class="RichText CopyrightRichText-richText"]')
        #print(answers)
        for ans in answers:
            #text_content=i.xpath("string(.)") + '\r\n'
            for eachP in (ans.xpath('./text()')):
                text_content = eachP + '\r\n'
                self.save(filename,text_content)
            self.save(filename, "\r\n\r\n-----------------next Answer--------------------\r\n\r\n")
            #print(text_content)

    def __getUrls(self):
        #agent = '537.36 (KHTML, like Gecko) Chrome'
        agent = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'

        headers = {'Host': 'www.zhihu.com',
                           'Referer': 'https://www.zhihu.com',
                           'User-Agent': agent}

        try:
            html = requests.get(self.__url, headers=headers)
            selector = etree.HTML(html.text)
        except:
            return
        #print(self.__url)
        self.urls = selector.xpath('//div[@class="content"]/h2/a/@href')
        self.questions = selector.xpath('//div[@class="content"]/h2/a/text()')

        for page in range(2,89):
            try:
                html = requests.get(self.__url + '?page='+str(page), headers=headers)
                html.encoding = 'utf-8'
                selector = etree.HTML(html.content)
            except:
                return
            urls = selector.xpath('//div[@class="content"]/h2/a/@href')
            questions = selector.xpath('//div[@class="content"]/h2/a/text()')
            if len(urls) == 0:
                break
            self.urls = self.urls + urls
            self.questions = self.questions + questions
            #print(page)
        #print(self.urls)

        urlHead = 'https://www.zhihu.com'
        data = np.transpose([self.urls, self.questions])
        #print(data)
        colomus = ['url', 'question']
        self.df = DataFrame(data=data, columns=colomus)
        self.df['classify'] = self.__classify
        #print(self.df)
        self.df.to_excel(r'D:/pythonResouce/' + self.__classify + '.xls')

    def sent_ins(self, begin=0, number=100):
        i = 0
        urlHead = 'https://www.zhihu.com'
        for (index, row) in self.df.iterrows():
            if row[2] == "装修":
                i += 1
                if i < begin:
                    continue
                elif i >= begin+number:
                    break
                print('%s' %(row[0]))
                self.ins.add_item(urlHead+row[1], title=row[0], selection=row[2])

    def parse_url_to_html(self, url):
        agent = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'

        headers = {'Host': 'www.zhihu.com',
                   'Referer': 'https://www.zhihu.com',
                   'User-Agent': agent}

        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.content, "html.parser")
        bodys = soup.find_all(class_="RichText CopyrightRichText-richText")
        html = str('')
        for body in bodys:
            html += str(body)

        with open('a.html', 'wb') as file:
            text_html = '<!DOCTYPE html>' \
                        '<html>' \
                        '<meta charset="utf-8">' \
                        '   <head> ' \
                        '   </head>' \
                        '       <body>' \
                        '           {0}' \
                        '       </body>' \
                        '</html>'.format(html)
            file.write(text_html.encode('utf-8'))

    def save_pdf(self, htmls):
        """
        把所有html文件转换成pdf文件
        """
        options = {
            'page-size': 'Letter',
            'encoding': "UTF-8",
            'custom-header': [
                ('Accept-Encoding', 'gzip')
            ]
        }
        options = {
            'page-size': 'Letter',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': "UTF-8",
            'no-outline': None
        }
        pdfkit.from_file(htmls, 'a.pdf', options=options)

zh = zhihu('https://www.zhihu.com/topic/19554051/top-answers', '装修', False)
#zh = zhihu('https://www.zhihu.com/topic/19629328/top-answers', '公务员考试', True)
zh.sent_ins(1*7+1, 7)



