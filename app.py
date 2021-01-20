from flask import Flask, render_template, url_for, redirect, abort
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from peewee import *
import boto3
import math
import base64
import datetime
import requests
import os

from models import *
from find_swf import find_swf

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ['FORMS_SECRET_KEY']

S3_ENDPOINT = os.environ['S3_ENDPOINT']
S3_ACCESS_KEY = os.environ['S3_ACCESS_KEY']
S3_SECRET_KEY = os.environ['S3_SECRET_KEY']
S3_BUCKET_NAME = os.environ['S3_BUCKET_NAME']
URL_PREFIX = os.environ['CONTENT_URL_PREFIX']

# S3 Setup
s3 = boto3.resource('s3',
    endpoint_url = S3_ENDPOINT,
    aws_access_key_id = S3_ACCESS_KEY,
    aws_secret_access_key = S3_SECRET_KEY
)
bucket = s3.Bucket(S3_BUCKET_NAME)

def copy_swf_to_s3(swf_url, pid: int, oid: int):
    """
    downloads the file from the given url and then uploads it to S3
    after storing it temporarily

    returns the url to access it at
    """
    filename = f"{pid}_{oid}.swf"
    r = requests.get(swf_url, stream=True)
    req_data = r.raw.read()
    print("downloaded SWF from", swf_url, "with length", len(req_data))
    bucket.put_object(Key=filename, Body=req_data, ContentType='application/x-shockwave-flash')

    return URL_PREFIX + '/' + filename

# page id <-> url functions - unused currently
def pid_to_url(pid: int):
    bytes_requred = math.ceil(pid.bit_length()/8)
    b = pid.to_bytes(bytes_requred, byteorder='big')
    print("bytes generated:",b)
    return base64.b32encode(b).decode() # convert to b32, then to a utf8 string from bytes

def url_to_pid(url: str):
    b = base64.b32decode(url.encode()) # convert from a string to utf8 bytes, then from b32 to raw bytes
    pid = int.from_bytes(b, byteorder="big") # convert raw bytes to a python int

#forms
class CreatePageForm(FlaskForm):
    url = StringField("URL: ", validators=[URL()])


@app.route('/', methods=['GET', 'POST'])
def home():
    form = CreatePageForm()
    if form.validate_on_submit():
        url = form.url.data
        print("got url:", url)
        try:
            existing_page = Page.select().where(Page.source_url == url).get()
            print("query returned", existing_page)
            return redirect(url_for('show_page', page_id=existing_page.pid))
        except DoesNotExist:
            pass

        print("adding new page")
        # add the new page
        try:
            new_pid = Page.select().order_by(Page.pid.desc()).get().pid + 1
        except DoesNotExist:
            new_pid = 1 # for the very first page created
        page_title, swf_urls = find_swf(url)

        # create page entry
        new_page = Page(
                source_url = url,
                pid = new_pid,
                title = page_title,
        )
        new_page.save()

        # create swf objects and link to this page
        i = 0 # used for creating "titles" since I'm too lazy to build a way for the user to define them
        for url in swf_urls:
            swf_url = copy_swf_to_s3(url, new_pid, i) # upload to s3 and get public URL
            print("adding swf url", swf_urls[0], flush=True)
            new_object = FlashObject(
                page = new_page,
                oid = i,
                title = f"Item {i+1}", # 1-index for normal people
                swf_url = swf_url
            )
            new_object.save()
            i += 1
        return redirect(url_for('show_page', page_id=new_pid))

    return render_template('home.html', form=form)

@app.route('/p/<page_id>')
@app.route('/p/<page_id>/<object_id>')
def show_page(page_id, object_id=None):
    print("rendering page", page_id, "and object", object_id, flush=True)
    try:
        page = Page.select().where(Page.pid == page_id).get()
    except DoesNotExist:
        abort(404) # raise a 404 error if this is missing
    flash_obj = None
    if object_id:
        try:
            flash_obj = page.objects.where(FlashObject.oid == object_id).get()
        except DoesNotExist:
            abort(404) # if object doesn't exist, raise 404
    return render_template('page.html', page=page, flash_obj=flash_obj)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
