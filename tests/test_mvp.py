"""
 Allow users to register by username (with validate)
 Allow users to create content by submitting posts that include a image and short description
 Allow users to comment on posts by submitting comments content
 Allow users to view all posts
 Allow users to view post from a specific user
 Allow users to view all comments on all of their own posts
"""
import json
from pathlib import Path
from unittest import mock

from faker import Faker

from insta_pic.commons.pagination import DEFAULT_PAGE_SIZE
from insta_pic.models import User, Post, Comment

faker = Faker()


def test_user_register_with_username(client, db):
    """
    Allow users to register by username (with validate)

    :param client:
    :param db:
    :return:
    """
    username = faker.name().lower().replace(' ', '')
    email = faker.email()
    password = faker.password()
    resp = client.post('/auth/register', data=json.dumps({'username': username, 'password': password, 'email': email}),
                       content_type='application/json')
    assert resp.status_code == 200
    assert 'user' in resp.json
    assert username == resp.json['user']['username']
    assert User.query.filter(User.username == username).first() is not None


def test_user_registration_validation(client, db):
    username = faker.name().lower().replace(' ', '')
    password = faker.password()
    resp = client.post('/auth/register', data=json.dumps({'username': username, 'password': password}),
                       content_type='application/json')
    assert resp.status_code == 422


@mock.patch('insta_pic.extensions.s3.upload_fileobj', return_value=True)
def test_create_post_with_image_and_description(upload_fileobj, client, db, admin_headers):
    """
    Allow users to create content by submitting posts that include a image and short description
    :param client:
    :param db:
    :param admin_headers:
    :return:
    """
    with open(Path(__file__).resolve().parent.joinpath('test_data/image002.png')) as photo:
        post_data = {
            'photo': photo.buffer,
            'description': 'description',
        }

        resp = client.post('/api/v1/posts', headers={
                **admin_headers,
                'content-type': 'multipart/form-data',
            }, data=post_data)
    assert resp.status_code == 201
    assert 'post' in resp.json
    assert 'id' in resp.json['post']
    assert Post.query.filter(Post.id == resp.json['post']['id']).first() is not None

    upload_fileobj.assert_called_once()


def test_create_post_with_invalid_image(client, db, admin_headers):
    with open(Path(__file__).resolve().parent.joinpath('test_data/invalid_file.pdf')) as photo:
        post_data = {
            'photo': photo.buffer,
            'description': 'description',
        }
        resp = client.post('/api/v1/posts', headers={
            **admin_headers,
            'content-type': 'multipart/form-data',
        }, data=post_data)
    assert resp.status_code == 400
    assert resp.json['msg'] == 'File type is not supported'


def test_create_post_without_image(client, db, admin_headers):
    resp = client.post('/api/v1/posts', headers={
        **admin_headers,
        'content-type': 'multipart/form-data',
    }, data={'description': 'description', 'photo': ''})
    assert resp.status_code == 422
    assert resp.json['msg'] == 'Photo is required'


def test_create_post_without_a_valid_photo(client, db, admin_headers):
    resp = client.post('/api/v1/posts', headers={
        **admin_headers,
        'content-type': 'multipart/form-data',
    }, data={'description': 'description', 'photo': 'photo'})
    assert resp.status_code == 422
    assert resp.json['msg'] == 'Photo is required'


def test_create_post_without_a_description(client, db, admin_headers):
    resp = client.post('/api/v1/posts', headers={
        **admin_headers,
        'content-type': 'multipart/form-data',
    }, data={'description': '', 'photo': 'photo'})
    assert resp.status_code == 422
    assert resp.json['msg'] == 'Description is required'


def test_comment_on_post(client, db, post, admin_headers):
    """
    Allow users to comment on posts by submitting comments content
    :param client:
    :param post:
    :param admin_headers:
    :return:
    """
    comment_data = {
        'text': 'comment text'
    }

    db.session.add(post)
    db.session.commit()
    post_id = post.id

    resp = client.post(f'/api/v1/posts/{post_id}/comments', headers=admin_headers, data=json.dumps(comment_data))
    assert resp.status_code == 201
    assert Comment.query.filter(Comment.post_id == post_id).first() is not None
    resp_data = resp.get_json()['comment']
    assert 'id' in resp_data


def test_user_view_all_posts(client, db, admin_headers, post_factory, user_factory):
    """
    Allow users to view all posts & pagination
    :param client:
    :param admin_headers:
    :return:
    """
    user = user_factory()
    total_posts = 30

    assert total_posts > DEFAULT_PAGE_SIZE  # must greater default page size to test pagination

    posts = post_factory.create_batch(total_posts, created_by=user)

    db.session.add_all(posts)
    db.session.commit()

    resp = client.get('/api/v1/posts', headers=admin_headers)
    assert resp.status_code == 200
    resp_data = json.loads(resp.get_data(as_text=True))
    assert 'results' in resp_data
    assert resp_data['total'] == total_posts
    assert len(resp_data['results']) == DEFAULT_PAGE_SIZE


def test_view_posts_from_a_user(client, db, admin_headers, user_factory, post_factory):
    """
    Allow users to view post from a specific user
    :param client:
    :param admin_headers:
    :return:
    """
    posts_of_one_user = 30

    assert posts_of_one_user > DEFAULT_PAGE_SIZE  # must greater default page size to test pagination

    author = user_factory()
    another_author = user_factory()
    posts = post_factory.create_batch(posts_of_one_user, created_by=author)
    another_author_posts = post_factory.create_batch(posts_of_one_user, created_by=another_author)

    db.session.add_all(posts + another_author_posts)
    db.session.commit()

    resp = client.get(f'/api/v1/users/{author.id}/posts', headers=admin_headers)
    assert resp.status_code == 200
    resp_data = json.loads(resp.get_data(as_text=True))
    assert 'results' in resp_data
    assert resp_data['total'] == posts_of_one_user
    assert len(resp_data['results']) == DEFAULT_PAGE_SIZE
    assert Post.query.count() != posts_of_one_user


def test_users_view_all_comments_of_their_posts(client, db, admin_user, admin_headers, post_factory, comment_factory):
    """
    Allow users to view all comments on all of their own posts
    :param client:
    :param admin_headers:
    :return:
    """
    # only 1 user now
    number_of_comments_for_one_post = 10
    posts = post_factory.create_batch(faker.random_int(10, 20), created_by=admin_user)
    for post in posts:
        comments = comment_factory.create_batch(number_of_comments_for_one_post, post=post)
        db.session.add_all(comments)
    db.session.add_all(posts)
    db.session.commit()

    resp = client.get('/api/v1/posts/all_comments', headers=admin_headers)
    assert resp.status_code == 200
    resp_data = json.loads(resp.get_data(as_text=True))

    assert resp_data['total'] == len(posts) * number_of_comments_for_one_post
