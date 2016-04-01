#-*- coding:utf8 -*-

import sys
from conf.options import actions

def help_msg():
    """
    打印可选操作参数
    :return:
    """
    for k,v in actions.items():
        print (k)

def from_command_run(argvs):
    #如果不跟选项，打印帮助，退出
    if len(argvs) < 2:
        help_msg()
        exit()
    #如果选项不存在，报错退出
    if argvs[1] not in actions:
        sys.stderr.write('\033[1;33mOptions [%s] is not exists;\33[0m')
        exit()
    #将参数传递给函数，根据views执行相应操作
    actions[argvs[1]](argvs[1:])
