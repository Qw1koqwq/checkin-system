from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Activity, User, Registration
from datetime import datetime
import json
from utils.auth_helper import parse_user_id, require_active_user

activity_bp = Blueprint('activity', __name__)

@activity_bp.route('', methods=['GET'])
def get_activities():
    """获取活动列表（支持筛选和分页）"""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 10, type=int)
    category = request.args.get('category')
    status = request.args.get('status')
    keyword = request.args.get('keyword')
    start_date = request.args.get('startDate')
    
    query = Activity.query
    
    # 筛选条件
    if category:
        query = query.filter_by(category=category)
    if status:
        query = query.filter_by(status=status)
    if keyword:
        query = query.filter(Activity.title.contains(keyword))
    if start_date:
        # 匹配当天开始的活动（从00:00:00到23:59:59）
        start_datetime = datetime.fromisoformat(start_date)
        end_datetime = start_datetime.replace(hour=23, minute=59, second=59, microsecond=999999)
        query = query.filter(Activity.start_time >= start_datetime, Activity.start_time <= end_datetime)
    
    # 分页
    pagination = query.order_by(Activity.created_at.desc()).paginate(
        page=page, per_page=page_size, error_out=False, max_per_page=100
    )
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': {
            'items': [activity.to_dict() for activity in pagination.items],
            'total': pagination.total,
            'page': page,
            'pageSize': page_size,
            'totalPages': pagination.pages
        }
    })


@activity_bp.route('/<int:activity_id>', methods=['GET'])
def get_activity(activity_id):
    """获取活动详情"""
    activity = Activity.query.get(activity_id)
    
    if not activity:
        return jsonify({'code': 404, 'message': '活动不存在'}), 404
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': activity.to_dict()
    })


@activity_bp.route('', methods=['POST'])
@jwt_required()
@require_active_user
def create_activity():
    """创建活动（仅组织者）"""
    user_id = parse_user_id(get_jwt_identity())
    
    if user_id is None:
        return jsonify({'code': 403, 'message': '仅组织者可访问'}), 403
    
    user = User.query.get(user_id)
    
    if not user or user.role != 'organizer':
        return jsonify({'code': 403, 'message': '权限不足'}), 403
    
    data = request.get_json()
    
    # 验证必填字段
    required_fields = ['title', 'description', 'category', 'startTime', 'endTime', 
                      'location', 'maxParticipants', 'registrationDeadline']
    for field in required_fields:
        if field not in data:
            return jsonify({'code': 400, 'message': f'缺少必填字段: {field}'}), 400
    
    # 处理图片数据
    images = data.get('images', [])
    cover_image = images[0] if images else None
    
    # 创建活动
    activity = Activity(
        title=data['title'],
        description=data['description'],
        category=data['category'],
        organizer_id=user_id,
        start_time=datetime.fromisoformat(data['startTime'].replace('Z', '+00:00')),
        end_time=datetime.fromisoformat(data['endTime'].replace('Z', '+00:00')),
        location=data['location'],
        max_participants=data['maxParticipants'],
        registration_deadline=datetime.fromisoformat(data['registrationDeadline'].replace('Z', '+00:00')),
        cover_image=cover_image,
        images=json.dumps(images),
        tags=json.dumps(data.get('tags', [])),
        sub_items=json.dumps(data.get('subItems', []))
    )
    
    db.session.add(activity)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '创建成功',
        'data': activity.to_dict()
    }), 201


@activity_bp.route('/<int:activity_id>', methods=['PUT'])
@jwt_required()
@require_active_user
def update_activity(activity_id):
    """更新活动信息（仅创建者）"""
    user_id = parse_user_id(get_jwt_identity())
    
    if user_id is None:
        return jsonify({'code': 403, 'message': '仅组织者可访问'}), 403
    
    activity = Activity.query.get(activity_id)
    
    if not activity:
        return jsonify({'code': 404, 'message': '活动不存在'}), 404
    
    # 验证是否为创建者
    if activity.organizer_id != user_id:
        return jsonify({'code': 403, 'message': '权限不足'}), 403
    
    # 检查活动状态，进行中和已结束的活动不能编辑
    now = datetime.utcnow()
    if now >= activity.start_time and now <= activity.end_time:
        return jsonify({'code': 400, 'message': '进行中的活动不能编辑'}), 400
    if now > activity.end_time:
        return jsonify({'code': 400, 'message': '已结束的活动不能编辑'}), 400
    
    data = request.get_json()
    
    # 更新字段
    if 'title' in data:
        activity.title = data['title']
    if 'description' in data:
        activity.description = data['description']
    if 'category' in data:
        activity.category = data['category']
    if 'startTime' in data:
        activity.start_time = datetime.fromisoformat(data['startTime'].replace('Z', '+00:00'))
    if 'endTime' in data:
        activity.end_time = datetime.fromisoformat(data['endTime'].replace('Z', '+00:00'))
    if 'location' in data:
        activity.location = data['location']
    if 'maxParticipants' in data:
        if data['maxParticipants'] < activity.current_participants:
            return jsonify({'code': 400, 'message': '人数限制不能少于已报名人数'}), 400
        activity.max_participants = data['maxParticipants']
    if 'registrationDeadline' in data:
        activity.registration_deadline = datetime.fromisoformat(data['registrationDeadline'].replace('Z', '+00:00'))
    if 'images' in data:
        images = data['images']
        activity.images = json.dumps(images)
        activity.cover_image = images[0] if images else None
    if 'tags' in data:
        activity.tags = json.dumps(data['tags'])
    if 'subItems' in data:
        activity.sub_items = json.dumps(data['subItems'])
    
    activity.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '更新成功',
        'data': activity.to_dict()
    })


