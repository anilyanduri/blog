from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, TextAreaField, ValidationError, SubmitField, DateField

# FormField, BooleanField, SelectField, FieldList, SelectMultipleField
from wtforms.validators import DataRequired, Email
# from blog.constants import KEY_WORDS
from blog.models import Post, Photograph, Tag
from sqlalchemy import func
from wtforms.fields.html5 import EmailField


class PostForm(FlaskForm):
    id = HiddenField("id")
    title = StringField("Title", validators=[DataRequired()])
    body = TextAreaField("Blog Post", validators=[DataRequired()], render_kw={'rows': 30})
    meta_tags = TextAreaField("Meta tags")
    tag_ids = HiddenField("tag_ids")
    category_id = HiddenField("category_id")
    submit = SubmitField('Save Blog')

    def validate_title(self, field):
        if Post.query.filter(Post.title == field.data, Post.id != self.id.data).first():
            raise ValidationError('Title has been taken already!')


class PhotoForm(FlaskForm):
    id = HiddenField("id")
    title = StringField("Title", validators=[DataRequired()])
    photograph_url = StringField("photograph url", validators=[DataRequired()])
    tag_ids = HiddenField("tag_ids")
    capture_date = DateField('captured date', validators=[DataRequired()], format='%m/%d/%Y')
    location = StringField("Location", validators=[DataRequired()])
    submit = SubmitField('Save Photo')

    def validate_title(self, field):
        if Photograph.query.filter(Photograph.title == field.data, Photograph.id != self.id.data).first():
            raise ValidationError('Title has been taken already!')


class TagForm(FlaskForm):
    id = HiddenField("id")
    tag_name = StringField("Tag Name", validators=[DataRequired()])
    category = StringField("Tag Category")
    submit = SubmitField('Save Tag')

    def validate_tag_name(self, field):
        if Tag.query.filter(func.lower(Tag.tag_name) == func.lower(field.data), Tag.id != self.id.data).first():
            raise ValidationError('Tag exists already!')


class ContactMeForm(FlaskForm):
    name = StringField("Your Name", validators=[DataRequired()], render_kw={'placeholder': "Your Name", 'class': 'form-control'})
    email = EmailField("Your Email", validators=[DataRequired(), Email()], render_kw={'placeholder': "Your Email", 'class': 'form-control'})
    subject = StringField("Subject", render_kw={'placeholder': "Subject", 'class': 'form-control'})
    message = TextAreaField("Message", validators=[DataRequired()],
                            render_kw={'rows': 5, 'cols': 30, 'placeholder': "Message", 'class': 'form-control'})
    recaptcha_response = HiddenField("recaptcha_response_token", validators=[DataRequired()])
