from insta_pic.app import create_app

app = create_app()


@app.route('/')
def home():
    return '<h1><center>InstaPic demo application</center></h1>'
