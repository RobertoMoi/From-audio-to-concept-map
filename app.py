import routes

if __name__ == '__main__':
    routes.app.secret_key = 'mykey'
    routes.app.run()



