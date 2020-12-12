# -*- coding: utf-8 -*-
"""
Created on Fri Dec  4 14:39:32 2020

@author: LeeSeungJoon
"""
from flask import Flask, render_template, json, request, redirect
from flaskext.mysql import MySQL
from time import gmtime,strftime
import pymysql
import datetime

app = Flask(__name__)

#open connection
conn = pymysql.connect(
    host = "127.0.0.1",
    user  = "root",
    password = "1234",
    db = "movie",
    charset = "utf8"
    )


@app.route('/search_m', methods = ['POST','GET'])
def search_m():
    global USERID
    if request.method == 'GET':
        name = request.args.get('movie')
        genre = request.args.get('genre')
        sql = "Select * from movie_view Where MovieName like %s and Genre Like %s"
        curs = conn.cursor()
        #빈칸일 경우 고려 
        curs.execute(sql,('%'+name+'%',('%'+genre+'%')))
        rows1 = curs.fetchall()
        rows1_l = list(rows1)
        for i in range(len(rows1)):
            rows1_l[i] = list(rows1[i])
            rows1_l[i][5]=float(rows1_l[i][5])
        
        #출력 
        if USERID=="":
            return render_template('search.html', data = name, genre = genre, searchData=rows1_l)
        else:
            return render_template('search2.html', data = name, genre = genre, searchData=rows1_l)

@app.route('/search_a', methods = ['POST','GET'])
def search_a():
    global USERID
    if request.method == 'GET':
        name = request.args.get('actor')
        sql = "Select * from movie_actor Where actorName like %s"
        curs = conn.cursor()
        #빈칸일 경우 고려 
        curs.execute(sql,('%'+name+'%'))
        rows1 = curs.fetchall()
        rows1_l = list(rows1)
        for i in range(len(rows1)):
            rows1_l[i] = list(rows1[i])
            rows1_l[i][5]=float(rows1_l[i][5])
        #출력 
        if USERID=="": 
            return render_template('search.html', data = name, searchData=rows1_l)
        else:
            return render_template('search2.html', data = name, searchData =rows1_l)

@app.route('/login', methods = ['POST','GET'])
def login():
    if request.method =='GET':
        global USERID
        ID = request.args.get('ID')
        sql = "Select Count(*) from customers where CustomerID = %s"
        curs = conn.cursor()
        curs.execute(sql,ID)
        rows1 = curs.fetchall()
        if int(rows1[0][0]) == 0:
            message = "Incorrect ID"
            return render_template('login.html',message=message)
        else:
            USERID = ID
            return render_template('main2.html')
        
@app.route('/register', methods = ['POST','GET'])
def register():
    if request.method == 'GET':
        ID = request.args.get('ID')
        Lname = request.args.get('Lname')
        Fname = request.args.get('Fname')
        Address = request.args.get('Address')
        City = request.args.get('City')
        State = request.args.get('State')
        ZipCode = request.args.get('ZipCode')
        Telephone = request.args.get('Telephone')
        Email = request.args.get('Email')
        CreditCard = request.args.get('CreditCard')
        Type = request.args.get('type')
        sql = "Select Count(*) from customers where CustomerID = %s"
        curs = conn.cursor()
        curs.execute(sql,ID)
        rows1 = curs.fetchall()
        if int(rows1[0][0]) == 1 or len(ID) != 9:
            message = "Incorrect/Duplicate ID"
            return render_template('register.html', message=message)
        elif Lname=="" or Fname=="" or Telephone=="" or  Email=="" or CreditCard=="" :
            message = "Blank cirteria"
            return render_template('register.html',message=message)
        elif Type=="":
            message = "Choose type of subsciption"
            return render_template('register.html',message=message)
        elif '@' not in Email:
            message = "Email format error"
            return render_template('register.html',message=message)
        else:
            today = datetime.date.today()
            sql = 'insert into customers values('+ID+',"'+Lname+'","'+Fname+'","'+Address+\
                '","'+City+'","'+State+'",'+ZipCode+','+Telephone+',"'+Email+'",'+CreditCard+\
                ',"'+Type+'",%s)'
            curs = conn.cursor()
            curs.execute(sql,str(today))
            conn.commit()
            message = "Register completed"
            return render_template('register.html',message=message)
    
