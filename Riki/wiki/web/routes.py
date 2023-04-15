"""
    Routes
    ~~~~~~
"""
import os
import config
from io import BytesIO
from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask import send_file
from flask_login import current_user
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user


from wiki.core import Processor
from wiki.core import Wiki
from wiki.web.forms import EditorForm
from wiki.web.forms import LoginForm
from wiki.web.forms import SignupForm
from wiki.web.forms import SearchForm
from wiki.web.forms import URLForm
from wiki.web import current_wiki
from wiki.web import current_users
from wiki.web.user import protect
from wiki.web.userDAO import UserDaoManager
from wiki.web.userDAO import UserDao
from wiki.web.pageDAO import PageDaoManager
import sqlite3
from PIL import Image

bp = Blueprint('wiki', __name__)

@bp.route('/')
@protect
def home():
    page = current_wiki.get('home')
    if page:
        return display('home')
    return render_template('home.html')


@bp.route('/index/')
@protect
def index():
    pages = current_wiki.index()
    return render_template('index.html', pages=pages)


@bp.route('/<path:url>/')
@protect
def display(url):
    page = current_wiki.get_or_404(url)
    return render_template('page.html', page=page)


@bp.route('/create/', methods=['GET', 'POST'])
@protect
def create():
    form = URLForm()
    if form.validate_on_submit():
        return redirect(url_for(
            'wiki.edit', url=form.clean_url(form.url.data)))
    
    
    return render_template('create.html', form=form)

@bp.route('/edit/<path:url>/', methods=['GET', 'POST'])
@protect
def edit(url):
    page = current_wiki.get(url)
    form = EditorForm(obj=page)


    if form.validate_on_submit():
        if not page:
            page = current_wiki.get_bare(url)


        form.populate_obj(page)
        page.save()

        # Connect to the database
        pageDaoManager = PageDaoManager()

        # Update the page index
        pageDaoManager.update_page_index(page)


        flash('"%s" was saved.' % page.title, 'success')
        return redirect(url_for('wiki.display', url=url))
    return render_template('editor.html', form=form, page=page)


@bp.route('/preview/', methods=['POST'])
@protect
def preview():
    data = {}
    processor = Processor(request.form['body'])
    data['html'], data['body'], data['meta'] = processor.process()
    return data['html']


# This route handles moving a page to a new URL
# This route handles moving a page to a new URL
@bp.route('/move/<path:url>/', methods=['GET', 'POST'])
@protect
def move(url):
    # Get the page object based on the URL provided
    # Get the page object based on the URL provided
    page = current_wiki.get_or_404(url)

    # Get the id of the old page
    old_page_id = current_wiki.get(url).id

    # Create a URLForm object with the page data

    # Get the id of the old page
    old_page_id = current_wiki.get(url).id

    # Create a URLForm object with the page data
    form = URLForm(obj=page)


    if form.validate_on_submit():
        # Get the new URL from the form data
        # Get the new URL from the form data
        newurl = form.url.data

        # Move the page to the new URL

        # Move the page to the new URL
        current_wiki.move(url, newurl)

        # Get the id of the new page
        new_page_id = current_wiki.get(newurl).id

        # Connect to the database
        pageDaoManager = PageDaoManager()

        # Update the page_index tokens to point to the new page id
        pageDaoManager.update_page_index_id(new_page_id, old_page_id)
        pageDaoManager.close_db()

        # Redirect the user to the new URL
        return redirect(url_for('wiki.display', url=newurl))

    # Render the move.html template with the form and page objects

    # Render the move.html template with the form and page objects
    return render_template('move.html', form=form, page=page)


@bp.route('/delete/<path:url>/')
@protect
def delete(url):
    page = current_wiki.get_or_404(url)
    current_wiki.delete(url)
    
    pageDaoManager = PageDaoManager()
    pageDaoManager.delete(page)
    pageDaoManager.close_db()

    flash('Page "%s" was deleted.' % page.title, 'success')

    return redirect(url_for('wiki.home'))


@bp.route('/tags/')
@protect
def tags():
    tags = current_wiki.get_tags()
    return render_template('tags.html', tags=tags)


@bp.route('/tag/<string:name>/')
@protect
def tag(name):
    tagged = current_wiki.index_by_tag(name)
    return render_template('tag.html', pages=tagged, tag=name)


@bp.route('/search/', methods=['GET', 'POST'])
@protect
def search():
    form = SearchForm()
    if form.validate_on_submit():
        results = current_wiki.search(form.term.data, form.ignore_case.data)
        return render_template('search.html', form=form,
                               results=results, search=form.term.data)
    return render_template('search.html', form=form, search=None)


@bp.route('/user/login/', methods=['GET', 'POST'])
def user_login():
    form = LoginForm()
    if form.validate_on_submit():
        user = current_users.get_user(form.name.data)
        login_user(user)
        user.set('authenticated', True)
        flash('Login successful.', 'success')
        return redirect(request.args.get("next") or url_for('wiki.index'))
    return render_template('login.html', form=form)


@bp.route('/user/logout/')
@login_required
def user_logout():
    current_user.set('authenticated', False)
    logout_user()
    flash('Logout successful.', 'success')
    return redirect(url_for('wiki.index'))


@bp.route('/user/')
def user_index():
    pass

#TODO create a class to manage user (DAO data access object)

@bp.route('/user/create/', methods=['GET', 'POST'])
def user_create():

    form = SignupForm()
   

    if request.method == 'POST' and form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data
        confirm_password = form.confirm_password.data
        userDaoManager = UserDaoManager('/var/db/riki.db')
        user = UserDao(name, email, password)
        userDaoManager.create_user(user)
        users = userDaoManager.get_users()

        for user in users:
            flash(f'{user[0]} {user[1]} {user[2]} {user[3]}')
        # user = current_users.get_user(form.name.data)
        # login_user(user)
        # user.set('authenticated', True)
        flash('Sign up successful.', 'success')

        userDaoManager.close_db()

        return redirect(request.args.get("next") or url_for('wiki.index'))
    return render_template('signup.html', form=form)



@bp.route('/user/<string:user_id>/')
@login_required
def user_admin(user_id):
    if(current_user.get_id() == user_id):
        return render_template('admin.html')


@bp.route('/user/delete/<string:user_id>/')
def user_delete(user_id):
    pass

# Image uploading

@bp.route('/user/<string:user_id>/upload/', methods=['POST'])
@login_required
def upload_image(user_id):
    if 'an_image' not in request.files:
        flash('There is no image!')
    image = request.files['an_image']
    if image.filename != '':
        if image and current_wiki.allowed_file(image.filename):
            current_wiki.save_image(image)
            flash('Image Saved!')
            return redirect(request.referrer)
        else: 
            flash('Unacceptable file type!')
    flash('Image Not Saved!')
    return redirect(request.referrer)
    
    
@bp.route('/user/<string:user_id>/images/')
@login_required
def user_images(user_id):
    flash('This feature is not available yet!')
    return redirect(request.referrer)
    
@bp.route('/img/')
def index_images():
    flash('This feature is not available yet!')
    return redirect(request.referrer)

@bp.route('/img/<string:filename>/', methods=['GET'])
def view_image(filename):
    type = filename.rsplit('.', 1)[1].upper()
    if type=='JPG':
        type='JPEG'
    img = Image.open(os.path.join(config.PIC_BASE, filename))
    img_io = BytesIO()
    img.save(img_io, type, quality=70)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/'+type.lower())
    
"""
    Error Handlers
    ~~~~~~~~~~~~~~
"""


@bp.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

