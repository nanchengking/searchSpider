#searchSpiders
<h3>
scrapy crawl baiduSearch -a keyword="瓜皮,瓜皮猫" -a filters="瓜皮猫,豆瓣,可爱,贱,女神" -a blackURLs="douban" -a whiteURLs="baidu" -a whiteWords="瓜皮岛,酱,西瓜,养生" -a limit=5
</h3><br>
<h3>百度,搜狗,好搜,神马</h3><br>
<h4>
搜索引擎的搜索工作流程
</h4>
<p style="color:red">
    1.每一个keyword里面的关键字，都会被搜索引擎独立搜索一次，<br>
    然后分别被filters里面的关键字过滤一次，只有包涵该关键字的才会被接收<br>
    2.判断是否在url白名单里面，在就直接放弃<br>
    3.判断是否在url黑名单里面，在就直接收集<br>
    4.判断是否在关键字白名单里面，在就直接放弃<br>
    5.搜集到的数据直接存入mysql数据库<br>
</p>

<h3>
scrapy crawl baiduMusicSearch -a keyword="国际歌,国际歌 唐朝" -a name="国际歌" -a author="唐朝" -a limit=5
</h3><br>
<h3>百度音乐、虾米音乐、天天动听、酷狗音乐、酷我音乐、网易云音乐</h3><br>
<h4>
音乐搜索的搜索工作流程
</h4>
<p style="color:red">
    1.每一个keyword里面的关键字，都会被搜索引擎独立搜索一次，<br>
    2.每一条搜索结果如下判断：<br>
    a.标题包含歌曲名称，作者包含过滤作者<br>
    b.或者，标题中包含歌曲名字和作者<br>
    3.不同关键字的搜索都存在去重操作，避免不同关键字爬取到相同结果<br>
    4.搜集到的数据直接存入mysql数据库<br>
</p>

<h4>关键字之间的分隔符在setting里面统一设置SPLIT_SIGN=','</h4><br>
<h4>

  建表语句： <br>
  
  CREATE TABLE if not exists web_searchspider_results (<br>
   id int(11) PRIMARY KEY AUTO_INCREMENT,<br>
  platform varchar(20) references web_platform(name), <br>
  keyword varchar(50) NOT NULL,<br>
  resultUrl varchar(500) DEFAULT NULL,<br>
  targetUrl varchar(500) NOT NULL,<br>
  targetTitle varchar(500) DEFAULT NULL,<br>
  username varchar(100) DEFAULT NULL,<br>
  fetchCode varchar(10) DEFAULT NULL,<br>
  createDate date NOT NULL,<br>
  searchTask_id int(11) references web_searchtask(id),<br>
  status int(11) NOT NULL,<br>
  processDate datetime DEFAULT NULL,<br>
  project_id int(11) references web_project(id),<br>
  checkStatus int(11) DEFAULT NULL<br>
); <br>
</h4>
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