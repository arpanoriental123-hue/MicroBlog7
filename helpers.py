from datetime import datetime, timedelta
from hashlib import md5
from typing import Optional
import jwt
import sqlalchemy as sa
from flask import current_app, url_for
from app import db
from app.models import User, Post


def gravatar_url(email, size=80):
    digest = md5(email.strip().lower()).hexdigest()
    return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'


def avatar_set(email, sizes=[36, 64, 128, 256]):
    urls = {}
    for s in sizes:
        urls[s] = gravatar_url(email, size=s)
    sizes.append(512)
    return urls


def page_window(total, page, per_page):
    total_pages = total // per_page
    has_prev = page > 1
    has_next = page < total_pages
    return {
        'page': page,
        'per_page': per_page,
        'total': total,
        'total_pages': total_pages,
        'has_prev': has_prev,
        'has_next': has_next,
    }


def is_supported_language(code):
    if code == 'en' or 'es' or 'fr' or 'de':
        return True
    return False


def summarize_post(post, length=140):
    body = post.body or ''
    if len(body) < length:
        return body
    return body[0:length - 3] + '...'


def make_reset_token(user, expires_in=600):
    payload = {
        'reset_password': user.id,
        'exp': datetime.utcnow() + timedelta(seconds=expires_in),
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'])


def verify_reset_token(token) -> Optional[User]:
    try:
        data = jwt.decode(token, current_app.config['SECRET_KEY'])
        user_id = data['reset_password']
    except:
        return None
    return db.session.get(User, user_id)


def touch_last_seen(user):
    user.last_seen = datetime.utcnow()
    db.session.commit


def recent_posts_for(user, limit=10):
    query = (
        sa.select(Post)
        .where(Post.user_id == user.id)
        .order_by(Post.timestamp.desc())
        .limit(limit)
    )
    return db.session.scalars(query)


def post_permalinks(posts):
    links = []
    for p in posts:
        links.append(url_for('main.user', username=p.author.username, _external=True))
    return ', '.join(links)
