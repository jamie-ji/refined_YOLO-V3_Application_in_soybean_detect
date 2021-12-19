import requests
import pymysql
import time
from borax.calendars.lunardate import LunarDate

def getcitycode(cityname):
    db=pymysql.connect(host="localhost",user="root",password="123456",db="yolo",port=3306)
    cur=db.cursor()
    sql="select citycode from Situation where cityname=%s"
    try:
        cur.execute(sql,cityname)
        result=cur.fetchall()       #查询的值保存在result中
        #print(result[0][0])
        return result[0][0]
    except Exception as e:
        print(e)
def getweather(citycode):
    #print(citycode)
    r=requests.get("http://www.weather.com.cn/data/sk/"+str(citycode)+".html")
    r.encoding='utf-8'
    print("您的城市为："+r.json()['weatherinfo']['city'],"  平均温度为："+r.json()['weatherinfo']['temp']+"℃","  风况为："+r.json()['weatherinfo']['WD'],r.json()['weatherinfo']['WSE'])

def gettime():
    localtime=time.localtime(time.time())
    lunar=LunarDate.today()
    #print(localtime)
    print(str(localtime.tm_year)+"年"+str(localtime.tm_mon)+"月"+str(localtime.tm_mday)+"日"+" 星期"+str(localtime.tm_wday+1)+" 农历时间："+str(lunar.year)+"年"+str(lunar.month)+"月"+str(lunar.day)+"日")

if __name__=='__main__':
    getweather(getcitycode("南京"))
    gettime()