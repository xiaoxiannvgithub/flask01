import re
from flask import Blueprint, session, make_response, request, jsonify
from flask import g
from flask import redirect
from flask import render_template

from utils.captcha.captcha import captcha
from utils.ytx_sdk import ytx_send
import random
from models import UserInfo, db

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


@user_blueprint.route('/login',methods=['POST'])
def login():
    mobile=request.form.get('mobile')
    password=request.form.get('password')
    #验证
    if not all([mobile,password]):
        return jsonify(result=1)
    #处理:根据手机号查询对象，再对比密码
    user=UserInfo.query.filter_by(mobile=mobile).first()
    if not user:
        #如果没有查询到数据，则返回none
        #手机号错误
        return jsonify(result=2)
    #如果查询到对象，密码是加过密的
    if user.check_pwd(password):
        #状态保持．记录用户登录成功
        #只有登录成功以后，字典里才会有这个值user.id
        #看有没有登录过，就看session里面有没有这个user_id
        session['user_id']=user.id
        #密码正确
        return jsonify(result=4,nick_name=user.nick_name,avatar=user.avatar)
    else:
        #密码错误
        return jsonify(result=3)


@user_blueprint.route('/logout')
def logout():
    #退出，就是删除登录成功时的标记，如果字典中没有键的话删除会报错
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
@user_blueprint.route('/')
def index():
    #验证是否登录
     if 'user_id' not in session:
         return redirect('/')
     #查询当前登录的用户
     user_id=session.get('user_id')
     g.user=UserInfo.query.get(user_id)
     return render_template(
         'news/user.html',
          title='用户中心',
     )
@user_blueprint.route('/base',methods=['GET','POST'])
def base():
    pass
