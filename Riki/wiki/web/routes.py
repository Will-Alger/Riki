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
from wiki.web.forms import EditUserForm
from wiki.web import current_wiki
from wiki.web import current_users
from wiki.web.userDAO import protect
from wiki.web.userDAO import UserDaoManager
from wiki.web.userDAO import UserDao
from wiki.web.imageDAO import ImageDAO
from wiki.web.pageDAO import PageDaoManager
import sqlite3
from PIL import Image
from datetime import datetime


bp = Blueprint("wiki", __name__)


@bp.route("/")
@protect
def home():
    page = current_wiki.get("home")
    if page:
        return display("home")
    return render_template("home.html")


@bp.route("/index/")
@protect
def index():
    pages = current_wiki.index()
    return render_template("index.html", pages=pages)


@bp.route("/<path:url>/")
@protect
def display(url):
    page = current_wiki.get_or_404(url)
    return render_template("page.html", page=page)


@bp.route("/create/", methods=["GET", "POST"])
@protect
def create():
    form = URLForm()
    if form.validate_on_submit():
        return redirect(url_for("wiki.edit", url=form.clean_url(form.url.data)))

    return render_template("create.html", form=form)


@bp.route("/edit/<path:url>/", methods=["GET", "POST"])
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

        current_users.record_history(current_user.email, url, datetime.now())

        # Update the page index
        pageDaoManager.update_page_index(page)

        flash('"%s" was saved.' % page.title, "success")
        return redirect(url_for("wiki.display", url=url))
    return render_template("editor.html", form=form, page=page)


@bp.route("/preview/", methods=["POST"])
@protect
def preview():
    data = {}
    processor = Processor(request.form["body"])
    data["html"], data["body"], data["meta"] = processor.process()
    return data["html"]


# This route handles moving a page to a new URL
# This route handles moving a page to a new URL
@bp.route("/move/<path:url>/", methods=["GET", "POST"])
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

        # Redirect the user to the new URL
        return redirect(url_for("wiki.display", url=newurl))

    # Render the move.html template with the form and page objects

    # Render the move.html template with the form and page objects
    return render_template("move.html", form=form, page=page)


@bp.route("/delete/<path:url>/")
@protect
def delete(url):
    page = current_wiki.get_or_404(url)
    current_wiki.delete(url)

    pageDaoManager = PageDaoManager()
    pageDaoManager.delete(page)

    flash('Page "%s" was deleted.' % page.title, "success")

    return redirect(url_for("wiki.home"))


@bp.route("/tags/")
@protect
def tags():
    tags = current_wiki.get_tags()
    return render_template("tags.html", tags=tags)


@bp.route("/tag/<string:name>/")
@protect
def tag(name):
    tagged = current_wiki.index_by_tag(name)
    return render_template("tag.html", pages=tagged, tag=name)


@bp.route("/search/", methods=["GET", "POST"])
@protect
def search():
    form = SearchForm()
    if form.validate_on_submit():
        # Old search method
        # results = current_wiki.search(form.term.data, form.ignore_case.data)

        # Uses newly created search engine
        results = current_wiki.search(form.term.data, form.ignore_case.data)

        return render_template(
            "search.html", form=form, results=results, search=form.term.data
        )
    return render_template("search.html", form=form, search=None)


@bp.route("/user/login/", methods=["GET", "POST"])
def user_login():
    form = LoginForm()
    if form.validate_on_submit():
        user = current_users.get_user(form.email.data)
        login_user(user)
        user.set_authenticated(True)
        
        flash('Login successful.', 'success')
        return redirect(request.args.get("next") or url_for('wiki.index'))
    return render_template('login.html', form=form)


@bp.route("/user/logout/")
@login_required
def user_logout():
    current_user.set_authenticated(False)
    logout_user()
    flash("Logout successful.", "success")
    return redirect(url_for("wiki.index"))


@bp.route("/user/")
def user_index():
    pass


# TODO create a class to manage user (DAO data access object)


