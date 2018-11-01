import factory

from insta_pic.models import User, Post, Comment


class BaseFactory(factory.Factory):
    class Meta:
        abstract = True


class UserFactory(BaseFactory):
    username = factory.Sequence(lambda n: 'user%d' % n)
    email = factory.Sequence(lambda n: 'user%d@mail.com' % n)
    password = "mypwd"

    class Meta:
        model = User


class PostFactory(BaseFactory):
    description = factory.Faker('sentence')
    photo = '/tmp/test_photo.jpg'

    class Meta:
        model = Post


class CommentFactory(BaseFactory):
    text = factory.Faker('sentence')
    post = factory.SubFactory(PostFactory)

    class Meta:
        model = Comment
