#from flask import Flask, render_template

#app = Flask(__name__)

#@app.route('/')
#def home():
#    return render_template('index.html')

# @app.route('/bmi_calculator')
# def bmi_calculator():
#     return render_template('bmi_calculator.html')

# @app.route('/calorie_calculator')
# def calorie_calculator():
#     return render_template('calorie_calculator.html')

# @app.route('/diet_plan')
# def diet_plan():
#     return render_template('diet_plan.html')  # New page for the Diet Plan

# @app.route('/recipes')
# def recipes():
#     return render_template('recipes.html')  # New route for Recipes page

# @app.route('/blog')
# def blog():
#     return render_template('blog.html')  # New route for Blog page

# @app.route('/contact')
# def contact():
#     return render_template('contact.html')  # New route for Contact page

# @app.route('/foodsug')
# def foodsug():
#     return render_template('foodsug.html')  # New route for Foodsug page

# if __name__ == '__main__':
#     app.run(debug=True) { remove # hash only }








from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    username = db.Column(db.String(150), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(200))
    likes = db.Column(db.Integer, default=0)
    dislikes = db.Column(db.Integer, default=0)

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    username = db.Column(db.String(150), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(200))
    likes = db.Column(db.Integer, default=0)
    dislikes = db.Column(db.Integer, default=0)

# Helpers
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/bmi_calculator')
def bmi_calculator():
    return render_template('bmi_calculator.html')

@app.route('/calorie_calculator')
def calorie_calculator():
    return render_template('calorie_calculator.html')

@app.route('/diet_plan')
def diet_plan():
    return render_template('diet_plan.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/foodsug')
def foodsug():
    return render_template('foodsug.html')

# Auth Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            return redirect(url_for('blog'))
        else:
            flash('Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for('register'))

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists.", "danger")
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful!", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

# Blog Routes
@app.route('/blog', methods=['GET', 'POST'])
def blog():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        image = request.files.get('image')

        filename = None
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        new_post = BlogPost(
            title=title,
            content=content,
            image=os.path.join(app.config['UPLOAD_FOLDER'], filename) if filename else None,
            user_id=session['user_id'],
            username=session['username']
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('blog'))

    posts = BlogPost.query.all()
    return render_template('blog.html', posts=posts)

@app.route('/delete_post/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    post = BlogPost.query.get_or_404(post_id)
    if session['username'] != 'pratham' and session['user_id'] != post.user_id:
        return "Unauthorized", 403

    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('blog'))

@app.route('/like_post/<int:post_id>', methods=['POST'])
def like_post(post_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    post = BlogPost.query.get_or_404(post_id)
    post.likes += 1
    db.session.commit()
    return redirect(url_for('blog'))

@app.route('/dislike_post/<int:post_id>', methods=['POST'])
def dislike_post(post_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    post = BlogPost.query.get_or_404(post_id)
    post.dislikes += 1
    db.session.commit()
    return redirect(url_for('blog'))

@app.route('/share_post/<int:post_id>', methods=['POST'])
def share_post(post_id):
    return redirect(url_for('blog'))

# Recipe Routes
@app.route('/recipes', methods=['GET', 'POST'])
def recipes():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        image = request.files.get('image')

        filename = None
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        new_recipe = Recipe(
            title=title,
            content=content,
            image=os.path.join(app.config['UPLOAD_FOLDER'], filename) if filename else None,
            user_id=session['user_id'],
            username=session['username']
        )
        db.session.add(new_recipe)
        db.session.commit()
        return redirect(url_for('recipes'))

    all_recipes = Recipe.query.all()
    return render_template('recipe.html', recipes=all_recipes)

@app.route('/delete_recipe/<int:recipe_id>', methods=['POST'])
def delete_recipe(recipe_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    recipe = Recipe.query.get_or_404(recipe_id)
    if session['username'] != 'pratham' and session['user_id'] != recipe.user_id:
        return "Unauthorized", 403

    db.session.delete(recipe)
    db.session.commit()
    return redirect(url_for('recipes'))

@app.route('/like_recipe/<int:recipe_id>', methods=['POST'])
def like_recipe(recipe_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    recipe = Recipe.query.get_or_404(recipe_id)
    recipe.likes += 1
    db.session.commit()
    return redirect(url_for('recipes'))

@app.route('/dislike_recipe/<int:recipe_id>', methods=['POST'])
def dislike_recipe(recipe_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    recipe = Recipe.query.get_or_404(recipe_id)
    recipe.dislikes += 1
    db.session.commit()
    return redirect(url_for('recipes'))

@app.route('/share_recipe/<int:recipe_id>', methods=['POST'])
def share_recipe(recipe_id):
    return redirect(url_for('recipes'))

# Setup: Create Tables and Admin User
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='pratham').first():
        admin_user = User(username='pratham', password=generate_password_hash('pratham@123'), is_admin=True)
        db.session.add(admin_user)
        db.session.commit()
        print("✅ Admin user created.")

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)



# ID and password 
# usre id prathamesh Pass : 1234
# admin id pratham Pass : pratham@123