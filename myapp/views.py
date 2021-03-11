import re
import urllib
import markdown
from urllib import parse
from common.utils import *
from myapp.models import *
from itertools import chain
from bs4 import BeautifulSoup
from django.db.models import Q
from operator import attrgetter
from urllib.parse import unquote
from django.shortcuts import render
from django.core.cache import cache
from geopy.distance import geodesic
from django.utils.html import strip_tags
from ehaforum.settings import WEB_CONFIG
from django.core.validators import URLValidator
from django.http import HttpResponseRedirect, HttpResponse


def global_data(request):
    issign = False
    isreaded = None
    user = request.session.get('user', None)
    if user:
        user = User.objects.get(usermail=user)
        if user.location:
            user.location = json.loads(user.location.replace("'", '"'))
        isreaded = getisreaded(user.usermail)
        issign = todayissign(user)

    categorys = Category.objects.all().order_by('typesort')

    return {
        'user': user,
        'issign': issign,
        'isreaded': isreaded,
        'categorys': categorys,
        'web_config': WEB_CONFIG,
        'tops': forum_get_tops(),
        'bests': forum_get_bests(),
        'online': get_online_count(),
        'logs': forum_get_activelog(),
        'creates': forum_get_creates(),
        'signtops': forum_get_signtops(),
    }


def get_online_count():
    online_ips = cache.get("online_ips", [])
    if online_ips:
        online_ips = cache.get_many(online_ips).keys()
        return len(online_ips)
    return 0


def balance(request):
    renderdata = global_data(request)
    renderdata['curnav'] = 'balance'
    ranks = User.objects.all().order_by("-pointnum")[0:20]
    renderdata['objs'] = ranks
    return render(request, 'site/balance.html', renderdata)


def todaypoint(request):
    renderdata = global_data(request)
    renderdata['curnav'] = 'index'
    signusers = get_signtops()
    renderdata['objs'] = signusers
    return render(request, 'site/todaypoint.html', renderdata)


def tools(request):
    renderdata = global_data(request)
    renderdata['curnav'] = 'tools'
    return render(request, 'tools/index.html', renderdata)


def statistic(request):
    renderdata = global_data(request)
    renderdata['curnav'] = 'statistic'
    renderdata['register_count'] = User.objects.all().count()
    renderdata['thread_count'] = Thread.objects.all().count()
    renderdata['comment_count'] = Comment.objects.all().count()
    renderdata['good_count'] = GoodSystem.objects.all().count()
    renderdata['category_count'] = Category.objects.all().count()
    return render(request, 'site/statistic.html', renderdata)


def market(request):
    renderdata = global_data(request)
    renderdata['curnav'] = 'market'
    mtypes = Mtype.objects.all().order_by('typesort')
    mthreads = MThread.objects.all().order_by('-creatime')
    mthreads, paginator = getdjangopage(request, mthreads)
    renderdata['mtypes'] = mtypes
    renderdata['mthreads'] = mthreads
    renderdata['paginator'] = paginator
    return render(request, 'market/index.html', renderdata)


def marketdetail(request, id):
    renderdata = global_data(request)
    renderdata['curnav'] = 'market'
    market = MThread.objects.get(id=int(id))
    market.attachmt_source = \
        market.attachmt.split(".")[0] + "_source." + market.attachmt.split(".")[1]

    markdown_content = strip_tags(market.contents.replace("\u200b", ""))
    markdown_hidcont = strip_tags(market.hidecont.replace("\u200b", ""))

    ismypayed = False
    if renderdata['user']:
        pointsys = PointSystem.objects.filter(pointtyp="商品交易")
        for point in pointsys:
            if point.pointusr == renderdata['user'] and \
                    "您购买了某商品(id=" + str(id) + ")" == point.pointdes:
                ismypayed = True
                break
    renderdata['ismypayed'] = ismypayed

    market.contents = markdown.markdown(
        markdown_content,
        extensions=['markdown.extensions.extra', 'markdown.extensions.codehilite', ]
    )
    market.hidecont = markdown.markdown(
        markdown_hidcont,
        extensions=['markdown.extensions.extra', 'markdown.extensions.codehilite', ]
    )
    renderdata['market'] = market
    return render(request, 'market/detail.html', renderdata)


def pbmarket(request):
    renderdata = global_data(request)
    renderdata['curnav'] = 'market'
    mtypes = Mtype.objects.all().order_by('typesort')
    renderdata['mtypes'] = mtypes

    if renderdata['user'] and request.method == 'POST':
        try:
            mktitle = request.POST.get("mktitle", None)
            mkcatgr = request.POST.get("mkcatgr", None)
            mkprice = request.POST.get("mkprice", None)
            mkstock = request.POST.get("mkstock", None)
            mkdescp = request.POST.get("mkdescp", None)
            mkhiden = request.POST.get("mkhiden", None)
            mkconct = request.POST.get("mkconct", None)
            mkphoto = request.FILES.get("mkphoto", None)

            thauthor = renderdata['user']
            if not thauthor.activeml:
                raise RuntimeError('请先到个人主页激活邮箱！')

            mktitle = mktitle.strip()
            if len(mktitle) < 5 or len(mktitle) > 60:
                raise RuntimeError("商品标题请填写5到60个字符之间!")

            if int(mkprice) < 0 or int(mkprice) > 999:
                raise RuntimeError("商品价格请填写0到999肥宅币之间!")

            if int(mkstock) < 0 or int(mkstock) > 999:
                raise RuntimeError("商品数量请填写0到999个之间!")

            if (int(time.time()) - int(thauthor.endptime)) < 10:
                raise RuntimeError('发布间隔10秒，请稍后再发布！')

            thauthor.endptime = str(int(time.time()))
            thauthor.save()

            if mkphoto:
                result_obj = uploadtoserver(mkphoto)
                if result_obj["code"] == 0:
                    raise RuntimeError(result_obj["msg"])
            else:
                raise RuntimeError("请选择一张商品的封面图片!")

            thauthor.endptime = str(int(time.time()))
            thauthor.save()

            mkcatgr = Mtype.objects.get(nickname=mkcatgr)
            mkthread = MThread.objects.create(
                mketname=mktitle,
                contents=mkdescp,
                hidecont=mkhiden,
                mktprice=int(mkprice),
                mktstock=int(mkstock),
                mketchat=mkconct,
                attachmt=result_obj["msg"],
                mkettype=mkcatgr,
                postuser=thauthor)

            return HttpResponseRedirect('/market/' + str(mkthread.id))
        except Exception as e:
            renderdata['error'] = str(e)
            return render(request, 'market/publish.html', renderdata)

    return render(request, 'market/publish.html', renderdata)


