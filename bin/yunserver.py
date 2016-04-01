#-*- coding:utf8 -*-

from core.models import verify_user,host_list
from core.demo_simple import Login

def user_passwd():
    """
    程序账号输入
    :return:
    """
    while True:
        username = input('Username:').strip()
        if len(username) == 0:continue
        password = input('Password:').strip()
        if len(password) == 0:continue
        break
    return username,password

def user_login():
    """
    根据输入，进行程序账号验证
    :return: 如果验证通过，返回用户名及密码
    """
    login_verify = False
    while not login_verify:
        username,password = user_passwd()
        login_verify = verify_user(username,password)
        if login_verify:login_verify = True
    return username,password

def start():
    """
    开始程序
    :return:
    """
    #获取正确的用户名及密码
    username,password = user_login()
    #获取程序账号对应的组、主机信息
    host_info = host_list(username)
    while True:
        #打印该用户下可以登录的主机信息
        for k,v in host_info.items():
            print (k,'Group:%s'%v[0],'Hostname:%s'%v[1],'%s@%s'%(v[4],v[2]))
        try:
            options = int(input('Please select the host you want to login:'))
        except ValueError as e:
            continue
        if options not in host_info:continue
        #获取用户选择登录的主机IP、端口、主机账号及密码
        hostname,port,hostuser,password = host_info[options][2:6]
        s = Login(hostname,port,hostuser,password)
        #执行程序
        s.run(username)
