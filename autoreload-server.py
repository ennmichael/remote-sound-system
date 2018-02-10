import livereload


server = livereload.Server()
server.watch('py', livereload.shell('./server.sh'))
server.serve()

