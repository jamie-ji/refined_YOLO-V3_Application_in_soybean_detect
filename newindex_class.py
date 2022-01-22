############################################################
#  
#  author: jamie                                             
#  e-mail: jamieji0615@gmail.com                                      
#  version: 1.0
#  brief introduction: This software is based on yolov3 algorithm of improved loss function, and develops soybean seedling management system.                                              
#                                                                              
############################################################

from tkinter.constants import TRUE
from typing import Optional
import pyzbar.pyzbar as pyzbar
from PIL import Image, ImageDraw, ImageFont
from weathe_data import getcitycode, getweather
from PyQt5.QtWidgets import QApplication, QMainWindow,QMessageBox
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtGui import QPixmap
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QMainWindow, QTextEdit, QAction, QApplication
import os
from PIL import Image
import cv2
from login_GUI import Login_MainWindow
from newindex_GUI import newindex_MainWindow
import xlrd     #excel读库
import xlwt     #excel写库
import webbrowser
import requests
import pymysql
import time
from detect import detect
import argparse
import torch
from utils.general import strip_optimizer
import globalvar as gl
from PyQt5.QtCore import *
import xlrd     #excel读库
import xlwt     #excel写库
from xlutils.copy import copy
import imutils
from borax.calendars.lunardate import LunarDate


