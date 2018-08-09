from flask import Blueprint, jsonify
from flask import abort
from flask import g
from flask import render_template
from flask import request
from flask import session

from models import NewsCategory, NewsInfo, UserInfo, db

news_blueprint = Blueprint('new', __name__)


@news_blueprint.route('/')
def index():
    # 处理
    # 功能：分类、登录状态、点击排行，业务逻辑都是数据库查询
    # 分类
    category_list = NewsCategory.query.all()
    # 登录状态　
    if 'user_id' in session:
        user_id = session.get('user_id')  # 从session字典中用键取值　　
        g.user = UserInfo.query.get(user_id)  # 根据主键查询对象
    else:
        g.user = None
        # 点击排行　　select * fron  newsinfo  order by (newsinfo.click_count.desc())
    click_list = NewsInfo.query.order_by(NewsInfo.click_count.desc())[0:6]
    return render_template('news/index.html', click_list=click_list,
                           category_list=category_list, title='首页')


# 新闻首页
@news_blueprint.route('/newslist')
def newslist():
    # 接收
    category_id = int(request.args.get('category_id', 0))
    # 如果请求方式是ｇｅｔ，则用args,如果是ｐｏｓｔ，则用ｆｏｒｍ
    page = int(request.args.get('page', 1))
    # 验证如果没有page则为１如果没有category则为０
    # 处理

    query = NewsInfo.query  # select * from NewsInfo
    # 查询时进行语句的拼接，直到用到数据时，才会执行查询
    # 在用数据之前，所有的语句都是在进行ＳＱＬ语句的拼接，直到用到for 遍历数据时，才会去查询数据库，这是orm的优化
    # 如果编号＝０，表示查询所有的分类，如果大于０，表示查询某个分类
    if category_id > 0:
        query = query.filter_by(category_id=category_id)
    # 排序，分页
    query = query.order_by(NewsInfo.id.desc()).paginate(page, 4, False)
    # 响应
    news_list = query.items  # [news,news,.....]
    # news对象无法直接转成json语句，需要先转成字典，再转成json数据
    # 获取数据，转成字典
    # 页面需要什么数据，就找什么数据就可以
    total_page = query.pages
    news_list2 = []
    for news in news_list:  # 在字典里取值
        news_list2.append({
            'id': news.id,
            'pic': news.pic_url,
            'title': news.title,
            'summary': news.summary,
            'avatar': news.user.avatar_url,
            'nick_name': news.user.nick_name,
            # python中的datatime类型有个方法strftime()日期格式化，转成字符串
            'create_time': news.create_time.strftime('%Y-%m-%d')
        })
    return jsonify(news_list=news_list2, total_page=total_page)


# 新闻详情页
@news_blueprint.route('/<int:news_id>')
def detail(news_id):
    if 'user_id' in session:
        g.user = UserInfo.query.get(session.get('user_id'))
    else:
        g.user = None
    # 根据主键查询新闻对象
    news = NewsInfo.query.get(news_id)
    # 如果没有查询到新闻对象，则返回none
    if not news:
        abort(404)
    # 更新点击量
    news.click_count += 1
    db.session.commit()
    # 点击排行
    click_list = NewsInfo.query.order_by(NewsInfo.click_count.desc())[0:6]
    return render_template('news/detail.html', click_list=click_list,
                           news=news, title='文章详情页')


# 关注和取消关注
@news_blueprint.route('/follow', methods=['POST'])
def follow():
    # 接收
    author_id = request.form.get('author_id')

    # 验证
    if not author_id:
        return jsonify(result=1)
    if 'user_id' not in session:
        return jsonify(result=2)
    user_id = session.get('user_id')
    # 查询对象
    user = UserInfo.query.get(user_id)
    author = UserInfo.query.get(author_id)

    # 处理
    if author in user.authors:
        # 取消
        user.authors.remove(author)
        # 粉丝数-1
        author.follow_count -= 1
    else:
        user.authors.append(author)
        author.follow_count += 1

    db.session.commit()
    return jsonify(result=3)
    # 响应
