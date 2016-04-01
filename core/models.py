#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'Yuntu'

from sqlalchemy import create_engine,and_,Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String,ForeignKey,DateTime
from  sqlalchemy.orm import sessionmaker,relationship
from sqlalchemy_utils import ChoiceType
from sqlalchemy.sql import select
from datetime import datetime

from conf import settings

#生成一个SqlORM 基类,这个类的所有子类会自动与表进行关联
Base = declarative_base()

#创建一个表，对表外键关系进行关联,维护host_user与groups之间的关系
#host_user包含主机登录用户ID，用户对应主机ID、认证方式、主机用户、主机用户密码
#groups包含组ID,组用户名
#该关系表将实际主机账号跟组进行关联
#例如 web主机1的user1属于运维组
#web主机1的test1属于测试组
#配置relationship，需要指定secondary=HostUser2Group
#组合索引，确保没有重复数据出现
HostUser2Group = Table('hostuser_2_group',Base.metadata,
    Column('hostuser_id',ForeignKey('host_user.id'),primary_key=True),
    Column('group_id',ForeignKey('groups.id'),primary_key=True),
)

#创建一个表，对表外键关系进行关联，维护user_profile与group 之间的关系
#user_profile表包含用户ID、用户名、用户密码
#groups表包含组ID、组名称
#该关系表将用户ID与组ID进行关联，意思就是用户属于哪个组
#例如程序账号（不是主机账号）user1属于组运维组
#程序账号test1属于测试组
#配置relationship，需要指定secondary=UserProfile2Group
#组合索引，确保没有重复数据出现
User2Group = Table('user_2_group',Base.metadata,
    Column('user_id',ForeignKey('users.id'),primary_key=True),
    Column('group_id',ForeignKey('groups.id'),primary_key=True),
)

"""
#暂不添加临时账号关系表，感觉不规范
#创建一个表，对表外键关系进行关联，维护user_profile与host_user 之间的关系
#users表包含用户ID、用户名、用户密码
#host_user包含主机登录用户ID，用户对应主机ID，认证方式，主机用户，主机用户密码
#该关系表将程序账号（不是主机账号）与主机账号进行关联
#配置relationship，需要指定secondary=userprofile_2_hostuser
#组合索引，确保没有重复数据出现
UserProfile2HostUser= Table('user_2_hostuser',Base.metadata,
    Column('user_id',ForeignKey('users.id'),primary_key=True),
    Column('hostuser_id',ForeignKey('host_user.id'),primary_key=True),
)
"""
#关系表
#hostuser_2_group 主机账号关联组
#user_2_group     程序账号关联组
#2个关系表实现，程序账号登录后，直到改账号属于哪些组；
#组又关联一些包含主机及主机账号的信息
#效果就是，用户登陆后：
# test1@192.168.1.1 root@192.168.1.2

class Host(Base):
    """
    主机表，表名 host
    id: 主机ID
    hostname:主机名
    ip_addr:主机IP
    port:ssh端口
    """
    __tablename__='hosts'
    id = Column(Integer,primary_key=True,autoincrement=True)
    hostname = Column(String(64),unique=True,nullable=False)
    ip_addr = Column(String(128),unique=True,nullable=False)
    port = Column(Integer,default=22)
    def __repr__(self):
        return  "<id=%s,hostname=%s, ip_addr=%s>" %(self.id,
                                                    self.hostname,
                                                    self.ip_addr)
class Group(Base):
    """
    主机用户组
    id:组ID
    name:组名
    """
    __tablename__ = 'groups'
    id = Column(Integer,primary_key=True)
    name = Column(String(64),unique=True,nullable=False)
    def __repr__(self):
        return  "<id=%s,name=%s>" %(self.id,self.name)

class User(Base):
    """
    表名 user_profile
    id 用户ID
    username 用户名
    password 密码
    """
    __tablename__ = 'users'
    id = Column(Integer,primary_key=True)
    username = Column(String(64),unique=True,nullable=False)
    password = Column(String(255),nullable=False)
    groups = relationship('Group',
                          secondary=User2Group,
                          backref='userprofiles')
    def __repr__(self):
        return  "<id=%s,name=%s>" %(self.id,self.username)

class HostUser(Base):
    """
    主机账号
    id:账号ID
    host_id:主机ID
    auth_type:登录方式
    username:主机账号
    password:主机账号密码
    """
    __tablename__ = 'host_user'
    id = Column(Integer,primary_key=True)
    host_id = Column(Integer,ForeignKey('hosts.id'))
    AuthTypes = [
        (u'ssh-passwd',u'SSH/Password'),
        (u'ssh-key',u'SSH/KEY'),
    ]
    auth_type = Column(ChoiceType(AuthTypes))
    username = Column(String(64),nullable=False)
    password = Column(String(255))
    groups = relationship('Group',
                          secondary=HostUser2Group,
                          backref='host_list')

    def __repr__(self):
        return  "<id=%s,name=%s>" %(self.id,self.username)

class AuthLog(Base):
    """
    用户执行命令记录
    id:
    username:登录账号
    groupname:所属组
    command：执行的命令
    exec_time:执行时间
    """
    __tablename__ = 'authlog'
    id = Column(Integer,primary_key=True)
    username = Column(String(64),nullable=False)
    groupname = Column(String(64),nullable=False)
    command = Column(String(256),nullable=False)
    exec_time = Column(DateTime,default=datetime.now)

engine = create_engine(settings.DB_CONN,echo=settings.ECHO)

#创建与数据库的会话session class,返回的还是一个类
#配置ORM的操作句柄(Handle)
SessionCls = sessionmaker(bind=engine)
#实例化该SessionCls,session获取到由engine维护的数据库连接池，
#并且会维持内存中的映射数据直到提交(commit)更改或者关闭会话对象
session = SessionCls()

def verify_user(username,password):
    """
    验证用户及密码是否正确
    :param username: 用户名
    :param password: 密码
    :return:
    """
    ret = session.query(User).filter(and_(User.username == username,User.password == password)).first()
    if ret:return True

def host_list(username):
    """
    根据登录用户名，获取该用户可以登录主机信息
    :param username: 登录用户名
    :return: 主机信息字典
    """
    #初始化字典
    hd = {}
    num = 1
    #根据登录账号，获取用户信息
    user = session.query(User).filter(User.username == username).first()
    #获取用户的所属组信息
    group = user.groups[0]
    #获取组内的主机信息
    sql = select([HostUser2Group.c.hostuser_id]).where(HostUser2Group.c.group_id == group.id)
    hostusers = engine.execute(sql).fetchall()
    #格式化主机信息，添加到字典中
    for i in hostusers:
        hostuser = session.query(HostUser).filter(HostUser.id == i[0]).first()
        host = session.query(Host).filter(Host.id == hostuser.host_id).first()
        hd[num] = [group.name,host.hostname,host.ip_addr,host.port,hostuser.username,hostuser.password]
        num += 1
    return hd

def auth_log(username,command):
    """
    将用户执行命令记录到数据库
    :param username: 登录用户
    :param command: 执行命令
    :return:
    """
    #根据登录账号，获取用户信息
    user = session.query(User).filter(User.username == username).first()
    #获取用户的所属组信息
    group = user.groups[0]
    insert_log = AuthLog(username=username,groupname=group.name,command=command)
    session.add(insert_log)
    session.commit()
    session.close()
