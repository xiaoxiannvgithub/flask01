from flask import Blueprint, jsonify
from flask import current_app
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from datetime import datetime
from models import UserInfo, NewsInfo, NewsCategory, db

admin_blueprint = Blueprint('admin', __name__, url_prefix='/admin')


# 登录
@admin_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    # 接收
    if request.method == 'GET':
        return render_template('admin/login.html')
    name = request.form.get('username')
    pwd = request.form.get('password')
    if not all([name, pwd]):
        return render_template('admin/login.html', msg='请填写完整')

    user = UserInfo.query.filter_by(mobile=name, isAdmin=True).first()

    if user:
        if user.check_pwd(pwd):
            # 登录成功
            session['admin_id'] = user.id
            return redirect('/admin/')
        else:
            return render_template('admin/login.html', msg='密码错误')
    else:
        return render_template('admin/login.html', msg='用户名错误')


@admin_blueprint.before_request
def login_valid():
    ignore_list = ['/admin/login']
    if request.path not in ignore_list:
        if 'admin_id' not in session:
            return redirect('/admin/login')
        g.user = UserInfo.query.get(session.get('admin_id'))


# 首页
@admin_blueprint.route('/')
def index():
    return render_template('admin/index.html')


# 退出
@admin_blueprint.route('/logout')
def logout():
    del session['admin_id']
    return redirect('/admin/login')


# 用户统计
@admin_blueprint.route('/usercount')
def usercount():
    # 接收  用户总数
    totla_count = UserInfo.query.filter_by(isAdmin=False).count()
    # 用户月新増数  先定义出这个月的第一天的，大于这一天的所有的用户
    now = datetime.now()
    month_first = datetime(now.year, now.month, 1)
    month_count = UserInfo.query.filter_by(isAdmin=False). \
        filter(UserInfo.create_time >= month_first).count()
    # 用户日增数
    day_first = datetime(now.year, now.month, now.day)
    day_count = UserInfo.query.filter_by(isAdmin=False). \
        filter(UserInfo.create_time >= day_first).count()
    # 用户登录活跃书
    key = 'login' + now.strftime('%Y%m%d')
    # app.redis_cli = redis.StrictRedis(config.REDIS_HOST, config.REDIS_PORT, config.REDIS_DB)
    # 通过current_app连接数据库redis,获取数据库中的StrictRedis类，可以调用类里面的方法
    redis_cli = current_app.redis_cli
    # 获取所有的属性，（时间）
    times = redis_cli.hkeys(key)
    # 获取所有的值（总量）键是login20180806
    counts = redis_cli.hvals(key)
    # for time in times:
    #     times=time.decode()
    #     print(times)
    times = [item.decode() for item in times]
    # for count in counts:
    #     counts=int(count)
    #     print(counts)
    counts = [int(item) for item in counts]
    return render_template('admin/user_count.html', totla_count=totla_count,
                           month_count=month_count, day_count=day_count, times=times, counts=counts)
    # 处理


# 新闻列表
@admin_blueprint.route('/news_review')
def news_review1():
    return render_template('admin/news_review.html')


@admin_blueprint.route('/news_review2')
def news_review2():
    # 接收参数
    # 搜索关键字
    title = request.args.get('title')
    # 页码
    page = int(request.args.get('page', 1))
    # 拼接查询语句
    query = NewsInfo.query
    if title:
        # 查询新闻标题包括制定字符串的数据
        query = query.filter(NewsInfo.title.contains(title))
    pagination = query.order_by(NewsInfo.id). \
        paginate(page, 5, False)
    # 获取当前页的数据
    news_list = pagination.items
    # 获取总页数
    total_page = pagination.pages
    news_list2 = []
    for news in news_list:
        news_list2.append({
            'id': news.id,
            'title': news.title,
            'create_time': news.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            'status': news.status
        })
    return jsonify(news_list=news_list2, total_page=total_page)


# 后台管理－－新闻分类管理
@admin_blueprint.route('/type_list')
def type_list():
    return render_template('admin/news_type.html')


@admin_blueprint.route('/type_list_json')
def type_list_json():
    # 查询
    category_list = NewsCategory.query.all()
    # 把列表转成字典
    category_list2 = []
    for category in category_list:
        category_list2.append(
            {
                'id': category.id,
                'name': category.name
            }
        )
        # 返回json
    return jsonify(category_list=category_list2)


@admin_blueprint.route('/type_add', methods=['POST'])
def type_add():
    # 接收参数
    name = request.form.get('name')
    # 验证
    # 非空
    if not name:
        return jsonify(result=1)
    # 如果新闻种类中有同名的种类
    if NewsCategory.query.filter_by(name=name).count() > 0:
        return jsonify(result=2)
    # #如果没有修改
    # if category_name==category_name:
    #     return jsonify(result=3)
    # 处理
    category = NewsCategory()
    category.name = name
    db.session.add(category)
    db.session.commit()

    return jsonify(result=3)


@admin_blueprint.route('/type_edit/<int:category_id>', methods=['POST'])
def type_edit(category_id):
    # 参数
    name = request.form.get('name')

    if not name:
        return jsonify(result=1)
    # 是否修改
    category = NewsCategory.query.get(category_id)
    if category.name == name:
        return jsonify(result=2)

    #
    if NewsCategory.query.filter_by(name=name).count() > 0:
        return jsonify(result=3)
    # 处理
    category.name = name
    db.session.commit()

    return jsonify(result=4)