@bp.route("/user/create/", methods=["GET", "POST"])
def user_create():
    form = SignupForm()

    if request.method == 'POST' and form.validate_on_submit():
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data
        password = form.password.data
        signup_time = form.signup_time

        user = UserDao(first_name, last_name, email, password, signup_time)
        current_users.create_user(user)
        users = current_users.get_users()

        for item in users:
            flash(f'{item[0]} {item[1]} {item[2]} {item[3]}')

        login_user(user)
        user.set_authenticated(True)
        flash(f'Sign up successful. You signed up at {user.signup_time}.', 'success')

        current_users.close_db()

        return redirect(request.args.get("next") or url_for("wiki.index"))
    return render_template("signup.html", form=form)


@bp.route("/user/<string:user_id>/")
@login_required
def user_admin(user_id):
    if current_user.get_id() == user_id:
        return render_template("admin.html")


@bp.route("/user/delete/")
def user_delete():
    current_users.delete_user(current_user.email)
    current_user.set_authenticated(False)
    logout_user()
    flash('Your account has been deleted.', 'success')
    return redirect(url_for('wiki.index'))


@bp.route('/user/profile/', methods=['GET'])
@login_required
def user_profile():
    edits = current_users.get_edit_history(current_user.email)
    return render_template('profile.html', user=current_user, edits=edits)


@bp.route('/user/edit/', methods=['GET', 'POST'])
@login_required
def user_edit():

    form = EditUserForm()

    if request.method == 'POST' and form.validate_on_submit():
        updated_first_name = form.updated_first_name.data
        updated_last_name = form.updated_last_name.data
        # email = form.email.data
        # password = form.password.data

        current_users.update_user(current_user.email, updated_first_name, updated_last_name)

        flash(f'Edit successful.', 'success')

        current_users.close_db()

        return redirect(request.args.get("next") or url_for("wiki.user_profile"))
    return render_template("edit.html", form=form, user=current_user)

# Image uploading
def allowed_file(filename): 
        dao = ImageDAO()
        ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
        if dao.filename_exists(filename):
            dao.close_db()
            return False
        if not ('.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS):
            dao.close_db()
            return False
        return True

@bp.route('/user/upload/', methods=['POST'])
@login_required
def upload_image():
    if 'an_image' not in request.files:
        flash('There is no image!')
        return redirect(request.referrer)
    image = request.files['an_image']
    if image.filename != '':
        if allowed_file(image.filename):
            path = os.path.join(config.PIC_BASE, image.filename)
            image.save(path)
            imageDAO = ImageDAO()
            imageDAO.save_image(image.filename, email=current_user.email)
            imageDAO.close_db()
            flash('Image Saved!')
            return redirect(request.referrer)
        else:
            flash('File name not allowed! Either unsupported type (jpg, jpeg, png are supported file types) or reused file name.')
            return redirect(request.referrer)
    
    
@bp.route('/user/images/')
@login_required
def user_images():
    dao = ImageDAO()
    images = dao.get_user_images(current_user.email)
    dao.close_db()
    return render_template('user_images.html', images = images)
    
@bp.route('/img/')
def index_images():
    images = os.listdir(config.PIC_BASE)
    dao = ImageDAO()
    final = []
    for filename in images:
        arr = []
        arr.append(filename)
        arr.append(dao.get_image_owner(filename))
        final.append(arr)
    return render_template('index_images.html', images=final)


@bp.route("/img/<string:filename>/", methods=["GET"])
def view_image(filename):
    type = filename.rsplit(".", 1)[1].upper()
    if type == "JPG":
        type = "JPEG"
    img = Image.open(os.path.join(config.PIC_BASE, filename))
    img_io = BytesIO()
    img.save(img_io, type, quality=70)
    img_io.seek(0)
    return send_file(img_io, mimetype="image/" + type.lower())


"""
    Error Handlers
    ~~~~~~~~~~~~~~
"""


@bp.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404
