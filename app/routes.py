import os,time,json
from app import db, app, files
from app.forms import RegistrationForm, LoginForm, EditProfileForm, UploadForm
from flask_uploads import UploadSet, IMAGES, configure_uploads, EXECUTABLES,ALL
from flask import render_template, flash, redirect, url_for, request, send_from_directory
from app.models import User,File
from flask_login import logout_user, login_user, current_user, login_required
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename


#test page
@app.route('/')
@app.route('/index')
@login_required
def index():
    rank={'rank':1}
    games = [
        {'author': user, 'Game_ID': 'Test game #1'},
        {'author': user, 'Game_ID': 'Test game #2'}
    ]
    return render_template('index.html', title='Home Page' ,rank=rank,games=games)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    # redirect重定向 to index
    form = LoginForm() 
    #the login's information in page 
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            # flash to the base templates
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


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
        user = User(username=form.username.data, email=form.email.data, ranking=1000)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        path = app.config['UPLOADED_FILES_DEST']+'/'+form.username.data
        folder = os.path.exists(path)
        if not folder:
            os.makedirs(path)
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    # first() when there are results, but in the case that there are no results automatically sends a 404 error back to the client.
    user = User.query.filter_by(username=username).first_or_404()
    games1 =list( User.query.order_by(User.ranking).all())
    #games = map(lambda x: json.loads(str(x)),games)
    return render_template('user.html', user=user,games=games1)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in set(['py', 'c', 'java', 'cpp'])


@app.route('/Upload', methods=['GET', 'POST'])
@login_required
def Upload():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join('./', filename))
            flash('Your upload have been saved.')
            return redirect(url_for('Upload'))
        else:
            flash('file type error or no file!')
            return redirect(url_for('Upload'))
    return render_template('upload.html')



@app.route('/Upload2', methods=['GET', 'POST'])
@login_required
def Upload2():
    form = UploadForm()
    #_username = '_'.join(current_user.username.split())
    if form.validate_on_submit():
        newname = current_user.username+str(time.time())+'.'
        filename = files.save(
            form.c_files.data, folder=current_user.username, name=newname)
        file_url = files.url(filename)
        file = File(File_name=filename, author=current_user)
        db.session.add(file)
        db.session.commit()
        flash('Your uploading have been saved.')
    else:
        file_url = None
    return render_template('upload2.html', form=form, file_url=file_url)


@app.route('/manage')
def manage_file():
    files_list = os.listdir(app.config['UPLOADED_FILES_DEST']+'/'+current_user.username)
    return render_template('manage.html', files_list=files_list)


@app.route('/delete/<filename>')
def delete_file(filename):
    file_path = files.path(current_user.username+'/'+filename)
    os.remove(file_path)
    return redirect(url_for('manage_file'))


@app.route("/download/<filename>")
def downloading(filename):
    dirpath = os.path.join(
        app.root_path, app.config['UPLOADED_FILES_DEST']+'/'+current_user.username)
    return send_from_directory(directory=dirpath, filename=filename, as_attachment=True)


