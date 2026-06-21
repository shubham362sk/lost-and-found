from flask import Flask, render_template, request, redirect, session, url_for, flash
from werkzeug.utils import secure_filename
import os

from extensions import db
from models import User, Item, Claim

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")

database_url = os.environ.get('DATABASE_URL', 'sqlite:///site.db')
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'

db.init_app(app)

with app.app_context():
    db.create_all()


@app.route('/')
def home():
    return render_template('login.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email, password=password).first()
        if user:
            session['user_id'] = user.id
            session['user_name'] = user.name
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        college_id = request.form['college_id']
        phone = request.form['phone']
        email = request.form['email']
        branch = request.form['branch']
        course = request.form['course']
        semester = request.form['semester']
        password = request.form['password']

        existing_user = User.query.filter(
            (User.email == email) | (User.college_id == college_id)
        ).first()

        if existing_user:
            if existing_user.email == email:
                flash("Email already registered. Please use another email.", "error")
            elif existing_user.college_id == college_id:
                flash("College ID already registered. Please check again.", "error")
            return redirect(url_for('register'))

        new_user = User(
            name=name,
            college_id=college_id,
            phone=phone,
            email=email,
            branch=branch,
            course=course,
            semester=semester,
            password=password
        )

        try:
            db.session.add(new_user)
            db.session.commit()
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash("Something went wrong. Please try again.", "error")
            return redirect(url_for('register'))

    return render_template('register.html')


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    items = Item.query.all()
    return render_template('dashboard.html', items=items, user_name=session.get('user_name'))


@app.route('/post', methods=['GET', 'POST'])
def post_item():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        file = request.files['attachment']
        filename = None
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        print("Selected type:", request.form.get('item_type'))

        item = Item(
            title=request.form['title'],
            description=request.form['description'],
            item_type=request.form['item_type'],
            attachment=filename,
            contact_email=request.form['contact_email'],
            contact_number=request.form['contact_number'],
            user_id=session['user_id']
        )
        db.session.add(item)
        db.session.commit()
        flash('Item posted successfully.')
        return redirect(url_for('dashboard'))
    return render_template('post_item.html')


@app.route('/claim/<int:item_id>', methods=['GET', 'POST'])
def claim_item(item_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    item = Item.query.get_or_404(item_id)
    if request.method == 'POST':
        claim = Claim(
            item_id=item_id,
            claimer_name=request.form.get('claimer_name'),
            claimer_info=request.form.get('contact_info'),
            reason=request.form.get('reason'),
            claimer_id=session['user_id']
        )
        db.session.add(claim)
        db.session.commit()
        flash('Claim submitted successfully.')
        return redirect(url_for('dashboard'))
    return render_template('claim_form.html', item=item)


@app.route('/delete/<int:item_id>')
def delete(item_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    item = Item.query.get_or_404(item_id)

    if item.user_id != session['user_id']:
        flash("You are not authorized to delete this post.")
        return redirect(url_for('dashboard'))

    db.session.delete(item)
    db.session.commit()
    flash("Post deleted successfully.")
    return redirect(url_for('dashboard'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
