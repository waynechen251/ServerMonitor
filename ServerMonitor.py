import socket,threading,time,json,os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog

#
# waynechen251
# Server
#

sleepTime = 1 #執行暫停秒數
threadList = [] #任務清單
infoDict = {} #主機回報系統資訊彙整
threadCount = 0 #當前處理連線數
runTime = True #繼續執行程式
#View
rootTitle = "小哨兵 Ver1.0 - 2022041701"
root = None #視窗主體
Listbox_serverList = None #回報主機列表
Label_dateTime = None #最後更新時間
StringVar_dateTime = "" #最後更新時間
Label_hostName = None #主機名稱
StringVar_hostName = "" #主機名稱
Label_CpuLoading = None #CPU使用率
StringVar_CpuLoading = "" #CPU使用率
Label_CpuCount_P = None #CPU核心數
StringVar_CpuCount_P = "" #CPU核心數
Label_CpuCount_L = None #CPU執行緒數
StringVar_CpuCount_L = "" #CPU執行緒數
Label_LocalIP = None #內網網路位址
StringVar_LocalIP = "" #內網網路位址
Label_InternetIP = None #外網網路位址
StringVar_InternetIP = "" #外網網路位址
Label_clientVersion = None #回報端版本
StringVar_clientVersion = "" #回報端版本
Label_os_name = None #os_name
StringVar_os_name = "" #os_name
Label_sys_platform = None #sys_platform
StringVar_sys_platform = "" #sys_platform
Label_platform_system = None #platform_system
StringVar_platform_system = "" #platform_system
Label_bit = None #回報端版本
StringVar_bit = "" #回報端版本

#当新的客户端连入时会调用这个方法
def onNewConnection(client_executor, addr):
    global infoDict,threadCount
    #print('Accept new connection from %s:%s...' % addr)

    # 发送一个欢迎信息
    #client_executor.send(bytes('Welcome'.encode('utf-8')))

    # 进入死循环，读取客户端发送的信息。
    while True:
        try:
            msg = client_executor.recv(1024).decode('utf-8')

            ip = addr[0]
            port = addr[1]

            if(msg!=""):
                infoDict_temp = json.loads(msg)
                infoDict[infoDict_temp['NetWorkInfo']['LocalIP']] = infoDict_temp

                print("當前處理連線之Thread數: ",threadCount)
                print("當前紀錄之主機回報資訊: \n",infoDict,"\n")

                exist = False
                for i in range(0,Listbox_serverList.size()):
                    #print("\n\n\n",key,"\t",infoDict_temp['NetWorkInfo']['LocalIP'])
                    #print(key == infoDict_temp['NetWorkInfo']['LocalIP'])
                    if(Listbox_serverList.get(i) == infoDict_temp['NetWorkInfo']['LocalIP']):
                        exist=True

                #print("exist=",exist)
                if(not exist):
                    for i in range(0,Listbox_serverList.size()):
                        Listbox_serverList.selection_clear(i,None)

                    Listbox_serverList.insert(tk.END,infoDict_temp['NetWorkInfo']['LocalIP'])
                    Listbox_serverList.selection_set(Listbox_serverList.size()-1,None)
                #print('%s:%s: %s' % (addr[0], addr[1], msg))

                updateView(Listbox_serverList.curselection())
        except:
            break
    client_executor.close()
    threadCount = threadCount-1
    #print('Connection from %s:%s closed.' % addr)

#監聽Server回報連線
def listenNewConnection():
    global threadCount

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    LocalIP = s.getsockname()[0]
    s.close()
    # 构建Socket实例、设置端口号和监听队列大小
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind((LocalIP, 666))
    listener.listen(5)
    #print('Waiting for connect...')

    # 进入死循环，等待新的客户端连入。一旦有客户端连入，就分配一个线程去做专门处理。然后自己继续等待。
    while runTime:
        client_executor, addr = listener.accept()
        t = threading.Thread(target=onNewConnection, args=(client_executor, addr))
        t.start()
        threadCount = threadCount+1

#定義任務清單
def initThread():
    global threadList

    taskList = [main,listenNewConnection]
    for task in taskList:
        t = threading.Thread(target=task,args=())
        threadList.append(t)

#啟動任務
def startThread():
    for i in threadList:
        i.start()
    for i in threadList:
        i.join()

