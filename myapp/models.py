from django.db import models


class User(models.Model):
    endptime = models.CharField('最后', max_length=128, default=0)
    profsite = models.CharField('主页', max_length=255, null=True)
    usravatr = models.CharField('头像', max_length=255, null=True)
    whatdoth = models.CharField('此刻', max_length=255, null=True)
    usersage = models.CharField('年龄', max_length=255, null=True)
    userback = models.CharField('封面', max_length=255, null=True)
    password = models.CharField('密码', max_length=255)

    niminswh = models.BooleanField('匿名', default=False)
    backswih = models.BooleanField('封面', default=False)

    location = models.TextField('位置', null=True)
    pointnum = models.IntegerField('积分', default=0, db_index=True)
    usrgrade = models.IntegerField('等级', default=0, db_index=True)
    recvmail = models.BooleanField('接收', default=False, db_index=True)
    activeml = models.BooleanField('激活', default=False, db_index=True)
    uaddress = models.GenericIPAddressField('地址', null=True, db_index=True)
    usermail = models.CharField('邮箱', max_length=255, unique=True, db_index=True)

    creatime = models.DateTimeField(auto_now_add=True, verbose_name='创建')
    urgender = models.CharField('性别', max_length=255, blank=True, null=True)
    nickname = models.CharField('编号', max_length=128, unique=True, null=True)

    class Meta:
        ordering = ['-creatime']
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.usermail


class Black(models.Model):
    uaddress = models.GenericIPAddressField('地址')
    bkreason = models.CharField('理由', max_length=255, null=True)
    endptime = models.DateTimeField(verbose_name='结束')
    creatime = models.DateTimeField(auto_now_add=True, verbose_name='创建')
    fuckuser = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户', blank=True, null=True)

    class Meta:
        ordering = ['-creatime']
        verbose_name = '黑单'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.bkreason


class Mtype(models.Model):
    typesort = models.IntegerField('排序', default=0, db_index=True)
    typename = models.CharField('名称', max_length=20, db_index=True)
    nickname = models.CharField('匿名', max_length=20, db_index=True)

    creatime = models.DateTimeField(auto_now_add=True, verbose_name='创建')
    typelogo = models.CharField('图片', max_length=255, blank=True, null=True)

    class Meta:
        ordering = ['typesort']
        verbose_name = '商类'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.typename


class MThread(models.Model):
    contents = models.TextField('描述')
    hidecont = models.TextField('隐藏', blank=True, null=True)
    howmanyp = models.IntegerField('人数', default=0, db_index=True)
    mktprice = models.IntegerField('价格', default=0, db_index=True)
    mktstock = models.IntegerField('库存', default=0, db_index=True)
    mketname = models.CharField('名称', max_length=255, db_index=True)
    creatime = models.DateTimeField(auto_now_add=True, verbose_name='创建')
    mketchat = models.CharField('联系', max_length=255, blank=True, null=True)
    attachmt = models.CharField('附件', max_length=255, blank=True, null=True)
    postuser = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    mkettype = models.ForeignKey(Mtype, on_delete=models.CASCADE, verbose_name='商类')

    class Meta:
        ordering = ['-creatime']
        verbose_name = '商品'
        verbose_name_plural = verbose_name


class Category(models.Model):
    typesort = models.IntegerField('排序', default=0, db_index=True)
    nickname = models.CharField('匿名', max_length=20, db_index=True)
    typename = models.CharField('类别', max_length=20, db_index=True)

    creatime = models.DateTimeField(auto_now_add=True, verbose_name='创建')

    class Meta:
        ordering = ['typesort']
        verbose_name = '类别'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.typename


class Thread(models.Model):
    contents = models.TextField('正文')
    attachmt = models.CharField('附件', max_length=255, blank=True, null=True)
    videourl = models.CharField('视频', max_length=255, blank=True, null=True)

    commnumb = models.IntegerField('评论', default=0, db_index=True)
    likenumb = models.IntegerField('喜欢', default=0, db_index=True)
    niminswh = models.BooleanField('匿名', default=False)

    updatime = models.DateTimeField(auto_now=True, verbose_name='更新')
    creatime = models.DateTimeField(auto_now_add=True, verbose_name='创建')
    thauthor = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='作者')
    thontype = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='类别')

    class Meta:
        ordering = ['-updatime']
        verbose_name = '线程'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.contents


class Comment(models.Model):
    contents = models.TextField('正文', default='')
    attachmt = models.CharField('附件', max_length=255, blank=True, null=True)

    parentid = models.IntegerField('父评', default=0, db_index=True)
    commfoor = models.IntegerField('楼层', default=1, db_index=True)
    likenumb = models.IntegerField('喜欢', default=0, db_index=True)
    niminswh = models.BooleanField('匿名', default=False)

    creatime = models.DateTimeField(auto_now_add=True, verbose_name='创建')
    cmauthor = models.ForeignKey(User, verbose_name='作者', on_delete=models.CASCADE, )
    cmthread = models.ForeignKey(Thread, verbose_name='线程', on_delete=models.CASCADE, )

    class Meta:
        ordering = ['-creatime']
        verbose_name = '评论'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.contents


class GoodSystem(models.Model):
    creatime = models.DateTimeField(auto_now_add=True, verbose_name='创建')

    gooduser = models.ForeignKey(User, verbose_name='用户', on_delete=models.CASCADE, )
    goodthed = models.ForeignKey(Thread, verbose_name='线程', on_delete=models.CASCADE, null=True)
    goodcomm = models.ForeignKey(Comment, verbose_name='评论', on_delete=models.CASCADE, null=True)

    class Meta:
        ordering = ['-creatime']
        verbose_name = '点赞'
        verbose_name_plural = verbose_name


class EmailActive(models.Model):
    creatime = models.DateTimeField(auto_now_add=True, verbose_name='创建')

    activecd = models.CharField('代码', max_length=255)
    endptime = models.CharField('最后', max_length=128, default=0)
    mailuser = models.ForeignKey(User, verbose_name='用户', on_delete=models.CASCADE, )

    class Meta:
        ordering = ['-creatime']
        verbose_name = '激活'
        verbose_name_plural = verbose_name


class PointSystem(models.Model):
    pointnum = models.IntegerField('点数', default=0, db_index=True)
    pointlat = models.IntegerField('余额', default=0, db_index=True)

    pointtyp = models.CharField('类型', max_length=128, blank=True, null=True, db_index=True)
    pointdes = models.CharField('描述', max_length=255, blank=True, null=True, db_index=True)

    pointusr = models.ForeignKey(User, verbose_name='用户', on_delete=models.CASCADE, )
    creatime = models.DateTimeField(auto_now_add=True, verbose_name='时间')

    class Meta:
        ordering = ['-creatime']
        verbose_name = '积分'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.pointtyp


class NotifySystem(models.Model):
    replymys = models.CharField('我的', max_length=128, db_index=True)
    isreaded = models.BooleanField('已读', default=False, db_index=True)
    creatime = models.DateTimeField(auto_now_add=True, verbose_name='创建')

    replyhes = models.ForeignKey(User, verbose_name='他的', on_delete=models.CASCADE, )
    replythd = models.ForeignKey(Thread, verbose_name='线程', on_delete=models.CASCADE, )
    replycom = models.ForeignKey(Comment, verbose_name='评论', on_delete=models.CASCADE, )

    class Meta:
        ordering = ['-creatime']
        verbose_name = '通知'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.replymys
