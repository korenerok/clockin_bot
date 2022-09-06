from datetime import datetime, timedelta, date, time
import mysql.connector
from configparser import ConfigParser

config = ConfigParser().read("./.env")
dbSettings = config['CONECTIONS']

def mysql_connect():
    try:
        connection = mysql.connector.connect(
            host=dbSettings['db_host'],
            user=dbSettings['db_user'],
            passwd=dbSettings['db_password'],
            database=dbSettings['db_database']
        )
    except OSError:
        print(OSError)
        return None
    return connection


def addDataIn(telegram_id, name, user):
    connection=mysql_connect()
    if connection is None:
        return f"""Error with the database, please check database settings"""

    cursor = connection.cursor()
    today=date.today()
    cursor.execute("SELECT id, in_time FROM clockins WHERE telegram_id = %s AND date = %s AND out_time IS NULL",(telegram_id,today))
    found = cursor.fetchone()
    if found is None:
        now=datetime.now().replace(microsecond=0)
        cursor.execute("INSERT INTO clockins (telegram_id, name, user, date, in_time) VALUES (%s,%s,%s,%s,%s)",(telegram_id, name, user,today,now))
        connection.commit()
        cursor.close() 
        return f"""CONFIRMED: [{name}](tg://user?id='{telegram_id}')  CLOCKED IN at {now.strftime('%H:%M:%S')}"""
    else: 
        time = found[1]
        return f"""Hi [{name}](tg://user?id='{telegram_id}') You already entered at {time}"""

        
def addDataOut(telegram_id, name, user):
    connection=mysql_connect()
    if connection is None:
        return f"""Error with the database, please check database settings"""

    cursor = connection.cursor()
    today=date.today()
    cursor.execute("SELECT id, in_time FROM clockins WHERE telegram_id = %s AND date = %s AND out_time IS NULL",(telegram_id,today))
    found = cursor.fetchone()
    if found is not None:
        inTime=datetime.combine(today,time()) + found[1]
        now=datetime.now().replace(microsecond=0)
        sessionTime=now - inTime
        cursor.execute("UPDATE clockins SET name = %s, user = %s, out_time = %s, total_time=%s WHERE date = %s AND out_time IS NULL AND telegram_id = %s",(name,user,now,sessionTime,today,telegram_id))
        connection.commit()
        cursor.close()
        return f"""Hi [{name}](tg://user?id='{telegram_id}') You time was {sessionTime}"""
    else: 
        return f"""Hi [{name}](tg://user?id='{telegram_id}') You can't clock out because you did not clocked in"""
                

def calculateDayHours():
    connection=mysql_connect()
    if connection is None:
        return f"""Error with the database, please check database settings"""
    
    cursor = connection.cursor()

    #select sessions which have no out_time yet
    total_time=timedelta()
    now=datetime.now().replace(microsecond=0)
    today=date.today()
    cursor.execute("select in_time from clocking_user where date = %s and out_time is null",(today,))
    sessions = cursor.fetchall()
    for inTime in sessions:
        datetime_intime=datetime.combine(today,time()) + inTime[0]
        total_time += (now - datetime_intime)

    #select sessions which have total_time
    cursor.execute("select total_time from clocking_user where date = %s and out_time is not null",(today,))
    sessions = cursor.fetchall()
    for session in sessions:
        total_time += session[0]

    formattedTime = '%02d:%02d:%02d' % (total_time.days*24 + total_time.seconds // 3600, (total_time.seconds % 3600) // 60, total_time.seconds % 60)

    if total_time.total_seconds() > 0:
        cursor.execute("SELECT * FROM daily_total WHERE date =  %s",(today,))
        select = cursor.fetchone()
        if select is not None:
            cursor.execute("UPDATE daily_total SET time = %s where date = %s",(formattedTime,today))
            connection.commit()
            cursor.close()
        else: 
            cursor.execute("INSERT INTO daily_total (date, time) VALUES (%s, %s)",(today,formattedTime))
            connection.commit()
            cursor.close()


        return f"""Today the team has worked a total of (hh:mm:ss) {formattedTime}.""" 
    else: 
        return f"""Today the team has worked a total of (hh:mm:ss) 00:00:00.""" 
            
    
def calculateWeekHours():
    connection=mysql_connect()
    if connection is None:
        return f"""Error with the database, please check database settings"""

    cursor = connection.cursor()
    aWeekAgo=(datetime.now() - timedelta(days=7)).date()
    cursor.execute("SELECT date,time FROM daily_total where date and date > %s",(aWeekAgo,))
    weekHours = cursor.fetchall()
    week_delta=timedelta()
    for dayHours in weekHours:
        week_delta += dayHours[1]
    
    return f"""This week we work a total time (hh:mm:ss) {str(week_delta)}.""" 


#print(addDataOut("123","user name","user"))
#calculate_totalTime()