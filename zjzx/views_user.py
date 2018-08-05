import re

import functools
from flask import Blueprint, session, make_response, request, jsonify
from flask import current_app
from flask import g
from flask import redirect
from flask import render_template

from utils.captcha.captcha import captcha
from utils.ytx_sdk import ytx_send
import random
from models import UserInfo, db, NewsInfo, NewsCategory
from utils import qiniu_upload

user_blueprint = Blueprint('user', __name__, url_prefix='/user')


@user_blueprint.route('/image_code')
def image_code():
    # 调用第三方的工具，生成图形验证码数据
    name, text, image = captcha.generate_captcha()
    # 保存text值，用于后续的对比
    session['image_code'] = text
    print(text)
    # 创建响应对象，响应体为图片数据
    response = make_response(image)
    # 设置响应数据的类型为图片
    response.content_type = 'image/png'
    # 返回
    return response


@user_blueprint.route('/sms_code')
def sms_code():
    # 接收:手机号，图形验证码
    mobile = request.args.get('mobile')
    imagecode = request.args.get('imagecode')

    # 验证
    # 1.值必填  空在python中为False
    # if not mobile or not imagecode:
    if not all([mobile, imagecode]):
        # return jsonify(msg='请将数据填写完整')
        return jsonify(result=1)
    # 2.验证手机号合法：正则
    # 3.图形验证码一致
    imagecode_session = session.get('image_code')

    if not imagecode_session:
        return jsonify(result=4)
    # 强制图形验证码过期，防止客户端不停尝试
    del session['image_code']

    if imagecode != imagecode_session:
        return jsonify(result=2)

    # 处理
    # 1.生成随机的验证码
    smscode = str(random.randint(100000, 999999))
    # 2.保存验证码，用于后续验证
    session['sms_code'] = smscode
    # 3.发送短信  1是云通讯上面的一个模板号码
    # ytx_send.sendTemplateSMS(mobile, [smscode, '10'], 1)
    print(smscode)

    # 响应
    return jsonify(result=3)


# 注册
@user_blueprint.route('/register', methods=['POST'])
def register():
    # print("12312312321")
    # 接收
    mobile = request.form.get('mobile')
    smscode = request.form.get('smscode')
    password = request.form.get('password')
    # 验证
    if not all([mobile, smscode, password]):
        return jsonify(result=1)
    # 短信验证码
    smscode_session = session.get('sms_code')
    # 使用一次后，强制删除，防止客户端不断的重试
    del session['sms_code']
    if not smscode_session:
        return jsonify(result=2)
    # 对比短信验证码
    if smscode != smscode_session:
        return jsonify(result=3)
    # 手机号是否存在
    if UserInfo.query.filter_by(mobile=mobile).count() > 0:
        return jsonify(result=4)
    # 验证密码
    if not re.match(r'^[0-9a-zA-Z]{6,20}$', password):
        return jsonify(result=5)

        # 处理:向用户表中添加信息
    user = UserInfo()
    user.mobile = mobile
    user.nick_name = mobile
    # 密码加密后保存在表中,把用户输入的值交给方式进行加密，方法在models中
    # password别装饰，调用password的属性会自动调用password.setting方法
    user.password = password
    # 保存到 数据库

    db.session.add(user)
    db.session.commit()

    # 响应
    # print("12312312321")
    return jsonify(result=6)


@user_blueprint.route('/login', methods=['POST'])
def login():
    mobile = request.form.get('mobile')
    password = request.form.get('password')
    # 验证
    if not all([mobile, password]):
        return jsonify(result=1)
    # 处理:根据手机号查询对象，再对比密码
    user = UserInfo.query.filter_by(mobile=mobile).first()
    if not user:
        # 如果没有查询到数据，则返回none
        # 手机号错误
        return jsonify(result=2)
    # 如果查询到对象，密码是加过密的
    if user.check_pwd(password):
        # 状态保持．记录用户登录成功
        # 只有登录成功以后，字典里才会有这个值user.id
        # 看有没有登录过，就看session里面有没有这个user_id
        session['user_id'] = user.id
        # 密码正确
        return jsonify(result=4, nick_name=user.nick_name,
                       avatar=user.avatar_url)
    else:
        # 密码错误
        return jsonify(result=3)


# 登录验证用装饰器装饰
def login_valid(view_fun):
    # 输出原有函数的名称，不用fun
    @functools.wraps(view_fun)
    def fun(*args, **kwargs):
        # 验证是否登录
        if 'user_id' not in session:
            return redirect('/')
            # 查询当前登录的用户
        user_id = session.get('user_id')
        g.user = UserInfo.query.get(user_id)
        # 执行视图函数
        # 将视图函数的响应内容返回给客户
        return view_fun(*args, **kwargs)

    return fun


@user_blueprint.route('/logout')
def logout():
    # 退出，就是删除登录成功时的标记，如果字典中没有键的话删除会报错
    if 'user_id' in session:
        del session['user_id']
    return jsonify(result=1)


