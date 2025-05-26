from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Image_bib(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(80), nullable=False)
    bib_number = db.Column(db.Integer)