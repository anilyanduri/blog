from . import posts
from blog import db
from blog.constants import rECAPTCHA_SITE_KEY_V2, rECAPTCHA_SECRET_V2, rECAPTCHA_SITE_KEY_V3
from flask import render_template, redirect, url_for, request
from forms import PostForm, PhotoForm, TagForm, ContactMeForm
from blog.models import Post, Tag, post_tags, photo_tags, Photograph, ContactRequest
from datetime import datetime
import json, requests


@posts.app_context_processor
def helpers_for_templates():
    def cur_act():
        return request.path.split("/")[1]

    def key_words():
        tags = Tag.query.all()
        tags_json = list()
        for tag in tags:
            tags_json.append(tag.auto_complete_dict())
        # print("size of tags_json is {}".format(tags_json))
        return json.dumps(tags_json)

    def tag_cloud(limit=20):
        return Tag.top_tags(limit=limit)

    def archives():
        return Post.archives()

    def top_categories():
        return Tag.top_categories()

    def photo_archives():
        return Photograph.archives()

    def top_photo_tags():
        return Tag.top_photo_tags(limit=5)

    return dict(current_action=cur_act(), all_tags_json=key_words(), tag_cloud=tag_cloud(),
                top_categories=top_categories(),
                archives=archives(),
                photo_archives=photo_archives(),
                top_photo_tags=top_photo_tags(),
                site_key_v2=rECAPTCHA_SITE_KEY_V2, site_key_v3=rECAPTCHA_SITE_KEY_V3)


@posts.route('/')
def homepage():
    """
    Render the homepage template on the / route
    """
    return render_template('home.html', title="Welcome")


@posts.route('/photography')
def photography():
    statues = ["PUBLISHED"]
    page_no = request.args.get('page', 1, type=int)
    _all = request.args.get('all', 0, type=int)
    photos = Photograph.query.filter(Photograph.status.in_(statues))

    category_id = request.args.get('category_id', None, type=int)
    if category_id is not None:
        photos = photos.join(Photograph.tags).filter(Tag.id == category_id)
        _all = 1

    category = request.args.get('category', None)
    if category is not None:
        photos = photos.join(Photograph.tags).filter(Tag.tag_name == category)
        _all = 1

    month = request.args.get('month', None)
    if month is not None:
        photos = photos.filter(db.func.MONTHNAME(Photograph.capture_date) == month)
        _all = 1

    year = request.args.get('year', None)
    if year is not None:
        photos = photos.filter(db.func.year(Photograph.capture_date) == year)
        _all = 1

    if _all == 1:
        photos = photos.order_by(Photograph.capture_date.desc()).all()
    else:
        photos = photos.order_by(Photograph.capture_date.desc()).paginate(page_no, 12, False).items

    return render_template('photography.html', title="Photography", photographs=photos,
                           category_id=category_id)


@posts.route('/travel')
def travel():
    return render_template('travel.html', title="Travel Blog")


@posts.route('/contact', methods=["POST", "GET"])
def contact():
    form = ContactMeForm()
    if request.method == "POST":
        if form.validate_on_submit():
            if verify_recaptcha(form.recaptcha_response.data):
                create_contact_request(form)
                form = None
    return render_template('contact.html', title="Contact Me", form=form)


@posts.route('/about')
def about():
    return render_template('about.html', title="About")