##View
def creat_label(_win, _text, _row, _column): #文字,行,列
    temp = ttk.Label(_win, text=_text)
    temp.grid(row=_row, column=_column)
    return temp

def creat_button(_win, _text, _command, _row, _column): #文字,事件,行,列
    temp = ttk.Button(_win, text=_text, command=_command)
    temp.grid(row=_row, column=_column)
    return temp

def creat_text(_win, _height, _width,_row,_column):
    temp = tk.Text(root, height=_height, width=_width)
    temp.grid(row=_row, column=_column)
    return temp

def creat_Listbox(_win, _height, _width,_row,_column):
    temp = tk.Listbox(root, height=_height, width=_width)
    temp.grid(row=_row, column=_column)
    return temp

#刷新介面資訊
def updateView(index):
    global Label_dateTime,Label_hostName,Label_CpuLoading,Label_CpuCount_P,Label_CpuCount_L,Label_LocalIP,Label_InternetIP,Label_RamLoading,Label_RamTotal,Label_RamUsed,Label_RamFree,Label_clientVersion,Label_os_name,Label_sys_platform,Label_platform_system,Label_bit
    global StringVar_dateTime,StringVar_hostName,StringVar_CpuLoading,StringVar_CpuCount_P,StringVar_CpuCount_P,StringVar_LocalIP,StringVar_InternetIP,StringVar_RamLoading,StringVar_RamTotal,StringVar_RamUsed,StringVar_RamFree,StringVar_clientVersion,StringVar_os_name,StringVar_sys_platform,StringVar_platform_system,StringVar_bit

    #row 0
    StringVar_dateTime = infoDict[Listbox_serverList.get(index)]['OtherInfo']['dateTime']
    Label_dateTime.config(text=f"最後更新時間: {StringVar_dateTime}")

    StringVar_clientVersion = infoDict[Listbox_serverList.get(index)]['OtherInfo']['clientVersion']
    Label_clientVersion.config(text=f"Client Version: {StringVar_clientVersion}")

    StringVar_os_name = infoDict[Listbox_serverList.get(index)]['OtherInfo']['os_name']
    Label_os_name.config(text=f"os_name: {StringVar_os_name}")

    StringVar_sys_platform = infoDict[Listbox_serverList.get(index)]['OtherInfo']['sys_platform']
    Label_sys_platform.config(text=f"sys_platform: {StringVar_sys_platform}")

    StringVar_platform_system = infoDict[Listbox_serverList.get(index)]['OtherInfo']['platform_system']
    Label_platform_system.config(text=f"platform_system: {StringVar_platform_system}")

    StringVar_bit = infoDict[Listbox_serverList.get(index)]['OtherInfo']['bit']
    Label_bit.config(text=f"系統位元: {StringVar_bit}")

    StringVar_hostName = infoDict[Listbox_serverList.get(index)]['OtherInfo']['hostName']
    Label_hostName.config(text=f"主機名稱: {StringVar_hostName}")

    StringVar_LocalIP = infoDict[Listbox_serverList.get(index)]['NetWorkInfo']['LocalIP']
    Label_LocalIP.config(text=f"內網網路位址: {StringVar_LocalIP}")

    StringVar_InternetIP = infoDict[Listbox_serverList.get(index)]['NetWorkInfo']['InternetIP']
    Label_InternetIP.config(text=f"外網網路位址: {StringVar_InternetIP}")

    StringVar_CpuLoading = infoDict[Listbox_serverList.get(index)]['CpuInfo']['CpuLoading']
    Label_CpuLoading.config(text=f"CPU使用率: {StringVar_CpuLoading} %")

    StringVar_CpuCount_P = infoDict[Listbox_serverList.get(index)]['CpuInfo']['CpuCount_P']
    Label_CpuCount_P.config(text=f"CPU核心數: {StringVar_CpuCount_P}")

    StringVar_CpuCount_L = infoDict[Listbox_serverList.get(index)]['CpuInfo']['CpuCount_L']
    Label_CpuCount_L.config(text=f"CPU執行緒數: {StringVar_CpuCount_L}")

    StringVar_RamLoading = infoDict[Listbox_serverList.get(index)]['RamInfo']['RamLoading']
    Label_RamLoading.config(text=f"記憶體使用率: {StringVar_RamLoading} %")

    StringVar_RamTotal = infoDict[Listbox_serverList.get(index)]['RamInfo']['RamTotal']
    Label_RamTotal.config(text=f"記憶體總容量: {StringVar_RamTotal} GB")

    StringVar_RamUsed = infoDict[Listbox_serverList.get(index)]['RamInfo']['RamUsed']
    Label_RamUsed.config(text=f"已使用記憶體容量: {StringVar_RamUsed} GB")

    StringVar_RamFree = infoDict[Listbox_serverList.get(index)]['RamInfo']['RamFree']
    Label_RamFree.config(text=f"可用記憶體容量: {StringVar_RamFree} GB")

