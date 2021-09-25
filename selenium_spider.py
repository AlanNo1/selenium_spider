# coding:utf-8
"""Author:1924885288@qq.com"""
"""Time:2021_09_25"""
"""-----------------------"""
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
import urllib
from lxml import etree
import random
import urllib.request
from selenium.common.exceptions import WebDriverException
import requests
import json

class BaolifengSpider(object):
    # 初始化参数
    def __init__(self):
        self.i = 0  # 提取代理个数
        self.proxyList = []  # 代理列表
        self.used_proxyList = []  # 使用的代理列表
        self.proxy = None  # 代理IP
        self.baidu_driver = None  # 浏览器驱动对象
        self.url = 'www.blflogo.com'  # 搜索的网站地址
        self.ip_pay_url = 'http://dps.kdlapi.com/api/getdps/?orderid=953240278749313&num=1&pt=1&dedup=1&format=json&sep=1'  # 付费的快代理网址
        self.key_word = ['不锈钢标牌', '金属标牌']  # 搜索的关键字
        self.title = ['首页', '不锈钢标牌', '电铸标牌', '酒标牌', '铝标牌', '行业案例', '新闻资讯', '联系我们', '电铸厚标', '镍片标牌']  # 需要点击的标签

    # 获取浏览器驱动
    def get_baidu_driver(self, proxy, headers, Ifdup=True):
        """Ifdup:是否去重IP"""
        while Ifdup:
            # 代理去重
            if proxy in self.used_proxyList:
                try:
                    self.proxy = random.choice(self.proxyList)
                except:
                    print('没有获取到代理')
                    return
            else:
                self.proxy = proxy
                break
        print("当前使用的代理IP是：", self.proxy)
        if self.baidu_driver is None:
            option = Options()
            # 无头模式
            # option.add_argument('--headless')
            # option.add_argument('--no-sandbox')
            # option.add_argument('--disable-dev-shm-usage')
            # option.add_argument('--disable-gpu')
            # 设置参数
            option.add_argument(f'--user-agent={headers}')
            option.add_argument(f'--proxy-server={self.proxy}')
            self.baidu_driver = webdriver.Chrome(options=option)
            self.baidu_driver.implicitly_wait(10)
            self.baidu_driver.delete_all_cookies()
        return self.baidu_driver

    # 获取当前关键字的百度排名
    def get_keyword_order(self, headers, keyword):
        sort_url = 'https://apidatav2.chinaz.com/single/baidupc/keywordranking'
        #真实地址：http://apidatav2.chinaz.com/single/baidupc/keywordranking?key=b761a081f5fb41af8bfcfb8ca642f1bf&domain=blflogo.com&keyword=金属标牌
        params = {
            "key": 'b761a081f5fb41af8bfcfb8ca642f1bf',
            'domain': 'blflogo.com',
            'keyword': keyword
        }
        try:
            response = requests.get(sort_url, params=params, headers=headers).text
            time.sleep(5)
            print('百度响应的内容是：', response)
            order_title = json.loads(response)
            order_sort = order_title['Result']['Ranks'][0]['RankStr']
            print(f"当前的关键字在百度排名第{order_sort.split('-')[0]}页，第{order_sort.split('-')[-1]}位")
            return order_sort.split('-')[0]
        except:
            print("通过API当前无法获取到该关键字页码，需要充值-----")
            return 0

    # 获取代理AGENT
    def get_headers(self):
        with open('package.json') as agent:
            USER_AGENTS = json.load(agent)['browsers']['chrome']
        headers = {
            "User-Agent": f"{random.choice(USER_AGENTS)}"
        }
        return headers

    # 获取当前的代理IP列表
    def get_proxy(self, headers, freePay=True):
        if freePay:
            self.i += 1
            # 使用免费IP
            print("当前使用免费IP-------")
            request = urllib.request.Request("https://www.kuaidaili.com/free/intr/" + str(self.i), headers=headers)
            #普通代理:https://www.kuaidaili.com/free/intr/ 高匿代理:https://www.kuaidaili.com/free/inha/
            html = urllib.request.urlopen(request).read()
            # 解析网页信息，从中提取代理 ip 的数据
            content = etree.HTML(html)
            ip = content.xpath('//td[@data-title="IP"]/text()')
            port = content.xpath('//td[@data-title="PORT"]/text()')
            # 将代理 ip 信息存入 proxyList 列表
            for i in ip:
                for p in port:
                    self.proxyList.append(i + ':' + p)
            return self.proxyList
        else:
            # 付费IP,URL参考格式'http://dps.kdlapi.com/api/getdps/?orderid=953240278749313&num=1&pt=1&dedup=1&format=json&sep=1'
            print("当前使用付费IP-------")
            content = requests.get(self.ip_pay_url, headers=headers).content
            proxydict = json.loads(content)
            try:
                proxy_List = proxydict['data']['proxy_list'][0]
                self.i += 1
                print("正在提取第{self.i}个IP")
                self.proxyList.append(proxy_List)
                print(f'代理列表是：{self.proxyList}')
                return random.choice(self.proxyList)
            except:
                return ["注意：此次是没有获取到代理的!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"]

    def run(self, baidu_driver, keyword, order_no):
        try:
            baidu_driver.get(f'https://www.baidu.com')
            baidu_driver.maximize_window()
            key_word = baidu_driver.find_element_by_xpath('//*[@id="kw"]')
            key_word.send_keys(keyword)
            search_word = baidu_driver.find_element_by_xpath('//*[@id="su"]')
            search_word.click()
            for page in range(1, 300):
                time.sleep(random.choice([0.01, 0.02]))
                baidu_driver.execute_script(f"document.documentElement.scrollTop={page * 10}")
            page_no = baidu_driver.find_element_by_xpath(f'//*[@id="page"]/div/a[{order_no}]/span')
            page_no.click()
            btn = baidu_driver.find_element_by_xpath('//a[text()="www.blflogo.com/"]')
            btn.send_keys(Keys.ENTER)
            time.sleep(5)
            # 切换窗口
            baidu_driver.switch_to.window(self.baidu_driver.window_handles[-1])
            tlist = ['首页', '不锈钢标牌', '电铸标牌', '酒标牌', '铝标牌', '行业案例', '新闻资讯', '联系我们', '电铸厚标', '镍片标牌']
            for title in range(1, 9):
                time.sleep(random.choice([3, 4, 5]))
                print(f'正在点击第{title}个控件..........')
                title_word = self.baidu_driver.find_element_by_xpath(f'//a[text()="{random.choice(tlist)}"]')
                title_word.click()
            baidu_driver.quit()
            self.used_proxyList.append(self.proxy)
            print(f"当前可用代理列表是:{self.used_proxyList},共{len(self.used_proxyList)}个")
        except NoSuchElementException:
            print('第{order_no}页没有找到该网站')
            # 翻页,点击下一页
            baidu_driver.find_element_by_xpath("//div[@id='page']//a[@class='n'][last()]").click()
        except WebDriverException:
            print('代理异常')
            baidu_driver.quit()
            time.sleep(random.choice([3, 4, 5]))

if __name__ == '__main__':
    while True:
        Baolifeng = BaolifengSpider()
        # 1、获取关键字
        keyword = random.choice(Baolifeng.key_word)
        print("当前关键字是：",keyword)
        # 2、获取代理AGENT
        headers = Baolifeng.get_headers()
        print("当前AGENT代理是：",headers)
        # 3、获取当前的代理IP列表
        proxy = random.choice(Baolifeng.get_proxy(headers, freePay=True))
        print("当前获取到的IP代理是：",proxy)
        # 4、获取当前关键字的百度排名
        order_no = Baolifeng.get_keyword_order(Baolifeng, keyword)
        # 5、获取浏览器驱动对象
        baidu_driver = Baolifeng.get_baidu_driver(proxy, headers)
        # 6、执行浏览器模拟事件
        Baolifeng.run(baidu_driver, keyword, order_no)
