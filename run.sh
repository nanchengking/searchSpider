#!/usr/bin/env bash
echo "===运行Spider==="
scrapy crawl haosouSearch -a keyword="瓜皮,瓜皮猫" -a filters="猫,豆瓣,可爱，贱" -a blackURLs="douban" -a whiteURLs="baidu" -a whiteWords="瓜皮" -a limit=10
echo "===运行结束，按回车退出运行==="
read a