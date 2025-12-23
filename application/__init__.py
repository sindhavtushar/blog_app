# from flask import Flask
# from application.config import Config
# from application.database import db, migrate
# from application.views.blog import blog_bp

# def create_app():
#     app = Flask(__name__)
#     app.config.from_object(Config)

#     # db.init_app(app)
#     migrate.init_app(app, db)

#     app.register_blueprint(blog_bp)

#     return app

# import os
# from flask import Flask
# from application.config import Config
# from application.database import db, migrate
# # from application.views.blog import blog_bp

# def create_app():
#     app = Flask(__name__)
#     app.config.from_object(Config)
#     print(app.config.get("SQLALCHEMY_DATABASE_URI"))


#     # 1️⃣ Bind SQLAlchemy
#     db.init_app(app)

#     # 2️⃣ Bind Migrate
#     migrate.init_app(app, db)

#     # 3️⃣ Register blueprints
#     # app.register_blueprint(blog_bp)

#     return app


# def create_app():
#     app = Flask(__name__)
#     app.config.from_object(Config)

#     db.init_app(app)
#     migrate.init_app(app, db)

#     from application.views.blog import blog_bp
#     app.register_blueprint(blog_bp)

#     return app


# from dotenv import load_dotenv
# import os

# load_dotenv()   # 👈 sabse pehle

# print("FROM RUN.PY:", os.getenv("DATABASE_URL"))

# def create_app():
#     app = Flask(__name__)
#     app.config.from_object(Config)

#     print("URI FROM CONFIG:", Config.SQLALCHEMY_DATABASE_URI)
#     print("URI FROM APP:", app.config.get("SQLALCHEMY_DATABASE_URI"))

#     db.init_app(app)
#     migrate.init_app(app, db)

#     from application.views.blog import blog_bp
#     app.register_blueprint(blog_bp)

#     return app


# def create_app():
#     app = Flask(__name__)

#     app.config.from_object(Config)

#     # 🔥 inject env AFTER load_dotenv
#     import os
#     app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")

#     print("URI FROM APP:", app.config.get("SQLALCHEMY_DATABASE_URI"))

#     db.init_app(app)
#     migrate.init_app(app, db)

#     from application.views.blog import blog_bp
#     app.register_blueprint(blog_bp)

#     return app

from dotenv import load_dotenv
load_dotenv()   # 🔥 ALWAYS load env when app module is imported

from flask import Flask
from application.config import Config
from application.database import db, migrate
import os

def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    print("URI FROM APP:", app.config.get("SQLALCHEMY_DATABASE_URI"))

    db.init_app(app)
    migrate.init_app(app, db)

    from application.views.blog import blog_bp
    app.register_blueprint(blog_bp)

    return app