def paymarket(request, id):
    user = request.session.get('user', None)
    if user and request.method == 'GET':
        try:
            user = User.objects.get(usermail=user)
            market = MThread.objects.get(id=id)
            recvuser = market.postuser

            if (int(time.time()) - int(user.endptime)) < 10:
                return HttpResponse(json.dumps({"code": 0, "msg": "购买间隔10秒，请稍后再购买!"}))

            user.endptime = str(int(time.time()))
            user.save()

            if not user.activeml:
                raise RuntimeError('请先到个人主页激活邮箱！')

            pointsys = PointSystem.objects.filter(pointtyp="商品交易")
            for point in pointsys:
                if point.pointusr == user and "您购买了某商品(id=" + str(id) + ")" == point.pointdes:
                    return HttpResponse(json.dumps({"code": 0, "msg": "重复购买商品!"}))

            if user.nickname == recvuser.nickname:
                return HttpResponse(json.dumps({"code": 0, "msg": "不能购买自己发布的商品!"}))

            if market.mktstock <= 0:
                return HttpResponse(json.dumps({"code": 0, "msg": "该商品已没有库存!"}))

            if market.mktprice >= user.pointnum:
                return HttpResponse(json.dumps({"code": 0, "msg": "很抱歉您的余额不足!"}))

            user.pointnum = user.pointnum - market.mktprice
            user.save()
            recvuser.pointnum = recvuser.pointnum + market.mktprice
            recvuser.save()

            market.howmanyp += 1
            market.mktstock -= 1
            market.save()

            PointSystem.objects.create(
                pointusr=recvuser, pointdes="您的商品(id=" + str(market.id) + ")被购买", pointtyp="商品交易",
                pointlat=recvuser.pointnum,
                pointnum=market.mktprice)
            PointSystem.objects.create(
                pointusr=user, pointdes="您购买了某商品(id=" + str(market.id) + ")", pointtyp="商品交易",
                pointlat=user.pointnum,
                pointnum=-market.mktprice)

            return HttpResponse(json.dumps({"code": 1, "msg": "商品购买成功！"}))
        except Exception as e:
            return HttpResponse(json.dumps({"code": 0, "msg": str(e)}))
    return HttpResponse(json.dumps({"code": 0, "msg": "错误的提交方式！"}))


def about(request):
    renderdata = global_data(request)
    renderdata['curnav'] = 'about'
    return render(request, 'site/about.html', renderdata)


def index(request):
    renderdata = global_data(request)
    renderdata['curnav'] = 'index'
    nickname = request.GET.get('type', None)

    currentype = None
    if nickname:
        currentype = Category.objects.get(nickname=nickname)
        threads = Thread.objects.filter(thontype=currentype).order_by('-updatime')
    else:
        threads = Thread.objects.all().order_by('-updatime')

    threads = getthreads(request, renderdata['user'], threads, False)
    threads, paginator = getdjangopage(request, threads, nickname=nickname)
    renderdata['objs'] = threads
    renderdata['paginator'] = paginator
    renderdata['currentype'] = currentype
    return render(request, 'index/index.html', renderdata)


def search(request):
    renderdata = global_data(request)
    if request.method == 'POST':
        try:
            keyword = request.POST.get('keyword', '')
            renderdata["keyword"] = keyword
            threads = Thread.objects.filter(contents__contains=keyword).order_by('-updatime')
            threads = getthreads(request, renderdata['user'], threads, False)
            renderdata['objs'] = threads
            return render(request, 'index/search.html', renderdata)
        except Exception as e:
            raise Http404("search not exist")
    return HttpResponseRedirect('/')


def getisreaded(usermail):
    notifys = NotifySystem.objects.filter(replymys=str(usermail))
    for notify in notifys:
        if not notify.isreaded:
            return True
    return False


def notifications(request):
    renderdata = global_data(request)
    renderdata['curnav'] = 'index'
    if renderdata['user']:
        try:
            notifys = NotifySystem.objects.filter(replymys=renderdata['user'].usermail).order_by('-creatime')
            notifycount = 0
            for item in notifys:
                if not item.isreaded:
                    notifycount += 1
            notifys, paginator = getdjangopage(request, notifys)
            renderdata['objs'] = notifys
            renderdata['paginator'] = paginator
            return render(request, "profile/notice.html", renderdata)
        except Exception as e:
            renderdata['error'] = str(e)
            return render(request, 'profile/notice.html', renderdata)
    return HttpResponse(json.dumps({"code": 0, "msg": "未登录！"}))


