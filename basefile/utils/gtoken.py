#encoding:utf-8
'''
规则：
content='didi'+timestamp+appkey+appsecret    #appkey   appsecret由我们提供
signature=Lowercase(Binaery2HEX(HMAC-SHA256(secret_key,MD5(content))))

secret_key 加密密钥： 47735f03babbdcbd708d8  我们保留

'''
import datetime
import hmac
import hashlib



class Token(object):
    def __init__(self,appkey,appsecret):
        self.appkey=appkey   #相当于username
        self.appsecret=appsecret #相当于分配给用户的密码

    def content(self,timestr):
        return 'didi'+ '.' +'bigdata_ailab' + '.' + timestr + str(self.appkey) + str(self.appsecret)


    # MD5加密
    def MD5(self,src):
        m = hashlib.md5()
        m.update(src.encode('UTF-8'))
        return m.hexdigest()


    def get_hmac_sha256(self,timestr):
        secret_key='47735f03babbdcbd708d8'   #密钥key，保留，只有自己知道
        #  # hmac_sha256加密 第一个参数是密钥key，第二个参数是待加密的字符串，第三个参数是hash函数
        signature = hmac.new(bytes(secret_key, encoding='utf-8'), bytes(self.MD5(self.content(timestr)), encoding='utf-8'),digestmod=hashlib.sha256).digest()
        HEX = signature.hex()  #二进制转为HEX
        lowsign = HEX.lower()
        return lowsign

if __name__=='__main__':
    timestr = str(datetime.datetime.now())
    print(timestr)
    print(Token('woqu','woqudidi').get_hmac_sha256(timestr))

