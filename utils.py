from __future__ import absolute_import
from __future__ import print_function
import mammoth
from docx import Document
from pypdf import PdfReader
import json
from datetime import datetime
from django.db.models import Count
from payments.models import Discount, Discount_Usage
from time import mktime

def is_ajax(request):
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'

def get_epoch():
    dt = datetime.now()
    sec_since_epoch = mktime(dt.timetuple()) + dt.microsecond/1000000.0

    millis_since_epoch = sec_since_epoch * 1000
    return str(sec_since_epoch)


def get_file_content(path):
    content = ""
    # try:
    if path.split('.')[-1] == 'docx':
        with open(path,'rb') as doc_file:
            result = mammoth.convert_to_html(doc_file)
            content = result.value
    elif path.split('.')[-1] == 'pdf':
        content = convert_pdf_to_txt(path)
        if not content.strip():
            content = get_pdf_content(path)
    if not content.strip():
        content = "No Preview Available"
    # except:
    #     print('File was not found')
    return content.strip()

def get_file_text(path):
    content = ""
    # try:
    if path.split('.')[-1] == 'docx':
        doc_file = Document(path)
        full_text = []
        for para in doc_file.paragraphs:
            full_text.append(para.text)
        content = '\n'.join(full_text)
    elif path.split('.')[-1] == 'doc':
        import subprocess
        content,errors = subprocess.Popen(
                            [
                                "antiword", 
                                path,
                                "-f",
                                "-i", 
                                "1"
                            ],
                            stdout = subprocess.PIPE,
                            stderr = subprocess.PIPE,
                            stdin = subprocess.PIPE
                        ).communicate()

    else:
        content = convert_pdf_to_txt(path)
        if not content.strip():
            content = get_pdf_content(path)
    if not content.strip():
        content = ""
    # except:
    #     print('File was not found')
    return content

def get_pdf_content(pdf_path, page_nums=[]):
    content = ''
    try:
        p = open(pdf_path, "rb")
        pdf = PdfReader(p)
        if page_nums:
            for page_num in range(len(pdf.pages)):
                content += pdf.pages[page_num].extract_text() or '' + '\n'
            # print(content)
        else:
            for page_num in page_nums:
                content += pdf.pages[page_num].extract_text() or '' + '\n'
            # print(content)
    except: 
        pass
    return content

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO

