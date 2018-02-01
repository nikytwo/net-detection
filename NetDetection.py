#!/usr/bin/python
# -*- coding: UTF-8 -*-
import csv
import datetime
import os
import pycurl
import re
import subprocess
import sys
import time
import urllib
import ConfigParser

from bs4 import BeautifulSoup

# set the default encoding to utf-8
# reload sys model to enable the getdefaultencoding method.
reload(sys)
# using exec to set the encoding, to avoid error in IDE.
exec "sys.setdefaultencoding('utf-8')"
assert sys.getdefaultencoding().lower() == "utf-8"

# 加载配置
config = ConfigParser.ConfigParser()
config.read("app.conf")
try:
    items = config.items("ips")
    ip_list = []
    for k, v in items:
        ip_list.append(v)
except:
    ip_list = ["www.baidu.com", "www.wenweipo.com"]

try:
    items = config.items("urls")
    url_list = []
    for k, v in items:
        url_list.append(v)
except:
    url_list = [
        "http://oss-cn-foshan.midea.com:17480/userDownload/F6678E6FD4054150BA37521FBA8A67A6/test-tsp/test.pdf?certification=v1991c2edb40af2c01df803ba16757d42aec"
    ]

def get_info():
    cmd = 'ipconfig /all'
    p = subprocess.Popen(cmd,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         shell=True
                         )
    out = p.stdout.read().decode('gbk')

    print out

    return out


def get_outside_ip():
    html = urllib.urlopen("http://2017.ip138.com/ic.asp").read()
    soup = BeautifulSoup(html, "html.parser")
    txt = soup.body.center.string
    print txt
    return txt


def test_ping(domain):
    cmd = 'ping %s' % domain
    p = subprocess.Popen(cmd,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         shell=True
                         )
    out = p.stdout.read().decode('gbk')

    # Pinging www.a.shifen.com [115.239.211.112] with 32 bytes of data
    reg_ip = u'\d+\.\d+\.\d+\.\d+'
    # Packets: Sent = 4, Received = 4, Lost = 0 (0% loss)
    # 数据包: 已发送 = 4，已接收 = 4，丢失 = 0 (0% 丢失)，
    reg_lost = u'\(\d+%'
    # Minimum = 37ms, Maximum = 38ms, Average = 37ms
    # 最短 = 37ms，最长 = 77ms，平均 = 48ms
    reg_minimum = u'Minimum = \d+ms|最短 = \d+ms'
    reg_maximum = u'Maximum = \d+ms|最长 = \d+ms'
    reg_average = u'Average = \d+ms|平均 = \d+ms'
    ip = re.search(reg_ip, out)
    lost = re.search(reg_lost, out)
    minimum = re.search(reg_minimum, out)
    maximum = re.search(reg_maximum, out)
    average = re.search(reg_average, out)
    if ip:
        ip = ip.group()[0:]
    if lost:
        lost = lost.group()[1:]
    if lost is None:
        lost = '100%'
    if minimum:
        minimum = filter(lambda x: x.isdigit(), minimum.group())
    if maximum:
        maximum = filter(lambda x: x.isdigit(), maximum.group())
    if average:
        average = filter(lambda x: x.isdigit(), average.group())

    now_time = datetime.datetime.now()

    print ""
    print 'ping %s' % domain
    print 'ip: %s' % ip
    print 'lost: %s ms' % lost
    print 'minimum time: %s ms' % minimum
    print 'maximum time: %s ms' % maximum
    print "average time: %s ms" % average
    print "now: %s" % now_time.strftime('%Y-%m-%d %H:%M:%S')

    return domain, ip, lost, minimum, maximum, average, now_time.strftime('%Y-%m-%d %H:%M:%S')


def body_callback(buf):
    pass


def test_download(url):
    c = pycurl.Curl()
    c.setopt(pycurl.WRITEFUNCTION, body_callback)
    c.setopt(pycurl.SSL_VERIFYPEER, 0)
    c.setopt(pycurl.SSL_VERIFYHOST, 0)
    c.setopt(pycurl.URL, url)
    c.setopt(pycurl.MAXREDIRS, 5)
    c.perform()

    http_code = c.getinfo(pycurl.HTTP_CODE)
    dns_resolve = c.getinfo(pycurl.NAMELOOKUP_TIME) * 1000
    http_conn_time = c.getinfo(pycurl.CONNECT_TIME) * 1000
    http_pre_trans = c.getinfo(pycurl.PRETRANSFER_TIME) * 1000
    http_start_trans = c.getinfo(pycurl.STARTTRANSFER_TIME) * 1000
    http_total_time = c.getinfo(pycurl.TOTAL_TIME) * 1000
    http_size_download = c.getinfo(pycurl.SIZE_DOWNLOAD) / 1024
    http_header_size = c.getinfo(pycurl.HEADER_SIZE)
    http_speed_downlaod = c.getinfo(pycurl.SPEED_DOWNLOAD) / 1024

    now_time = datetime.datetime.now()

    print ""
    print 'download: %s' % url
    print 'HTTP code: %d' % http_code
    print 'DNS resolve time: %.2f ms' % dns_resolve
    print 'connect time: %.2f ms' % http_conn_time
    print 'pre transfer time: %.2f ms' % http_pre_trans
    print "start transfer time: %.2f ms" % http_start_trans
    print "total time: %.2f ms" % http_total_time
    print "package size: %d kb" % http_size_download
    print "HTTP header size: %d byte" % http_header_size
    print "avg download speed: %d k/s" % http_speed_downlaod
    print "now: %s" % now_time.strftime('%Y-%m-%d %H:%M:%S')

    return (http_code, dns_resolve, http_conn_time, http_pre_trans, http_start_trans, http_total_time,
            http_size_download, http_header_size, http_speed_downlaod, now_time.strftime('%Y-%m-%d %H:%M:%S'), url)


def test():
    if not os.path.exists('report'):
        os.mkdir('report')
    if not os.path.exists('report/ping.csv'):
        with open('report/ping.csv', 'ab') as f:
            writer = csv.writer(f)
            writer.writerow(["domain", "ip", "lost(%)", "min(ms)", "max(ms)", "avg(ms)", "time"])
    if not os.path.exists('report/download.csv'):
        with open('report/download.csv', 'ab') as f:
            writer = csv.writer(f)
            writer.writerow(["code", "dns(ms)", "connect(ms)", "preTrans(ms)", "startTrans(ms)", "total(ms)",
                             "size(kb)", "header(byte)", "speed(kb/s)", "time", "url"])

    with open('report/ping.csv', 'ab') as f:
        writer = csv.writer(f)
        for ip in ip_list:
            rst = test_ping(ip)
            writer.writerow(rst)

    with open('report/download.csv', 'ab') as f:
        writer = csv.writer(f)
        for url in url_list:
            info = test_download(url)
            writer.writerow(info)

    time.sleep(300)


if __name__ == "__main__":

    try:
        if not os.path.exists('report'):
            os.mkdir('report')

        outside_ip = get_outside_ip()
        net_info = get_info()
        output = open('report/info.txt', 'w+')
        output.write(outside_ip)
        output.write(net_info)
        output.close()
    except Exception as ex:
        print ex

    for n in range(120):
        try:
            test()
        except Exception as ex:
            print ex
