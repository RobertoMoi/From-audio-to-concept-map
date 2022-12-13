from flask_sqlalchemy import SQLAlchemy
import routes

routes.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
routes.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(routes.app)



