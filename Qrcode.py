import qrcode
import qrcode
from pyzbar import pyzbar
from PIL import Image

def create_qrcode(name,row_str,dir_path):
        img=qrcode.make(row_str)
        img.save(dir_path+'/'+name+'.png')
        #print(dir_path+'/'+name+'.png')
        #解码，生成时查看
        decodeDisplay(dir_path+'/'+name+'.png')

def decodeDisplay(image_path):
    result=pyzbar.decode(Image.open(image_path),symbols=[pyzbar.ZBarSymbol.QRCODE])
    if len(result):
        #得到品种名，其他信息获得方式类似
        #s=str(result[0].data.decode('utf-8')).split('\n')
        #strain=str(s[0]).split(': ')
        #print(strain[1])

        #输出完整二维码信息
        print(result[0].data.decode('utf-8'))
    else:
        print("Can not recognize.")
def decodegetname(image_path):
    result=pyzbar.decode(Image.open(image_path),symbols=[pyzbar.ZBarSymbol.QRCODE])
    if len(result):
        #得到品种名，其他信息获得方式类似
        s=str(result[0].data.decode('utf-8')).split('\n')
        strain=str(s[0]).split(': ')
        date=str(s[1]).split(': ')
        history=str(s[2]).split(': ')
        xixing=str(s[3]).split(': ')
        lishishijian=str(s[4]).split(': ')
        bozhongshu=str(s[5]).split(': ')
        bozhongdate=str(s[6]).split(': ')

        #品种名
        print(strain[1])
        #播期
        #print(date[1])
        #历史产量
        #print(history[1])
        #结荚习性
        #print(xixing[1])
        #历史平均发育期时长
        #print(lishishijian[1])
        #print(bozhongdate[1])

        return strain[1],date[1],history[1],xixing[1],lishishijian[1],bozhongshu[1],bozhongdate[1]
    else:
        
        print("Can not recognize.")
        return -1
def decodeonlygetname(image_path):

    
    result=pyzbar.decode(Image.open(image_path),symbols=[pyzbar.ZBarSymbol.QRCODE])
    if len(result):
        #得到品种名，其他信息获得方式类似
        s=str(result[0].data.decode('utf-8')).split('\n')
        strain=str(s[0]).split(': ')
        #品种名
        #print(strain[1])
        #播期
        #print(date[1])
        #历史产量
        #print(history[1])
        #结荚习性
        #print(xixing[1])
        #历史平均发育期时长
        #print(lishishijian[1])
        #print(bozhongdate[1])

        return strain[1]
    else:
        
        print("Can not recognize.")
        return -1
if __name__ == '__main__':
    decodegetname(r'C:\Users\11507\Desktop\1.png')