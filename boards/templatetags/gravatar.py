import hashlib
from urllib.parse import urlencode

from django import template
from django.conf import settings

register = template.Library()


@register.filter
def gravatar(user, size=256):
    """
    生成Gravatar头像URL
    Args:
        user: User对象
        size: 头像尺寸，默认256px
    Returns:
        Gravatar头像URL字符串
    """
    # 检查用户和邮箱
    if not user or not hasattr(user, 'email') or not user.email:
        return get_default_gravatar(size)

    try:
        # 处理邮箱
        email = user.email.lower().strip()
        email_hash = hashlib.md5(email.encode('utf-8')).hexdigest()

        # 构建URL参数
        params = {
            'd': 'identicon',  # 默认头像类型：根据邮箱生成图案
            's': str(size),
            'r': 'pg'  # 评级：适合所有年龄段
        }

        return f'https://www.gravatar.com/avatar/{email_hash}?{urlencode(params)}'

    except Exception as e:
        return get_default_gravatar(size)


def get_default_gravatar(size=256):
    """获取默认Gravatar头像"""
    params = {'d': 'identicon', 's': str(size)}
    return f'https://www.gravatar.com/avatar/00000000000000000000000000000000?{urlencode(params)}'