# encoding:utf-8
import requests
import random
import lxml.html
import pymysql
import datetime
import time
from SETTINGS import USER_AGENT_LIST,MYSQL_HOST,MYSQL_USER,MYSQL_PASSWORD,MYSQL_DATABASE


class CourtSpider:
    ''''''

    def __init__(self):
        self.main_url = [
            'http://www.court.gov.cn/fabu-gengduo-16.html',
            'http://www.court.gov.cn/fabu-gengduo-17.html',
        ]
        self.domain = 'http://www.court.gov.cn'
        self.conn = pymysql.connect(
            host= MYSQL_HOST,
            user= MYSQL_USER,
            password= MYSQL_PASSWORD,
            db=MYSQL_DATABASE,
            charset='utf8mb4',
        )
        self.cursor = self.conn.cursor()

    def main(self):
        for base_url in self.main_url:
            html = self.get_html(base_url)
            # for i in range(1,2):
            page_num=self.page_num(html)
            url_list =[base_url+'?page={}'.format(str(i)) for i in range(1,(page_num // 20)+2)]
            for page_url in url_list:
                print(page_url)
                page_info = self.get_html(page_url)  #get the page content
                urls = self.law_urls(page_info)
                # print(urls)
                titles = self.law_titles(page_info)                
                for url, title in zip(urls, titles):
                    html2 = self.get_html(url)
                    date = self.publish_date(html2)
                    content = self.law_content(html2)
                    ret = self.exist(url)
                    if ret[0] == 1:
                        print('《{}》已经存在了'.format(title))
                        pass
                    else:
                        self.write_db(title, url, date, content)
                        print('《{}》已采集入库'.format(title))
                    time.sleep(random.random())
        self.conn.commit()

    def exist(self, url):
        sql = "SELECT EXISTS(SELECT 1 FROM laws WHERE src_url=%(url)s)"
        value = {'url': url}
        self.cursor.execute(sql, value)
        return self.cursor.fetchall()[0]

    def write_db(self, title, url, date, content):
        sql = 'INSERT INTO laws (`title`,`src_url`,`publish_date`,`content`) VALUES (%(title)s,%(src_url)s,%(publish_date)s,%(content)s)'
        value = {
            'title': title,
            'src_url': url,
            'publish_date': date,
            'content': content
        }
        self.cursor.execute(sql, value)

    def publish_date(self, html):
        rule = '//ul[@class="clearfix fl message"]/li'
        date = self.get_by_xpath(html,
                                 rule)[1].xpath('string(.)').split('：')[1].split(' ')[0]
        date_new = datetime.datetime.strptime(date, "%Y-%m-%d")
        return date_new

    def law_content(self, html):
        rule = '//div[@class="txt_txt"]'
        content = self.get_by_xpath(html, rule)[0].xpath('string(.)').strip()
        return content

    def law_urls(self, html):
        '''get law content'''
        rule = '//div[@class="sec_list"]/ul/li/a/@href'
        urls = [self.domain + i for i in self.get_by_xpath(html, rule)]
        return urls

    def law_titles(self, html):
        rule = '//div[@class="sec_list"]/ul/li/a/@title'
        law_titles = [i.strip().replace('\r','').replace('\n','').replace('\t','') for i in self.get_by_xpath(html, rule)]
        return law_titles

    def page_num(self, html):
        rule = '//span[@class="num"]/text()'
        page_num = int(self.get_by_xpath(html, rule)[0])
        return page_num

    def get_by_xpath(self, html, rule):
        '''extract the content by xpath'''
        selector = lxml.html.fromstring(html)
        content = selector.xpath(rule)
        return content

    def get_html(self, url):        
        response = requests.get(url, headers=self.request_headers())
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

if __name__ =='__main__':
    obj = CourtSpider()
    obj.main()
    # obj.conn.commit()