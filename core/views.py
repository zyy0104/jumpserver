#-*- coding:utf8 -*-

import yaml
from sqlalchemy.sql import select
from sqlalchemy import and_
from core.models import session,HostUser,User,Group,Host,User2Group,HostUser2Group
from bin.yunserver import start
from core.models import Base,engine


def format_yaml(yfile):
    try:
        f = open(yfile,'r')
        d = yaml.load(f)
        return d
    except Exception as e:
        print (e)

def start_server(argvs):
    """
    启动程序
    :param argvs:
    :return:
    """
    start()

def create_users(argvs):
    """
    创建新用户
    :param argvs:
    :return:
    """
    #获取文件
    yfile = argvs[argvs.index('-f')+1]
    d = format_yaml(yfile)
    #循环创建新用户,如果用户已经存在，更新密码
    for k,v in d.items():
        u = session.query(User).filter(User.username == str(k)).first()
        if u:
            print ('---\033[1;33muser [%s] has exists,Update password.\33[0m---'%str(k))
            #更新密码
            session.query(User).filter(User.username == str(k)).update({'password':str(v['password'])})
        else:
            insert_user = User(username=str(k),password=str(v['password']))
            #新建用户
            session.add(insert_user)
            session.commit()
            print ('\033[1;34mSuccess\033[0m')
    session.close()

def create_groups(argvs):
    """
    创建组，如果组已经存在，则增加组用户
    :param argvs:
    :return:
    """
    #获取文件
    yfile = argvs[argvs.index('-f')+1]
    d = format_yaml(yfile)
    #
    for k,v in d.items():
        #判断组是否已经存在
        g = session.query(Group).filter(Group.name == str(k)).first()
        #如果不存在，新建组
        if not g:
            insert_group = Group(name=str(k))
            session.add(insert_group)
            session.commit()
            g = session.query(Group).filter(Group.name == str(k)).first()
            print ('\033[1;34mSuccess\033[0m')
        else:
            for user in v['user']:
                u = session.query(User).filter(User.username == user).first()
                #如果程序账号存在，则建立用户组关系
                if u:
                    engine.execute(User2Group.insert(),{'user_id':u.id,'group_id':g.id})
                    print ('\033[1;34mSuccess\033[0m')
    session.close()

def create_hosts(argvs):
    """
    创建主机
    :param argvs:
    :return:
    """
    #获取文件
    yfile = argvs[argvs.index('-f')+1]
    d = format_yaml(yfile)
    #
    for k,v in d.items():
        #判断主机是否存在
        h = session.query(Host).filter(Host.hostname == str(k)).first()
        #如果不存在，新建主机信息
        if not h:
            insert_host = Host(hostname=k,ip_addr=v['ip_addr'],port=v['port'])
            session.add(insert_host)
            session.commit()
            print ('\033[1;34mSuccess\033[0m')
        #如果主机名已经存在,打印报错
        else:
            print ('\033[1;33mHostname [%s] has exists.\33[0m'%v['ip_addr'])
    session.close()

def create_hostusers(argvs):
    """
    创建主机账号，并与主机进行关联
    :param argvs:
    :return:
    """
    #获取文件
    yfile = argvs[argvs.index('-f')+1]
    d = format_yaml(yfile)
    for k,v in d.items():
        #print(k,v)
        for host in v['ip_addr']:
            h = session.query(Host).filter(Host.ip_addr == host).first()
            if h:
                #判断是否有账号已经在主机上
                unique = session.query(HostUser).filter(and_(HostUser.host_id==h.id,\
                                                             HostUser.username==v['username'])).first()
                #如果在指定主机上没有，则新建
                if not unique:
                    insert_hostuser = HostUser(host_id=h.id,
                                               auth_type='ssh-passwd',
                                               username=str(v['username']),
                                               password=str(v['password']))
                    #print (h.id,v['username'],v['password'])
                    session.add(insert_hostuser)
                    session.commit()
                    print ('\033[1;34mSuccess\033[0m')
                #如果存在重复账号，则更新密码
                else:
                    print ('\033[1;33mUsername [%s] at [%s] has exists.Update password\33[0m'%(v['username'],
                                                                                h.ip_addr))
                    session.query(HostUser).filter(and_(HostUser.host_id==h.id,\
                                                             HostUser.username==v['username'])
                                                   ).update({'password':str(v['password'])})
                    print ('\033[1;34mSuccess\033[0m')
            else:
                print ('\033[1;33mHost [%s] is not exists.\33[0m'%host)
        session.close()

def bind(argvs):
    """
    将组跟主机账号绑定
    :param argvs:
    :return:
    """
    #获取文件
    yfile = argvs[argvs.index('-f')+1]
    d = format_yaml(yfile)
    for k,v in d.items():

        #判断组是否存在
        g = session.query(Group).filter(Group.name == str(k)).first()
        #如果组存在
        if g:
            #得到host.id
            h = session.query(Host).filter(Host.ip_addr==v['ip_addr']).first()
            #判断hostuser是否存在
            if h:
                u = session.query(HostUser).filter(and_(HostUser.host_id==h.id,
                                                        HostUser.username==v['username'])).first()
                #如果hostuser对应主机正确，在hostuser_2_group中插入关系

                if u:
                    engine.execute(HostUser2Group.insert(),{'hostuser_id':u.id,'group_id':g.id})
                    print ('\033[1;34mSuccess\033[0m')
                else:
                     print ('\033[1;33HostUser [%s@%s] is not exists.\33[0m'%(v['username'],
                                                                                 v['ip_addr']))

            else:
                print ('\033[1;33mHost [%s] is not exists.\33[0m'%v['ip_addr'])
        else:
            print ('\033[1;33Group [%s] is not exists.\33[0m'%str(k))

def syncdb(argvs):
    """
    同步数据库，第一次运行，或删除表后进行初始化
    :param argvs:
    :return:
    """
    print ('...Syncdb...')
    Base.metadata.create_all(engine) #创建所有表结构
