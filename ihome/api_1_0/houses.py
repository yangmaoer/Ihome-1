# coding:utf-8

from . import api
from ihome.utils.commons import login_required
from flask import g, current_app, jsonify, request
from ihome.utils.response_code import RET
from ihome.utils.image_storage import storage
from ihome.models import Area, House, HouseImage, Facility, User, Order
from ihome import db, constants, redis_store
from flask import session, json
from datetime import datetime


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
    if not house.index_image_url:
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


@api.route('/user/houses', methods=['GET'])
@login_required
def get_user_houses():
    user_id = g.user_id
    try:
        # House.query.filter_by(user_id=user_id)
        user = User.query.get(user_id)
        houses = user.houses
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取数据失败")

    # 将查询到的房屋信息转换为字典存放到列表中
    houses_list = []
    if houses:
        for house in houses:
            houses_list.append(house.to_basic_dict())
    return jsonify(errno=RET.OK, errmsg="OK", data={"houses": houses_list})


# search.html?aid=3&aname=朝阳区&sd=2017-12-01&ed=2017-12-03
@api.route('/houses', methods=['GET'])
def get_houses_list():
    """获取房屋的列表信息（搜索页面）"""
    start_date = request.args.get("sd", "")  # 用户想要的起始时间
    end_date = request.args.get("ed", "")  # 用户想要的结束时间
    area_id = request.args.get("aid", "")  # 区域编号
    sort_key = request.args.get("sk", "new")  # 排序关键字
    page = request.args.get("p")  # 页数

    # 处理时间
    try:
        if start_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")

        if end_date:
            end_date = datetime.strptime(end_date, "%Y-%m-%d")

        if start_date and end_date:
            assert start_date <= end_date
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="日期参数有误")

    # 判断区域id
    if area_id:
        try:
            area = Area.query.get(area_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.PARAMERR, errmsg="区域参数有误")

    # 处理页数
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    # 获取缓存数据
    redis_key = 'house_%s_%s_%s_%s' % (start_date, end_date, area_id, sort_key)
    try:
        resp_json = redis_store.hget(redis_key, page)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if resp_json:
            return resp_json, 200, {'Content-Type': 'application/json'}

    # 过滤条件的参数列表容器
    filter_params = []
    conflict_orders = None

    # 填充过滤参数
    # 时间条件
    try:
        # 查询冲突的订单
        if start_date and end_date:
            conflict_orders = Order.query.filter(Order.begin_date <= end_date, Order.end_date >= start_date).all()
        elif start_date:
            conflict_orders = Order.query.filter(Order.end_date >= start_date).all()
        elif end_date:
            conflict_orders = Order.query.filter(Order.begin_date <= end_date).all()

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库异常")

    if conflict_orders:
        conflict_house_ids = [order.house_id for order in conflict_orders]
        if conflict_house_ids:
            filter_params.append(House.id.notin__(conflict_house_ids))

    # 区域条件
    if area_id:
        filter_params.append(House.area_id == area_id)

    # 查询数据库
    # 补充排序条件

    if sort_key == 'booking':
        house_query = House.query.filter(*filter_params).order_by(House.order_count.desc())
    elif sort_key == 'price-inc':
        house_query = House.query.filter(*filter_params).order_by(House.price.asc())
    elif sort_key == 'price-desc':
        house_query = House.query.filter(*filter_params).order_by(House.price.desc())
    else:
        house_query = House.query.filter(*filter_params).order_by(House.create_time.desc())

    # 处理分页
    try:
        # 创建分页对象                     当前页数              每页显示个数                     抛出错误信息,默认为True
        page_obj = house_query.paginate(page=page, per_page=constants.HOUSE_LIST_PAGE_CAPACITY, error_out=False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库异常')

    # 获取页面数据
    house_li = page_obj.items
    houses = []
    for house in house_li:
        houses.append(house.to_basic_dict())

    # 获取总页数
    total_pages = page_obj.pages

    json_dict = dict(errno=RET.OK, errmsg='OK', data={'pages': total_pages, 'houses': houses, 'current_page': page})
    resp_json = json.dumps(json_dict)

    # 设置缓存
    if page <= total_pages:
        redis_key = 'house_%s_%s_%s_%s' % (start_date, end_date, area_id, sort_key)
        try:
            redis_store.hset(redis_key, page, resp_json)
            redis_store.expire(redis_key, constants.HOUES_LIST_PAGE_REDIS_CACHE_EXPIRES)
            # 创建管道
            # pipline = redis_store.pipline()
            # pipline.multi()
            #
            # pipline.hset(redis_key,page,resp_json)
            # pipline.expire(redis_key,constants.HOUES_LIST_PAGE_REDIS_CACHE_EXPIRES)
            #
            # pipline.execute()

        except Exception as e:
            current_app.logger.error(e)

    return resp_json, 200, {'Content-Type': 'application/json'}

