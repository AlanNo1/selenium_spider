import random
import requests
import json
from lxml import etree
from concurrent.futures import ThreadPoolExecutor
# 获取代理AGENT
def get_headers():
    agent_list = ['chrome', 'opera', 'firefox', 'internetexplorer']
    with open('package.json') as agent:
        USER_AGENTS = json.load(agent)['browsers'][random.choice(agent_list)]
    headers = {
        "User-Agent": f"{random.choice(USER_AGENTS)}"
    }
    return headers

#代理IP列表
proxyList =[]
# 获取当前的代理IP列表
def get_proxy(i,ip_pay_url):
    content = requests.get(ip_pay_url, headers=get_headers()).content
    proxydict = json.loads(content)
    try:
        proxy_List = proxydict['data']['proxy_list'][0]
        print("当前使用付费IP-------")
        print(f"正在提取第{i}个IP")
        proxyList.append(proxy_List)
        print(f'代理列表是：{proxyList}')
        return random.choice(proxyList)
    except:
        # 使用免费IP
        print("当前使用免费IP-------")
        print(f"正在提取第{i}个IP")
        try:
            request = requests.get("https://www.kuaidaili.com/free/inha/" + str(i), headers=get_headers()).content
            # 普通代理:https://www.kuaidaili.com/free/intr/ 高匿代理:https://www.kuaidaili.com/free/inha/
            # 解析网页信息，从中提取代理 ip 的数据
            content = etree.HTML(request)
            ip = content.xpath('//td[@data-title="IP"]/text()')
            port = content.xpath('//td[@data-title="PORT"]/text()')
            # 将代理 ip 信息存入 proxyList 列表
            for i in ip:
                for p in port:
                    proxyList.append(i + ':' + p)
            return random.choice(proxyList)
        except:
            print("当前没有获取到免费IP")

if __name__ == '__main__':
    # 使用线程池
    with ThreadPoolExecutor(50) as t:
        for i in range(1,100):
            t.submit(get_proxy,i,'http://dps.kdlapi.com/api/getdps/?orderid=953240278749313&num=1&pt=1&dedup=1&format=json&sep=1')
    print("代理IP列表：",proxyList,"长度：",len(proxyList))
