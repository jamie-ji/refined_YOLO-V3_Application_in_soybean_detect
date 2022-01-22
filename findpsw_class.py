from PyQt5.QtWidgets import QApplication, QMainWindow,QMessageBox
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtGui import QPixmap
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QMainWindow, QTextEdit, QAction, QApplication
import os

from login_GUI import Login_MainWindow
from Qrcode_excel_GUI import Qrcode_excel_MainWindow
from findpsw_GUI import findpsw_MainWindow
from main import Login_MainWindow
import pymysql

class findpsw_MainWindow(QtWidgets.QMainWindow,findpsw_MainWindow):
    
    def __init__(self):
        super(findpsw_MainWindow,self).__init__()
        self.cwd=os.getcwd()
        self.setupUi(self)
    def goback(self):
        self.login=Login_MainWindow()
        self.login.show()
        self.close()

    def findpsw(self):
        sql="select id from user"
        db=pymysql.connect(host="localhost",user="root",password="123456",db="yolo",port=3306)
        cur=db.cursor()
        cur.execute(sql)
        result=cur.fetchall()

        name=self.textEdit.toPlainText()
        phonenum=self.textEdit_2.toPlainText()
        newpasswd=self.textEdit_3.toPlainText()
        flag=False

        if(name!=''and phonenum!='' and newpasswd!=''):
            if(len(result)!=0):
                for i in range (0,len(result)):
                    if(name==result[i][0]):
                        flag=True
                        cur.execute("select phonenum from user where id=%s" % (name))
                        result=cur.fetchall()
                        #print(result[0][0])
                        if(result[0][0]==phonenum):
                            cur.execute("update user set passwd='%s' where id='%s'" % (newpasswd,name))
                            db.commit()
                            reply=QMessageBox.question(self,'系统提示','密码已更新',QMessageBox.Ok)
                            #YES的返回值为0x40000
                            if(reply==0x4000):
                                #加个self
                                self.sign=findpsw_MainWindow()
                                self.sign.show()
                                self.close() 
                        else:
                            reply=QMessageBox.question(self,'系统提示','与输入预留手机号不匹配',QMessageBox.Ok)
                            #YES的返回值为0x40000
                            if(reply==0x4000):
                                #加个self
                                self.sign=findpsw_MainWindow()
                                self.sign.show()
                                self.close() 
                        break
                if(flag==False):
                    reply=QMessageBox.question(self,'系统提示','查无此ID，请重新输入',QMessageBox.Ok)
                    #YES的返回值为0x40000
                    if(reply==0x4000):
                        #加个self
                        self.sign=findpsw_MainWindow()
                        self.sign.show()
                        self.close() 
        else:
            #print("请输入用户名！")
            reply=QMessageBox.question(self,'系统提示','三项均不能为空',QMessageBox.Ok)
            #YES的返回值为0x40000
            if(reply==0x4000):
                #加个self
                self.sign=findpsw_MainWindow()
                self.sign.show()
                self.close() 


