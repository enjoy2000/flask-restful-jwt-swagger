import os
from uuid import uuid4

from flask import request, current_app
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from marshmallow import validate

from insta_pic.models import Post
from insta_pic.extensions import ma, db, s3
from insta_pic.commons.pagination import paginate


class PostSchema(ma.ModelSchema):
    description = ma.String(required=True, validate=validate.NoneOf(['']))
    photo = ma.String()

    class Meta:
        model = Post
        sqla_session = db.session


class PostResource(Resource):
    """Single object resource
    """
    method_decorators = [jwt_required]

    def get(self, post_id):
        schema = PostSchema()
        post = Post.query.get_or_404(post_id)
        return {"post": schema.dump(post).data}


class PostList(Resource):
    """
    Creation and get_all
    """
    method_decorators = [jwt_required]

    def get(self):
        schema = PostSchema(many=True)
        query = Post.query
        return paginate(query, schema)

    def post(self):
        """
        Creating a post with image uploaded to s3
        Using s3 to deploy easier
        TODO use ImageField with multiple storage support
        :return:
        """
        description = request.values.get('description').strip()
        if not description:
            return {'msg': 'Description is required'}, 422

        photo = request.files.get('photo')
        if not photo or not photo.filename:
            return {'msg': 'Photo is required'}, 422

        allowed_extensions = ['png', 'jpg', 'jpeg', 'gif']
        extension = os.path.splitext(photo.filename)[1][1:]
        if extension not in allowed_extensions:
            return {'msg': 'File type is not supported'}, 400

        file_path = f'uploads/photos/{uuid4()}.{extension}'
        bucket = current_app.config['AWS_BUCKET_NAME']
        s3.upload_fileobj(photo, bucket, file_path, ExtraArgs={'ACL': 'public-read'})

        # for the simplicity we are using public-acl here
        # TODO use private object and create signed url on schema dump
        absolute_file_url = f'https://s3-ap-southeast-1.amazonaws.com/{bucket}/{file_path}'

        schema = PostSchema()
        post, _ = schema.load({
            'photo': absolute_file_url,
            'description': description
        })

        db.session.add(post)
        db.session.commit()

        return {"msg": "post created", "post": schema.dump(post).data}, 201


class UserPostList(Resource):
    """
    List all post of a user
    """
    method_decorators = [jwt_required]

    def get(self, user_id):
        schema = PostSchema(many=True)
        query = Post.query.filter(Post.created_by_id == user_id)
        return paginate(query, schema)
