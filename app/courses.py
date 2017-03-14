from flask import render_template, redirect, url_for, request, g
from app import webapp
import tempfile
import os

from wand.image import Image
import boto3
import mysql.connector

from app.config import db_config




def connect_to_database():
    return mysql.connector.connect(user=db_config['user'], 
                                   password=db_config['password'],
                                   host=db_config['host'],
                                   database=db_config['database'])

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect_to_database()
    return db

@webapp.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@webapp.route('/userUI',methods=['GET'])
# Display an HTML list of all courses.
def courses_list():
    cnx = get_db()

    cursor = cnx.cursor()

    query = "SELECT * FROM users"

    cursor.execute(query)
    
    return render_template("courses/list.html",title="User UI", cursor=cursor)



@webapp.route('/courses/create',methods=['GET'])
# Display an empty HTML form that allows users to define new student.
def courses_create():
    return render_template("courses/new.html",title="Create New User")


@webapp.route('/courses/secret',methods=['GET'])
# Display an empty HTML form that allows users to define new student.
def courses_secret():
    return render_template("courses/secret.html",title="User Login")


@webapp.route('/courses/hello',methods=['GET'])
# Display an empty HTML form that allows users to define new student.
def hello():
    return render_template("courses/hello.html")

@webapp.route('/courses/success/<username>',methods=['GET'])
# 登陆成功，进入选择文档上传界面
def success(username):
    s3 = boto3.resource('s3')

    bucket = s3.Bucket(username)

    for key in bucket.objects.all():
        k = key

    keys = bucket.objects.all()
    return render_template("courses/success.html",title="S3 Bucket Contents",username = username, keys=keys)


@webapp.route('/courses/success/upload/<username>',methods=['POST'])
#Upload a new file to an existing bucket
def s3_upload(username):
    # check if the post request has the file part
    if 'new_file' not in request.files:
        return redirect(url_for('success',username = username))

    new_file1 = request.files['new_file']



    # if user does not select file, browser also
    # submit a empty part without filename
    if new_file1.filename == '':
        return redirect(url_for('success', username = username))


#    s3 = boto3.client('s3')
#    s3.upload_fileobj(new_file1, username, new_file1.filename)

    tempdir = tempfile.gettempdir()

    fname = os.path.join('app/static', 'rotated0_'+new_file1.filename)

    new_file1.save(fname)

    img = Image(filename=fname)

    i = img.clone()
    i.rotate(90)
    fname_rotated = os.path.join('app/static', 'rotated90_' + new_file1.filename)
    i.save(filename=fname_rotated)

    i2 = img.clone()
    i2.rotate(180)
    fname_rotated180 = os.path.join('app/static', 'rotated180_' + new_file1.filename)
    i2.save(filename=fname_rotated180)

    i3 = img.clone()
    i3.rotate(270)
    fname_rotated270 = os.path.join('app/static', 'rotated270_' + new_file1.filename)
    i3.save(filename=fname_rotated270)

    """    aa = 'app/static/rotated90_'+new_file1.filename
    bb = 'app/static/rotated180_'+new_file1.filename
    cc = 'app/static/rotated270_'+new_file1.filename
    print(aa)
    s3 = boto3.resource('s3')
    s3.meta.client.upload_file(aa, username, 'rotated90_' + new_file1.filename)
    s3.meta.client.upload_file(bb, username, 'rotated180_' + new_file1.filename)
    s3.meta.client.upload_file(cc, username, 'rotated270_' + new_file1.filename)
"""

    it0 = img.clone()
    it0.rotate(0)
    it0.resize(200, 200)
    fname_thumb0 = os.path.join('app/static', 'thumbnail0_' + new_file1.filename)
    it0.save(filename=fname_thumb0)

    it90 = img.clone()
    it90.rotate(90)
    it90.resize(200, 200)
    fname_thumb90 = os.path.join('app/static', 'thumbnail90_' + new_file1.filename)
    it90.save(filename=fname_thumb90)

    it180 = img.clone()
    it180.rotate(180)
    it180.resize(200, 200)
    fname_thumb180 = os.path.join('app/static', 'thumbnail180_' + new_file1.filename)
    it180.save(filename=fname_thumb180)

    it270 = img.clone()
    it270.rotate(270)
    it270.resize(200, 200)
    fname_thumb270 = os.path.join('app/static', 'thumbnail270_' + new_file1.filename)
    it270.save(filename=fname_thumb270)

    print(fname_thumb90[4:])
    print(fname_thumb180[4:])


    return render_template("courses/viewpicture.html",
                           f1=fname_thumb0[3:],
                           f2=fname_thumb90[3:],
                           f3=fname_thumb180[3:],
                           f4=fname_thumb270[3:])


