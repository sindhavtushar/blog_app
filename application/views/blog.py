# applicatio/views/blog.py

from flask import Blueprint, redirect, render_template, request, url_for
from werkzeug.security import generate_password_hash, check_password_hash

from application.models.db_service import create_user
from application.models.db_tables import Category, Post
from application.database import db

blog_bp = Blueprint("blog", __name__)

@blog_bp.route('/')
def index():
    return render_template("index.html")

@blog_bp.route('/user_register', methods = ['GET', 'POST'])
def register_user():
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        password_hash = generate_password_hash(password)

        # Insert user in databse
        create_user(username, email, password_hash, is_admin=False)
        print('(dev only):', username, email)

        return render_template('register.html')
    # create_user(username, email, password_hash, is_admin=False)
    
    return render_template('register.html')

@blog_bp.route('/user_profile')
def user_profile():
    return render_template("user_profile.html")

@blog_bp.route("/create_post", methods=["GET", "POST"])
def create_post():
    categories = Category.query.all()

    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        category_id = request.form["category_id"]
        is_published = True if request.form.get("is_published") else False

        # For now, author_id = 1 (first user)
        post = Post(
            title=title,
            content=content,
            category_id=category_id,
            author_id=1,  # later: current_user.id
            is_published=is_published
        )

        db.session.add(post)
        db.session.commit()

        return redirect(url_for("blog.index"))

    return render_template("create_post.html", categories=categories)