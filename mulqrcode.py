import pyzbar.pyzbar as pyzbar
import numpy
from PIL import Image, ImageDraw, ImageFont
import cv2
 
frame = cv2.imread(r'C:\Users\11507\Desktop\1.png')
 
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
        result.append(str(nndata[1]))   #品种名
        #分离最近时间
        data=str(strl).split('\n')
        #print("scan result=="+data[0])
        newdata=str(data[1]).split(':')
        nndata=str(newdata[1]).split(' ')
        bestdate.append(str(nndata[1]))   #品种名

        #分离历史所需时间
        data=str(strl).split('\n')
        #print("scan result=="+data[0])
        newdata=str(data[2]).split(':')
        nndata=str(newdata[1]).split(' ')
        lishishijian.append(str(nndata[1]))   #品种名

        #分离播种数
        data=str(strl).split('\n')
        #print("scan result=="+data[0])
        newdata=str(data[3]).split(':')
        nndata=str(newdata[1]).split(' ')
        bozhongshu.append(str(nndata[1]))   #品种名

        #分离播种日期
        data=str(strl).split('\n')
        #print("scan result=="+data[0])
        newdata=str(data[4]).split(':')
        nndata=str(newdata[1]).split(' ')
        bozhongdate.append(str(nndata[1]))   #品种名
        
        #print("scan result=="+data[0])
        
        #print("位置信息："+str(position[1]))#Y坐标

print(result)
print(pos)
print(bestdate)
print(lishishijian)
print(bozhongshu)
print(bozhongdate)

'''
pos.append(str(200))
count=count+1
pos.append(str(100))
count=count+1
result.append(str(1))
result.append(str(2))

#print(pos)

if(count!=1):
        for i in range (count):
                for j in range(0,count-i-1):
                        if(int(pos[j])>int(pos[j+1])):
                                pos[j],pos[j+1]=pos[j+1],pos[j]
                                result[j],result[j+1]=result[j+1],result[j]
        print(pos)
#print(pos)
print(result)'''






    