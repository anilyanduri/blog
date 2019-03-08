# wsgi.py

from blog import create_app

config_name = 'PRODUCTION'
app = create_app(config_name)


if __name__ == '__main__':
        app.run()

