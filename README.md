<h1 align="center">Welcome to Pixiu 👋</h1>

> 基于Django和Asyncio的RSS阅读器。  
> RSS reader based on Django and asyncio.

## 概览 Overview

- 前端（还没开始写）：[Pixiu-FE](https://github.com/40huo/pixiu-fe.git)
- 后端：[Pixiu](https://github.com/40huo/pixiu.git)

---

- Frontend (Not started yet): [Pixiu-FE](https://github.com/40huo/pixiu-fe.git)
- Backend: [Pixiu](https://github.com/40huo/pixiu.git)

## 背景及意义 Introduction

RSS作为上一个资讯阅读领域的热点技术，在21世纪的今天已经举步维艰，除了少数技术社区和博客，绝大部分有价值的资讯、文章都散布于各色各样的论坛、微信公众号等小圈子当中，给日常的阅读带来了非常多的不便。

因此，「智能」RSS技术应运而生，其中具有代表性的服务有Feed43、RSSHub等，此类服务能自行抓取不提供RSS源的站点文章内容，生成新的RSS XML文件供各类RSS阅读器使用。

本项目也是「智能」RSS技术的一种，相较于其他类似服务，本项目的优势在于

- 没什么优势
- 文章内容落盘存储
- 抓取插件高度自定义（因为需要自己写）

在本项目启动之初，Feed43在国内的访问速度不理想，RSSHub项目的关注度还较低，但由于种种原因，本项目的开发一度停滞，直到2019年初才完成了基础功能的开发，作为一个「智能」RSS项目，功能上的独创性和先进性已经不足，但仍是一个有独特场景的Python后端项目。

## 技术路线 Technical Roadmap

本项目基于Django Web框架开发，由Django REST Framework提供REST API服务，由 `django-environ` 提供配置分离功能。爬虫部分基于Asyncio和aiohttp，在保证爬取效率的同时尽量减少资源消耗。

进程管理推荐使用Systemd，日志收集使用Sentry（Sentry真的神器）。

Web后端启动后只有API功能，爬虫需要启动独立进程，与API交互获取任务相关信息，结果存储也通过API完成。

## 安装与使用 Installation and Usage

等开源了再说。

## 样例 Example

也是目前仅有的两个订阅源。

- [喷嚏图卦](https://pixiu.40huo.cn/rss/喷嚏图卦/)
- [暗网交易市场——数据版](https://pixiu.40huo.cn/rss/暗网交易市场/)

## 作者 Author

👤 **40huo**

* Twitter: [@40huo](https://twitter.com/40huo)
* Github: [@40huo](https://github.com/40huo)

## 支持 Show your support

Give a ⭐️ if this project helped you!