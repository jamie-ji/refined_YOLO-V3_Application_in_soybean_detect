import sys
from PyQt5.QtWidgets import QApplication, QMainWindow,QMessageBox
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtGui import QPixmap
import sys
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QMainWindow, QTextEdit, QAction, QApplication
import os,sys
from PIL import Image
import cv2
import PIL
import numpy
import Qrcode

from login_GUI import Login_MainWindow
from newindex_class import newindex_MainWindow
from signin_class import signin_MainWindow
import pymysql

#登录界面
class Login_MainWindow(QtWidgets.QMainWindow,Login_MainWindow):
    def __init__(self):
        super(Login_MainWindow,self).__init__()
        self.setupUi(self)
        

    def btn_login_func(self):
        #获取账号密码
        account=self.textEdit.toPlainText()
        passwd=self.lineEdit.text()
        flag=False
        if account=="" or passwd == "":
            reply=QMessageBox.warning(self,"警告","帐号密码不能为空")
            return 
        else: 
            sql="select id from user"
            db=pymysql.connect(host="localhost",user="root",password="123456",db="yolo",port=3306)
            cur=db.cursor()
            cur.execute(sql)
            result=cur.fetchall()

            if(len(result)!=0):
                for i in range (0,len(result)):
                    if(account==result[i][0]):
                        flag=True
                        cur.execute("select passwd from user where id=%s" % (account))
                        result=cur.fetchall()
                        #print(result[0][0])
                        if(result[0][0]==passwd):
                            #print("密码正确")
                            self.index=newindex_MainWindow()
                            self.index.show()
                            self.close()
                        else:
                            reply=QMessageBox.question(self,'系统提示','密码错误！',QMessageBox.Ok)
                            #YES的返回值为0x40000
                            if(reply==0x4000):
                                #加个self
                                self.sign=Login_MainWindow()
                                self.sign.show()
                                self.close() 
                        break
                if(flag==False):
                    reply=QMessageBox.question(self,'系统提示','查无此ID，请重新输入',QMessageBox.Ok)
                    #YES的返回值为0x40000
                    if(reply==0x4000):
                        #加个self
                        self.sign=Login_MainWindow()
                        self.sign.show()
                        self.close() 
    
    def signin(self): 
        self.signing=signin_MainWindow()
        self.signing.show()
        self.close()
    def findpsw(self):
        from findpsw_class import findpsw_MainWindow
        self.findp=findpsw_MainWindow()
        self.findp.show()
        self.close()

if __name__ == '__main__':
    app=QtWidgets.QApplication(sys.argv)
    my_login=Login_MainWindow()
    #!实例化，才能显示
    my_login.show()
    sys.exit(app.exec_())