def convert_pdf_to_txt(path):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = open(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos=set()
    try:
        for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
            interpreter.process_page(page)
        text = retstr.getvalue()
    except:
        text = ""

    fp.close()
    device.close()
    retstr.close()
    return text

def validate_code(code, plan, company):
    if code:
        discount = Discount.objects.filter(enabled = True, label__iexact = code, plans__in=[int(plan.id)])
        if not discount:
            return False
        discount = discount[0]
        if discount.expiry < datetime.now().date():
            discount.enabled = False
            discount.save()
            return False
        if not company in discount.companies.all():
            return False
        if discount.discount_usage_set.all().filter(company = company)[0].used_count >= discount.max_usage_per_company:
            return False
        total = 0
        for usage in discount.discount_usage_set.all():
            total = total + usage.used_count
        if discount.max_usage <= total:
            discount.enabled = False
            discount.save()
            return False
    return True

from random import choice
from string import ascii_lowercase, digits
from common.models import User

def generate_random_username(length=10, chars=ascii_lowercase+digits, split=4, delimiter='-'):
    
    username = ''.join([choice(chars) for i in range(length)])
    
    if split:
        username = delimiter.join([username[start:start+split] for start in range(0, len(username), split)])
    
    try:
        User.objects.get(username=username)
        return generate_random_username(length=length, chars=chars, split=split, delimiter=delimiter)
    except User.DoesNotExist:
        return username

import requests
# import hmac
# import hashlib
import json
from TRM import settings

# def get_fb_app_secret_proof(access_token):
#     consumer_key = settings.SOCIALAUTH_FACEBOOK_OAUTH_KEY
#     consumer_secret = settings.SOCIALAUTH_FACEBOOK_OAUTH_SECRET
#     h = hmac.new(
#         consumer_secret.encode('utf-8'),
#         msg=access_token.encode('utf-8'),
#         digestmod=hashlib.sha256
#     )
#     return h.hexdigest()

def posttofbprofile(fbtoken, message="", link=""):
    post_url = "https://graph.facebook.com/me/feed/"
    token = fbtoken.oauth_token
    r = requests.post(
        post_url,
        data = {
                'link': link,
                'message': message,
                'access_token': token,
                # 'appsecret_proof': str(get_fb_app_secret_proof(str(token))),
            }
        )
    print((r.status_code))
    # raise ValueError(r.reason)
    return r

def posttofbgroup(fbtoken, groupid, message="", link=""):
    request_token_url = "https://graph.facebook.com/"+str(groupid)+"/feed/"
    r = requests.post(
        request_token_url, 
        data={
            'message': message,
            'link': link,
            'access_token': str(fbtoken.oauth_token),
            # 'appsecret_proof': str(get_fb_app_secret_proof(str(fbtoken.oauth_token))),
            }
        )
    print((r.status_code))
    return r


def get_page_token(fbtoken,pageid):
    url = "https://graph.facebook.com/"+str(pageid)+"/?fields=access_token&access_token="+str(fbtoken.oauth_token) #+"&appsecret_proof="+str(get_fb_app_secret_proof(str(fbtoken.oauth_token)))
    resp = requests.get(url)
    Data = json.loads(resp.content)
    return Data['access_token']


def posttofbpage(fbtoken, pageid, message = "", link = ""):
    request_token_url = "https://graph.facebook.com/"+str(pageid)+"/feed/"
    pagetoken = get_page_token(fbtoken,pageid)
    r = requests.post(
        request_token_url, 
        data={
            'message': message,
            'link': link,
            'access_token': str(pagetoken),
            # 'appsecret_proof': str(get_fb_app_secret_proof(str(pagetoken))),
            }
        )
    if r.status_code == 403:
        r = requests.post(
            request_token_url, 
            data={
                'message': message,
                'link': link,
                'access_token': str(fbtoken.oauth_token),
                # 'appsecret_proof': str(get_fb_app_secret_proof(str(fbtoken.oauth_token))),
                }
            )
    print((r.status_code))
    return r

def posttoliprofile(litoken, message="", og={}):
    token = litoken.oauth_token
    post_url = "https://api.linkedin.com/v1/people/~/shares?format=json&oauth2_access_token=" + token
    headers = {
        'Content-Type': 'application/json',
        'x-li-format': 'json'
    }
    data = {
                "comment": str(message),
                "content": {
                    "title": str(og['title']),
                    "description": str(og['description']),
                    "submitted-url": str(og['url']),
                    "submitted-image-url": str(og['image'])
                },
                "visibility": {
                    "code": "anyone"
                }  
            }
    r = requests.post(
        post_url,
        data = json.dumps(data),
        headers = headers
        )
    print((r.status_code))
    print((r.content))
    return r

def posttolicompany(litoken, pageid, message="", og={}):
    token = litoken.oauth_token
    post_url = "https://api.linkedin.com/v1/companies/" + str(pageid) + "/shares?format=json&oauth2_access_token=" + token
    headers = {
        'Content-Type': 'application/json',
        'x-li-format': 'json'
    }

    data = {
                "comment": str(message),
                "content": {
                    "title": str(og['title']),
                    "description": str(og['description']),
                    "submitted-url": str(og['url']),
                    "submitted-image-url": str(og['image'])
                },
                "visibility": {
                    "code": "anyone"
                }  
            }
    r = requests.post(
        post_url,
        data = json.dumps(data),
        headers = headers
        )
    print((r.status_code))
    return r
from requests_oauthlib import OAuth1
from urllib.parse import urlencode
def posttotwitter(twtoken, message = "", link=""):
    consumer_key = settings.SOCIALAUTH_TWITTER_OAUTH_KEY
    consumer_secret = settings.SOCIALAUTH_TWITTER_OAUTH_SECRET
    token = twtoken.oauth_token.split('|-|')
    auth = OAuth1(consumer_key, consumer_secret, token[0],token[1])
    querystring = {
        'include_entities': True,
        'status': link + ' ' + message
    }
    post_url = "https://api.twitter.com/1.1/statuses/update.json?"+ urlencode(querystring)
    r = requests.post(
            post_url, auth=auth, data=""
        )
    print((r.status_code))
    print((r.content))
    return r

# def gettweets(twtoken):
#     consumer_key = settings.SOCIALAUTH_TWITTER_OAUTH_KEY
#     consumer_secret = settings.SOCIALAUTH_TWITTER_OAUTH_SECRET
#     token = twtoken.oauth_token.split('|-|')
#     print(token)
#     url = 'https://api.twitter.com/1.1/statuses/lookup.json'
#     url = 'https://api.twitter.com/1.1/account/verify_credentials.json'
#     print(consumer_key)
#     print(consumer_secret)
#     print(token[0])
#     print(token[1])
#     auth = OAuth1(consumer_key, consumer_secret, token[0], token[1])
#     print(auth)
#     r = requests.get(url,auth=auth)
#     print(r.status_code)
#     print(r.content)
#     return auth

from math import log
def tagcloud(tags, related_name, threshold=0, maxsize=1.75, minsize=.75):
    """usage: 
        -threshold: Tag usage less than the threshold is excluded from
            being displayed.  A value of 0 displays all tags.
        -maxsize: max desired CSS font-size in em units
        -minsize: min desired CSS font-size in em units
    Returns a list of dictionaries of the tag, its count and
    calculated font-size.
    """
    counts, taglist, tagcloud = [], [], []
    for tag in tags():
        count = tag.__getattribute__(related_name).count()
        count >= threshold and (counts.append(count), taglist.append(tag))
    if counts:
        maxcount = max(counts)
        mincount = min(counts)
    else:
        maxcount = 0
        mincount = 0
    constant = log(maxcount - (mincount - 1))/(maxsize - minsize or 1) or 1
    tagcount = list(zip(taglist, counts))
    for tag, count in tagcount:
        size = log(count - (mincount - 1))/constant + minsize
        tagcloud.append({'tag': tag, 'count': count, 'size': round(size, 7)})
    return tagcloud