# coding=utf-8

from . import api
from ihome.utils.commons import login_required
from flask import g, current_app, jsonify, request
from ihome.utils.response_code import RET
from ihome.utils.image_storage import storage
from ihome.models import Area, House, HouseImage, Facility
from ihome import db, constants, redis_store
from flask import session, json


@api.route('/areas')
def get_area_info():
    # 首先从redis中获取信息
    try:
        resp_json = redis_store.get('area_info')
    except Exception as e:
        current_app.logger.error(e)
    else:
        if resp_json is not None:
            # redis有缓存数据
            current_app.logger.info("hit redis area_info")
            return resp_json, 200, {"Content-Type": "application/json"}

    # 获取区域列表
    try:
        area_li = Area.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询区域信息失败')
    if area_li is None:
        return jsonify(errno=RET.DATAERR, errmsg='未查找到区域信息')

    # 构造返回信息对象
    area_dict_li = []
    for area in area_li:
        area_dict_li.append(area.to_dict())

    # 将返回数据类型转换为字符串
    resp_dict = dict(errno=RET.OK, errmsg='OK', data=area_dict_li)

    # print(resp_dict['data'])  # 调试打印区域信息

    resp_json = json.dumps(resp_dict)

    # 将数据存储到redis_store中
    try:
        redis_store.setex('area_info', constants.AREA_INFO_REDIS_CACHE_EXPIRES, resp_json)
    except Exception as e:
        current_app.logger.error(e)

    # 返回信息
    return resp_json, 200, {'Content-Type': 'application/json'}


@api.route('/house/info', methods=['POST'])
@login_required
def set_new_house():
    """保存房屋的基本信息
    前端发送过来的json数据
    {
        "title":"",
        "price":"",
        "area_id":"1",
        "address":"",
        "room_count":"",
        "acreage":"",
        "unit":"",
        "capacity":"",
        "beds":"",
        "deposit":"",
        "min_days":"",
        "max_days":"",
        "facility":["7","8"]
    }
    """
    # 获取需要获得的信息
    user_id = g.user_id
    house_data = request.get_json()

    title = house_data.get("title")  # 房屋名称标题
    price = house_data.get("price")  # 房屋单价
    area_id = house_data.get("area_id")  # 房屋所属城区的编号
    address = house_data.get("address")  # 房屋地址
    room_count = house_data.get("room_count")  # 房屋包含的房间数目
    acreage = house_data.get("acreage")  # 房屋面积
    unit = house_data.get("unit")  # 房屋布局（几室几厅)
    capacity = house_data.get("capacity")  # 房屋容纳人数
    beds = house_data.get("beds")  # 房屋卧床数目
    deposit = house_data.get("deposit")  # 押金
    min_days = house_data.get("min_days")  # 最小入住天数
    max_days = house_data.get("max_days")  # 最大入住天数

    # 检验参数
    if not all(
            [title, price, area_id, address, room_count, acreage, unit, capacity, beds, deposit, min_days, max_days]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

    # 将数据进行分析处理并存储到数据库中
    # 判断金额是否完全正确
    try:
        price = int(float(price) * 100)
        deposit = int(float(deposit) * 100)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='参数有误')

    # 判断城区id是否存在
    try:
        area = Area.query.get(area_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库异常')

    if area is None:
        return jsonify(errno=RET.NODATA, errmsg='未获取到城区信息')
    # 保存房屋信息
    house = House(
        user_id=user_id,
        area_id=area_id,
        title=title,
        price=price,
        address=address,
        room_count=room_count,
        acreage=acreage,
        unit=unit,
        capacity=capacity,
        beds=beds,
        deposit=deposit,
        min_days=min_days,
        max_days=max_days
    )

    # 处理房屋的设施信息
    facility_ids = house_data.get('facility')

    # 如果用户勾选了设施信息，再保存数据库
    if facility_ids:
        try:
            facilities = Facility.query.filter(Facility.id.in_(facility_ids)).all()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg='数据库错误')
        if facilities:
            house.facilities = facilities
            db.session.add(house)
    # 进行数据库提交操作
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='保存数据库失败')

    # 保存数据成功
    return jsonify(errno=RET.OK, errmsg='OK', data={'house_id': house.id})


@api.route('/house/img', methods=['POST'])
@login_required
def set_house_img():
    # 获取图片和对应的房屋id
    image_file = request.files.get('house_image')
    house_id = request.form.get('house_id')
    if not all([image_file, house_id]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数有误')

    # 判断house_id正确性
    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(ernro=RET.DBERR, errmsg='数据库异常')
    if house is None:
        return jsonify(ernro=RET.NODATA, errmsg='未获取到房屋数据')

    # 上传图片到服务器
    try:
        image_data = image_file.read()
        file_name = storage(image_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg='上传图片失败')

    # 将上传后返回的url保存到house属性
    # 保存图片信息到数据库中
    house_image = HouseImage(house_id=house_id, url=file_name)
    db.session.add(house_image)

    # 处理房屋的主图片
    if house.index_image_url is None:
        house.index_image_url = file_name
        db.session.add(house)

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='数据库异常')

    img_url = constants.QINIU_URL_DOMAIN + file_name
    return jsonify(errno=RET.OK, errmsg='OK', data={'img_url': img_url})
