# coding:utf-8

# 设置图片验证码的redis有效期
IMAGE_REDIS_EXPIRES = 180

# 短信验证码的redis有效期, 单位：秒
SMS_CODE_REDIS_EXPIRES = 300

# 发送短信验证码的间隔, 单位：秒
SEND_SMS_CODE_INTERVAL = 60

# 设置最多允许错误次数
LOGIN_ERROR_MAX_TIMES = 5

# 设置输入错误后禁止输入时长
LOGIN_ERROR_FORBID_TIME = 600

# 七牛的域名
QINIU_URL_DOMAIN = "http://o91qujnqh.bkt.clouddn.com/"

# 城区信息的缓存时间, 单位：秒
AREA_INFO_REDIS_CACHE_EXPIRES = 7200