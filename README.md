# Chatter

Chatter is a statically generated comment engine for embedding on any website. Being statically
generated means no database is needed, which makes it very lightweight.

Running on AWS lambda makes it incredibly cost effective for small sites, and leaning on
[Zappa](https://github.com/Miserlou/Zappa) makes management simple.

<a href='https://joealcorn.github.io/chatter/' target='_blank'>
    <p>See an example</p>
    <img width="540" alt="Example comment box" src="https://user-images.githubusercontent.com/1097349/35779514-1fa29c60-09c6-11e8-8ab8-570a4bb042c9.png">
</a>

## How it works

New comments are submitted to an API endpoint running inside [AWS Lambda](https://aws.amazon.com/lambda/),
which writes the comment to an S3 bucket. A second lambda function will then build a json index of the
comments, which is what will be read by the user's browser.

At the moment it's up to you to submit and render comments, but there's some example code on the gh-pages
branch.

## Getting started

### Authentication

You must [set up an AWS credentials file](https://aws.amazon.com/blogs/security/a-new-and-standardized-way-to-manage-credentials-in-the-aws-sdks/).

### Installation

Install the dependencies using [pipenv](http://pipenv.readthedocs.io/en/latest/)

`$ pipenv install`

Go inside the virtualenv pipenv created so Zappa recognises it as a venv

`$ source $(pipenv --venv)/bin/activate`

### Configuration

- Change the bucket in the top of chatter.py. This is where we'll store comments and indexes.
- Change `arn` in `zappa_settings.json` to match the input bucket so zappa can register an event handler.
- Change `s3_bucket` in `zappa_settings.json`. This is where zappa will build the packages for lambda.
- Add the url of the websites you're going to be creating new comments on to the `CORS` call under
  `app = Flask(__name__)` so we can set HTTP headers appropriately

### Deployment

`$ zappa deploy dev`
