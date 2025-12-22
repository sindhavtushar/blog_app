from flask import Blueprint, render_template, request
from werkzeug.security import generate_password_hash, check_password_hash

from application.models.db_service import create_user

blog_bp = Blueprint("blog", __name__)

@blog_bp.route('/')
def index():
    return render_template("index.html", posts = ['First Post', 'Second Post'])

@blog_bp.route('/user_register', methods = ['GET', 'POST'])
def register_user():
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        password_hash = generate_password_hash(password=password)
        # Insert user in databse
        create_user(username, email, password_hash, is_admin=False)
        print(username, password, email)
        return render_template('register.html')
    # create_user(username, email, password_hash, is_admin=False)
    
    return render_template('register.html')

@blog_bp.route('/user_profile')
def user_profile():
    return render_template("user_profile.html")