def main():
    global runTime,root,Listbox_serverList,threadList
    global Label_dateTime,Label_hostName,Label_CpuLoading,Label_CpuCount_P,Label_CpuCount_L,Label_LocalIP,Label_InternetIP,Label_RamLoading,Label_RamTotal,Label_RamUsed,Label_RamFree,Label_clientVersion,Label_os_name,Label_sys_platform,Label_platform_system,Label_bit
    global StringVar_dateTime,StringVar_hostName,StringVar_CpuLoading,StringVar_CpuCount_P,StringVar_CpuCount_P,StringVar_LocalIP,StringVar_InternetIP,StringVar_RamLoading,StringVar_RamTotal,StringVar_RamUsed,StringVar_RamFree,StringVar_clientVersion,StringVar_os_name,StringVar_sys_platform,StringVar_platform_system,StringVar_bit

    root = tk.Tk()
    root.resizable(False, False)
    root.title(rootTitle)
    root.geometry("800x400")

    row = 0
    StringVar_dateTime = "最後更新時間: "
    Label_dateTime = creat_label(root, StringVar_dateTime, row, 0)

    StringVar_clientVersion = "Client Version: "
    Label_clientVersion = creat_label(root, StringVar_clientVersion, row, 1)

    row = 1
    StringVar_hostName = "主機名稱: "
    Label_hostName = creat_label(root, StringVar_hostName, row, 0)
    StringVar_LocalIP = "內網網路位址: "
    Label_LocalIP = creat_label(root, StringVar_LocalIP, row, 1)
    StringVar_InternetIP = "外網網路位址: "
    Label_InternetIP = creat_label(root, StringVar_InternetIP, row, 2)

    row = 2
    StringVar_os_name = "os_name: "
    Label_os_name = creat_label(root, StringVar_os_name, row, 0)
    StringVar_sys_platform = "sys_platform: "
    Label_sys_platform = creat_label(root, StringVar_sys_platform, row, 1)
    StringVar_platform_system = "platform_system: "
    Label_platform_system = creat_label(root, StringVar_platform_system, row, 2)
    StringVar_bit = "系統位元: "
    Label_bit = creat_label(root, StringVar_bit, row, 3)

    row = 3
    StringVar_CpuLoading = "CPU使用率: "
    Label_CpuLoading = creat_label(root, StringVar_CpuLoading, row, 0)
    StringVar_CpuCount_P = "CPU核心數: "
    Label_CpuCount_P = creat_label(root, StringVar_CpuCount_P, row, 1)
    StringVar_CpuCount_L = "CPU執行緒數: "
    Label_CpuCount_L = creat_label(root, StringVar_CpuCount_L, row, 2)

    row = 4
    StringVar_RamLoading = "記憶體使用率: "
    Label_RamLoading = creat_label(root, StringVar_RamLoading, row, 0)
    StringVar_RamTotal = "記憶體總容量: "
    Label_RamTotal = creat_label(root, StringVar_RamTotal, row, 1)
    StringVar_RamUsed = "已使用記憶體容量: "
    Label_RamUsed = creat_label(root, StringVar_RamUsed, row, 2)
    StringVar_RamFree = "可用記憶體容量: "
    Label_RamFree = creat_label(root, StringVar_RamFree, row, 3)

    Listbox_serverList = creat_Listbox(root,20,110,100,0) #連線列表
    Listbox_serverList.grid(row=101, column=0, columnspan=5, sticky=tk.S + tk.W + tk.E + tk.N)
    scroll = ttk.Scrollbar(orient="vertical",command=Listbox_serverList.yview)
    Listbox_serverList.config(yscrollcommand = scroll.set)
    scroll.grid(row=101,column=5, sticky=tk.S + tk.W + tk.E + tk.N)

    root.mainloop()
    runTime = False
##View

initThread()
startThread()