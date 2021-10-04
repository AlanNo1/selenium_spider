import random
import requests
import json
from lxml import etree
import asyncio
import time
import aiohttp
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
async def get_proxy(i,ip_pay_url):
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
            # await asyncio.sleep(10)#需要等待时加这句话
            # request = (await requests.get("https://www.kuaidaili.com/free/inha/" + str(i), headers=get_headers())).content
            async with aiohttp.ClientSession() as session:
                async with session.get("https://www.kuaidaili.com/free/inha/" + str(i), headers=get_headers()) as response:
                    request = await response.content.read()
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

async def main(url):
    task=[get_proxy(i,url) for i in range(1,10)]
    await asyncio.wait(task)

if __name__ == '__main__':
    curent_time= time.time()
    # 使用协程
    #方法一：建议使用
    # asyncio.run(main(url='http://dps.kdlapi.com/api/getdps/?orderid=953240278749313&num=1&pt=1&dedup=1&format=json&sep=1'))
    #方法二：方法一运行报错使用
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(url='http://dps.kdlapi.com/api/getdps/?orderid=953240278749313&num=1&pt=1&dedup=1&format=json&sep=1'))
    print("耗时：",time.time()-curent_time)
