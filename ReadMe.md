# VophanEngine

> 一个智能化的垂直搜索引擎的高可用解决方案

## language

- python
- golang

## Feature

- 多种子链接爬取
- url去重
- 内容去重
- 基于主题词库的主题判别模型
- PageRank链接预测做任务调度
- 基于文本密度的正文抽取
- 导航页与正文页的智能辨别
- websocket 长连接导入elasticsearch
- 功能完善的backend，实现了长连接数据导入，数据增删改查，用户权限认证，用户数据存储，搜索可视化。

## implement

- redis：实现url和content去重
- mongo：实现内容存储
- elasticsearch：实现内容索引与存储
- elastichd: 实现es可视化监控



To be continued....
