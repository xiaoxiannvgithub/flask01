from qiniu import Auth, put_data


def upload(f1):
    # 注册后的账号信息
    access_key = 'H999S3riCJGPiJOity1GsyWufw3IyoMB6goojo5e'
    secret_key = 'uOZfRdFtljIw7b8jr6iTG-cC6wY_-N19466PXUAb'
    # 空间名称
    bucket_name = 'itcast20171104'
    # 构建鉴权对象　　做身份验证的
    q = Auth(access_key, secret_key)
    # 生成上传 Token　通脱鉴权对象调用upload_token
    token = q.upload_token(bucket_name)
    # NONE 是七牛起的名字．上传文件数据，ret是字典，键为hash、key，值为新文件名，info是response对象
    ret, info = put_data(token, None, f1.read())
    # 返回文件名  ret 是字典，键的名字是key　通过键返回值的名字
    return ret.get('key')