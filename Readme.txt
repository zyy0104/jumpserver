#python3.0
#__author__:Yuntu

syncdb  #初始化表结构
create_users #新建程序账号，如果判断用户已存在，更新密码；
create_groups #创建组及用户关系，如果组已经存在，则更新组用户关系
create_hosts   #创建主机，如果主机名已经存在,打印报错
create_hostusers #创建主机账号，如果存在重复账号，则更新密码
bind #将组跟主机账号绑定，如果组或主机账号存在异常，则打印报错
start   #启动程序

目录结构：
├── bin 执行目录
│   ├── command.py 回调选项
│   ├── __init__.py
│   └── yunserver.py 启动程序
├── conf
│   ├── __init__.py
│   ├── options.py 注册选项
│   └── settings.py 配置文件
├── core 核心目录
│   ├── demo_simple.log
│   ├── demo_simple.py  #paramiko模块
│   ├── __init__.py
│   ├── interactive.py #paramiko模块
│   ├── models.py  #数据库表创建调用
│   └── views.py  #选项函数
├── __init__.py
├── Readme.txt
├── share 模板
│   ├── bind.yaml
│   ├── new_group.yaml
│   ├── new_hostuser.yaml
│   ├── new_host.yaml
│   └── new_user.yaml
└── yserver.py 执行程序

