from PyQt5.QtWidgets import QApplication, QMainWindow,QMessageBox
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtGui import QPixmap
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QMainWindow, QTextEdit, QAction, QApplication
import os
from login_GUI import Login_MainWindow
from Qrcode_excel_GUI import Qrcode_excel_MainWindow
from signin_GUI import signin_MainWindow
from main import Login_MainWindow
import pymysql

class signin_MainWindow(QtWidgets.QMainWindow,signin_MainWindow):
    
    def __init__(self):
        super(signin_MainWindow,self).__init__()
        self.cwd=os.getcwd()
        self.setupUi(self)
    def signin(self):
        sql="select id from user"
        db=pymysql.connect(host="localhost",user="root",password="123456",db="yolo",port=3306)
        cur=db.cursor()
        cur.execute(sql)
        result=cur.fetchall()
        
        #print(result)
        name=self.textEdit.toPlainText()
        passwd=self.lineEdit.text()
        phonenum=self.textEdit_3.toPlainText()
        flag=False

        if(name!=''):
            if(len(result)!=0):
                for i in range (0,len(result)):
                    if(name==result[i][0]):
                        flag=True
                        #print("发现重复，请更换id")
                        reply=QMessageBox.question(self,'系统提示','发现重复，请输入新的id',QMessageBox.Ok)
                        #YES的返回值为0x40000
                        if(reply==0x4000):
                            #加个self
                            self.sign=signin_MainWindow()
                            self.sign.show()
                            self.close()      
                        break
                if(flag==False):
                    cur.execute("insert into user(id,passwd,phonenum) values('%s','%s','%s')" % (name,passwd,phonenum))
                    db.commit()
                    #print("插入数据")
        else:
            #print("请输入用户名！")
            reply=QMessageBox.question(self,'系统提示','id不能为空',QMessageBox.Ok)
            #YES的返回值为0x40000
            if(reply==0x4000):
                #加个self
                self.sign=signin_MainWindow()
                self.sign.show()
                self.close() 

    def goback(self):   
        self.login=Login_MainWindow()
        self.login.show()
        self.close()