@app.route('/wishlist', methods = ['POST','GET'])
def wihlist():
    if request.method == 'GET':
        global USERID
        curs = conn.cursor()
        sql = 'select count(*) from wishlist where customerID ='+USERID
        curs.execute(sql)
        rows = curs.fetchall()
        sql = 'select AccountType from customers where customerID='+USERID
        curs.execute(sql)
        rows_t = curs.fetchall()
        if int(rows[0][0]) <2 or rows_t[0][0]=="unlimited":
            movieID = request.args.get('movieID')
            sql_t0 = 'Select movieID from movies where movies.movieID ='+movieID
            curs.execute(sql_t0)
            rows_t0 = curs.fetchall()
            if not rows_t0:
                message = 'Movie number you typed does not exist!'
                return render_template('search2.html',searchData = [], message = message)
            else:
                sql_t1 = 'Select MAX(wishlist.wishlistID) From wishlist'
                curs.execute(sql_t1)
                rows_t1 = curs.fetchall()
                if rows_t1[0][0] == None:   #wishlist 비어있다면 
                    sql = 'insert into wishlist values(0,'+USERID+','+movieID+')'
                    curs.execute(sql)
                    conn.commit()
                    message = 'Wishlist added successfully!'
                    return render_template('search2.html', searchData = [], message = message)
                else:
                    sql_t2 = 'select count(*) from wishlist AS w where w.movie ='+movieID+\
                        ' and w.customerID ='+USERID
                    curs.execute(sql_t2)
                    rows_t2 = curs.fetchall()
                    sql_t3 = 'select count(*) from Accounts AS a where a.movie ='+movieID+\
                        ' and a.customerID ='+USERID
                    curs.execute(sql_t3)
                    rows_t3 = curs.fetchall()
                    if int(rows_t2[0][0]) == 0 and rows_t3[0][0] == 0: #일반 삽입 
                        sql = 'insert into wishlist values(%d,'%(rows_t1[0][0]+1)+USERID+','+movieID+')'
                        curs.execute(sql)
                        conn.commit()
                        message = 'Wishlist added successfully!'
                        return render_template('search2.html', searchData = [], message = message)
                    else:
                        message = 'You already have this movie in your wishlist or already rented!'
                        return render_template('search2.html', searchData = [], message = message)
        else:
            message = 'Your wishlist is full!'
            return render_template('search2.html', searchData = [], message = message)
    
@app.route('/rental')
def rental_movie():
    global USERID
    movieID = request.args.get('movieID_rental')
    curs = conn.cursor()
    sql_t0 = 'Select count(*) from movies where movieID ='+movieID
    curs.execute(sql_t0)
    rows_t0 = curs.fetchall()
    if int(rows_t0[0][0]) == 1:
        sql_t1 = 'Select count(*) from wishlist where movie ='+movieID+\
            ' and customerID ='+USERID
        curs.execute(sql_t1)
        rows_t1 = curs.fetchall()
        if int(rows_t1[0][0]) == 1:
            sql_t0 = 'Select AccountNo from Accounts where CustomerId='+USERID
            curs.execute(sql_t0)
            rows_t0 = curs.fetchall()
            if not rows_t0: #Accounts에 없다
                sql_t1 = 'Select MAX(AccountNo) From Accounts'
                curs.execute(sql_t1)
                rows_t1 = curs.fetchall()
                #accounts 삽입
                sql_1 = 'insert into accounts values('+USERID+',%d'%(rows_t1[0][0]+1)+\
                    ','+movieID+')'
                curs.execute(sql_1)
            else:
                sql_1 = 'insert into accounts values('+USERID+',%d'%(rows_t0[0][0])+\
                    ','+movieID+')'
                curs.execute(sql_1)
            conn.commit()
            #orders 삽입
            sql_t2 = 'Select MAX(OrderID) From Orders'
            curs.execute(sql_t2)
            rows_t2 = curs.fetchall()
            sql_t3 = 'select DISTINCT AccountNo from Accounts where CustomerID='+USERID
            curs.execute(sql_t3)
            rows_t3 = curs.fetchall()
            now = strftime("%Y-%m-%d %H:%M:%S",gmtime())
            sql_3 = 'insert into orders values(%d'%(rows_t2[0][0]+1)+',%d'%(rows_t3[0][0])+\
                ','+movieID+',"'+now+'",null)'
            curs.execute(sql_3)
            conn.commit()
            
            message = 'Rented successfully! please refresh'
            return render_template('status.html',message=message, myRentals=[], Queue=[])
    else:
        message = 'Movie number you typed does not exist! please refresh'
        return render_template('status.html', message=message, myRentals =[], Queue=[])
    