"""在开发一个功能前，先回答如下问题：
	1.业务逻辑：查询当前登录的用户，并展示页面
	2.请求方式是什么？答：get
	3.是否ajax?答：否
	4.参数是什么？答：不需要
	5.返回什么数据？答：用户中心的页面
"""


# 先生成路由规则，当有具体用户请求后，才能验证用户是否登录
# 先写的先执行，后写的后执行
@user_blueprint.route('/')
@login_valid
def index():
    # 验证是否登录
    # if 'user_id' not in session:
    #     return redirect('/')
    #     # 查询当前登录的用户
    # user_id = session.get('user_id')
    # g.user = UserInfo.query.get(user_id)
    return render_template(
        'news/user.html',
        title='用户中心',
    )


@user_blueprint.route('/base', methods=['GET', 'POST'])
@login_valid
def base():
    # # 验证是否登录
    # if 'user_id' not in session:
    #     return redirect('/')
    # g.user = UserInfo.query.get(session.get('user_id'))

    if request.method == 'GET':
        return render_template('news/user_base_info.html')
    # 如果是post请求，则修改用户：签名，昵称，性别
    # 接收
    nick_name = request.form.get('nick_name')
    gender = request.form.get('gender')
    signature = request.form.get('signature')
    # 验证
    if not all([nick_name, gender, signature]):
        return jsonify(result=1)
    # 处理
    g.user.nick_name = nick_name
    g.user.gender = bool(int(gender))
    g.user.signature = signature
    db.session.commit()
    # 响应
    return jsonify(result=2)


@user_blueprint.route('/pic', methods=['GET', 'POST'])
@login_valid
def pic():
    if request.method == 'GET':
        return render_template('news/user_pic_info.html')
    # post请求，接收文件并保存，修改头像属性并保存，返回新的头像
    # 接收文件
    avatar = request.files.get('avatar')
    # 保存文件：文件被保存在了py代码所在的磁盘上
    # 实际情况下，文件被保存到了单独的服务器：第三方文件服务器，自己搭建文件服务器
    # 将头像图片上传到七牛服务器
    # print(type)
    # 保存文件　　　把文件保存在这个路径下  +再加上文件的名字
    # avatar.save(current_app.config.get('UPLOAD_FILE_PATH')+avatar.filename)
    # 将文件上传到七牛服务器
    avatar_name = qiniu_upload.upload(avatar)
    user = g.user
    user.avatar = avatar_name
    db.session.commit()

    return jsonify(avatar=user.avatar_url)


# 新闻发布
@user_blueprint.route('/release', methods=['GET', 'POST'])
@login_valid
def release():
    if request.method == 'GET':
        #查询新闻分类
        category_list=NewsCategory.query.all()
        return render_template('news/user_news_release.html',category_list=category_list)
    # post请求时
    # 接收:标题、分类、摘要、内容
    title = request.form.get('title')
    category_id = request.form.get('category_id')
    summary = request.form.get('summary')
    content = request.form.get('content')
    # 文件
    pic = request.files.get('pic')

    # 验证
    # 1.非空
    if not all([title, category_id, summary, content, pic]):
        return render_template(
            'news/user_news_release.html',
            msg='请将数据填写完整'
        )
    # 2.与定义一致的长度

    # 处理：保存到七牛
    pic_name = qiniu_upload.upload(pic)

    # 处理:创建对象，属性赋值，提交
    news = NewsInfo()
    news.title = title
    news.category_id = int(category_id)
    news.summary = summary
    news.content = content
    news.pic = pic_name
    news.user_id = g.user.id  # session.get('user_id')
    # 提交到数据库
    db.session.add(news)
    db.session.commit()

    # 响应
    return redirect('/user/newslist')


#新闻列表
@user_blueprint.route('/newslist')
@login_valid
def newslist():
    #接收页码  默认是第一页
    page=int(request.args.get('page','1'))
    #查询指定页的新闻列表  怎么判断出是哪个用户发布的新闻，所以用user_id来查询
    #把查询出来的列表分页，每页３条数据，输入的页码大于设置的页数也不会报错
    pagination=NewsInfo.query.filter_by(user_id=g.user.id).\
              order_by(NewsInfo.id.desc()).\
              paginate(page,3,False)
    #获取当前的数据
    news_list=pagination.items
    #查询总页数
    total_page=pagination.pages
    #响应
    return render_template("news/user_news_list.html",news_list=news_list,
                           total_page=total_page,page=page)


@user_blueprint.route('/password',methods=['GET','POST'])
@login_valid
def password():
    if request.method=='GET':
        return render_template('news/user_pass_info.html')
    #接收
    old_password=request.form.get('old_password')
    new_password = request.form.get('new_password')
    new_que_password=request.form.get('new_que_password')
    if g.user.check_pwd(old_password):
        session['user_id'] = g.user.id
    else:
        # 密码错误
        return jsonify(result=1)
    if not all([password,new_password]):
        return jsonify(result=2)
    if new_password !=new_que_password:
        return jsonify(result=3)
    if not re.match(r'^[0-9a-zA-Z]{6,20}$', new_password):
        return jsonify(result=4)
    # 处理
    user=g.user
    user.password=new_password
    db.session.commit()
    # 响应
    return jsonify(result=5)



