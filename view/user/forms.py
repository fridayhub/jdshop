#!/usr/bin/env python3
# -*-coding:utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Regexp, Length
from view.models import Tuser


class AddTaskForm(FlaskForm):
    goods_id = StringField(
        label='商品编号',
        validators=[
            DataRequired('请输入商品编号!')
        ],
        description='商品编号',
        render_kw={
            'class': "form-control",
            'placeholder': "商品编号"
        }
    )

    goods_name = StringField(
        label='商品名称',
        validators=[
            DataRequired('请输入商品名称!')
        ],
        description='商品名称',
        render_kw={
            'class': "form-control",
            'placeholder': "商品名称"
        }
    )

    goods_channel = SelectField(
        label='商品渠道',
        validators=[
            DataRequired('请输入商品渠道！')
        ],
        coerce=int,
        choices=[(1, '京东'), (2, '天猫')],
        description='商品渠道...',
        render_kw={
            'class': 'form-control',
        }
    )

    buy_type = SelectField(
        label='购买类型',
        validators=[
            DataRequired('请输入购买类型！')
        ],
        coerce=int,
        choices=[(1, '抢购'), (2, '秒杀')],
        description='购买类型...',
        render_kw={
            'class': 'form-control',
        }
    )

    buy_time = StringField(
        label='抢购时间',
        validators=[
            DataRequired('请输入抢购时间!')
        ],
        description='抢购时间',
        render_kw={
            'class': "form-control",
            'placeholder': "抢购时间",
            'id': 'input_buy_time'
        }
    )

    original_price = StringField(
        label='原价',
        validators=[
            DataRequired('请输入原价!')
        ],
        description='原价',
        render_kw={
            'class': "form-control",
            'placeholder': "原价"
        }
    )

    buy_price = StringField(
        label='抢购\秒杀价',
        validators=[
            DataRequired('请输入购买价!')
        ],
        description='购买价',
        render_kw={
            'class': "form-control",
            'placeholder': "购买价"
        }
    )

    submit = SubmitField(
        '提交',
        render_kw={
            'class': 'btn btn-success'
        }
    )


class RegisterForm(FlaskForm):
    name = StringField(
        label="用户名",
        validators=[
            DataRequired("用户名不能为空")
        ],
        description='用户名',
        render_kw={
            'class': 'form-control input-lg',
            'placeholder': '请输入用户名',
        }
    )

    email = StringField(
        label="邮箱",
        validators=[
            DataRequired("邮箱不能为空"),
            Email('邮箱格式不正确...')
        ],
        description='邮箱',
        render_kw={
            'class': 'form-control input-lg',
            'placeholder': '请输入邮箱',
        }
    )

    phone = StringField(
        label="手机",
        validators=[
            DataRequired("手机号码不能为空"),
            Regexp('1[34578]\\d{9}', message='手机格式不正确!'),
            Length(min=11, max=11, message='手机号码长度有误!')
        ],
        description='手机',
        render_kw={
            'class': 'form-control input-lg',
            'placeholder': '请输入手机',
        }
    )

    pwd = PasswordField(
        label='密码',
        validators=[
            DataRequired('密码不能为空！')
        ],
        description='密码',
        render_kw={
            'class': 'form-control input-lg',
            'placeholder': '请输入密码',
        }
    )

    repwd = PasswordField(
        label='确认密码',
        validators=[
            DataRequired('请输入确认密码！'),
            EqualTo('pwd', message='两次输入密码不一致!')
        ],
        description='确认密码',
        render_kw={
            'class': 'form-control input-lg',
            'placeholder': '请输入确认密码',
        }
    )

    submit = SubmitField(
        '注册',
        render_kw={
            "class": "btn btn-lg btn-success btn-block",
        }
    )

    def validate_name(self, field):
        name = field.data
        user = Tuser.query.filter_by(Huser_name=name).count()
        if user == 1:
            raise ValidationError('昵称已经存在！')

    def validate_email(self, field):
        email = field.data
        user = Tuser.query.filter_by(Hemail=email).count()
        if user == 1:
            raise ValidationError('邮箱已经存在!')

    def validate_phone(self, field):
        phone = field.data
        user = Tuser.query.filter_by(Hmobile=phone).count()
        if user == 1:
            raise ValidationError('手机号码已经存在!')


class LoginForm(FlaskForm):
    name = StringField(
        label="账号",
        validators=[
            DataRequired("账号不能为空！")
        ],
        description="账号",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "请输入账号！",
        }
    )
    pwd = PasswordField(
        label="密码",
        validators=[
            DataRequired("密码不能为空！")
        ],
        description="密码",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "请输入密码！",
        }
    )
    submit = SubmitField(
        '登录',
        render_kw={
            "class": "btn btn-lg btn-primary btn-block",
        }
    )


class PwdForm(FlaskForm):
    old_pwd = PasswordField(
        label="旧密码",
        validators=[
            DataRequired("旧密码不能为空")
        ],
        description="旧密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入旧密码...",
        }
    )

    new_pwd = PasswordField(
        label="新密码",
        validators=[
            DataRequired("新密码不能为空")
        ],
        description="新密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入新密码...",
        }
    )

    submit = SubmitField(
        '修改密码',
        render_kw={
            "class": "btn btn-success",
        }
    )

class UserInfoForm(FlaskForm):
    name = StringField(
        label="用户名",
        validators=[
            DataRequired("用户名不能为空")
        ],
        description='用户名',
        render_kw={
            'class': 'form-control input-lg',
            'placeholder': '请输入用户名',
        }
    )

    email = StringField(
        label="邮箱",
        validators=[
            DataRequired("邮箱不能为空"),
            Email('邮箱格式不正确...')
        ],
        description='邮箱',
        render_kw={
            'class': 'form-control input-lg',
            'placeholder': '请输入邮箱',
        }
    )

    phone = StringField(
        label="手机",
        validators=[
            DataRequired("手机号码不能为空"),
            Regexp('1[34578]\\d{9}', message='手机格式不正确!'),
            Length(min=11, max=11, message='手机号码长度有误!')
        ],
        description='手机',
        render_kw={
            'class': 'form-control input-lg',
            'placeholder': '请输入手机',
        }
    )

    area = StringField(
        label="地区",
        validators=[
            DataRequired("地区不能为空")
        ],
        description='地区',
        render_kw={
            'id': 'addr-send',
            'type': 'hidden',
        }
    )

    show_area = StringField(
        label="地区",
        validators=[
            DataRequired("地区不能为空")
        ],
        description='地区',
        render_kw={
            'id': 'addr-show',
            'placeholder': '请选择收获地区'
        }
    )

    submit = SubmitField(
        '提交',
        render_kw={
            "class": "btn btn-success",
        }
    )