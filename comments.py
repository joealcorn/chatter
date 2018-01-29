from datetime import datetime
import hashlib
import json
import logging

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import boto3
import pytz
import simpleflake

logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins=[
    'http://127.0.0.1:4000',
    'https://joealcorn.co.uk',
])

s3 = boto3.resource('s3')
bucket = s3.Bucket('zappa-comments-input')


@app.route('/', methods=['POST'])
def submit_comment():
    # slug should be something like a url
    slug = request.form.get('slug')
    comment_text = request.form.get('comment')
    name = request.form.get('name')
    email = request.form.get('email')

    if not comment_text or not name or not slug:
        return jsonify({
            'error': '`comment`, `name` and `slug` needed',
        }), 400

    comment_id = str(simpleflake.simpleflake())
    comment = {
        'id': comment_id,
        'text': comment_text,
        'name': name,
        'email': email,
        'version': '0',
        'ip_address': request.remote_addr,
        'created_at': datetime.utcnow().replace(tzinfo=pytz.utc).isoformat(),
    }
    comment_json = json.dumps(comment)

    # store comment in appropriate place in bucket
    file_name = 'comments/%s/%s.json' % (slug, comment_id)
    bucket.put_object(
        Body=bytes(comment_json, encoding='utf8'),
        Key=file_name,
        ACL='private',
        ContentType='application/json',
    )

    return Response(comment_json, headers={
        'Access-Control-Allow-Origin': '*',
    }, content_type='application/json')


def get_comments_from_bucket(slug):
    prefix = 'comments/%s/' % slug
    comments = []
    etags = []

    print('Getting comments from bucket with prefix %s' % prefix)
    for obj in bucket.objects.filter(Prefix=prefix):
        file_name = obj.key.rsplit('/', 1)[1]
        comment_id = file_name.rsplit('.', 1)[0]

        try:
            comment_json = json.loads(obj.get()['Body'].read().decode('utf8'))
            assert comment_json['id'] == comment_id
            comments.append({
                'id': comment_json['id'],
                'text': comment_json['text'],
                'name': comment_json['name'],
                'version': comment_json['version'],
                'created_at': comment_json['created_at'],
            })
            etags.append(obj.e_tag)
        except Exception as ex:
            logger.exception('Error when fetting comment')
            continue

    return (comments, etags)


def rebuild_comment_index(event, context):
    '''
    This event handler fires when a file is added or removed from the bucket.
    It triggers a rebuild of the appropriate index file.
    '''

    obj = event['Records'][0]['s3']['object']
    directory, file_name = obj['key'].rsplit('/', 1)

    # if this file is in not in a comments/<slug>/ directory,
    # do not process
    if not directory.startswith('comments/'):
        return

    _, slug = directory.split('/', 1)
    index_slug(slug)


def index_slug(slug):
    comments, etags = get_comments_from_bucket(slug)

    etag = bytes('.'.join(etags), encoding='utf8')
    etag = hashlib.md5(etag).hexdigest()
    data = {
        'comments': comments,
        'etag': etag,
    }

    bucket.put_object(
        Key='indexes/%s.json' % slug,
        Body=bytes(json.dumps(data), encoding='utf8'),
        ACL='public-read',
        ContentType='application/json',
    )




if __name__ == '__main__':
    app.run(debug=True)
