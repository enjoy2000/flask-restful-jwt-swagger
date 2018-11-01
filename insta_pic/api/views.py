from flask import Blueprint
from flask_restful import Api

from insta_pic.api.resources import UserResource, UserList, PostResource, PostList, CommentResource, CommentList, \
    MyPostCommentList, UserPostList

blueprint = Blueprint('api', __name__, url_prefix='/api/v1')
api = Api(blueprint)


api.add_resource(UserResource, '/users/<int:user_id>')
api.add_resource(UserList, '/users')

api.add_resource(PostResource, '/posts/<int:post_id>')
api.add_resource(PostList, '/posts')
api.add_resource(UserPostList, '/users/<int:user_id>/posts')

api.add_resource(CommentResource, '/posts/<int:post_id>/comments/<int:comment_id>')
api.add_resource(CommentList, '/posts/<int:post_id>/comments')
api.add_resource(MyPostCommentList, '/posts/all_comments')
