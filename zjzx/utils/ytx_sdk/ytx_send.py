from .CCPRestSDK import REST

# 主帐号
accountSid = '8aaf070864b08c210164cd08fd881061'

# 主帐号Token
accountToken = 'e49a2757496c449eb581f9157d3b4961'

# 应用Id
appId = '8aaf070864b08c210164cd08fde31068'

# 请求地址，格式如下，不需要写http://
serverIP = 'app.cloopen.com'

# 请求端口
serverPort = '8883'

# REST版本号
softVersion = '2013-12-26'

# 发送模板短信
# @param to 手机号码
# @param datas 内容数据 格式为列表 例如：[验证码，以分为单位的有效时间]
# @param $tempId 模板Id

def sendTemplateSMS(to, datas, tempId):

    # 初始化REST SDK
    rest = REST(serverIP, serverPort, softVersion)
    rest.setAccount(accountSid, accountToken)
    rest.setAppId(appId)

    result = rest.sendTemplateSMS(to, datas, tempId)
    return result.get('statusCode')