def mypoint(request):
    renderdata = global_data(request)
    renderdata['curnav'] = 'index'
    if renderdata['user']:
        try:
            pointrecords = PointSystem.objects.filter(pointusr=renderdata['user']).order_by('-creatime')
            pointrecords, paginator = getdjangopage(request, pointrecords)
            renderdata['objs'] = pointrecords
            renderdata['paginator'] = paginator
            return render(request, "profile/mypoint.html", renderdata)
        except Exception as e:
            renderdata['error'] = str(e)
            return render(request, 'profile/notice.html', renderdata)
    return HttpResponse(json.dumps({"code": 0, "msg": "未登录！"}))


def saveisread(id, user):
    notifys = NotifySystem.objects.filter(replymys=user.usermail)
    for item in notifys:
        if str(item.replythd.id) == id:
            item.isreaded = True
            item.save()


def detail(request, threadid):
    renderdata = global_data(request)
    renderdata['curnav'] = 'index'

    try:
        thread = Thread.objects.get(id=threadid)
    except Thread.DoesNotExist:
        raise Http404("Thread does not exist")

    renderdata['thread'] = getthreads(request, renderdata['user'], [thread], False)[0]

    if renderdata['user']:
        saveisread(threadid, renderdata['user'])

    comments = Comment.objects.filter(cmthread=thread).order_by('creatime')
    comments = getcomments(renderdata['user'], comments)
    comments, paginator = getdjangopage(request, comments, size=30)
    renderdata['objs'] = comments
    renderdata['paginator'] = paginator

    return render(request, "index/detail.html", renderdata)


def login(request):
    renderdata = global_data(request)
    if request.method == 'POST':
        try:
            email = request.POST.get('email', '')
            password = request.POST.get('password', '')
            uaddress = "127.0.0.1"  # request.headers['X-Real-IP']

            user = User.objects.filter(usermail=email)
            if not user.exists():
                raise RuntimeError('邮箱或密码错误！')

            user = user.first()
            if getmd5(password) != user.password:
                raise RuntimeError('邮箱或密码错误！')

            request.session['user'] = user.usermail
            user.uaddress = uaddress
            user.save()

            return HttpResponseRedirect('/')
        except Exception as e:
            renderdata['error'] = str(e)
            return render(request, 'site/login.html', renderdata)

    return render(request, 'site/login.html', renderdata)


def logout(request):
    request.session.flush()
    return HttpResponseRedirect('/')


def getcomments(user, comments):
    for comment in comments:
        if comment.cmauthor.location:
            comment.cmauthor.location = json.loads(
                comment.cmauthor.location.replace("'", '"')
            )
            if user:
                try:
                    comment.cmauthor.distance = getdistance(user, comment.cmauthor)
                except:
                    pass
        if comment.parentid != 0:
            try:
                parentcomment = Comment.objects.get(id=comment.parentid)
                comment.parentcomment = parentcomment
            except:
                pass
        if comment.attachmt:
            if "gif" in comment.attachmt:
                comment.gifpng = comment.attachmt.replace(".gif", ".png")
                comment.gifpng_source = comment.attachmt
            else:
                a = comment.attachmt.split('.')[0]
                b = comment.attachmt.split('.')[1]
                comment.attachmt_source = a + '_source.' + b

    return comments


def getthreads(request, user, threads, getcomment=True):
    for thread in threads:
        if getcomment:
            comments = Comment.objects.filter(cmthread=thread).order_by("creatime")
            thread.commentCount = comments.count()
            comments = getcomments(user, comments[:3])
            thread.comments = comments

        if thread.thauthor.location:
            thread.thauthor.location = json.loads(
                thread.thauthor.location.replace("'", '"')
            )
            if user:
                try:
                    thread.thauthor.distance = getdistance(user, thread.thauthor)
                except:
                    pass

        if thread.attachmt:
            if "gif" in thread.attachmt:
                thread.gifpng = thread.attachmt.replace(".gif", ".png")
                thread.gifpng_source = thread.attachmt
            else:
                a = thread.attachmt.split('.')[0]
                b = thread.attachmt.split('.')[1]
                thread.attachmt_source = a + '_source.' + b
        if thread.videourl:
            if "#sp#" in thread.videourl:
                thread.imageurl = thread.videourl.split("#sp#", 1)[1]
            if ".mp4" in thread.videourl:
                thread.mp4video = thread.videourl.split("#sp#", 1)[0]
            elif ".mp3" in thread.videourl:
                thread.mp3url = thread.videourl.split("#sp#", 1)[0]
            elif "player.bilibili.com" in thread.videourl:
                thread.biliblivideo = thread.videourl
            else:
                thread.m3u8video = thread.videourl.split("#sp#", 1)[0]
        if thread.contents.startswith("[markdown]") \
                and thread.contents.endswith("[/markdown]"):
            thread.contents = thread.contents.replace("#sp#", "!!!", 1)
            temp = thread.contents.lstrip("[markdown]").rstrip("[/markdown]")
            thread.title = temp.split("!!!", 1)[0]
            thread.contents = markdown.markdown(
                temp.split("!!!", 1)[1],
                extensions=['markdown.extensions.extra', 'markdown.extensions.codehilite', ]
            )
            thread.markdown = True

    return threads