@activity_bp.route('/<int:activity_id>', methods=['DELETE'])
@jwt_required()
@require_active_user
def delete_activity(activity_id):
    """删除活动（仅创建者）"""
    user_id = parse_user_id(get_jwt_identity())
    
    if user_id is None:
        return jsonify({'code': 403, 'message': '仅组织者可访问'}), 403
    
    activity = Activity.query.get(activity_id)
    
    if not activity:
        return jsonify({'code': 404, 'message': '活动不存在'}), 404
    
    # 验证是否为创建者
    if activity.organizer_id != user_id:
        return jsonify({'code': 403, 'message': '权限不足'}), 403
    
    # 检查活动状态，进行中的活动不能删除
    now = datetime.utcnow()
    if now >= activity.start_time and now <= activity.end_time:
        return jsonify({'code': 400, 'message': '进行中的活动不能删除'}), 400
    
    db.session.delete(activity)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '删除成功'
    })


@activity_bp.route('/my', methods=['GET'])
@jwt_required()
@require_active_user
def get_my_activities():
    """获取我创建的活动（组织者）"""
    user_id = parse_user_id(get_jwt_identity())
    
    if user_id is None:
        return jsonify({'code': 403, 'message': '仅组织者可访问'}), 403
    
    user = User.query.get(user_id)
    
    if not user or user.role != 'organizer':
        return jsonify({'code': 403, 'message': '权限不足'}), 403
    
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 10, type=int)
    
    pagination = Activity.query.filter_by(organizer_id=user_id).order_by(
        Activity.created_at.desc()
    ).paginate(page=page, per_page=page_size, error_out=False, max_per_page=100)
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': {
            'items': [activity.to_dict() for activity in pagination.items],
            'total': pagination.total,
            'page': page,
            'pageSize': page_size,
            'totalPages': pagination.pages
        }
    })


@activity_bp.route('/categories', methods=['GET'])
def get_categories():
    """获取活动分类"""
    categories = ['academic', 'cultural', 'sports', 'volunteer', 'other']
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': categories
    })


@activity_bp.route('/admin/<int:activity_id>', methods=['DELETE'])
@jwt_required()
def admin_delete_activity(activity_id):
    """管理员删除活动（除了进行中的活动）"""
    identity = get_jwt_identity()
    
    # 验证是否为管理员
    if not identity or not identity.startswith('admin_'):
        return jsonify({'code': 403, 'message': '权限不足，仅管理员可访问'}), 403
    
    activity = Activity.query.get(activity_id)
    
    if not activity:
        return jsonify({'code': 404, 'message': '活动不存在'}), 404
    
    # 检查活动状态，进行中的活动不能删除
    now = datetime.utcnow()
    if now >= activity.start_time and now <= activity.end_time:
        return jsonify({'code': 400, 'message': '进行中的活动不能删除'}), 400
    
    db.session.delete(activity)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '删除成功'
    })


@activity_bp.route('/admin/export', methods=['GET'])
@jwt_required()
def admin_export_activities():
    """管理员导出活动列表"""
    from flask import make_response
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    from io import BytesIO
    
    identity = get_jwt_identity()
    
    # 验证是否为管理员
    if not identity or not identity.startswith('admin_'):
        return jsonify({'code': 403, 'message': '权限不足，仅管理员可访问'}), 403
    
    # 获取所有活动
    activities = Activity.query.order_by(Activity.created_at.desc()).all()
    
    # 创建Excel工作簿
    wb = Workbook()
    ws = wb.active
    ws.title = '活动列表'
    
    # 设置标题样式
    header_fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
    header_font = Font(color='FFFFFF', bold=True, size=12)
    header_alignment = Alignment(horizontal='center', vertical='center')
    
    # 写入表头
    headers = [
        'ID', '活动标题', '分类', '状态', '组织者', '开始时间', '结束时间', 
        '地点', '最大人数', '当前人数', '报名截止时间', '创建时间'
    ]
    ws.append(headers)
    
    # 设置表头样式
    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = header_alignment
    
    # 分类映射
    category_map = {
        'academic': '学术',
        'cultural': '文化',
        'sports': '体育',
        'volunteer': '志愿',
        'other': '其他'
    }
    
    # 写入数据
    for activity in activities:
        # 计算实际状态
        now = datetime.utcnow()
        if activity.status == 'cancelled':
            actual_status = '已取消'
        elif now < activity.start_time:
            actual_status = '未开始'
        elif now >= activity.start_time and now <= activity.end_time:
            actual_status = '进行中'
        else:
            actual_status = '已结束'
        
        row = [
            activity.id,
            activity.title,
            category_map.get(activity.category, activity.category),
            actual_status,
            activity.organizer.username,
            activity.start_time.strftime('%Y-%m-%d %H:%M:%S'),
            activity.end_time.strftime('%Y-%m-%d %H:%M:%S'),
            activity.location,
            activity.max_participants,
            activity.current_participants,
            activity.registration_deadline.strftime('%Y-%m-%d %H:%M:%S'),
            activity.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ]
        ws.append(row)
    
    # 调整列宽
    column_widths = [8, 30, 10, 10, 15, 20, 20, 20, 10, 10, 20, 20]
    for i, width in enumerate(column_widths, start=1):
        ws.column_dimensions[chr(64 + i)].width = width
    
    # 保存到内存
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    
    # 创建响应
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response.headers['Content-Disposition'] = f'attachment; filename=activities_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    
    return response
