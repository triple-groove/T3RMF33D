# T3RMF33D
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import re
import secrets  # For generating invitation tokens

# ---------------------------------------
# Configuration
# ---------------------------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret-key'  # Change this for production!
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'posts.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Folder to store uploaded media
UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)

# ---------------------------------------
# Flask-Login Setup
# ---------------------------------------
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# ---------------------------------------
# Database Models
# ---------------------------------------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    media_filename = db.Column(db.String(120), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    author = db.relationship('User', backref=db.backref('posts', lazy=True))

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    post = db.relationship('Post', backref=db.backref('comments', lazy=True))
    author = db.relationship('User', backref=db.backref('comments', lazy=True))

class InvitationToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(64), unique=True, nullable=False)
    is_used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ---------------------------------------
# Custom Filter to Embed YouTube Links
# Ensures videos appear on a new line
# ---------------------------------------
def embed_youtube_links(content):
    pattern = re.compile(
        r'(https?://(?:www\.)?youtube\.com/watch\?v=([\w-]+))'
        r'|(https?://youtu\.be/([\w-]+))'
    )
    def repl(m):
        video_id = m.group(2) if m.group(2) else m.group(4)
        return f'<br><iframe width="100%" height="315" src="https://www.youtube-nocookie.com/embed/{video_id}?rel=0" frameborder="0" allowfullscreen></iframe><br>'
    return pattern.sub(repl, content)

app.jinja_env.filters['embed_youtube'] = embed_youtube_links

# ---------------------------------------
# Routes
# ---------------------------------------
@app.route('/')
@login_required
def index():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('index.html', posts=posts, site_name="T3RMF33D")

@app.route('/new', methods=['GET', 'POST'])
@login_required
def new_post():
    if request.method == 'POST':
        content = request.form.get('content', '').strip()
        file = request.files.get('media')

        if not content:
            flash("Post content cannot be empty.", "error")
            return redirect(url_for('new_post'))

        media_filename = None
        if file and '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'webm'}:
            media_filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], media_filename)
            file.save(filepath)

        post = Post(author_id=current_user.id, content=content, media_filename=media_filename)
        db.session.add(post)
        db.session.commit()

        flash('Post created successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('new_post.html')

@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/reply/<int:post_id>', methods=['GET', 'POST'])
@login_required
def reply(post_id):
    post = Post.query.get_or_404(post_id)
    if request.method == 'POST':
        content = request.form.get('content', '').strip()
        if not content:
            flash("Reply cannot be empty.", "error")
            return redirect(url_for('reply', post_id=post.id))
        
        comment = Comment(post_id=post.id, author_id=current_user.id, content=content)
        db.session.add(comment)
        db.session.commit()
        flash('Reply added successfully!', 'success')
        return redirect(url_for('index'))
    
    return render_template('reply.html', post=post)


@app.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    if post.author_id != current_user.id and not current_user.is_admin:
        flash("You don't have permission to edit this post.", "error")
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        content = request.form.get('content', '').strip()
        if not content:
            flash("Post content cannot be empty.", "error")
            return redirect(url_for('edit_post', post_id=post.id))

        post.content = content
        db.session.commit()
        flash('Post updated successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('edit_post.html', post=post)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'error')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/delete_post/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    # Ensure only the author or an admin can delete the post
    if post.author_id != current_user.id and not current_user.is_admin:
        flash("You don't have permission to delete this post.", "error")
        return redirect(url_for('index'))

    # Delete associated comments
    Comment.query.filter_by(post_id=post.id).delete()

    # Delete media file if exists
    if post.media_filename:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], post.media_filename)
        if os.path.exists(file_path):
            os.remove(file_path)

    # Delete post from the database
    db.session.delete(post)
    db.session.commit()

    flash('Post deleted successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password').strip()
        invite_token = request.form.get('invite_token').strip()

        if not username or not password:
            flash('Username and password are required.', 'error')
            return redirect(url_for('register'))

        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'error')
            return redirect(url_for('register'))

        # Check if this is the first user (they become admin automatically)
        if User.query.count() == 0:
            is_admin = True
        else:
            # Validate invitation token for non-admin users
            token_entry = InvitationToken.query.filter_by(token=invite_token, is_used=False).first()
            if not token_entry:
                flash('Invalid or expired invitation token.', 'error')
                return redirect(url_for('register'))

            is_admin = False
            token_entry.is_used = True  # Mark token as used

        # Create user
        user = User(username=username, is_admin=is_admin)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/delete_reply/<int:reply_id>', methods=['POST'])
@login_required
def delete_reply(reply_id):
    reply = Comment.query.get_or_404(reply_id)

    # Ensure only the author or an admin can delete the reply
    if reply.author_id != current_user.id and not current_user.is_admin:
        flash("You don't have permission to delete this reply.", "error")
        return redirect(url_for('index'))

    # Delete reply from database
    db.session.delete(reply)
    db.session.commit()

    flash('Reply deleted successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/user/<int:user_id>')
@login_required
def user_posts(user_id):
    user = User.query.get_or_404(user_id)
    posts = Post.query.filter_by(author_id=user.id).order_by(Post.created_at.desc()).all()
    
    return render_template('user_posts.html', user=user, posts=posts, site_name="T3RMF33D")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