def getdistance(user1, user2):
    location1 = user1.location
    coor1 = (location1['result']['location']['lng'], location1['result']['location']['lat'])
    location2 = user2.location
    coor2 = (location2['result']['location']['lng'], location2['result']['location']['lat'])
    distance = round(geodesic(coor1[::-1], coor2[::-1]).km, 2)
    return distance


def uploadavator(usravatr_post, user):
    extern = os.path.splitext(usravatr_post.name)[1].lower()
    if extern != '.jpg' and extern != '.png':
        raise RuntimeError('图片格式不支持！')
    if usravatr_post.size > 4194304:
        raise RuntimeError('图片大小不能超过4兆！')
    avatordir = '/static/avator/' + str(user.id) + "_avator" + extern
    avatorfilename = os.getcwd() + avatordir
    tempfile = open(avatorfilename, 'wb')
    for line in usravatr_post.chunks(): tempfile.write(line)
    tempfile.close()
    if extern == '.png': png2jpg(avatorfilename)
    for infile in glob.glob(avatorfilename):
        im = Image.open(infile)
        size = im.size
        im.thumbnail(size, Image.ANTIALIAS)
        im.save(avatorfilename.replace(extern, ".jpg"), 'jpeg')
    im = Image.open(avatorfilename.replace(extern, ".jpg"))
    im.thumbnail((100, 100))
    im.save(avatorfilename.replace(extern, ".jpg"))
    return avatordir.replace(extern, ".jpg")


def profile(request):
    renderdata = global_data(request)
    renderdata['curnav'] = 'index'
    if request.method == 'GET':
        other = request.GET.get('u', None)
        try:
            renderdata['sameuser'] = False
            if not other and not renderdata['user']:
                raise Http404("404")

            if (not other and renderdata['user']) \
                    or (other and renderdata['user']
                        and renderdata['user'].nickname == other):
                renderdata['sameuser'] = True
                threads = Thread.objects.filter(thauthor=renderdata['user']).all()
                comments = Comment.objects.filter(cmauthor=renderdata['user']).all()
                renderdata['thread_count'] = threads.count()
                renderdata['comment_count'] = comments.count()
                threads = getthreads(request, renderdata['user'], threads[0:10], False)
                renderdata['objs'] = threads
                return render(request, 'profile/index.html', renderdata)

            other = User.objects.filter(nickname=other)
            if not other.exists():
                raise Http404("404")

            other = other.first()
            if other.location:
                other.location = json.loads(other.location.replace("'", '"'))
            renderdata['other'] = other
            threads = Thread.objects.filter(thauthor=other).all()
            comments = Comment.objects.filter(cmauthor=other).all()

            if renderdata['user']:
                try:
                    other.distance = getdistance(renderdata['user'], other)
                except:
                    pass

            renderdata['thread_count'] = threads.count()
            renderdata['comment_count'] = comments.count()
            threads = getthreads(request, renderdata['user'], threads[0:10], False)
            renderdata['objs'] = threads

            return render(request, 'profile/index.html', renderdata)
        except Exception as e:
            return HttpResponseRedirect("/login/")
    elif request.method == 'POST':
        try:
            if not renderdata['user']:
                return HttpResponseRedirect('/')
            renderdata['sameuser'] = True

            whatdoth = request.POST.get('signal', '')
            profsite = request.POST.get('mysite', '')
            urgender = request.POST.get('gender', '')
            usersage = request.POST.get('usrage', '')
            usravatr_post = request.FILES.get('uploadfile', None)
            userback_post = request.FILES.get('userBackimg', None)

            if urgender:
                renderdata['user'].urgender = urgender
            if usersage:
                try:
                    if int(usersage) <= 0 and int(usersage) >= 120:
                        raise RuntimeError("err")
                    else:
                        renderdata['user'].usersage = usersage
                except Exception as e:
                    raise RuntimeError("年龄填写有问题！")
            if profsite:
                profsite = unquote(profsite.strip())
                try:
                    validate = URLValidator(schemes=('http', 'https'))
                    validate(profsite)
                    renderdata['user'].profsite = profsite
                except Exception as e:
                    raise RuntimeError('个人主页的网址不合法！')
            if whatdoth:
                whatdoth = whatdoth.strip()
                if len(whatdoth) > 50:
                    raise RuntimeError('个性签名过长！')
                renderdata['user'].whatdoth = whatdoth
            if usravatr_post:
                renderdata['user'].usravatr = uploadavator(usravatr_post, renderdata['user'])
            if userback_post:
                result_obj = uploadtoserver(userback_post)
                if result_obj["code"] == 0:
                    raise RuntimeError(result_obj["msg"])
                source = result_obj["msg"]
                if "gif" in source:
                    renderdata['user'].userback = source
                else:
                    renderdata['user'].userback = source.split(".")[0] + "_source." + source.split(".")[1]
            renderdata['user'].save()
            return HttpResponseRedirect('/profile/')
        except Exception as e:
            renderdata['error'] = str(e)
            return render(request, 'profile/index.html', renderdata)


