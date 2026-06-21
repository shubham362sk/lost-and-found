from extensions import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    college_id = db.Column(db.String(50), unique=True)
    phone = db.Column(db.String(15))
    email = db.Column(db.String(120), unique=True)
    branch = db.Column(db.String(50))
    course = db.Column(db.String(50))
    semester = db.Column(db.String(10))
    password = db.Column(db.String(100))
    
    items = db.relationship('Item', backref='user', lazy=True)
    claims = db.relationship('Claim', backref='claimer', lazy=True)


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    item_type = db.Column(db.String(10))
    attachment = db.Column(db.String(255))
    contact_email = db.Column(db.String(120))
    contact_number = db.Column(db.String(15))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    claims = db.relationship('Claim', backref='item', lazy=True, cascade="all, delete-orphan")


class Claim(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    claimer_name = db.Column(db.String(100))
    claimer_info = db.Column(db.String(100))
    reason = db.Column(db.Text)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    claimer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
