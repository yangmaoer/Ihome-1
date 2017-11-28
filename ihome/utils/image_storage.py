# coding: utf-8

from qiniu import Auth, put_data, etag, urlsafe_base64_encode
import qiniu.config

# 需要填写你的 Access Key 和 Secret Key
access_key = 'S0zPGk49YL22ShjaGIbE-Ne-NY0aQPVeMiUsE70t'
secret_key = 'DAME-9JAqsxhnh449_iX3c0QY2unG5j-JBSvgCcV'


def storage(filedata):
    # 构建鉴权对象
    q = Auth(access_key, secret_key)

    # 要上传的空间
    bucket_name = 'ihome'

    # # 上传到七牛后保存的文件名
    # key = 'my-python-logo.png'

    # 生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, None, 3600)

    # # 要上传文件的本地路径
    # localfile = './sync/bbb.jpg'

    ret, info = put_data(token, None, filedata)

    if info.status_code == 200:
        return ret.get('key')
    else:
        raise Exception('上传七牛失败')

    # # assert ret['key'] == key
    # assert ret['hash'] == etag(localfile)

if __name__ == '__main__':
    with open('./01.jpg','rb') as f:
        filedata = f.read()
        storage(filedata)