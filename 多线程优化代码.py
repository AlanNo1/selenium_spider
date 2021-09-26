# coding:utf-8
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from lxml import etree
import random
from selenium.common.exceptions import WebDriverException
import requests
import json
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from threading import Thread


class BaolifengSpider(Thread):
    # 初始化参数
    def __init__(self, tname, ip_pay_url):
        super().__init__()
        self.i = 0  # 提取代理个数
        self.proxyList = []  # 代理列表
        self.used_proxyList = []  # 使用的代理列表
        self.url = 'www.blflogo.com'  # 搜索的网站地址
        self.key_word = ['不锈钢标牌', '金属标牌']  # 搜索的关键字
        self.title = ['不锈钢标牌', '电铸标牌', '酒标牌', '铝标牌', '行业案例', '新闻资讯', '联系我们']  # 需要点击的标签
        self.tname = tname  # 线程名
        self.ip_pay_url = ip_pay_url

    # 获取浏览器驱动
    def get_baidu_driver(self, proxy, headers, Ifdup=True, IfShowHeaders=True):
        """Ifdup:是否去重IP"""
        while Ifdup:
            # 代理去重
            if proxy in self.used_proxyList:
                try:
                    proxy = random.choice(self.proxyList)
                except:
                    print('没有获取到代理')
                    return
            else:
                break
        print("当前使用的代理IP是：", proxy)
        option = Options()
        if IfShowHeaders:
            print("当前浏览器页面为有界面浏览器")
        else:
            # 无头模式
            option.add_argument('--headless')
            option.add_argument('--no-sandbox')
            option.add_argument('--disable-dev-shm-usage')
            option.add_argument('--disable-gpu')
            print("当前浏览器页面为无界面浏览器")
        # 设置参数
        option.add_argument(f'--user-agent={headers["User-Agent"]}')
        option.add_argument(f'--proxy-server={proxy}')
        baidu_driver = webdriver.Chrome(options=option)
        baidu_driver.implicitly_wait(10)
        baidu_driver.delete_all_cookies()
        return baidu_driver

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
            try:
                request = requests.get("https://www.kuaidaili.com/free/inha/" + str(self.i), headers=headers).content
                # 普通代理:https://www.kuaidaili.com/free/intr/ 高匿代理:https://www.kuaidaili.com/free/inha/
                # 解析网页信息，从中提取代理 ip 的数据
                content = etree.HTML(request)
                ip = content.xpath('//td[@data-title="IP"]/text()')
                port = content.xpath('//td[@data-title="PORT"]/text()')
                # 将代理 ip 信息存入 proxyList 列表
                for i in ip:
                    for p in port:
                        self.proxyList.append(i + ':' + p)
                return random.choice(self.proxyList)
            except:
                return ["注意：此次是没有获取到免费代理的!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"]
        else:
            # 付费IP,URL参考格式'http://dps.kdlapi.com/api/getdps/?orderid=953240278749313&num=1&pt=1&dedup=1&format=json&sep=1'
            print("当前使用付费IP-------")
            content = requests.get(self.ip_pay_url, headers=headers).content
            proxydict = json.loads(content)
            try:
                proxy_List = proxydict['data']['proxy_list'][0]
                self.i += 1
                print(f"正在提取第{self.i}个IP")
                self.proxyList.append(proxy_List)
                print(f'代理列表是：{self.proxyList}')
                return random.choice(self.proxyList)
            except:
                return ["注意：此次是没有获取到付费代理的!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"]

    # 执行浏览器事件
    def run(self):
        while True:
            print(f'线程{self.tname}启动中')
            # 1、获取关键字
            keyword = random.choice(self.key_word)
            print("当前关键字是：", keyword)
            # 2、获取代理AGENT
            headers = self.get_headers()
            print("当前AGENT代理是：", headers)
            # 3、获取当前的代理IP列表
            proxy = self.get_proxy(headers, freePay=True)
            print("当前获取到的IP代理是：", proxy)
            # 4、获取当前关键字的百度排名
            # order_no = self.get_keyword_order(Baolifeng, keyword)
            order_no = 0  # 默认排第一页
            # 5、获取浏览器驱动对象
            baidu_driver = self.get_baidu_driver(proxy, headers)
            try:
                # 打开浏览器并最大化
                baidu_driver.get('https://www.baidu.com')
                time.sleep(20)
                baidu_driver.maximize_window()
                baidu_driver.refresh()
                # 1、设置每页搜索50条数据的方法------
                element = WebDriverWait(baidu_driver, 30).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="s-usersetting-top"]')))
                # 把鼠标移动到设置上
                ActionChains(baidu_driver).move_to_element(element).perform()
                time.sleep(2)
                # 获取下拉菜单中的“搜索设置”
                setting_btn = baidu_driver.find_element_by_xpath('//*[@id="s-user-setting-menu"]//a[@class="setpref"]')
                setting_btn.click()
                time.sleep(2)
                # 选择每页为50条
                nr = baidu_driver.find_element_by_xpath('//*[@id="se-setting-3"]/span[3]/label')
                nr.click()
                time.sleep(2)
                # 保存设置
                nr_save = baidu_driver.find_element_by_xpath(
                    '//a[@class="prefpanelgo setting-btn c-btn c-btn-primary"]')
                nr_save.click()
                time.sleep(2)
                baidu_driver.switch_to.alert.accept()
                time.sleep(2)

                # 2、开始执行搜索事件- -----
                key_word = baidu_driver.find_element_by_xpath('//*[@id="kw"]')
                time.sleep(2)
                key_word.send_keys(keyword)
                search_word = baidu_driver.find_element_by_xpath('//*[@id="su"]')
                search_word.click()
                btn = baidu_driver.find_element_by_xpath('//a[text()="www.blflogo.com/"]')
                baidu_driver.execute_script("arguments[0].scrollIntoView();", btn)
                time.sleep(2)
                btn.send_keys(Keys.ENTER)
                time.sleep(5)
                tlist = []
                # 切换窗口
                baidu_driver.switch_to.window(baidu_driver.window_handles[-1])
                for i in range(1, 7):
                    title_name = random.choice(self.title)
                    while True:
                        if title_name in tlist:
                            title_name = random.choice(self.title)
                        else:
                            tlist.append(title_name)
                            break
                    title_word = baidu_driver.find_element_by_xpath(f'//a[text()="{title_name}"]')
                    title_word.click()
                    time.sleep(random.choice([3, 4, 5]))
                    for page in range(1, 280):
                        time.sleep(random.choice([0.01, 0.02]))
                        baidu_driver.execute_script(f"document.documentElement.scrollTop={page * 10}")
                    print(f'正在点击首页标签{title_name}----->的第{i}个子标签')
                    title_item = baidu_driver.find_element_by_xpath(
                        f'//*[@class="widget widget_tag_cloud"]//ul/li[{random.choice(range(1, 13))}]/a')
                    title_item.send_keys(Keys.ENTER)
                    time.sleep(random.choice([1, 2]))
                    print('正在点击子标签的三级页面')
                    title_item = baidu_driver.find_element_by_xpath(
                        '//div[@class="entry-item fadeInUp animated"][1]//a')
                    title_item.send_keys(Keys.ENTER)
                    time.sleep(random.choice([1, 2]))
                baidu_driver.quit()
                self.used_proxyList.append(proxy)
                print(f"当前可用代理列表是:{self.used_proxyList},共{len(self.used_proxyList)}个")
            except NoSuchElementException:
                print(f'第{order_no + 1}页没有找到该网站')
                baidu_driver.quit()
                time.sleep(random.choice([3, 4, 5]))
                # 翻页,点击下一页
                # baidu_driver.find_element_by_xpath("//div[@id='page']//a[@class='n'][last()]").click()
            except WebDriverException:
                print('代理异常')
                baidu_driver.quit()
                time.sleep(random.choice([3, 4, 5]))

if __name__ == '__main__':
    ip_pay_url = input("请输入快代理的提取API链接：")
    for i in range(1, 8):  # 使用多进程开启7个浏览器
        t = BaolifengSpider(i, ip_pay_url)  # 创建线程，并传递参数
        t.start()
        time.sleep(5)
