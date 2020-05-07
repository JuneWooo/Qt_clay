import requests
from lxml import html
import time


# 获取页面选择器
def get_selector(url):
    resp = requests.get(url).content
    selector = html.fromstring(resp)

    return selector


# 获取首页url
def get_index_url(url, selector):
    important_notice_url = selector.xpath("/html/body/main/div/section[1]/section[1]/ul/li[1]/a/@href")[0]
    important_notice_url = important_notice_url.replace('/hc/zh-cn', '')
    urls = url + important_notice_url

    # 获取子页中的url链接
    resp1 = requests.get(urls).content
    selector1 = html.fromstring(resp1)
    allinfo_urls = selector1.xpath('//*[@id="main-content"]/section[1]/h2/a/@href')[0].replace('/hc/zh-cn', '')
    allinfo_urls = url + allinfo_urls

    return allinfo_urls


# 获取子页url列表
def get_info_index(allinfo_urls, selector):
    info_list = []
    new_url = allinfo_urls.split("/hc")[0]
    li = selector.xpath('//*[@id="main-content"]/ul/li/a/@href')
    # 获取信息
    for i in li:
        i = new_url + i
        info_list.append(i)

    return info_list


def get_info(url, selector):
    info_dict = {
        'title': '',
        'date': '',
        'url': ''
    }
    title = selector.xpath('//*[@id="main-content"]/header/h1/text()')[0]
    date = selector.xpath('//*[@id="main-content"]/section/div/div[1]/p[last()]/text()[last()]')[0]
    info_dict['title'] = title.strip()
    info_dict['date'] = date.strip()
    info_dict['url'] = url
    return info_dict


if __name__ == '__main__':
    url = "https://tokenbetter.zendesk.com/hc/zh-cn"
    allinfo_urls = get_index_url(url, get_selector(url))
    info_list = get_info_index(allinfo_urls, get_selector(allinfo_urls))
    try:
        for i in info_list:
            selector = get_selector(i)
            # 解析数据
            info_dict = get_info(i, selector)
            # 导出文本
            with open('tokenbetter.txt', 'a', encoding='utf-8') as f:
                f.write(str(info_dict) + "\n")
            time.sleep(0.5)
    except Exception as e:
        print("Something error, Please retry later!")