@app.route('/return')
def return_movie():
    global USERID
    movieID = request.args.get('movieID_return')
    rating = request.args.get('rating')
    curs = conn.cursor()
    sql_t0 = 'select count(*) From Accounts where movie ='+movieID+' and CustomerID ='+USERID
    curs.execute(sql_t0)
    count = curs.fetchall()
    if count[0][0] == 1:
        if not(rating == ""):
            sql_r = 'insert into Rating values('+movieID+','+rating+')'
            curs.execute(sql_r)
            conn.commit()
        today = datetime.date.today()
        sql_t2 = 'update orders set Return_time = %s\
             where AccountID = (select DISTINCT AccountNo from Accounts where CustomerID ='+USERID+\
                ') and Return_time is null and movie ='+movieID
        curs.execute(sql_t2,str(today))
        sql_t1 = 'delete from Accounts where movie ='+movieID+' and CustomerID ='+USERID
        curs.execute(sql_t1)
        sql_t3 = 'select num_of_copies from movies where movieID ='+movieID
        curs.execute(sql_t3)
        num = curs.fetchall()
        num_l = list(num)
        num_l[0] = list(num[0])
        sql_t4 = 'update movies set Num_of_Copies ='+str(int(num_l[0][0])+1)+' where movieID ='+movieID
        curs.execute(sql_t4)
        conn.commit()
        message = 'Successfully returned! please refresh'
        return render_template('status.html',message = message, myRentals = [],Queue = [])
    else:
        message = 'You do not possess that movie right now! please refresh'
        return render_template('status.html',message = message, myRentals = [],Queue = [])
    
@app.route('/')
def init():
    global USERID
    USERID=""
    return render_template('main.html')

@app.route('/_search')
def _search():
    return render_template('search.html', data= "", searchData=[])

@app.route('/_main')
def _main():
    global USERID
    if USERID=="":
        return render_template('main.html')
    else:
        return render_template('main2.html')

@app.route('/_login')
def _login():
    return render_template('login.html')

@app.route('/_logout')
def _logout():
    global USERID
    USERID=""
    return render_template('main.html')

@app.route('/_register')
def _register():
    return render_template('register.html')

@app.route('/_search2')
def _search2():
    return render_template('search2.html',data= "", searchData=[])

@app.route('/_status')
def _status():
    sql1 = "Select * from movie_view where movie_view.movieID in"+\
        "(select movie from Accounts where CustomerID ="+USERID+")"
    curs = conn.cursor()
    curs.execute(sql1)
    rows1 = curs.fetchall()        
    rows1_l = list(rows1)
    for i in range(len(rows1)):
        rows1_l[i] = list(rows1[i])
        rows1_l[i][5]=float(rows1_l[i][5])
    sql2 = "Select * from movie_view where movie_view.movieID in"+\
        "(Select movie from Wishlist Where CustomerID ="+USERID+")"
    curs.execute(sql2)
    rows2 = curs.fetchall()
    rows2_l = list(rows2)
    for i in range(len(rows2)):
        rows2_l[i] = list(rows2[i])
        rows2_l[i][5]=float(rows2_l[i][5])
    return render_template('status.html',CustomerID = USERID, myRentals = rows1_l, Queue = rows2_l)

@app.route('/_information')
def _information():
    global USERID
    sql = "Select * from Customers where CustomerID = "+USERID
    curs = conn.cursor()
    curs.execute(sql)
    rows = curs.fetchall()
    rows_l = list(rows)
    rows_l[0] = list(rows[0])
    rows_l[0][11] = str(rows[0][11])
    return render_template('information.html', ID = USERID, Data = rows_l)

if __name__ == '__main__':
    app.run()

#close connection
conn.commit()
conn.close()