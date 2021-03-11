import os
import glob
import json
import time
import random
import string
import hashlib
import requests
import datetime
import cv2 as cv
from PIL import Image
from aip import AipImageCensor
from django.http import Http404
from django.core.paginator import Paginator, EmptyPage


def getmd5(t):
    md5_object = hashlib.md5()
    md5_object.update(t.encode())
    return str(md5_object.hexdigest())


def png2jpg(path):
    img = cv.imread(path, 0)
    w, h = img.shape[::-1]
    infile = path
    outfile = os.path.splitext(infile)[0] + ".jpg"
    img = Image.open(infile)
    try:
        if len(img.split()) == 4:
            r, g, b, a = img.split()
            img = Image.merge("RGB", (r, g, b))
            img.convert('RGB').save(outfile, quality=100)
            os.remove(path)
        else:
            img.convert('RGB').save(outfile, quality=100)
            os.remove(path)
        return outfile
    except Exception as e:
        print(e)


def randomnk():
    nks = []
    while True:
        nk = set(random.sample(string.ascii_letters + string.digits, 8))
        if nk.intersection(string.ascii_uppercase) and nk.intersection(
                string.ascii_lowercase) and nk.intersection(string.digits):
            nks.append(''.join(nk))
        if len(nks) != 0:
            break
    return nks[0]


def randomactivecode():
    nks = []
    while True:
        nk = set(random.sample(string.ascii_letters + string.digits, 12))
        if nk.intersection(string.ascii_uppercase) and nk.intersection(
                string.ascii_lowercase) and nk.intersection(string.digits):
            nks.append(''.join(nk))
        if len(nks) != 0:
            break
    return nks[0]


def contentany(content):
    client = AipImageCensor(
        '百度ai自己申请', '百度ai自己申请', '百度ai自己申请'
    )
    result = client.textCensorUserDefined(content)
    result = json.loads(str(result).replace("'", '"'))
    if "error_code" in result:
        return result["error_msg"]
    if result["conclusionType"] != 1 \
            and result["conclusionType"] != 3:
        return result["data"][0]["msg"]
    return False


def uploadtoserver(file, type=1):
    extern = os.path.splitext(file.name)[1].lower()
    if type == 1:
        if extern != '.jpg' and extern != '.png' and extern != '.gif':
            return {"code": 0, "msg": '图片格式不支持！'}
        if file.size > 4194304:
            return {"code": 0, "msg": '图片大小不能超过4兆！'}
    elif type == 2:
        if extern != '.mp4':
            return {"code": 0, "msg": '视频格式不支持！'}
        if file.size > 5242880:
            return {"code": 0, "msg": '视频大小不能超过5兆！'}

    basepath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    uploaddir = '/static/upload/' + datetime.datetime.now().strftime('%Y/%m/%d/')
    systemdir = os.getcwd() + uploaddir
    if not os.path.isdir(systemdir):
        os.makedirs(systemdir)

    filename = str(int(time.time()))
    filepath = uploaddir + filename + extern
    tempfile = open(basepath + filepath, 'wb')
    for line in file.chunks():
        tempfile.write(line)
    tempfile.close()

    if type != 1: return {
        "code": 1, "msg": filepath
    }

    if extern != ".gif":
        if extern == '.png':
            png2jpg(basepath + filepath)

        filepath = uploaddir + filename + '.jpg'
        for infile in glob.glob(basepath + filepath):
            im = Image.open(infile)
            size = im.size
            im.thumbnail(size, Image.ANTIALIAS)
            im.save(basepath + uploaddir + filename + "_source" + '.jpg', 'jpeg')

        im = Image.open(basepath + filepath)
        w, h = im.size
        if w > 200:
            im.thumbnail((200, int(200 / (w / h))))
        im.save(basepath + filepath)
        return {"code": 1, "msg": filepath}

    image = Image.open(basepath + filepath)
    current = image.tell()
    image.save(basepath + filepath.replace(".gif", ".png"), quality=60)
    im = Image.open(basepath + filepath.replace(".gif", ".png"))
    w, h = im.size
    if w > 200:
        im.thumbnail((200, int(200 / (w / h))))
    im.save(basepath + filepath.replace(".gif", ".png"))

    if file.size > 1048576:
        os.system("gifsicle -O3 {} -o {} --colors 16".format(basepath + filepath, basepath + filepath))

    return {
        "code": 1, "msg": filepath
    }


def getdjangopage(request, objs, size=15, nickname=None):
    paginator = Paginator(objs, size, )
    if paginator.num_pages <= 1:
        objs = objs
    else:
        page = int(request.GET.get('page', 1))

        try:
            objs = paginator.page(page)
        except EmptyPage:
            raise Http404("Page does not exist")

        left = []
        right = []
        last = False
        first = False
        left_has_more = False
        right_has_more = False
        page_range = paginator.page_range
        total_pages = paginator.num_pages

        if page == 1:
            right = page_range[page:page + 2]
            if right[-1] < total_pages - 1:
                right_has_more = True
            if right[-1] < total_pages:
                last = True
        elif page == total_pages:
            left = page_range[(page - 3) if (page - 3) > 0 else 0:page - 1]
            if left[0] > 2:
                left_has_more = True
            if left[0] > 1:
                first = True
        else:
            left = page_range[(page - 3) if (page - 3) > 0 else 0:page - 1]
            right = page_range[page:page + 2]
            if left[0] > 2:
                left_has_more = True
            if left[0] > 1:
                first = True
            if right[-1] < total_pages - 1:
                right_has_more = True
            if right[-1] < total_pages:
                last = True
        paginator = {
            'left': left,
            'last': last,
            'page': page,
            'right': right,
            'first': first,
            'total_pages': total_pages,
            'left_has_more': left_has_more,
            'right_has_more': right_has_more
        }
        if nickname: paginator['nickname'] = nickname
    return objs, paginator


def gettimedeltadate(days):
    return (datetime.date.today() + datetime.timedelta(days=days)).strftime("%Y-%m-%d")
