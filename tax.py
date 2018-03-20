# encoding:utf-8
import requests
import random
import lxml.html
import pymysql
import datetime
import time
from SETTINGS import USER_AGENT_LIST, MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE


class TaxSpider:
    ''''''

    def __init__(self):
        self.main_url = [
            'http://www.chinatax.gov.cn/n810341/n810755/index.html',
        ]
        self.domain = 'http://www.chinatax.gov.cn'
        self.conn = pymysql.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            db=MYSQL_DATABASE,
            charset='utf8mb4',
        )
        self.cursor = self.conn.cursor()

    def main(self):
        response = self.get_html(self.main_url[0])
        page_urls= self.page_urls(response)
        for i in page_urls:
        # url='http://www.chinatax.gov.cn/n810341/n810755/c3348045/content.html'
            h = self.get_html(i)
            urls,titles = self.law_urls_titles(h)
            for url,title in zip(urls,titles):
                r= self.get_html(url)
                content=self.law_content(r)
                dept_name=self.law_department(r)
                doc_num=self.doc_num(r)
                ret = self.exist(url)
                if ret[0] == 1:
                    print('《{}》已经存在了'.format(title))
                    pass
                else:
                    self.write_db(title, url, dept_name, content,doc_num)
                    print('《{}》已采集入库'.format(title))
                time.sleep(random.random())
        self.conn.commit()

        # response = self.get_html(self.main_url[0])
        # page_urls= self.page_urls(response)
        # resp = self.get_html(page_urls[0])
        # print(self.law_urls_titles(resp))

    def exist(self, url):
        sql = "SELECT EXISTS(SELECT 1 FROM tax WHERE src_url=%(url)s)"
        value = {'url': url}
        self.cursor.execute(sql, value)
        return self.cursor.fetchall()[0]

    def write_db(self, title, url, dept_name, content, doc_num):
        sql = 'INSERT INTO tax (`title`,`src_url`,`department`,`content`,`doc_num`) VALUES (%(title)s,%(src_url)s,%(department)s,%(content)s,%(doc_num)s)'
        value = {
            'title': title,
            'src_url': url,
            'department': dept_name,
            'content': content,
            'doc_num': doc_num
        }
        self.cursor.execute(sql, value)


    def law_department(self,html):
        rule='//li[@class="sv_blue24"]/text()'
        dept_name=self.get_by_xpath(html,rule)
        try:        
            return dept_name[0]
        except Exception as e:
            print(e)

    def doc_num(self,html):
        rule='//li[@class="sv_black14_30"]/text()'
        doc_num=self.get_by_xpath(html,rule)
        try:
            return doc_num[0]
        except Exception as e:
            print(e)
            
    def law_content(self, html):
        rule='//li[@id="tax_content"]/p/text()'
        content= self.get_by_xpath(html,rule)
        # r_content=[self.remove_tags(i) for i in content]
        li =self.remove_blank([self.remove_tags(i) for i in content])        
        r_content='\r\n'.join(li)
        return r_content

    def remove_blank(self,li):
        while '' in li:
            li.remove('')
        return li

    def remove_tags(self,text):
        t= text.strip().replace('\n','').replace('\t','').replace('\u3000','')       
        return t

    def law_urls_titles(self,html):
        rule='//dl/dd/a/@href'
        rule1='//dl/dd/a/@title'
        law_urls= self.get_by_xpath(html,rule)
        law_titles = self.get_by_xpath(html,rule1)
        law_url_list= [self.domain+i.split('../..')[1] for i in law_urls]
        return law_url_list,law_titles    

    def page_urls(self,html):
        rule = '//div[@style="display:none"]/a/@href'
        page_urls = self.get_by_xpath(html, rule)
        url_list = [self.domain+i.split('../..')[1] for i in page_urls]
        return url_list

    def get_by_xpath(self, html, rule):
        '''extract the content by xpath'''
        selector = lxml.html.fromstring(html)
        content = selector.xpath(rule)
        return content

    def get_html(self, url):
        response = requests.get(url, headers=self.request_headers())
        response.encoding ='utf-8'
        return response.text

    def request_headers(self):
        headers = {
            'Accept':
            'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding':
            'gzip, deflate',
            'Accept-Language':
            'zh-CN,zh;q=0.9',
            'Cache-Control':
            'max-age=0',
            'User-Agent':
            self.user_agent(),
        }
        return headers

    def user_agent(self):
        ua = random.choice(USER_AGENT_LIST)
        return ua


if __name__ == '__main__':
    obj = TaxSpider()
    obj.main()
    # obj.conn.commit()