@webapp.route('/courses/viewbigpicture/<papa>',methods=['POST'])
#Return file upload form
def viewbig(papa):
    print(papa)
    papa1 = papa[9:]
    print(papa1)

    datu = '/static/rotated'  + papa1
    return render_template("courses/viewbig.html",f2=datu)



#   s3 = boto3.resource('s3')
#   s3.meta.client.upload_file('app/static/Pink_Flowers.jpg', username, 'fensedehua')



#    img = Image(filename=new_file)

#    i = img.clone()
#    rotate180 = i.rotate(180)


#    return redirect(url_for('success', username = username,f1=fname_rotated[4:],
 #                          f2=fname_rotated180[4:],
  #                         f3 = fname_rotated270[4:]))




@webapp.route('/courses/secret',methods=['POST'])
# Create a new student and save them in the database.
def courses_secret_save():
    l = request.form.get('login',"")
    x = request.form.get('passwords',"")


    error = False

    if l  == "" or x == "" :
        error=True
        error_msg="Error: All fields are required!"

    if error:
        return render_template("courses/secret.html",title="User Login",error_msg=error_msg, login=l, passwords=x)

    cnx = get_db()
    cursor = cnx.cursor()
    query   =  "  SELECT login  FROM users  "   #choose login

    cursor.execute(query)

    totalloginlist = []
    totalpasswordlist = []

    for login in cursor:
        loginstring = ''.join(list(login))      #tuple--list--string
        print(loginstring)
        totalloginlist.append(loginstring)

    print(totalloginlist)

    print('123445')

    query  =  " SELECT passwords FROM users  "    #choose passwords
    cursor.execute(query)

    for passwords in cursor:
        passwordstring = ''.join(list(passwords))  # tuple--list--string
        print(passwordstring)
        totalpasswordlist.append(passwordstring)

    print(totalpasswordlist)


    if l in totalloginlist :                       # 在 code数组中的位置是否等于 tilte该位置的内容
        l_position = totalloginlist.index(l)
        if x == totalpasswordlist[l_position]:
            print(' zhongyutamade chengongle')

            return redirect(url_for('success',username = l ))

        print ('yes')
        print(l_position)

    else:
        error_msg = "Error: Wrong Password or User Name !"
        print('wrong password or wrong user name')
        return render_template("courses/secret.html", title="User Login", error_msg=error_msg, login=l, passwords=x)


    return redirect(url_for('hello'))


@webapp.route('/courses/create', methods=['POST'])
# Create a new student and save them in the database.
def courses_create_save():


    a = request.form.get('login', "")
    title = request.form.get('passwords', "")

    error = False

    if a == "" or title == "" :
        error = True
        error_msg = "Error: All fields are required!"

    if error:
        return render_template("courses/new.html", title="Create New User", error_msg=error_msg, login=a, passwords=title)

    cnx = get_db()
    cursor = cnx.cursor()

    query = "  SELECT login  FROM users  "  # 查询用户名是否存在重复

    cursor.execute(query)

    totalloginlist2 = []

    for login in cursor:
        loginstring2 = ''.join(list(login))  # tuple--list--string
        totalloginlist2.append(loginstring2)

    if a in totalloginlist2:
        error_msg = "Error: User name already used !"
        return render_template("courses/new.html", title="Create New User", error_msg=error_msg, login=a, passwords=title)

    s3 = boto3.resource('s3')  ########
    s3.create_bucket(Bucket=a)  #######  创建bucket  名字为a


    query = ''' INSERT INTO users (login,passwords)
                       VALUES (%s,%s)
    '''

    cursor.execute(query, (a, title))
    cnx.commit()

    return redirect(url_for('courses_list'))



@webapp.route('/courses/delete/<int:id>',methods=['POST'])
# Deletes the specified student from the database.
def courses_delete(id):
    cnx = get_db()
    cursor = cnx.cursor()

    query = "DELETE FROM users WHERE id = %s"
    
    cursor.execute(query,(id,))
    cnx.commit()

    return redirect(url_for('courses_list'))
