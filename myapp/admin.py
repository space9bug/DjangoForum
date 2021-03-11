from django.contrib import admin

from .models import *

admin.site.site_title = "站点管理"
admin.site.site_header = "值班室"


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'usermail', 'activeml', 'backswih', 'nickname', 'endptime', 'profsite', 'usravatr', 'location', 'password',
        'pointnum', 'usrgrade', 'whatdoth', 'userback', 'usersage', 'urgender', 'recvmail', 'niminswh', 'uaddress',
        'creatime')


class BlackAdmin(admin.ModelAdmin):
    list_display = (
        'uaddress', 'bkreason', 'endptime', 'fuckuser', 'creatime')


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('typename', 'nickname', 'typesort', 'creatime')


class ThreadAdmin(admin.ModelAdmin):
    list_display = (
        'contents', 'attachmt', 'videourl', 'commnumb', 'likenumb', 'niminswh',
        'updatime', 'creatime', 'thauthor', 'thontype')


class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'contents', 'attachmt', 'parentid', 'commfoor', 'likenumb', 'niminswh', 'creatime', 'cmauthor',
        'cmthread')


class PointSystemAdmin(admin.ModelAdmin):
    list_display = ('pointnum', 'pointlat', 'pointtyp', 'pointdes', 'pointusr', 'creatime')


class NotifySystemAdmin(admin.ModelAdmin):
    list_display = ('replymys', 'isreaded', 'creatime', 'replyhes', 'replythd', 'replycom')


class GoodSystemAdmin(admin.ModelAdmin):
    list_display = ('creatime', 'gooduser', 'goodthed', 'goodcomm')


class EmailActiveAdmin(admin.ModelAdmin):
    list_display = ('creatime', 'activecd', 'endptime', 'mailuser')


class MtypeAdmin(admin.ModelAdmin):
    list_display = ('typename', 'nickname', 'typesort', 'typelogo', 'creatime')


class MThreadAdmin(admin.ModelAdmin):
    list_display = (
        'mketname', 'contents', 'hidecont', 'howmanyp', 'mktprice', 'mktstock', 'mketchat', 'attachmt', 'postuser',
        'mkettype', 'creatime')


admin.site.register(User, UserAdmin)
admin.site.register(Black, BlackAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Thread, ThreadAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(PointSystem, PointSystemAdmin)
admin.site.register(NotifySystem, NotifySystemAdmin)
admin.site.register(GoodSystem, GoodSystemAdmin)
admin.site.register(EmailActive, EmailActiveAdmin)
admin.site.register(Mtype, MtypeAdmin)
admin.site.register(MThread, MThreadAdmin)