def publish(request):
    user = request.session.get('user', None)
    if user and request.method == 'POST':
        try:
            contents = request.POST.get("content", None)
            nickname = request.POST.get("category", None)
            attachmt = request.FILES.get("uploadfile", None)
            videofile = request.FILES.get("uploadvideofile", None)

            contents = contents.strip()
            if len(contents) < 3 or len(contents) > 5000:
                raise RuntimeError('内容少于3个字符，或者超出范围！')

            thauthor = User.objects.get(usermail=user)
            if not thauthor.activeml:
                raise RuntimeError('请先到个人主页激活邮箱！')

            if (int(time.time()) - int(thauthor.endptime)) < 10:
                raise RuntimeError('发布间隔10秒，请稍后再发布！')

            thauthor.endptime = str(int(time.time()))
            thauthor.save()

            videourl = None
            if contents.startswith("[mp3]") and contents.endswith("[/mp3]"):
                temp = contents.replace("[mp3]", "").replace("[/mp3]", "")
                if temp.split("!!!", 1)[1]:
                    alink = temp.split("!!!", 1)[1]
                    contents = temp.split("!!!", 1)[0]
                    if alink.startswith("http://") or alink.startswith("https://"):
                        if alink.endswith(".mp3"):
                            videourl = alink
                            attachmt = None
                        else:
                            RuntimeError('音乐格式不正确!')
                    else:
                        RuntimeError('音乐格式不正确!')
                else:
                    RuntimeError('音乐格式不正确!')
            if contents.startswith("[video]") and contents.endswith("[/video]"):
                temp = contents.replace("[video]", "").replace("[/video]", "")
                if temp.split("!!!", 1)[1]:
                    vlink = temp.split("!!!", 1)[1]
                    contents = temp.split("!!!", 1)[0]

                    if "|" in vlink:
                        vtemp = vlink.split("|", 1)[0]
                        vphoto = vlink.split("|", 1)[1]
                    else:
                        vtemp = vlink
                        vphoto = None

                    if vtemp.startswith("http://") or vtemp.startswith("https://"):
                        if vtemp.endswith(".mp4") or vtemp.endswith(".m3u8"):
                            if vphoto:
                                if (vphoto.startswith("http://") or vphoto.startswith("https://")) and (
                                        vphoto.endswith(".jpg") or vphoto.endswith(".png")):
                                    pass
                                else:
                                    raise RuntimeError('封面格式不正确！')
                            videourl = vtemp
                            attachmt = None
                            if vphoto: videourl = videourl + "#sp#" + vphoto
                        else:
                            raise RuntimeError('视频格式不正确！')
                    else:
                        raise RuntimeError('视频格式不正确！')
                else:
                    raise RuntimeError('视频格式不正确！')
            if contents.startswith("[bilibili]") and contents.endswith("[/bilibili]"):
                temp = contents.replace("[bilibili]", "").replace("[/bilibili]", "")
                if temp.split("!!!", 1)[1]:
                    contents = temp.split("!!!", 1)[0]
                    temp = temp.split("!!!", 1)[1]
                    if '<iframe src="//player.bilibili.com/' in temp:
                        a = '<iframe src="//player.bilibili.com/'
                        b = '<iframe style="width:100%;height:217px" src="//player.bilibili.com/'
                        videourl = temp.replace(a, b)
                        attachmt = None
                    else:
                        raise RuntimeError('视频格式不正确！')
                else:
                    raise RuntimeError('视频格式不正确！')
            if contents.startswith("[markdown]") and contents.endswith("[/markdown]"):
                temp = contents.lstrip("[markdown]").rstrip("[/markdown]")
                if not temp.split("!!!")[1]:
                    raise RuntimeError('markdown格式不正确！')

            # 内容审核
            # if thauthor.usrgrade < 3:
            #     baidu_result = contentany(contents)
            #     if baidu_result:
            #         raise RuntimeError(str(baidu_result))

            result_obj = {}
            if videofile and not attachmt and not videourl:
                result_obj = uploadtoserver(videofile, type=2)
                if result_obj["code"] == 0:
                    raise RuntimeError(result_obj["msg"])
                videourl = result_obj['msg']
            elif not videourl:
                videourl = None

            if attachmt and not videofile and not videourl:
                result_obj = uploadtoserver(attachmt)
                if result_obj["code"] == 0:
                    raise RuntimeError(result_obj["msg"])
            else:
                result_obj["msg"] = None

            thontype = Category.objects.get(nickname=nickname)
            Thread.objects.create(
                contents=contents, thauthor=thauthor, attachmt=result_obj["msg"], thontype=thontype,
                videourl=videourl,
                niminswh=thauthor.niminswh)

            return postnew_point(thauthor, '发帖奖励', '发帖积分奖励')
        except Exception as e:
            return HttpResponse(json.dumps({"code": 0, "msg": str(e)}))
    return HttpResponse(json.dumps({"code": 0, "msg": "错误的提交方式！"}))


def active(request):
    renderdata = global_data(request)
    if renderdata['user']:
        try:
            if not renderdata['user'].activeml:
                tempactive = EmailActive.objects.filter(mailuser=renderdata['user'])
                if tempactive.exists():
                    if (int(time.time()) - int(tempactive.first().endptime)) < 20:
                        raise RuntimeError('激活邮件发布间隔为20秒！')
                    tempactive = tempactive.first()
                else:
                    tempactive = None

                activecd = randomactivecode()
                if not tempactive:
                    EmailActive.objects.create(
                        activecd=activecd, mailuser=renderdata['user'], endptime=str(int(time.time())))
                    # 这里是发送激活链接
                else:
                    tempactive.endptime = str(int(time.time()))
                    tempactive.save()
                    # 这里是发送激活链接
            else:
                raise RuntimeError('邮箱已激活！')
        except Exception as e:
            renderdata['error'] = str(e)
            return render(request, 'site/register.html', renderdata)
    return HttpResponse(json.dumps({"code": 0, "msg": "未登录！"}))


