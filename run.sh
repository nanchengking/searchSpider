#!/usr/bin/env bash
echo "===运行Spider==="
scrapy crawl haosouSearch -a keyword="瓜皮 瓜皮猫" -a filters="瓜皮 猫 豆瓣" -a blackURLs="douban" -a whiteURLs="baidu" -a whiteWords="瓜皮岛 酱 西瓜 养生" -a limit=5
echo "===运行结束，按回车退出运行==="
read a