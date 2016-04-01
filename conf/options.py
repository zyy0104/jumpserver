#-*- coding:utf8 -*-

from core import views

#字典的keys为命令选项
#字典的values为命令选项对应的回调函数对象
actions = {
    'start': views.start_server,
    'create_users': views.create_users,
    'create_groups': views.create_groups,
    'create_hosts': views.create_hosts,
    'create_groups': views.create_groups,
    'create_hostusers': views.create_hostusers,
    'bind':views.bind,
    'syncdb':views.syncdb
}