def invite(request):
    if request.method == "POST":
        try:
            towho = request.POST.get("towho")
            if not re.match(r'^[0-9a-zA-Z_]{0,19}@[0-9a-zA-Z]{1,13}\.[com,cn,net]{1,3}$', towho):
                raise RuntimeError('邮箱格式错误！')
            # 这里是发送激活链接
            return HttpResponse(json.dumps({"code": 1, "msg": "发送成功！"}))
        except Exception as e:
            return HttpResponse(json.dumps({"code": 0, "msg": str(e)}))
    return HttpResponse(json.dumps({"code": 0, "msg": "错误的提交方式！"}))


def good(request, type, id):
    user = request.session.get('user', None)
    if not user:
        return HttpResponse(json.dumps({"code": 0, "msg": "未登录！"}))

    if request.method == 'GET':
        try:
            user = User.objects.get(usermail=user)
            if type == 1:
                thread = Thread.objects.get(id=id)
                goods = GoodSystem.objects.filter(goodthed=thread)
                for good in goods:
                    if good.gooduser.usermail == user.usermail:
                        raise RuntimeError('您已经赞过了！')
                thread.likenumb += 1
                thread.save(update_fields=['likenumb'])
                GoodSystem.objects.create(gooduser=user, goodthed=thread)
            elif type == 0:
                comment = Comment.objects.get(id=id)
                goods = GoodSystem.objects.filter(goodcomm=comment)
                for good in goods:
                    if good.gooduser.usermail == user.usermail:
                        raise RuntimeError('您已经赞过了！')
                comment.likenumb += 1
                comment.save()
                GoodSystem.objects.create(gooduser=user, goodcomm=comment)
            return HttpResponse(json.dumps({"code": 1, "msg": "点赞成功！"}))
        except Exception as e:
            return HttpResponse(json.dumps({"code": 0, "msg": str(e)}))
    return HttpResponse(json.dumps({"code": 0, "msg": "错误的提交方式！"}))


def signpoint(request):
    renderdata = global_data(request)
    if renderdata['user']:
        try:
            points = PointSystem.objects.filter(pointusr=renderdata['user']).order_by("-creatime")
            newpoints = []
            for point in points:
                if point.pointtyp == "签到奖励": newpoints.append(point)
            points = newpoints
            if points and len(points) > 0:
                day = points[0].creatime.day
                year = points[0].creatime.year
                month = points[0].creatime.month
                day2 = datetime.datetime.now().day
                year2 = datetime.datetime.now().year
                month2 = datetime.datetime.now().month
                if (year == year2) and (month == month2) and int(day2) <= int(day):
                    raise RuntimeError('你今天已签到过了！')
            pointnum = random.randint(1, 5)
            renderdata['user'].pointnum = pointnum + renderdata['user'].pointnum
            renderdata['user'].usrgrade = getusergrade(renderdata['user'].pointnum)
            renderdata['user'].save()
            PointSystem.objects.create(
                pointusr=renderdata['user'], pointdes="每日活跃度奖励", pointtyp="签到奖励",
                pointlat=renderdata['user'].pointnum, pointnum=pointnum)
            return HttpResponse(json.dumps({"code": 1, "msg": "获得" + str(pointnum) + "肥宅币！"}))
        except Exception as e:
            return HttpResponse(json.dumps({"code": 0, "msg": str(e)}))
    return HttpResponse(json.dumps({"code": 0, "msg": "未登录！"}))


def todayissign(user):
    points = PointSystem.objects.filter(pointusr=user).order_by("-creatime")
    newpoints = []
    for point in points:
        if point.pointtyp == "签到奖励": newpoints.append(point)
    points = newpoints
    if points and len(points) > 0:
        day = points[0].creatime.day
        year = points[0].creatime.year
        month = points[0].creatime.month
        day2 = datetime.datetime.now().day
        year2 = datetime.datetime.now().year
        month2 = datetime.datetime.now().month
        if (year == year2) and (month == month2) and int(day2) <= int(day):
            return True
    return False


def setniminswh(request, niminflag):
    renderdata = global_data(request)
    if renderdata['user']:
        try:
            renderdata['user'].niminswh = 0
            renderdata['user'].save()
            return HttpResponse(json.dumps({"code": 1, "msg": "设置成功！"}))
        except Exception as e:
            return HttpResponse(json.dumps({"code": 0, "msg": str(e)}))
    return HttpResponse(json.dumps({"code": 0, "msg": "未登录！"}))


def setbackswih(request, backflag):
    renderdata = global_data(request)
    if renderdata['user']:
        try:
            if int(backflag) == 0:
                renderdata['user'].backswih = backflag
            else:
                if renderdata['user'].usrgrade < 1:
                    raise RuntimeError("该功能需要达到1级才可使用！")
                if not renderdata['user'].userback:
                    raise RuntimeError("请先到个人主页设置封面！")
                renderdata['user'].backswih = backflag

            renderdata['user'].save()
            return HttpResponse(json.dumps({"code": 1, "msg": "设置成功！"}))
        except Exception as e:
            return HttpResponse(json.dumps({"code": 0, "msg": str(e)}))
    return HttpResponse(json.dumps({"code": 0, "msg": "未登录！"}))


