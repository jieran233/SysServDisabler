import sys
import os
import time
import easygui as g

if(sys.platform != 'win32'):
    sys.exit(1)

def cmd(cmd):
    res = os.popen(cmd)
    output_str = res.read() # 获得输出字符串
    return(output_str)


# START_TYPE 启动类型
# AUTO_START(自动), DEMAND_START(手动), DISABLED(禁用)
# 程序中直接使用startType[i]即可
startType = ['AUTO_START', 'DEMAND_START', 'DISABLED']
services = []
cmds=[]

def viewServStartType(serv):
    output = cmd("sc qc \"" + serv  + "\"")
    # print(output)
    for i in range(len(startType)):
        type = startType[i]
        count = output.count(type)
        # print(count)
        if (count == 1):
            return(type)

def AdminBat():
    RUN_AS_ADMIN = open('run_as_admin.txt', 'r').read()
    # runPath = sys.path[0] + '\\runtemp.bat'
    tmpFile = open('temp.bat', 'w')
    n = len(cmds)
    Cmd = ''
    for i in range(n):
        if (i == (n-1)):    #避免输出空行
            Cmd = Cmd + cmds[i] + '>>output.txt'
        else:
            Cmd = Cmd + cmds[i] + '>>output.txt\n'
    tmpFile.write(RUN_AS_ADMIN + '\n' + Cmd)
    return

def disableServ(serv):
    cmds.append("sc stop \"" + serv  + "\"")
    cmds.append("sc config \"" + serv  + "\" start= disabled")
    return

def enableServ(serv, type):
    if (type == startType[0]):
        cmds.append("sc config \"" + serv  + "\" start= auto")
    elif (type == startType[1]):
        cmds.append("sc config \"" + serv  + "\" start= demand")
    return

def backup():
    servFile = open('backup_serv.txt', 'w')
    typeFile = open('backup_type.txt', 'w')
    n = len(services)
    print(n)
    for i in range(n):
        serv = services[i]
        type = viewServStartType(serv)
        if (i == (n-1)):    #避免输出空行
            servFile.write(serv)
            typeFile.write(type)
        else:
            servFile.write(serv + '\n')
            typeFile.write(type + '\n')
    return('已备份。')

def afterBat():
    # 仅支持系统语言为简体中文
    output = open('output.txt', 'r').read()
    print(output)
    succeeded = output.count('成功')
    failed = output.count('失败')
    time.sleep(2)
    print(cmd('del temp.bat output.txt'))
    return('完成。成功' + str(succeeded) + '个，失败' + str(failed - succeeded) + '个。')

def reset():
    cmds.clear()
    servs = open('backup_serv.txt', 'r').read().split('\n')
    types = open('backup_type.txt', 'r').read().split('\n')
    for i in range(len(servs)):
        enableServ(servs[i], types[i])
    AdminBat()
    time.sleep(1)
    cmd("start temp.bat")
    return

def disable():
    cmds.clear()
    servs = open('backup_serv.txt', 'r').read().split('\n')
    for i in range(len(servs)):
        disableServ(servs[i])
    AdminBat()
    time.sleep(1)
    cmd("start temp.bat")
    return

def init():
    original = open('the_disabled_list.txt', 'r', encoding='utf-8').read().split('\n')    # 以UTF-8打开文件以适配文件中的中文注释
    for line in original:
        line = line.strip() # 去掉每行头尾空白
        if (not len(line) or line.startswith('#')): # 判断是否是空行或注释行
            continue    # 跳过当前for循环
        services.append(line)   # 输出结果到services
    services.sort() # 排序结果
    print(services)

    types = ''
    for i in range(len(services)):
        types = types + services[i] + '\t\t\t\t' + viewServStartType(services[i]) + "\n"
    summary = '禁用服务列表中共 ' + str(len(services)) + ' 个服务，其中 '+ str(types.count('DISABLED')) +' 个处于禁用状态'

    choices = ['查看：查看列表中服务及其状态', '备份：备份列表中服务及其状态（警告：将会覆盖现有备份）', '禁用：使列表中全部服务处于禁用状态', '还原：还原备份的数据']
    reply = g.choicebox(summary + '。\n\n选择一个操作：', 'SysServDisabler',choices = choices)
    if (reply == choices[0]):
        g.msgbox(types, summary)
        sys.exit(0)
    elif (reply == choices[1]):
        g.msgbox(backup(), 'Done.')
        sys.exit(0)

    elif (reply == choices[2]):
        disable()
    elif (reply == choices[3]):
        reset()

if (__name__ == '__main__'):
    init()
    while (True):
        if (os.path.exists('output.txt')):
            g.msgbox(afterBat(), 'Done.')
            sys.exit(0)  
        time.sleep(1)