class newindex_MainWindow(QtWidgets.QMainWindow,newindex_MainWindow):


    def __init__(self):
        super(newindex_MainWindow,self).__init__()
        self.cwd=os.getcwd()
        self.setupUi(self)  
    
    
    ################################
    #快捷导航
    ################################
    def webbrowser_click_nyxx(self):
        try:
            webbrowser.get('chrome').open_new_tab('http://www.agri.cn/')
        except Exception as e:
            webbrowser.open_new_tab('http://www.agri.cn/')
    def webbrowser_click_zgdd(self):
        try:
            webbrowser.get('chrome').open_new_tab('http://www.dadou.biz/')
        except Exception as e:
            webbrowser.open_new_tab('http://www.dadou.biz/')
    def webbrowser_click_dj(self):
        try:
            webbrowser.get('chrome').open_new_tab('https://www.dji.com/cn')
        except Exception as e:
            webbrowser.open_new_tab('https://www.dji.com/cn')
    def webbrowser_click_njau(self):
        try:
            webbrowser.get('chrome').open_new_tab('http://www.njau.edu.cn/')
        except Exception as e:
            webbrowser.open_new_tab('http://www.njau.edu.cn/')
   
    ################################
    #获取天气以及时间
    ################################
    def getweatheranddate(self):
        cityname=self.comboBox_2.currentText()
        db=pymysql.connect(host="localhost",user="root",password="123456",db="yolo",port=3306)
        cur=db.cursor()
        sql="select citycode from Situation where cityname=%s"
        cur.execute(sql,cityname)
        result=cur.fetchall()       #查询的值保存在result中
        #print(result[0][0])
        citycode=result[0][0]
        
        
        #print(citycode)
        r=requests.get("http://www.weather.com.cn/data/sk/"+str(citycode)+".html")
        r.encoding='utf-8'
        self.outtextBroswer("城市:"+str(r.json()['weatherinfo']['city'])+" 平均温度为:"+str(r.json()['weatherinfo']['temp'])+"℃"+" 风况为："+str(r.json()['weatherinfo']['WD']))
        
        localtime=time.localtime(time.time())
        lunar=LunarDate.today()
        #print(localtime)
        self.outtextBroswer_9(str(localtime.tm_year)+"年"+str(localtime.tm_mon)+"月"+str(localtime.tm_mday)+"日"+" 星期"+str(localtime.tm_wday+1)+" 农历时间："+str(lunar.year)+"年"+str(lunar.month)+"月"+str(lunar.day)+"日")
    
    ################################
    #导入新数据，并为之创建数据表
    # 1.向soybean表中导入数据
    # 2.扫描每张图片的二维码，将数据写入数据库  
    #文件夹名必须不同才能生成不同的数据表！！！
    ################################
    def upload_newdata(self):
        self.dic_path=QtWidgets.QFileDialog.getExistingDirectory(None,"选取读取的文件夹","C:/")
        dirs=os.listdir(self.dic_path)

        db=pymysql.connect(host="localhost",user="root",password="123456",db="yolo",port=3306)
        #print(result[1][0])     #WY002是1
        localtime=time.localtime(time.time())
        opetime=str(localtime.tm_year)+"/"+str(localtime.tm_mon)+"/"+str(localtime.tm_mday)

        for file in dirs:
            cur=db.cursor()
            sql="select strain from soybean"
            cur.execute(sql)
            result=cur.fetchall()
            flag=False  
            path=str(self.dic_path)+'/'+str(file)
            #print(path1)
            try:
                count,resultstrain,pos,bestdate,history,xixing,lishishijian,bozhongshu,bozhongdate=self.multipleqrcode(path)
                #strain,bestdate,history,xixing,lishishijian,bozhongshu,bozhongdate=Qrcode.decodegetname(path)
            
            except:
                reply=QMessageBox.question(self,'系统提示','所传图片存在没有二维码的情况！请检查图片',QMessageBox.Ok)
                #YES的返回值为0x40000
                if(reply==0x4000):
                    from newindex_class import newindex_MainWindow
                    #加个self
                    self.index=newindex_MainWindow()
                    self.index.show()
                    self.close()
            #print(count)
            if(count!=1):     
                #!!!
                #print(count)
                for i in range(count):
                    if(len(result)!=0):
                        for j in range(0,len(result)):
                            if(resultstrain[i]==result[j][0]):
                                cur.execute("select situation1 from soybean where strain='%s'"%(resultstrain[i]))
                                situation1=cur.fetchall()
                                cur.execute("select situation2 from soybean where strain='%s'"%(resultstrain[i]))
                                situation2=cur.fetchall()
                                cur.execute("select situation3 from soybean where strain='%s'"%(resultstrain[i]))
                                situation3=cur.fetchall()

                                #print(situation1[0][0])
                                #print(situation2[0][0])
                                #print(situation3[0][0])

                                if(situation1[0][0]!='0' and situation2[0][0]=='0'): 
                                    #print("1")   
                                    cur.execute("update soybean set bestdate='%s',history='%s',xixing='%s',lishishijian='%s',bozhongshu='%s',bozhongdate='%s',situation2='%s' where strain='%s'" % (bestdate[i],history[i],xixing[i],lishishijian[i],bozhongshu[i],bozhongdate[i],path,resultstrain[i]))
                                    #更新日志
                                    cur.execute("insert into journal (operation,date) values('%s','%s')" % (str("更新数据，数据路径："+path),str(opetime)))
                                    
                                    db.commit()
                                    flag=True
                                    #print("发现重复，进行更新")  
                                    break
                                if(situation2[0][0]!='0' and situation3[0][0]=='0'):
                                    #print("2")   
                                    cur.execute("update soybean set bestdate='%s',history='%s',xixing='%s',lishishijian='%s',bozhongshu='%s',bozhongdate='%s',situation3='%s' where strain='%s'" % (bestdate[i],history[i],xixing[i],lishishijian[i],bozhongshu[i],bozhongdate[i],path,resultstrain[i]))
                                    #更新日志
                                    cur.execute("insert into journal (operation,date) values('%s','%s')" % (str("更新数据，数据路径："+path),str(opetime)))
                                    db.commit()
                                    flag=True
                                    #print("发现重复，进行更新")  
                                    break
                                if(situation3[0][0]!='0'):
                                    flag=True
                                    #print("3")
                                    #print("发现重复，进行更新")
                                                            
                            else:  
                                #print("继续找是否有重复的")
                                continue
                        if(flag==False):
                            cur.execute("insert into soybean (strain,bestdate,history,xixing,lishishijian,bozhongshu,bozhongdate,situation1,situation2,situation3) values('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" % (resultstrain[i],bestdate[i],history[i],xixing[i],lishishijian[i],bozhongshu[i],bozhongdate[i],path,'0','0'))                 
                            #更新日志
                            cur.execute("insert into journal (operation,date) values('%s','%s')" % (str("导入新数据，数据路径："+path),str(opetime)))
                            #print("插入数据")
                            db.commit()
                    #初始时会insert       
                    else:
                        cur.execute("insert into soybean (strain,bestdate,history,xixing,lishishijian,bozhongshu,bozhongdate,situation1,situation2,situation3) values('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" % (resultstrain[i],bestdate[i],history[i],xixing[i],lishishijian[i],bozhongshu[i],bozhongdate[i],path,'0','0'))
                        #更新日志
                        cur.execute("insert into journal (operation,date) values('%s','%s')" % (str("导入新数据，数据路径："+path),str(opetime)))
                        db.commit()              
                        #print("数据第一次加入") 

            
            else:
                if(len(result)!=0):
                    for i in range(0,len(result)):
                        if(resultstrain[0]==result[i][0]):
                            cur.execute("select situation1 from soybean where strain='%s'"%(resultstrain[0]))
                            situation1=cur.fetchall()
                            cur.execute("select situation2 from soybean where strain='%s'"%(resultstrain[0]))
                            situation2=cur.fetchall()
                            cur.execute("select situation3 from soybean where strain='%s'"%(resultstrain[0]))
                            situation3=cur.fetchall()

                            #print(situation1[0][0])
                            #print(situation2[0][0])
                            #print(situation3[0][0])

                            if(situation1[0][0]!='0' and situation2[0][0]=='0'): 
                                #print("1")   
                                cur.execute("update soybean set bestdate='%s',history='%s',xixing='%s',lishishijian='%s',bozhongshu='%s',bozhongdate='%s',situation2='%s' where strain='%s'" % (bestdate[0],history[0],xixing[0],lishishijian[0],bozhongshu[0],bozhongdate[0],path,resultstrain[0]))
                                #更新日志
                                cur.execute("insert into journal (operation,date) values('%s','%s')" % (str("更新数据，数据路径："+path),str(opetime)))
                                
                                db.commit()
                                flag=True
                                #print("发现重复，进行更新")  
                                break
                            if(situation2[0][0]!='0' and situation3[0][0]=='0'):
                                #print("2")   
                                cur.execute("update soybean set bestdate='%s',history='%s',xixing='%s',lishishijian='%s',bozhongshu='%s',bozhongdate='%s',situation3='%s' where strain='%s'" % (bestdate[0],history[0],xixing[0],lishishijian[0],bozhongshu[0],bozhongdate[0],path,resultstrain[0]))
                                #更新日志
                                cur.execute("insert into journal (operation,date) values('%s','%s')" % (str("更新数据，数据路径："+path),str(opetime)))
                                db.commit()
                                flag=True
                                #print("发现重复，进行更新")  
                                break
                            if(situation3[0][0]!='0'):
                                flag=True
                                #print("3")
                                #print("发现重复，进行更新")
                                                        
                        else:  
                            #print("继续找是否有重复的")
                            continue
                    if(flag==False):
                        cur.execute("insert into soybean (strain,bestdate,history,xixing,lishishijian,bozhongshu,bozhongdate,situation1,situation2,situation3) values('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" % (resultstrain[0],bestdate[0],history[0],xixing[0],lishishijian[0],bozhongshu[0],bozhongdate[0],path,'0','0'))                 
                        #更新日志
                        cur.execute("insert into journal (operation,date) values('%s','%s')" % (str("导入新数据，数据路径："+path),str(opetime)))
                        #print("插入数据")
                        db.commit()
                #初始时会insert       
                else:
                    cur.execute("insert into soybean (strain,bestdate,history,xixing,lishishijian,bozhongshu,bozhongdate,situation1,situation2,situation3) values('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" % (resultstrain[0],bestdate[0],history[0],xixing[0],lishishijian[0],bozhongshu[0],bozhongdate[0],path,'0','0'))
                    #更新日志
                    cur.execute("insert into journal (operation,date) values('%s','%s')" % (str("导入新数据，数据路径："+path),str(opetime)))
                    db.commit()              
                    #print("数据第一次加入") 

        
        reply=QMessageBox.question(self,'系统提示','图片已上传！',QMessageBox.Ok)
        #YES的返回值为0x40000
        if(reply==0x4000):
            from newindex_class import newindex_MainWindow
             #加个self
            self.index=newindex_MainWindow()
            self.index.show()
            self.close()   
        db.close()

    ################################
    #生成二维码
    ################################
    def ToQrcode(self):
        #from Qrcode_class import Qrcode_MainWindow
        from Qrcode_excel_class import Qrcode_excel_MainWindow
        
        #加个self
        self.qrcode=Qrcode_excel_MainWindow()
        self.qrcode.show()
        self.close()

    ################################
    # 搜索数据库信息（已删除功能）
    # 1.获取text文本框内容，遍历数据库
    # 2.将相关信息打印到输出文本框
    ################################
    def searchstrain(self):
        
        strain=self.textEdit_6.toPlainText()
        sql='select strain,lishishijian,bozhongshu,bozhongdate,emergenum from soybean where strain=%s'
        db=pymysql.connect(host="localhost",user="root",password="123456",db="yolo",port=3306)
        cur=db.cursor()

        localtime=time.localtime(time.time())
        opetime=str(localtime.tm_year)+"/"+str(localtime.tm_mon)+"/"+str(localtime.tm_mday)
        try:
            
            
            #更新日志
            cur.execute("insert into journal (operation,date) values('%s','%s')" % (str("查询数据集"+strain),str(opetime)))
            db.commit()
           
            cur.execute(sql,strain)
            result=cur.fetchall()       #查询的值保存在result中
            #print(result[0][3])
            #self.outtextBroswer_2("最佳播种时间："+result[0][0]+"\n"+"历史产量："+result[0][1]+"\n"+"结荚习性："+result[0][2]+"\n"+"历史发育周期："+result[0][3]+"\n"+"播种数："+result[0][4])
            items = self.listWidget.findItems(strain, Qt.MatchContains)
            #print(type(items),items)
        
        
        
        except:
            reply=QMessageBox.question(self,'系统提示','输入品种名非法，请检查是否正确输入或是否已经存入数据库中！',QMessageBox.Ok)
            #YES的返回值为0x40000
            if(reply==0x4000):
                from newindex_class import newindex_MainWindow
                #加个self
                self.index=newindex_MainWindow()
                self.index.show()
                self.close()   
               
    ################################
    #根据不同的实际田块，来生产专属的拍摄方案，保存在txt文件中。
    # 1. 读取3个文本框的信息，根据转换公式来生成建议飞行高度以及飞行模式
    # 2. 将田块信息导入到数据库中
    ################################
    def createsolutionforline(self):
        

        linespan=float(self.textEdit_8.toPlainText())
        linelong=float(self.textEdit_9.toPlainText())

        #如果行距小于0.4m建议1m
        #行距在0.4-0.9建议飞行高度1.5m或一次拍一行
        #行距在0.9m以上建议2m或一次拍一行

        #行长度在在1.5m以内，1m能够覆盖，建议1m直飞
        #行长度在1.5-2.3m之间，1.5能够覆盖，建议1.5m直飞
        #行长度在2.3m-3m之间，2m能够覆盖，2m直飞
        #3m以上，需要S型飞，需填写下面times

        if(linespan<=0.4 and linelong<=1.5):
            strout="建议飞行高度：1m"+"飞行模式：直飞"
        if(linespan<=0.4 and 1.5<linelong<2.3):
            strout="建议飞行高度：1m"+"飞行模式：S型飞行"
        if(linespan<=0.4 and linelong>=2.3):
            strout="建议飞行高度：1m"+"飞行模式：S型飞行"
        
        if(0.4<linespan<0.9 and linelong<=1.5):
            strout="建议飞行高度：1.5m"+"飞行模式：直飞"
        if(0.4<linespan<0.9 and 1.5<linelong<2.3):
            strout="建议飞行高度：1.5m"+"飞行模式：S型飞行"  
        if(0.4<linespan<0.9 and linelong>=2.3):
            strout="建议飞行高度：1.5m"+"飞行模式：S型飞行" 

        if(linespan>=0.9 and linelong<=1.5):
            strout="建议飞行高度：2m"+"飞行模式：直飞"
        if(linespan>=0.9 and 1.5<linelong<2.3):
            strout="建议飞行高度：2m"+"飞行模式：S型飞行"  
        if(linespan>=0.9 and linelong>=2.3):
            strout="建议飞行高度：2m"+"飞行模式：S型飞行" 

        blockname=self.textEdit.toPlainText()
        blockwidth=self.textEdit_2.toPlainText()
        blocklong=self.textEdit_5.toPlainText()
        
        #加入到数据库
        db=pymysql.connect(host="localhost",user="root",password="123456",db="yolo",port=3306)
        cur=db.cursor()

        #sql="insert into soybean values('%s','%s','%s','%s','%s','%s','%s')"
        sql="select tname from field"
        cur.execute(sql)
        result=cur.fetchall()
        
        localtime=time.localtime(time.time())
        opetime=str(localtime.tm_year)+"/"+str(localtime.tm_mon)+"/"+str(localtime.tm_mday)
       
        flag=False 
        if(len(result)!=0):
            for i in range(0,len(result)):
                if(blockname==result[i][0]):
                    cur.execute("select tflydate1 from field where tname='%s'"%(blockname))
                    situation1=cur.fetchall()
                    cur.execute("select tflydate2 from field where tname='%s'"%(blockname))
                    situation2=cur.fetchall()
                    cur.execute("select tflydate3 from field where tname='%s'"%(blockname))
                    situation3=cur.fetchall()

                    #print(situation1[0][0])
                    #print(situation2[0][0])
                    #print(situation3[0][0])

                    if(situation1[0][0]!='0' and situation2[0][0]=='0'): 
                        #print("1")   
                        cur.execute("update field set tlong='%s',twidth='%s',tflydate2='%s',fangan2='%s' where tname='%s'" % (blocklong,blockwidth,str(opetime),strout,blockname))
                        #更新日志
                        cur.execute("insert into journal (operation,date) values('%s','%s')" % ("更新田间数据",str(opetime)))
                        
                        db.commit()
                        flag=True
                        #print("发现重复，进行更新")  
                        break
                    if(situation2[0][0]!='0' and situation3[0][0]=='0'):
                        #print("2")   
                        cur.execute("update field set tlong='%s',twidth='%s',tflydate3='%s',fangan3='%s' where tname='%s'" % (blocklong,blockwidth,str(opetime),strout,blockname))
                        #更新日志
                        cur.execute("insert into journal (operation,date) values('%s','%s')" % ("更新田间数据",str(opetime)))
                        db.commit()
                        flag=True
                        #print("发现重复，进行更新")  
                        break
                    if(situation3[0][0]!='0'):
                        flag=True
                        #print("3")
                        #print("发现重复，进行更新")
                                                
                else:  
                    #print("继续找是否有重复的")
                    continue
            if(flag==False):
                cur.execute("insert into field (tname,tlong,twidth,tflydate1,fangan1,tflydate2,fangan2,tflydate3,fangan3) values('%s','%s','%s','%s','%s','%s','%s','%s','%s')" % (blockname,blocklong,blockwidth,str(opetime),strout,'0','0','0','0'))                 
                #更新日志
                cur.execute("insert into journal (operation,date) values('%s','%s')" % ("更新田间数据",str(opetime)))
                #print("插入数据")
                db.commit()
        #初始时会insert       
        else:
            cur.execute("insert into field (tname,tlong,twidth,tflydate1,fangan1,tflydate2,fangan2,tflydate3,fangan3) values('%s','%s','%s','%s','%s','%s','%s','%s','%s')" % (blockname,blocklong,blockwidth,str(opetime),strout,'0','0','0','0'))
            #更新日志
            cur.execute("insert into journal (operation,date) values('%s','%s')" % ("导入田间数据",str(opetime)))
            db.commit()              
            #print("数据第一次加入") 

        reply=QMessageBox.information(self,'专属拍照方案保存在桌面',strout,QMessageBox.Ok)
        
        self.txtsaveplace="fangan.txt"
        #方案保存在根目录txt中：
        with open("fangan.txt","w") as f:
            f.write(str(strout))  # 自带文件关闭功能，不需要再写f.close()

        
        #print(result)        # 返回字符串：ok
        
    ################################
    #操作类似
    ################################
    def createsolutionforblock(self):
        blockname=self.textEdit.toPlainText()
        blockwidth=self.textEdit_2.toPlainText()
        blocklong=self.textEdit_5.toPlainText()
        
        #加入到数据库
        db=pymysql.connect(host="localhost",user="root",password="123456",db="yolo",port=3306)
        cur=db.cursor()

        #sql="insert into soybean values('%s','%s','%s','%s','%s','%s','%s')"
        sql="select tname from field"
        cur.execute(sql)
        result=cur.fetchall()
        
        localtime=time.localtime(time.time())
        opetime=str(localtime.tm_year)+"/"+str(localtime.tm_mon)+"/"+str(localtime.tm_mday)
        
        flag=False 
        if(len(result)!=0):
            for i in range(0,len(result)):
                if(blockname==result[i][0]):
                    cur.execute("select tflydate1 from field where tname='%s'"%(blockname))
                    situation1=cur.fetchall()
                    cur.execute("select tflydate2 from field where tname='%s'"%(blockname))
                    situation2=cur.fetchall()
                    cur.execute("select tflydate3 from field where tname='%s'"%(blockname))
                    situation3=cur.fetchall()

                    #print(situation1[0][0])
                    #print(situation2[0][0])
                    #print(situation3[0][0])

                    if(situation1[0][0]!='0' and situation2[0][0]=='0'): 
                        #print("1")   
                        cur.execute("update field set tlong='%s',twidth='%s',tflydate2='%s' where tname='%s'" % (blocklong,blockwidth,str(opetime),blockname))
                        #更新日志
                        cur.execute("insert into journal (operation,date) values('%s','%s')" % ("更新田间数据",str(opetime)))
                        
                        db.commit()
                        flag=True
                        #print("发现重复，进行更新")  
                        break
                    if(situation2[0][0]!='0' and situation3[0][0]=='0'):
                        #print("2")   
                        cur.execute("update field set tlong='%s',twidth='%s',tflydate3='%s' where tname='%s'" % (blocklong,blockwidth,str(opetime),blockname))
                        #更新日志
                        cur.execute("insert into journal (operation,date) values('%s','%s')" % ("更新田间数据",str(opetime)))
                        db.commit()
                        flag=True
                        #print("发现重复，进行更新")  
                        break
                    if(situation3[0][0]!='0'):
                        flag=True
                        #print("3")
                        #print("发现重复，进行更新")
                                                
                else:  
                    #print("继续找是否有重复的")
                    continue
            if(flag==False):
                cur.execute("insert into field (tname,tlong,twidth,tflydate1,tflydate2,tflydate3) values('%s','%s','%s','%s','%s','%s')" % (blockname,blocklong,blockwidth,str(opetime),'0','0'))                 
                #更新日志
                cur.execute("insert into journal (operation,date) values('%s','%s')" % ("更新田间数据",str(opetime)))
                #print("插入数据")
                db.commit()
        #初始时会insert       
        else:
            cur.execute("insert into field (tname,tlong,twidth,tflydate1,tflydate2,tflydate3) values('%s','%s','%s','%s','%s','%s')" % (blockname,blocklong,blockwidth,str(opetime),'0','0'))
            #更新日志
            cur.execute("insert into journal (operation,date) values('%s','%s')" % ("导入田间数据",str(opetime)))
            db.commit()              
            #print("数据第一次加入") 



        blockwidth=float(self.textEdit_7.toPlainText())
        blocklong=float(self.textEdit_6.toPlainText())

        #块宽<=0.8,块长<=1.5m  高度1m，直飞

        #0.8<块宽<1.3,块长<1.5m，高度1.5m
        if(blockwidth<=0.8 and blocklong<=1.5):
            strout="建议飞行高度：1m"+"飞行模式：直飞"
        if(0.8<blockwidth<1.3 and blocklong<=1.5):
            strout="建议飞行高度：1.5m"+"飞行模式：直飞"
        if(blockwidth>=1.3 and blocklong<=1.5):
            strout="建议飞行高度：2m"+"飞行模式：直飞"
        
        if(blockwidth<=0.8 and 1.5<=blocklong<=2.3):
            strout="建议飞行高度：1.5m"+"飞行模式：直飞"
        if(0.8<blockwidth<1.3 and 1.5<=blocklong<=2.3):
            strout="建议飞行高度：1.5m"+"飞行模式：直飞"
        if(blockwidth>=1.3 and 1.5<=blocklong<=2.3):
            strout="建议飞行高度：2m"+"飞行模式：直飞"
        
        if(blockwidth<=0.8 and blocklong>2.3):
            strout="建议飞行高度：2m"+"飞行模式：直飞"
        if(0.8<blockwidth<1.3 and blocklong>1.5):
            strout="建议飞行高度：2m"+"飞行模式：直飞"
        if(blockwidth>=1.3 and blocklong>2.3):
            strout="建议飞行高度：2m"+"飞行模式：直飞"
    
        reply=QMessageBox.information(self,'专属拍照方案',strout,QMessageBox.Ok)
        
        
        #print(result)        # 返回字符串：ok
    

    #####################################
    # 刷新田块信息
    #####################################
    def refreshfield(self):

        sql="select tname,tlong,twidth,tflydate1,fangan1,tflydate2,fangan2,tflydate3,fangan3 from field"
        db=pymysql.connect(host="localhost",user="root",password="123456",db="yolo",port=3306)
        cur=db.cursor()
        cur.execute(sql)
        result=cur.fetchall()
        #print(result[0][0])
        for i in range (0,len(result)): 
            #self.jiashuju(result[i][0]+"        "+result[i][1]+"            "+str(result[i][2])+"           "+result[i][3]+"        "+result[i][4]+"            "+str(result[i][5])+"               "+result[i][6])
            self.jiashuju(str(result[i][0])+"       "+str(result[i][1])+"              "+str(result[i][2])+"      "+str(result[i][3])+"+"+str(result[i][4])+"      "+str(result[i][5])+"+"+str(result[i][6])+"      "+str(result[i][7])+"+"+str(result[i][8]))
            
            #print(str(result[i][0])+"       "+str(result[i][1])+"              "+str(result[i][2])+"      "+str(result[i][3])+"+"+str(result[i][4])+"      "+str(result[i][5])+"+"+str(result[i][6])+"      "+str(result[i][7])+"+"+str(result[i][8]))

        self.setpushbutton_14disable()


    ################################
    #！！！！！
    #修改文件名，以及文件夹名
    # 1.用户选择上传的目录
    # 2.根据飞行方案来生成不同的更改方案
    # 3.直飞表示能够一次拍满一块，无需拼接，一张图为一个
    # 4.S型飞行表示需要拼接，多次修改
    ################################
    def adaptfile(self):
        dic_path=QtWidgets.QFileDialog.getExistingDirectory(None,"选取读取的文件夹","C:/")
        dirs=os.listdir(dic_path)
        times=int(self.textEdit_10.toPlainText())       #多少张拍满
        line=int(self.textEdit_11.toPlainText())        #一张多少行
        
        k=0     #控制文件向前读
        t=1
        m=1
        #if(self.radioButton.isChecked()==True):
        if(line==1):    #表示单行，需要拼接
            for i in dirs:
                oldname=dic_path+'/'+dirs[k]
                print("old"+oldname)
                
                if(t<=times):
                    newname=dic_path+'/'+str(m)+'_'+str(t)+'.jpg'
                    print("new"+newname)
                    os.rename(oldname,newname)
                    if(t==times):
                        t=1
                        m=m+1
                    else:
                        t=t+1
                k=k+1     

        else:             #多行情况，不允许重叠
            for i in dirs:
                oldname=dic_path+'/'+dirs[k]
                print("old  "+oldname)
                
                if(t<=times):
                    newname=dic_path+'/'+str(m)+'-'+str(m+1)+'_'+str(t)+'.jpg'
                    print("new  "+newname)
                    try:
                        os.rename(oldname,newname)
                    except:
                        reply=QMessageBox.question(self,'系统提示','已经重命名完成，无需重复！',QMessageBox.Ok)
                        #YES的返回值为0x40000
                        if(reply==0x4000):
                            from newindex_class import newindex_MainWindow
                            #加个self
                            self.index=newindex_MainWindow()
                            self.index.show()
                            self.close()
                            break     
                    if(t==times):
                        t=1
                        m=m+2
                    else:
                        t=t+1
                k=k+1     #控制文件向前读
        
        reply=QMessageBox.question(self,'系统提示','重命名完成！',QMessageBox.Ok)
                                          
                    
        
    

    #直飞，直接修改即可，方便查看图片之间的关系 
    # 新名字  例如：001（1）表示拍摄时的第一行的第一张图片       
    def zhifei(self):
        dic_path=QtWidgets.QFileDialog.getExistingDirectory(None,"选取读取的文件夹","C:/")
        dirs=os.listdir(dic_path)
        n=0  
        for i in dirs:
            oldname=dic_path+'/'+dirs[n]
            print(oldname)
            newname=dic_path+'/'+str(n+1)+'.jpg'
            os.rename(oldname,newname)
            n=n+1
        reply=QMessageBox.question(self,'系统提示','重命名完成！',QMessageBox.Ok)

    ##########################
    # 生长跟踪
    ##########################
    def searchstraindate(self):
        strain=self.textEdit_4.toPlainText()
        sql='select situation1,situation2,situation3 from soybean where strain=%s'
        db=pymysql.connect(host="localhost",user="root",password="123456",db="yolo",port=3306)
        cur=db.cursor()
        try:
            cur.execute(sql,strain)
            result=cur.fetchall()       #查询的值保存在result中       
            
            #print(result)   
                
            jpg = QtGui.QPixmap(result[0][0]).scaled(self.label_17.width(), self.label_17.height())
            self.label_17.setPixmap(jpg)

            jpg = QtGui.QPixmap(result[0][1]).scaled(self.label_20.width(), self.label_20.height())
            self.label_20.setPixmap(jpg)

            jpg = QtGui.QPixmap(result[0][2]).scaled(self.label_18.width(), self.label_18.height())
            self.label_18.setPixmap(jpg)

            localtime=time.localtime(time.time())
            opetime=str(localtime.tm_year)+"/"+str(localtime.tm_mon)+"/"+str(localtime.tm_mday)
            db=pymysql.connect(host="localhost",user="root",password="123456",db="yolo",port=3306)
            cur=db.cursor()
            #更新日志
            cur.execute("insert into journal (operation,date) values('%s','%s')" % (str("查询生长记录"+strain),str(opetime)))
            db.commit()
            
        except:
            reply=QMessageBox.question(self,'系统提示','输入品种名非法，请检查是否正确输入或是否已经存入数据库中！',QMessageBox.Ok)
            #YES的返回值为0x40000
            if(reply==0x4000):
                from newindex_class import newindex_MainWindow
                #加个self
                self.index=newindex_MainWindow()
                self.index.show()
                self.close()     
    ##########################
    # 系统日志功能
    ############################
    def journal(self):
        date=self.textEdit_3.toPlainText()
        sql='select operation,date from journal where date=%s'
        db=pymysql.connect(host="localhost",user="root",password="123456",db="yolo",port=3306)
        cur=db.cursor()
        cur.execute("select operation from journal where date='%s'" % (date))
        result1=cur.fetchall()

        localtime=time.localtime(time.time())
        opetime=str(localtime.tm_year)+"/"+str(localtime.tm_mon)+"/"+str(localtime.tm_mday)
        try:
            
            #更新日志
            cur.execute("insert into journal (operation,date) values('%s','%s')" % (str("查询系统日志"),str(opetime)))
            db.commit()
           
            cur.execute(sql,date)
            result=cur.fetchall()       #查询的值保存在result中
            for i in range (0,len(result1)):
            #print(result[i][0])
                self.outtextBroswer_8("执行的操作："+result[i][0]+"\n"+"操作时间："+result[i][1])
        
        except:
            reply=QMessageBox.question(self,'系统提示','日期非法，请按格式输入或当天没有纪录',QMessageBox.Ok)
            #YES的返回值为0x40000
            if(reply==0x4000):
                from newindex_class import newindex_MainWindow
                #加个self
                self.index=newindex_MainWindow()
                self.index.show()
                self.close()      

    
    ##################################
    # 单图多二维码，返回二维码个数以及品种名称
    #################################
    def multipleqrcode(self,path):
        frame = cv2.imread(path)
        # Convert to grayscale image
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        barcodes = pyzbar.decode(gray)

        count=0
        result=[]
        pos=[]
        bestdate=[]
        history=[]
        xixing=[]
        lishishijian=[]
        bozhongshu=[]
        bozhongdate=[]
        for barcode in barcodes:
                count=count+1
                        # Extract the position of the bounding box of the barcode
                        # Draw the bounding box of the barcode in the image
                (x, y, w, h) = barcode.rect
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 0), 2)
        
                        # The barcode data is a byte object, so if we want to output the image
                        # Draw it, you need to convert it to a string first
                barcodeData = barcode.data.decode("utf-8")
                        # Draw the barcode data and barcode type on the image
                barcodeType = barcode.type
                
                        # Convert the picture in cv2 format to the picture in PIL format and mark the contents of the QR code and barcode on it
                img_PIL = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        
                        # Parameters (font, default size)
                font = ImageFont.truetype('STFANGSO.TTF', 25)
        
                        # font color 
                fillColor = (0,255,0)
        
                        # Text output location
                position = (x, y-25)
        
                        # Output content
                strl = barcodeData
                        # Need to convert the output Chinese characters into Unicode encoding form (str.decode("utf-8))
                
                        # Create brush
                #draw = ImageDraw.Draw(img_PIL)
                #draw.text(position, strl, font=font,fill=fillColor)
                        # Use the save method in PIL to save the picture locally
                #img_PIL.save('Result picture.jpg','jpeg')
                        # Print barcode data and barcode type to the terminal
                pos.append(str(position[1]))
                #分离品种名
                data=str(strl).split('\n')
                #print("scan result=="+data[0])
                newdata=str(data[0]).split(':')
                nndata=str(newdata[1]).split(' ')
                result.append(str(nndata[1]))

                #分离最近时间
                data=str(strl).split('\n')
                #print("scan result=="+data[0])
                newdata=str(data[1]).split(':')
                nndata=str(newdata[1]).split(' ')
                bestdate.append(str(nndata[1]))   #品种名

                 #分离历史产量
                data=str(strl).split('\n')
                #print("scan result=="+data[0])
                newdata=str(data[2]).split(':')
                nndata=str(newdata[1]).split(' ')
                history.append(str(nndata[1]))   #品种名

                #分离习性
                data=str(strl).split('\n')
                #print("scan result=="+data[0])
                newdata=str(data[3]).split(':')
                nndata=str(newdata[1]).split(' ')
                xixing.append(str(nndata[1]))   #品种名

                #分离历史所需时间
                data=str(strl).split('\n')
                #print("scan result=="+data[0])
                newdata=str(data[4]).split(':')
                nndata=str(newdata[1]).split(' ')
                lishishijian.append(str(nndata[1]))   #品种名

                #分离播种数
                data=str(strl).split('\n')
                #print("scan result=="+data[0])
                newdata=str(data[5]).split(':')
                nndata=str(newdata[1]).split(' ')
                bozhongshu.append(str(nndata[1]))   #品种名

                #分离播种日期
                data=str(strl).split('\n')
                #print("scan result=="+data[0])
                newdata=str(data[6]).split(':')
                nndata=str(newdata[1]).split(' ')
                bozhongdate.append(str(nndata[1]))   #品种名


                #print("位置信息："+)
        #print("个数："+str(count))
        
        
        return count,result,pos,bestdate,history,xixing,lishishijian,bozhongshu,bozhongdate
    
    #######################################
    # 选择保存过程的文件夹路径
    #############################
    def choosesavepath(self):
        self.save_path=QtWidgets.QFileDialog.getExistingDirectory(None,"选取保存文件夹","C:/")

    ################################
    #开始检测并将结果写入excel
    # 遍历os.listdir()选择的文件夹，对每张图片依次进行
    # 1.将文件夹位置传入到detect,
    # 2.遍历文件夹，依次decode得到品种名,随后根据二维码个数取Kmeans聚类数
    # 3.将信息更新到数据库
    # 4.由用户选择是否保存到excel
    ################################
    def detect(self):
        
        modelname=self.comboBox.currentText()
        modelpath='weights\\'+modelname

        print(modelpath)
        #选择预处理完成后的文件夹
        dic_path=QtWidgets.QFileDialog.getExistingDirectory(None,"选取预处理后的数据集目录","C:/")

        #print(modelname)
        dirs=os.listdir(dic_path)
        for file in dirs:
            path=str(dic_path)+'/'+str(file)
            #print(path)

            #pos[i]即result[i]的Y轴坐标
            count,result,pos,bestdate,history,xixing,lishishijian,bozhongshu,bozhongdate=self.multipleqrcode(path)

            image=Image.open(path)
            #print(count)
            #print(result[0])

            #根据位置信息对result品种名排序
            if(count!=1):
                for i in range (count):
                        for j in range(0,count-i-1):
                                if(int(pos[j])<int(pos[j+1])):
                                        pos[j],pos[j+1]=pos[j+1],pos[j]
                                        result[j],result[j+1]=result[j+1],result[j]
                
            #print(result)
            #print(pos)

            
            
            
            #给Kmeans聚类用
            gl._init()
            gl.set_value("km",count)


            #opt
            parser = argparse.ArgumentParser()
            parser.add_argument('--weights', nargs='+', type=str, default=modelpath, help='model.pt path(s)')
            parser.add_argument('--source', type=str, default=path, help='source')  # file/folder, 0 for webcam
   
            parser.add_argument('--img-size', type=int, default=992, help='inference size (pixels)')
            #置信度
            parser.add_argument('--conf-thres', type=float, default=0.2, help='object confidence threshold')
            parser.add_argument('--iou-thres', type=float, default=0.5, help='IOU threshold for NMS')
            parser.add_argument('--device', default='', help='cuda device, i.e. 0 or 0,1,2,3 or cpu')
            parser.add_argument('--view-img', action='store_true', help='display results')
            # 去掉label
            parser.add_argument('--save-txt', default=self.save_path, help='save results to *.txt')
    
            parser.add_argument('--save-conf', action='store_true', help='save confidences in --save-txt labels')
            parser.add_argument('--classes', nargs='+', type=int, help='filter by class: --class 0, or --class 0 2 3')
            parser.add_argument('--agnostic-nms', action='store_true', help='class-agnostic NMS')
            parser.add_argument('--augment', action='store_true', help='augmented inference')
            parser.add_argument('--update', action='store_true', help='update all models')

            #保存文件路径
            parser.add_argument('--project', default=self.save_path, help='save results to project/name')
            #文件夹名
            parser.add_argument('--name', default='exp', help='save results to project/name')
    
            parser.add_argument('--exist-ok', action='store_true', help='existing project/name ok, do not increment')
            
            opt=parser.parse_args()

           
            gl.set_value("opt",opt)
            

            #print(self.opt)
            with torch.no_grad():
                if opt.update:  # update all models (to fix SourceChangeWarning)
                    for opt.weights in ['yolov3.pt', 'yolov3-spp.pt', 'yolov3-tiny.pt']:
                        num,cnt = detect(False)
                        strip_optimizer(opt.weights)
                        
                else:
                    num,cnt = detect(False)
            #对应的num就是检测模型的检测个数
            print("二维码数："+str(count))
            print("检测总对象数:"+str(num))

            db=pymysql.connect(host="localhost",user="root",password="123456",db="yolo",port=3306)
            
            sql="select strain from soybean"
            cur=db.cursor()
            cur.execute(sql)
            result1=cur.fetchall()  #数据库里的品种数

            #print(result1)
            #print(result1[0][0])
            #print(result1[1][0])
            #print(result1[2][0])

            if(count!=1):
                for i in range(0,count):
                    print("从下往上第"+str(i+1)+"行: "+"品种名为："+result[i]+"出苗数："+str(cnt[i]))
                    if(len(result1)!=0):
                        for j in range(0,len(result1)):
                            print(result1[j][0])
                            if(result[i]==result1[j][0]):
                                cur.execute("select emergenum from soybean where strain='%s'"%(result[i]))
                                situation1=cur.fetchall()
                                cur.execute("select emergenum2 from soybean where strain='%s'"%(result[i]))
                                situation2=cur.fetchall()
                                cur.execute("select emergenum3 from soybean where strain='%s'"%(result[i]))
                                situation3=cur.fetchall()

                                if(situation1[0][0]==None):
                                    cur.execute("update soybean set emergenum='%s' where strain='%s'" % (cnt[i],result[i]))
                                    break
                                
                                #有了第一次
                                if(situation1[0][0]!=None and situation2[0][0]==None): 
                                
                                    cur.execute("update soybean set emergenum2='%s' where strain='%s'" % (cnt[i],result[i]))  
                                    flag=True
                                    break
                                #重复了第二次
                                if(situation2[0][0]!=None and situation3[0][0]==None):
                                
                                    cur.execute("update soybean set emergenum3='%s' where strain='%s'" % (cnt[i],result[i]))  
                                    flag=True
                                    break
                                #重复三次满了
                                if(situation3[0][0]!=None):
                                    cur.execute("update soybean set emergenum3='%s' where strain='%s'" % (cnt[i],result[i]))
                                    flag=True
                                    break
                                    
                            else:  
                               #print("继续找是否有重复的")
                                continue
                    
                    db.commit()
            else:
                print("品种名为："+result[0]+"出苗数："+str(cnt[0]))
                
                
                #if(品种名在数据库中有，则判断emerge情况)
                #print(result1)
                #返回数据库中品种名，查看是否属于重复
                if(len(result1)!=0):
                        for i in range(0,len(result1)):
                            if(result[0]==result1[i][0]):
                                cur.execute("select emergenum from soybean where strain='%s'"%(result[0]))
                                situation1=cur.fetchall()
                                cur.execute("select emergenum2 from soybean where strain='%s'"%(result[0]))
                                situation2=cur.fetchall()
                                cur.execute("select emergenum3 from soybean where strain='%s'"%(result[0]))
                                situation3=cur.fetchall()

                                if(situation1[0][0]==None):
                                    cur.execute("update soybean set emergenum='%s' where strain='%s'" % (cnt[0],result[0]))
                                    break
                                
                                #有了第一次
                                if(situation1[0][0]!=None and situation2[0][0]==None): 
                                   
                                    cur.execute("update soybean set emergenum2='%s' where strain='%s'" % (cnt[0],result[0]))  
                                    flag=True
                                    break
                                #重复了第二次
                                if(situation2[0][0]!=None and situation3[0][0]==None):
                                   
                                    cur.execute("update soybean set emergenum3='%s' where strain='%s'" % (cnt[0],result[0]))  
                                    flag=True
                                    break
                                #重复三次满了
                                if(situation3[0][0]!=None):
                                    cur.execute("update soybean set emergenum3='%s' where strain='%s'" % (cnt[0],result[0]))
                                    flag=True
                                    break
                                    
                            else:  
                                print("继续找是否有重复的")
                                continue
                              
               
                db.commit()


        db.close() 

        #数据库——>excel



    ################################
    # 保存到EXCEL中
    # 数据库——>excel
    #################################
    def savetoexcel(self):
        sexcel_path = QFileDialog.getOpenFileName(self, 'choose excel', '.',"excel files (*.xlsx)")
        #写标题
        data=xlrd.open_workbook(sexcel_path[0])      #打开文件
        table=data.sheets()[0]      #读取第一张表
        nrows=table.nrows           #行数
        ncols=table.ncols
        datanew=copy(data)

        sheet=datanew.get_sheet(0)
        sheet.write(1,ncols,'出苗数重复1')
        sheet.write(1,ncols+1,'出苗数重复2')
        sheet.write(1,ncols+2,'出苗数重复3')
        ncols+=2

        l=list(sexcel_path[0])
        l[-1]=''
        savenew_path=''.join(l)
        #print(savenew_path)
        datanew.save(savenew_path)

        db=pymysql.connect(host="localhost",user="root",password="123456",db="yolo",port=3306)
        cur=db.cursor()
        cur.execute("select strain,emergenum,situation1,situation2,situation3,emergenum2,emergenum3 from soybean")
        result=cur.fetchall()
        #print(result[0][1])
        cur.execute("select count(emergenum) from soybean")
        num=cur.fetchall()
        #print(num[0][0])

        for i in range (0,num[0][0]):
            strain=result[i][0]
            emergenum=result[i][1]
            situation1=result[i][2]
            situation2=result[i][3]
            situation3=result[i][4]
            emergenum2=result[i][5]
            emergenum3=result[i][6]
            for j in range(2,nrows):
                row_data=table.row_values(j)
                name=str(row_data[0])

                if name==strain:
                    row=j
            #print(row)
            sheet=datanew.get_sheet(0)

            #print(emergenum2)
            #print(emergenum3)
            sheet.write(row,ncols,emergenum3)
            sheet.write(row,ncols-1,emergenum2)
            sheet.write(row,ncols-2,emergenum)
            sheet.write(row,ncols-3,situation3)
            sheet.write(row,ncols-4,situation2)
            sheet.write(row,ncols-5,situation1)

            datanew.save(savenew_path)


    ##################################
    # 拼接
    #################################
    def choosedataset(self):
        self.data_path=QtWidgets.QFileDialog.getExistingDirectory(None,"选取数据集文件夹","C:/")
    def choosedatasave(self):
        self.datasave_path=QtWidgets.QFileDialog.getExistingDirectory(None,"选择保存新数据的文件夹","C:/")
    def imgstitch(self):
        img_dir = self.data_path
        names = os.listdir(img_dir)
        names.sort()
        savedir=self.datasave_path
        #print(num)
        
        times=int(self.textEdit_12.toPlainText())
       

        images = []
        m=1
        k=0

        for name in names:
            img_path = os.path.join(img_dir, name)
            image = cv2.imread(img_path)
            images.append(image)
            if(k<times):        
                k+=1
                images.append(image)
                images.append(image)
            if(k==times):
                stitcher = cv2.createStitcher() if imutils.is_cv3() else cv2.Stitcher_create()
                status, stitched = stitcher.stitch(images)     
                if status==0:
                    cv2.imwrite(savedir+'/final'+str(m)+'.jpg', stitched)
                    m=m+1
                if status==1:
                    print("没有足够的匹配点！")
                
                k=0
                images=[]


        stitcher = cv2.createStitcher() if imutils.is_cv3() else cv2.Stitcher_create()
        status, stitched = stitcher.stitch(images)

        if status==0:
            cv2.imwrite('final1.jpg', stitched)
        if status==1:
            print("没有足够的匹配点！")


    ###################################
    # 刷新表单数据
    ##################################
    def refreshstrain(self):

        #if(str(result[0][4])=='None'):
            #self.listWidget.addItem(str(result[0][0])+"      "+str(result[0][1])+"              "+str(result[0][2])+"      "+str(result[0][3])+" "+"未统计 "+"未统计")
        
        sql="select strain,lishishijian,bozhongshu,bozhongdate,emergenum,emergenum2,emergenum3 from soybean"
        db=pymysql.connect(host="localhost",user="root",password="123456",db="yolo",port=3306)
        cur=db.cursor()
        cur.execute(sql)
        result=cur.fetchall()

        #print(result[5][0])
        for i in range (0,len(result)): 
            #self.jiashuju(result[i][0]+"        "+result[i][1]+"            "+str(result[i][2])+"           "+result[i][3]+"        "+result[i][4]+"            "+str(result[i][5])+"               "+result[i][6])
            if(str(result[i][4])=='None'):
                self.listWidget.addItem(str(result[i][0])+"      "+str(result[i][1])+"              "+str(result[i][2])+"      "+str(result[i][3])+" "+"未统计 "+"未统计")
            else:
                count=1
                if(str(result[i][5])=='None'):
                    emergenum2=0
                else:
                    emergenum2=float(result[i][5])
                    count+=1
                if(str(result[i][6])=='None'):
                    emergenum3=0   
                else:
                    emergenum3=float(result[i][6])
                    count+=1

                averagenum=(float(result[i][4])+emergenum2+emergenum3)/count
                
                #print("平均出苗数："+str(num))

                rate=float(averagenum)/float(result[i][2])
                self.listWidget.addItem(str(result[i][0])+"         "+str(result[i][1])+"                  "+str(result[i][2])+"            "+str(result[i][3])+"     "+str(averagenum)+"     "+str(rate))
        self.setpushbutton_13disable()

    def output(self):
        save_path=QtWidgets.QFileDialog.getExistingDirectory(None,"选取数据集文件夹","C:/")
       
        db=pymysql.connect(host="localhost",user="root",password="123456",db="yolo",port=3306)
        cur=db.cursor()
        sql="select strain from soybean"
        cur.execute(sql)
        numofstrain=cur.fetchall()
        num=len(numofstrain)
        

        localtime=time.localtime(time.time())
        timeline="****************本次识别时间为："+str(localtime.tm_year)+"/"+str(localtime.tm_mon)+"/"+str(localtime.tm_mday)+"*********************"
        qrcodesavepath=gl.get_value("savepath")
        Qrcodeline="####################二维码##########################+\n"+"二维码文件保存在"+qrcodesavepath

        sql="select tflydate1,fangan1,tflydate2,fangan2,tflydate3,fangan3 from field"
        cur.execute(sql)
        resultoffly=cur.fetchall()
        #print(resultoffly[0][1])
        if(resultoffly[0][4]!='0'):
            #输出第三方案
            flyline="\n\n####################飞行方案########################\n"+"飞行方案为："+str(resultoffly[0][5])+"\n飞行时间："+str(resultoffly[0][4])+"\n飞行方案txt保存在：fangan.txt"
        if(resultoffly[0][2]!='0' and resultoffly[0][4]=='0'):
            #输出第二方案
            flyline="\n\n####################飞行方案########################\n"+"飞行方案为："+str(resultoffly[0][3])+"\n飞行时间："+str(resultoffly[0][2])+"\n飞行方案txt保存在：fangan.txt"
        if(resultoffly[0][0]!='0' and resultoffly[0][2]=='0'):
            #输出第一方案
            flyline="\n\n####################飞行方案########################\n"+"飞行方案为："+str(resultoffly[0][1])+"\n飞行时间："+str(resultoffly[0][0])+"\n飞行方案txt保存在：fangan.txt"

        sql="select tname,tlong,twidth from field"
        cur.execute(sql)
        resultoffield=cur.fetchall()
        fieldline="\n\n###################田块信息#########################\n"+"田块名："+resultoffield[0][0]+"\n田块长度："+resultoffield[0][1]+"\n田块宽度："+resultoffield[0][2]

        sql="select strain,bozhongshu,bozhongdate,emergenum,emergenum2,emergenum3 from soybean"
        cur.execute(sql)
        resultofstrain=cur.fetchall()

        resultline="\n\n###################识别结果信息#########################\n"
        for i in range (0,num):
            if(str(resultofstrain[i][3])=='None'):
                s="\n————品种名:"+str(resultofstrain[i][0])+"\n"+"    播种日期："+str(resultofstrain[i][2])+"\n"+"    播种数："+str(resultofstrain[i][1])+"识别结果无"
                resultline=resultline+s
            else:
                count=1
                if(str(resultofstrain[i][4])=='None'):
                    emergenum2=0
                else:
                    emergenum2=float(resultofstrain[i][4])
                    count+=1
                if(str(resultofstrain[i][5])=='None'):
                    emergenum3=0   
                else:
                    emergenum3=float(resultofstrain[i][5])
                    count+=1

                averagenum=(float(resultofstrain[i][3])+emergenum2+emergenum3)/count
                
                #print("平均出苗数："+str(num))

                rate=float(averagenum)/float(resultofstrain[i][1])


                s="\n————品种名:"+str(resultofstrain[i][0])+"\n"+"    播种日期："+str(resultofstrain[i][2])+"\n"+"    播种数："+str(resultofstrain[i][1])+"\n    第一次重复出苗数:"+str(resultofstrain[i][3])+"\n    第二次重复出苗数:"+str(resultofstrain[i][4])+"\n    第三次重复出苗数:"+str(resultofstrain[i][5])+"\n    平均出苗数："+str(averagenum)+"\n    出苗率："+str(rate)+"\n"
                resultline=resultline+s

        with open(save_path+"/result.txt","w") as f:
            f.write(str(timeline+Qrcodeline+flyline+fieldline+resultline))  # 自带文件关闭功能，不需要再写f.close()

        