def setlocation(request, localflag):
    renderdata = global_data(request)
    if renderdata['user']:
        try:
            if int(localflag) == 0:
                renderdata['user'].location = None
            else:
                lng = request.GET.get("lng", 0)
                lat = request.GET.get("lat", 0)

                try:
                    req = requests.get(
                        "http://api.map.baidu.com/reverse_geocoding/v3/?ak=jOn0GQPIeXI3QsqkAtjztptU4c3AagC0&output=json&coordtype=wgs84ll&location={},{}".format(
                            lat, lng))
                    req.close()
                    renderdata['user'].location = json.dumps(req.json())
                except Exception as e:
                    raise RuntimeError("获取位置失败！")

            renderdata['user'].save()
            return HttpResponse(json.dumps({"code": 1, "msg": "设置成功！"}))
        except Exception as e:
            return HttpResponse(json.dumps({"code": 0, "msg": str(e)}))
    return HttpResponse(json.dumps({"code": 0, "msg": "未登录！"}))


def setrecvemail(request, recvflag):
    renderdata = global_data(request)
    if renderdata['user']:
        try:
            renderdata['user'].recvmail = int(recvflag)
            renderdata['user'].save()
            return HttpResponse(json.dumps({"code": 1, "msg": "设置成功！"}))
        except Exception as e:
            return HttpResponse(json.dumps({"code": 0, "msg": str(e)}))
    return HttpResponse(json.dumps({"code": 0, "msg": "未登录！"}))


def getusergrade(point):
    if point >= 1000:
        return 10
    elif point >= 900:
        return 9
    elif point >= 800:
        return 7
    elif point >= 700:
        return 7
    elif point >= 600:
        return 6
    elif point >= 500:
        return 5
    elif point >= 300:
        return 4
    elif point >= 300:
        return 3
    elif point >= 200:
        return 2
    elif point >= 100:
        return 1
    return 0


def register(request):
    renderdata = global_data(request)
    if request.method == 'POST':
        try:
            email = request.POST.get('email', '')
            password = request.POST.get('password', '')
            uaddress = "127.0.0.1"  # request.headers['X-Real-IP']

            if not re.match(r'^[0-9a-zA-Z_]{0,19}@[0-9a-zA-Z]{1,13}\.[com,cn,net]{1,3}$', email):
                raise RuntimeError('邮箱格式错误！')

            mailsuffix = email.split('@')[1]
            if mailsuffix != 'qq.com' and mailsuffix != '163.com' and mailsuffix != 'foxmail.com' \
                    and mailsuffix != 'outlook.com' and mailsuffix != 'gmail.com' and mailsuffix != 'sina.com' \
                    and mailsuffix != '126.com':
                raise RuntimeError('不支持的邮箱格式！')

            # 黑名单机器人
            # if User.objects.filter(uaddress=uaddress).exists():
            #     endptime = datetime.date.today() + datetime.timedelta(days=1)
            #     black = Black.objects.filter(uaddress=uaddress)
            #     if black.exists():
            #         black = black.first()
            #         black.endptime = endptime
            #         black.save()
            #     else:
            #         Black.objects.create(
            #             uaddress=uaddress,
            #             bkreason="检测到您似乎在恶意注册，已被惩罚。",
            #             endptime=endptime,
            #         )
            #     raise RuntimeError('您由于恶意注册，已被系统惩罚！')

            if User.objects.filter(usermail=email).exists():
                raise RuntimeError('邮箱已被注册！')

            nickname = randomnk()
            activecd = randomactivecode()

            userobj = User.objects.create(
                password=getmd5(password), usermail=email, uaddress=uaddress, recvmail=1,
                nickname=nickname, activeml=True
            )
            EmailActive.objects.create(
                activecd=activecd, mailuser=userobj, endptime=str(int(time.time())))
            request.session['user'] = userobj.usermail

            return HttpResponseRedirect('/')
        except Exception as e:
            renderdata['error'] = str(e)
            return render(request, 'site/register.html', renderdata)

    return render(request, 'site/register.html', renderdata)


def emailactive(request, nick, code):
    try:
        user = User.objects.filter(nickname=nick)
        if not user.exists():
            raise RuntimeError("该激活链接无效，请登录后重新发送。")
        user = user.first()
        email_db = EmailActive.objects.get(mailuser=user)

        if code == email_db.activecd:
            user.activeml = True
            user.save()
            email_db.delete()
            return HttpResponse('账号激活成功！<a href="/profile/">点此返回</a>。')

        raise RuntimeError("该激活链接无效，请登录后重新发送。")
    except Exception as e:
        return render(request, "500.html", {"message": e, "title": "提示信息"})