@posts.route('/blog')
@posts.route('/blog/')
def blog_list():
    statues = ["PUBLISHED"]
    page_no = request.args.get('page', 1, type=int)
    _posts = Post.query.filter(Post.status.in_(statues))

    tag_id = request.args.get('tag_id', None, type=int)
    if tag_id is not None:
        _posts = _posts.join(Post.tags).filter(Tag.id == tag_id)

    tag_name = request.args.get('tag', None)
    if tag_name is not None:
        _posts = _posts.join(Post.tags).filter(Tag.tag_name == tag_name)

    category_id = request.args.get('category_id', None, type=int)
    if category_id is not None:
        _posts = _posts.filter(Post.category_id == category_id)

    category = request.args.get('category', None)
    if category is not None:
        _posts = _posts.join(Post.category).filter(Tag.tag_name == category)

    month = request.args.get('month', None)
    if month is not None:
        _posts = _posts.filter(db.func.MONTHNAME(Post.published_at) == month)
        _all = 1

    year = request.args.get('year', None)
    if year is not None:
        _posts = _posts.filter(db.func.year(Post.published_at) == year)
        _all = 1

    _posts = _posts.order_by(Post.published_at.desc()).paginate(page_no, 2, False)

    next_url = url_for('posts.blog_list', page=_posts.next_num, tag_name=tag_name,
                                          tag_id=tag_id, category_id=category_id) if _posts.has_next else None
    prev_url = url_for('posts.blog_list', page=_posts.prev_num,
                                          tag_id=tag_id, category_id=category_id) if _posts.has_prev else None
    pages = _posts.pages
    start = page_no - 2
    if start < 1:
        start = 1
    first_page = url_for('posts.blog_list', page=1, tag_id=tag_id, tag_name=tag_name,
                                            category_id=category_id) if start != page_no else None
    end = page_no + 2
    if end > pages:
        end = pages
    last_page = url_for('posts.blog_list', page=_posts.pages, tag_id=tag_id, tag_name=tag_name,
                                           category_id=category_id) if end != page_no else None
    page_nos = range(start, end+1)
    return render_template('blog.html', posts=_posts.items, tag_name=tag_name,
                           title="Blog", next_url=next_url,
                           prev_url=prev_url, page_nos=page_nos,
                           first_page=first_page, last_page=last_page,
                           page_no=page_no, tag_id=tag_id, category_id=category_id)


@posts.route('/blog/<string:post_href>')
def blog(post_href):
    _post = Post.query.filter_by(href=post_href).first()
    return render_template('blog_single.html', title="Blog", post=_post)


def create_contact_request(form):
    cr = ContactRequest()
    cr.name = form.name.data
    cr.email = form.email.data
    cr.message = form.message.data
    cr.status = "UN_READ"

    db.session.add(cr)
    db.session.commit()
    return True


def verify_recaptcha(captcha_response_code):
    url = "https://www.google.com/recaptcha/api/siteverify"
    payload = {'secret': rECAPTCHA_SECRET_V2, 'response': captcha_response_code}
    response = requests.post(url, data=payload)
    success = json.loads(response.text)['success']
    print(success)
    return success


#  admin related stuff


@posts.route('/blog/list/all', methods=['GET'])
def list_all():
    statues = ["PUBLISHED", "DRAFT"]
    page = request.args.get('page', 1, type=int)
    _posts = Post.query.filter(Post.status.in_(statues)).order_by(Post.created_at.desc()).all()#.paginate(page, 4, False)
    return render_template('list.html', posts=_posts, title="All articles")


@posts.route('/photos/list/all', methods=['GET'])
def all_photos():
    statues = ["PUBLISHED", "DRAFT"]
    # page = request.args.get('page', 1, type=int)
    photos = Photograph.query.filter(Photograph.status.in_(statues)).\
                order_by(Photograph.capture_date.desc()).all()#.paginate(page, 4, False)
    return render_template('photo_list.html', photos=photos, title="All articles")


@posts.route('/blog/publish/<string:post_id>', methods=["POST"])
def publish(post_id):
    _post = Post.query.filter_by(id=post_id).first()
    _post.status = "PUBLISHED"
    _post.href = Post.generate_href(_post.title)
    _post.published_at = datetime.now()
    db.session.add(_post)
    db.session.commit()
    return render_template('blog_single.html', title="Blog", post=_post)


@posts.route('/blog/unpublish/<string:post_id>', methods=["POST"])
def unpublish(post_id):
    _post = Post.query.filter_by(id=post_id).first()
    _post.status = "DRAFT"
    # _post.href = Post.generate_href(_post.title)
    _post.published_at = None
    db.session.add(_post)
    db.session.commit()
    return redirect(url_for("posts.edit_blog", post_id=post_id))


