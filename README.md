#searchSpiders
<h3>
scrapy crawl baiduSearch -a keyword="瓜皮 瓜皮猫" -a filters="瓜皮 猫 豆瓣" -a blackURLs="douban" -a whiteURLs="baidu" -a whiteWords="瓜皮岛 酱 西瓜 养生" -a limit=5
</h3><br>
<p style="color:red">
    1.每一个keyword里面的关键字，都会被搜索引擎独立搜索一次，然后分别被filters里面的关键字过滤一次，只有包涵该关键字的才会被接收<br>
    2.判断是否在url白名单里面，在就直接放弃<br>
    3.判断是否在url黑名单里面，在就直接收集<br>
    4.判断是否在关键字白名单里面，在就直接放弃<br>
</p>
<h3>百度,搜狗,好搜,神马</h3><br>
linux:   <br>       
    2015-10-17 16:08:12 [root] INFO: 现在有多少self.realURLs： 49 <br>       
    2015-10-17 16:08:12 [root] INFO: 现在有多少self.faceURLs： 100 <br>       
    2015-10-17 16:08:12 [root] INFO: 现在解析了多少页面： 10 <br>       
    2015-10-17 16:08:12 [root] INFO: limit是： 5 <br>       
windows： <br>
    2015-10-17 16:17:35 [root] INFO: 现在有多少self.realURLs： 49 <br>
    2015-10-17 16:17:35 [root] INFO: 现在有多少self.faceURLs： 100 <br>
    2015-10-17 16:17:35 [root] INFO: 现在解析了多少页面： 10 <br>
    2015-10-17 16:17:35 [root] INFO: limit是： 5 <br>