def comment(request, threadid):
    user = request.session.get('user', None)
    if user and request.method == 'POST':
        try:
            contents = request.POST.get("content", None)
            parentid = request.POST.get("parentid", None)
            attachmt = request.FILES.get("uploadfile", None)

            contents = contents.strip()
            if len(contents) < 3 or len(contents) > 5000:
                raise RuntimeError('内容少于3个字符，或者超出范围！')

            thauthor = User.objects.get(usermail=user)
            if not thauthor.activeml:
                raise RuntimeError('请先到个人主页激活邮箱！')

            if (int(time.time()) - int(thauthor.endptime)) < 10:
                raise RuntimeError('发布间隔10秒，请稍后再发布！')

            thauthor.endptime = str(int(time.time()))
            thauthor.save()

            # 内容审核
            # if thauthor.usrgrade < 3:
            #     baidu_result = contentany(contents)
            #     if baidu_result:
            #         raise RuntimeError(str(baidu_result))

            parent_comment = None
            if parentid and parentid != threadid:
                thread = Thread.objects.get(id=threadid)
                comments = Comment.objects.filter(cmthread=thread)
                parent_error = False
                for comment in comments:
                    if int(parentid) == comment.id:
                        parent_error = True
                        break
                if not parent_error:
                    raise RuntimeError('指定的回复编号不在本贴子内！')

                parent_comment = Comment.objects.filter(id=int(parentid))
                if not parent_comment.exists():
                    raise RuntimeError('指定的回复编号不存在！')
                parent_comment = parent_comment.first()

            result_obj = {}
            if attachmt:
                result_obj = uploadtoserver(attachmt)
                if result_obj["code"] == 0:
                    raise RuntimeError(result_obj["msg"])
            else:
                result_obj["msg"] = None

            thread = Thread.objects.get(id=threadid)
            thread.commnumb += 1

            if parent_comment:
                newcomment = Comment.objects.create(
                    contents=contents, cmauthor=thauthor, attachmt=result_obj["msg"], cmthread=thread,
                    commfoor=thread.commnumb, parentid=int(parentid), niminswh=thauthor.niminswh)
                if parent_comment.cmauthor.usermail != thauthor.usermail:
                    if parent_comment.cmauthor.recvmail:
                        # 发送评论通知邮件
                        pass
                    NotifySystem.objects.create(
                        replymys=parent_comment.cmauthor.usermail, replyhes=thauthor, replycom=newcomment,
                        replythd=thread, isreaded=False)
            else:
                newcomment = Comment.objects.create(
                    contents=contents, cmauthor=thauthor, attachmt=result_obj["msg"], cmthread=thread,
                    commfoor=thread.commnumb,
                    niminswh=thauthor.niminswh)
                if thread.thauthor.usermail != thauthor.usermail:
                    if thread.thauthor.recvmail:
                        # 发送评论通知邮件
                        pass
                    NotifySystem.objects.create(
                        replymys=thread.thauthor.usermail, replyhes=thauthor, replycom=newcomment, replythd=thread,
                        isreaded=False)

            thread.save()

            return postnew_point(thauthor, '评论奖励', '评论积分奖励')
        except Exception as e:
            return HttpResponse(json.dumps({"code": 0, "msg": str(e)}))
    return HttpResponse(json.dumps({"code": 0, "msg": "错误的提交方式！"}))


def forum_get_tops():
    return User.objects.all().order_by("-endptime")[0:10]


def forum_get_bests():
    return User.objects.all().order_by("-pointnum")[0:10]


def forum_get_creates():
    return User.objects.all().order_by("-creatime")[0:10]


def get_signtops():
    signusers = []

    day2 = datetime.datetime.now().day
    year2 = datetime.datetime.now().year
    month2 = datetime.datetime.now().month

    points = PointSystem.objects.all().order_by("creatime")
    for point in points:
        if point.pointtyp == "签到奖励":
            day = point.creatime.day
            year = point.creatime.year
            month = point.creatime.month
            if (year == year2) and (month == month2) and (day2 == day):
                signusers.append(point)
    return signusers


def forum_get_signtops():
    signusers = get_signtops()
    return signusers[:10]


def is_markdown(obj):
    if obj.contents.startswith("[markdown]") \
            and obj.contents.endswith("[/markdown]"):
        obj.contents = obj.contents.replace("#sp#", "!!!", 1)
        temp = obj.contents.lstrip("[markdown]").rstrip("[/markdown]")
        title = temp.split("!!!", 1)[0]
        obj.title = title
        obj.markdown = True
    return obj


def forum_get_activelog():
    threads = Thread.objects.all().order_by('-creatime')[:5]
    for obj in threads:
        obj = is_markdown(obj)
        obj.active_type = "thread"
    comments = Comment.objects.all().order_by('-creatime')[:5]
    for obj in comments:
        obj.cmthread = is_markdown(obj.cmthread)
        obj.active_type = "comment"
    thgoods = GoodSystem.objects.all().order_by('-creatime')[:5]
    for obj in thgoods:
        if not obj.goodthed: continue
        obj.goodthed = is_markdown(obj.goodthed)
        obj.active_type = "good"
    markets = MThread.objects.all().order_by('-creatime')[:5]
    for obj in markets:
        obj.active_type = "market"
    results = sorted(chain(threads, thgoods, comments, markets), key=attrgetter('creatime'), reverse=True)
    return results


def postnew_point(thauthor, type, type2):
    newpoints = []
    allpointcount = 0
    upoints = PointSystem.objects.filter(pointusr=thauthor).order_by("-creatime")
    for point in upoints:
        if point.pointtyp == type: newpoints.append(point)
    for point in newpoints:
        day = point.creatime.day
        year = point.creatime.year
        month = point.creatime.month
        day2 = datetime.datetime.now().day
        year2 = datetime.datetime.now().year
        month2 = datetime.datetime.now().month
        if (year == year2) and (month == month2) and int(day2) == int(day):
            allpointcount += 1
    if allpointcount >= 5:
        return HttpResponse(json.dumps({"code": 1, "msg": "提交成功！今日" + type2 + "到达上限！"}))
    else:
        PointSystem.objects.create(
            pointusr=thauthor, pointdes=type2, pointtyp=type,
            pointlat=thauthor.pointnum + 1, pointnum=1)
        thauthor.pointnum += 1
        thauthor.save()
        return HttpResponse(json.dumps({"code": 1, "msg": "提交成功！积分+1！"}))
