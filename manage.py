from application import create_app
from application.database import db, migrate

app = create_app()
migrate.init_app(app, db)  # only here for migration commands

if __name__ == "__main__":
    app.run(debug=True)
