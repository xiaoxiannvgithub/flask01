import random
from datetime import datetime

from flask import current_app
from flask_script.commands import Command
from models import UserInfo, db


class CreateAdmin(Command):
    # Ｃｏｍｍａｎｄ里面有一个方法是run
    def run(self):
        name = input('请输入用户名')
        pwd = input('请输入密码')

        user = UserInfo()
        user.mobile = name
        user.nick_name = name
        user.password = pwd
        user.isAdmin = True
        db.session.add(user)
        db.session.commit()
        print('管理员创建成功')

#作用帮助造一些数据
class LoginTest(Command):
    def run(self):
        now = datetime.now()
        redis_cli = current_app.redis_cli
        key = 'login' + now.strftime('%Y%m%d')
        # redis_cli.hset(key,'8:00',120)
        # redis_cli.hset(key,'9:00',220)
        # redis_cli.hset(key,'10:00',130)
        for index in range(8, 20):
            redis_cli.hset(key, '%02d:00' % index, random.randint(200, 500))
        print('ok')
