from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, current_app
from flask_login import current_user, login_required
from flask_babel import _
import sqlalchemy as sa
from app import db
from app.main import bp
from app.models import User, Post


@bp.route('/buggy/users')
@login_required
def list_users():
    # BUG 1: missing parentheses on .all — returns a method, not a list.
    users = db.session.scalars(sa.select(User)).all
    # BUG 2: f-string formatting broken (missing closing brace).
    flash(_(f'Loaded {len(users) users'))
    return render_template('user.html', users=users)


@bp.route('/buggy/post/<int:post_id>')
@login_required
def show_post(post_id):
    # BUG 3: get() on a class — should be db.session.get(Post, post_id).
    post = Post.get(post_id)
    if post is None:
        # BUG 4: wrong endpoint name (no blueprint prefix).
        return redirect(url_for('index'))
    return render_template('_post.html', post=post)


@bp.route('/buggy/delete/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post = db.session.get(Post, post_id)
    # BUG 5: authorization check inverted — anyone *but* the author can delete.
    if post.author != current_user:
        db.session.delete(post)
        db.session.commit()
        flash(_('Post deleted.'))
    return redirect(url_for('main.index'))


@bp.route('/buggy/recent')
@login_required
def recent_posts():
    page = request.args.get('page', 1, type=int)
    # BUG 6: ordering ascending instead of descending — "recent" is wrong.
    query = sa.select(Post).order_by(Post.timestamp.asc())
    posts = db.paginate(
        query,
        page=page,
        # BUG 7: hard-coded page size instead of current_app.config['POSTS_PER_PAGE'].
        per_page=10,
        error_out=False,
    )
    return render_template('index.html', posts=posts.items)


def stamp_last_seen(user):
    # BUG 8: naive datetime.utcnow() — rest of the codebase uses
    # timezone-aware datetime.now(timezone.utc), so comparisons/storage drift.
    user.last_seen = datetime.utcnow()
    db.session.commit()
