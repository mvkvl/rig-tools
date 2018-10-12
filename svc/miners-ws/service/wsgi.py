from app import app as application

if __name__ == '__main__':
    application.run(debug=False,
                    use_reloader=False,
                    host = "0.0.0.0",
                    port = application.config['PORT'])
