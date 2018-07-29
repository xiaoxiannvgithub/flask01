from flask import Blueprint, session, make_response, request, jsonify
from utils.captcha.captcha import captcha
from utils.ytx_sdk import ytx_send
import random
user_blueprint=Blueprint('user',__name__,url_prefix='/user')
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
    #强制图形验证码过期，防止客户端不停尝试
    del session['image_code']

    if imagecode != imagecode_session:
        return jsonify(result=2)

    # 处理
    # 1.生成随机的验证码
    smscode = str(random.randint(100000, 999999))
    # 2.保存验证码，用于后续验证
    session['sms_code'] = smscode
    # 3.发送短信
    # ytx_send.sendTemplateSMS(mobile, [smscode, '10'], 1)
    print(smscode)

    # 响应
    return jsonify(result=3)