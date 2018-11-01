from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import validate

from insta_pic.models import Comment, Post
from insta_pic.extensions import ma, db
from insta_pic.commons.pagination import paginate


class CommentSchema(ma.ModelSchema):
    text = ma.String(required=True, validate=validate.NoneOf(['']))
    post_id = ma.Integer(required=True)

    class Meta:
        model = Comment
        sqla_session = db.session


class CommentResource(Resource):
    """Single object resource
    """
    method_decorators = [jwt_required]

    def get(self, post_id, comment_id):
        schema = CommentSchema()
        comment = Comment.query.filter(Comment.post_id == post_id).get_or_404(comment_id)
        return {"comment": schema.dump(comment).data}


class CommentList(Resource):
    """
    Creation and get_all
    """
    method_decorators = [jwt_required]

    def get(self, post_id):
        schema = CommentSchema(many=True)
        query = Comment.query.filter(Comment.post_id == post_id)
        return paginate(query, schema)

    def post(self, post_id):
        schema = CommentSchema()

        # check post_id
        post = Post.query.get_or_404(post_id)

        comment_data = {
            'post_id': post.id,
            **request.json
        }
        comment, errors = schema.load(comment_data)
        if errors:
            return errors, 422

        db.session.add(comment)
        db.session.commit()

        return {"msg": "comment created", "comment": schema.dump(comment).data}, 201


class MyPostCommentList(Resource):
    """
    Get all comments on all of current user post
    """
    method_decorators = [jwt_required]

    def get(self):
        current_user = get_jwt_identity()
        schema = CommentSchema(many=True)
        query = Comment.query.filter(Comment.post.has(created_by_id=current_user))
        return paginate(query, schema)

