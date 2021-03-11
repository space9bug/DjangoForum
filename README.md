![](https://pic.4nmb.com/images/2021/03/10/QQ20210311094441.png)

这是一个由本人用Django框架开发的一款社区论坛（[市肥宅中心](https://www.4nmb.com)），**目前在web端、app端、微信小程序端、qq小程序端均已上线**。

部署遇到的任何问题都可以在社区提出或者邮件联系，或者提issue。

**代码中涉及到百度内容审核API（需要自己申请），邮件发送功能（需要自己在utils.py设置邮箱密码），黑名单验证，网站seo（settings.py）等需要自己填写。**

**技术支持**

*   python3.7.5
*   django3.0.6
*   nginx1.8.0
*   宝塔
*   uniapp

**说明一下该社区目前拥有的功能**

*   注册（邮箱激活）、登录功能
*   发帖、回复、艾特回复、楼层功能
*   发帖支持发送 文章格式（markdown）、视频、mp3音乐、图文、bilibili视频
*   积分系统功能，支持每日签到、发帖获取积分、评论获取积分、积分记录查看
*   个人中心功能，可以编辑自己的社交资料，上传头像和封面图片
*   地理位置获取功能、个人资料页面可显示所在的位置（百度地图提供）
*   排行榜功能，目前支持积分排行榜
*   pixiv插画瀑布流功能
*   消息通知功能，回复有邮件通知，能在消息系统看到
*   地理位置开启和关闭功能
*   统计功能、统计爬虫日志、统计注册人数等等
*   在线人数功能
*   商品交易系统，支持发布商品，购买商品，积分充值
*   小工具功能，可以自行开发小工具添加到工具界面
*   在线聊天室功能
*   帖子搜索功能
*   黑名单功能（自动拦截恶意注册）
*   内容审核功能（百度AI审核）
*   简单支持SEO
*   待开发（目前还有找回密码等功能未实现）

**目前的缺点**

*   发帖编辑器需要优化
*   没有找回密码功能
*   消息通知需要优化
*   等等

目前暂时就这些，**这里说明一下（咱代码写的并不是很规范，有些地方功能虽实现了，但代码你懂得。。开源一方面就是希望有小伙伴能共同维护）。**

**Demo**

*   [市肥宅中心](https://www.4nmb.com)

下面上各端的截图。

**web端（适配wap）**

排行榜界面

![](https://pic.4nmb.com/images/2021/03/10/QQ20210311095456.png)

统计界面

![](https://pic.4nmb.com/images/2021/03/10/QQ20210311095537.png)

个人中心界面

![](https://pic.4nmb.com/images/2021/03/10/QQ20210311095702.png)

**手机端（app）、qq小程序、微信小程序**

![](https://pic.4nmb.com/images/2021/03/10/Screenshot_2021-03-11-09-58-50-902_uni.UNIFBE7FCE.jpg)

左侧菜单栏

![](https://pic.4nmb.com/images/2021/03/10/Screenshot_2021-03-11-09-59-49-623_uni.UNIFBE7FCE.jpg)

个人中心

![](https://pic.4nmb.com/images/2021/03/10/Screenshot_2021-03-11-09-59-54-068_uni.UNIFBE7FCE.jpg)

![](https://pic.4nmb.com/images/2021/03/10/Screenshot_2021-03-11-09-59-58-116_uni.UNIFBE7FCE.jpg)

**简单的说一下部署方法**

<div>1、安装虚拟环境</div>

> <div>python -m venv ./venv</div>
> 
> <div>切换到虚拟环境</div>
> 
> <div>pip install -r&nbsp;requirements.txt</div>

<div>2、安装数据库（需要在settings.py配置数据库账号密码）</div>

> <div>python manage.py makemigrations</div>
> 
> <div>python manage.py migrate</div>
> 
> <div>python manage.py makemigrations myapp</div>
> 
> <div>python manage.py migrate myapp</div>
> 
> <div>python manage.py createsupuser 创建管理员</div>

<div>3、启动服务</div>

> <div>python manage.py runserver</div>

<div>启动服务后登陆 /admin 后台添加几个分类，然后注册一个账号测试一下发布帖子。部署后的界面应该是这样的。</div>

<div>&nbsp;</div>

<div>![](https://pic.4nmb.com/images/2021/03/10/QQ20210311105436.png)</div>

<div>&nbsp;</div>

<div>**开源不易，如果觉得这个开源程序不错的话欢迎大家捐赠！**</div>

<div>微信</div>

<div>![](https://cdn.jsdelivr.net/gh/xyuansec/4nmb_com@master/static/images/wx.png)</div>

<div>&nbsp;</div>

<div>支付宝</div>

<div>![](https://cdn.jsdelivr.net/gh/xyuansec/4nmb_com@master/static/images/zfb.jpg)</div>