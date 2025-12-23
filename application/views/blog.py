# application/views/blog.py

from flask import Blueprint, redirect, render_template, request, url_for, flash
from flask_login import login_required, current_user
from application.database import db
from application.models.db_tables import Post, Category, Tag, Comment, Like

blog_bp = Blueprint("blog", __name__)


#Home / Index – Published Posts
@blog_bp.route("/")
def index():
    posts = (
        db.session.query(Post)
        .filter(Post.is_published.is_(True))
        .order_by(Post.created_at.desc())
        .all()
    )
    return render_template("index.html", posts=posts)

# Create Post

@blog_bp.route("/post/create", methods=["GET", "POST"])
@login_required
def create_post():

    categories = db.session.query(Category).all()

    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")
        category_id = request.form.get("category_id")
        tags = request.form.get("tags")  # comma separated

        if not title or not content:
            flash("Title and content are required", "danger")
            return redirect(url_for("blog.create_post"))

        post = Post(
            title=title,
            content=content,
            author_id=current_user.id,
            category_id=category_id,
            is_published=True
        )

        # tags handling
        if tags:
            for tag_name in tags.split(","):
                tag_name = tag_name.strip().lower()
                tag = db.session.query(Tag).filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                post.tags.append(tag)

        db.session.add(post)
        db.session.commit()

        flash("Post created successfully", "success")
        return redirect(url_for("blog.index"))

    return render_template("create_post.html", categories=categories)

# Post Detail + Comments

@blog_bp.route("/post/<int:post_id>", methods=["GET", "POST"])
def post_detail(post_id):
    post = db.session.query(Post).get_or_404(post_id)

    # Add comment
    if request.method == "POST":
        if not current_user.is_authenticated:
            flash("Login required to comment", "warning")
            return redirect(url_for("auth.login"))

        content = request.form.get("content")
        if content:
            comment = Comment(
                content=content,
                post_id=post.id,
                user_id=current_user.id
            )
            db.session.add(comment)
            db.session.commit()
            flash("Comment added", "success")

        return redirect(url_for("blog.post_detail", post_id=post.id))

    return render_template("post_detail.html", post=post)

# Edit Post (Author Only)

@blog_bp.route("/post/<int:post_id>/edit", methods=["GET", "POST"])
@login_required
def edit_post(post_id):
    post = db.session.query(Post).get_or_404(post_id)

    if post.author_id != current_user.id and not current_user.is_admin:
        flash("Unauthorized access", "danger")
        return redirect(url_for("blog.index"))

    categories = db.session.query(Category).all()

    if request.method == "POST":
        post.title = request.form.get("title")
        post.content = request.form.get("content")
        post.category_id = request.form.get("category_id")

        db.session.commit()
        flash("Post updated", "success")
        return redirect(url_for("blog.post_detail", post_id=post.id))

    return render_template("edit_post.html", post=post, categories=categories)

# Delete Post

@blog_bp.route("/post/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id):
    post = db.session.query(Post).get_or_404(post_id)

    if post.author_id != current_user.id and not current_user.is_admin:
        flash("Unauthorized action", "danger")
        return redirect(url_for("blog.index"))

    db.session.delete(post)
    db.session.commit()
    flash("Post deleted", "success")

    return redirect(url_for("blog.index"))

# Like / Unlike Post
@blog_bp.route("/post/<int:post_id>/like", methods=["POST"])
@login_required
def like_post(post_id):
    post = db.session.query(Post).get_or_404(post_id)

    like = db.session.query(Like).filter_by(
        user_id=current_user.id,
        post_id=post.id
    ).first()

    if like:
        db.session.delete(like)
    else:
        db.session.add(Like(user_id=current_user.id, post_id=post.id))

    db.session.commit()
    return redirect(url_for("blog.post_detail", post_id=post.id))

