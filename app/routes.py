from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required
from app import app, db
from app.forms import LoginForm, RegistrationForm, PostForm
from flask_login import current_user, login_user, logout_user
from app.models import User,Post
from werkzeug.urls import url_parse
from datetime import datetime
import os


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
	form = PostForm()
	if form.validate_on_submit():
		post = Post(body=form.post.data,author=current_user)
		db.session.add(post)
		db.session.commit()
		return redirect(url_for('index'))
	posts = Post.query.order_by(Post.timestamp.desc()).all()
	return render_template('index.html',title="Country Roads",posts=posts,form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = LoginForm()
	print(os.getcwd() + "\n")
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user is None or not user.check_password(form.password.data):
			flash('Invalid username or password')
			return redirect(url_for('login'))
		login_user(user, remember=form.remember_me.data)
		next_page = request.args.get('next')
		if not next_page or url_parse(next_page).netloc != '':
			next_page = url_for('index')
		return redirect(next_page)
	return render_template('login.html',title="Take Me Home",form=form)

@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = RegistrationForm()
	if form.validate_on_submit():
		user = User(username=form.username.data, email=form.email.data)
		user.set_password(form.password.data)
		db.session.add(user)
		db.session.commit()
		flash('Congratulations, you are now a registered user!')
		return redirect(url_for('login'))
	return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>',methods=['GET', 'POST'])
@login_required
def user(username):
	user = User.query.filter_by(username=username).first_or_404()
	return render_template('user.html', user=user)

@app.route('/browse/<path:req_path>')
@login_required
def browse(req_path):	
	BASE_DIR=os.getcwd()
	print(os.getcwd())
	abs_path = os.path.join(BASE_DIR, req_path)
	
	files = os.listdir(abs_path)
	print(req_path[:5])
	files = ['files/{}'.format(file) for file in files]

	print(files)
	return render_template('browse.html', files=files)