@posts.route('/blog/edit/<string:post_id>', methods=["GET", "POST"])
@posts.route('/blog/edit', methods=["POST"])
@posts.route('/blog/new', methods=["GET", "POST"])
def edit_blog(post_id=None):
    form = PostForm()
    post = None
    title = "Whats on your mind"
    if post_id is not None:
        post = Post.query.filter(Post.id == post_id).first()
    if post is None:
        post = Post(status="DRAFT")
    if request.method == 'POST':
        if form.validate_on_submit():
            post_id = update_post(form, post)
            return redirect(url_for("posts.edit_blog", post_id=post_id))

    if request.method == "GET":
        form = PostForm(id = post.id,
                        title = post.title,
                        body = post.body,
                        tag_ids = post.all_tag_ids(),
                        category_id = post.category_id
                        )
        title = post.title

    return render_template('edit_blog.html', title=title, form=form)


@posts.route('/photo/new', methods=["GET", "POST"])
@posts.route('/photo/edit', methods=["POST"])
@posts.route('/photo/edit/<string:photo_id>', methods=["GET", "POST"])
def edit_photo(photo_id=None):
    form = PhotoForm()
    print(form.capture_date)
    photo = None
    title = "Whats the pic about"
    if photo_id is not None:
        photo = Photograph.query.filter(Photograph.id == photo_id).first()
    if photo is None:
        photo = Photograph(status="DRAFT")
    if request.method == 'POST':
        if form.validate_on_submit():
            photo_id = update_photo(form, photo)
            return redirect(url_for("posts.edit_photo", photo_id=photo_id))

    if request.method == "GET":
        form = PhotoForm(id = photo.id,
                        title = photo.title,
                        photograph_url = photo.photograph_url,
                        tag_ids = photo.all_tag_ids(),
                        capture_date=photo.capture_date,
                        location=photo.location
                        )
        title = photo.title

    return render_template('edit_photo.html', title=title, form=form)


@posts.route('/photo/publish/<string:photo_id>', methods=["POST"])
def publish_photo(photo_id):
    photo = Photograph.query.filter_by(id=photo_id).first()
    photo.status = "PUBLISHED"
    photo.href = Post.generate_href(photo.title)
    photo.published_at = datetime.now()
    db.session.add(photo)
    db.session.commit()
    return redirect("/photography")


@posts.route('/photo/unpublish/<string:photo_id>', methods=["POST"])
def unpublish_photo(photo_id):
    photo = Photograph.query.filter_by(id=photo_id).first()
    photo.status = "Draft"
    photo.published_at = None
    db.session.add(photo)
    db.session.commit()
    return redirect("/photography")


@posts.route('/tag/new', methods=["GET", "POST"])
@posts.route('/tag/edit', methods=["POST"])
@posts.route('/tag/edit/<string:tag_id>', methods=["GET", "POST"])
def edit_tag(tag_id=None):
    form = TagForm()
    tag = None
    title = "tag "
    if tag_id is not None:
        tag = Tag.query.filter(Tag.id == tag_id).first()
    if tag is None:
        tag = Tag()
    if request.method == 'POST':
        if form.validate_on_submit():
            tag_id = update_tag(form, tag)
            return redirect(url_for("posts.edit_tag", tag_id=tag_id))

    if request.method == "GET":
        form = TagForm(id=tag.id,
                       tag_name=tag.tag_name,
                       category=tag.category,
                       )
        title = tag.tag_name

    return render_template('edit_tag.html', title=title, form=form)


def update_post(form, _post):
    _post.title = form.title.data
    _post.body = form.body.data
    _post.category_id = form.category_id.data

    db.session.add(_post)
    db.session.commit()
    for tag_id in form.tag_ids.data.split(","):
        stmt = post_tags.insert().values(post_id=_post.id, tag_id=tag_id)
        db.session.execute(stmt)

    db.session.commit()

    return _post.id


def update_photo(form, photo):
    photo.title = form.title.data
    photo.photograph_url = form.photograph_url.data
    photo.capture_date = form.capture_date.data
    photo.location = form.location.data
    photo.tags = []

    db.session.add(photo)
    db.session.commit()
    db.session.flush()

    for tag_id in form.tag_ids.data.split(","):
        stmt = photo_tags.insert().values(photograph_id=photo.id, tag_id=tag_id)
        db.session.execute(stmt)

    db.session.commit()

    return photo.id


def update_tag(form, tag):
    tag.tag_name = form.tag_name.data
    tag.category = form.category.data
    if tag.category is None or tag.category == '':
        tag.category = 'tag'

    db.session.add(tag)
    db.session.commit()

    return tag.id
