from PyQt5.QtWidgets import QApplication, QMainWindow,QMessageBox
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtGui import QPixmap
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QMainWindow, QTextEdit, QAction, QApplication
import os,sys
from PIL import Image
import Qrcode

from login_GUI import Login_MainWindow
from Qrcode_excel_GUI import Qrcode_excel_MainWindow
import xlrd     #excel读库
from newindex_class import newindex_MainWindow
import pymysql
import time
import globalvar as gl


class Qrcode_excel_MainWindow(QtWidgets.QMainWindow,Qrcode_excel_MainWindow):
    
    def __init__(self):
        super(Qrcode_excel_MainWindow,self).__init__()
        self.cwd=os.getcwd()
        self.setupUi(self)
    #返回上级
    def goback(self):
        self.newindex=newindex_MainWindow()
        self.newindex.show()
        self.close()
    #选择excel文件路径
    def chooseexcel(self):
        self.excel_path = QFileDialog.getOpenFileName(self, 'choose excel', '.',"txt files (*.xlsx)")
       
    #选择保存路径
    def choosesave(self):
        self.save_path=QtWidgets.QFileDialog.getExistingDirectory(None,"选取保存文件夹","C:/")
        gl._init()
        gl.set_value("savepath",self.save_path)
        
    #开始生成
    def begin(self):
        
        data=xlrd.open_workbook(self.excel_path[0])      #打开文件
        table=data.sheets()[0]      #读取第一张表
        nrows=table.nrows       #行数
        ncols=table.ncols
        firstdata=table.row_values(1)       #对应名称
        #firststr=''.join(firstdata)
        row_str=''
        for i in range(2,nrows):
            row_data=table.row_values(i)
            name=str(row_data[0])       #名称为第一列，规定好的，用于生成二维码文件命名！
            for j in range(ncols):
                row_str=row_str+firstdata[j]+': '+str(row_data[j])+'\n'

            Qrcode.create_qrcode(name,row_str,self.save_path)  
            row_str=''        
        

        localtime=time.localtime(time.time())
        opetime=str(localtime.tm_year)+"/"+str(localtime.tm_mon)+"/"+str(localtime.tm_mday)
        db=pymysql.connect(host="localhost",user="root",password="123456",db="yolo",port=3306)
        cur=db.cursor()
        #更新日志
        cur.execute("insert into journal (operation,date) values('%s','%s')" % (str("生成二维码"),str(opetime)))
        db.commit()
        reply=QMessageBox.question(self,'系统提示','生成完毕,需要返回上级？',QMessageBox.Yes | QMessageBox.No,QMessageBox.No)
        #YES的返回值为0x40000
        if(reply==0x4000):
            from newindex_class import newindex_MainWindow
            #加个self
            self.index=newindex_MainWindow()
            self.index.show()
            self.close()     
        