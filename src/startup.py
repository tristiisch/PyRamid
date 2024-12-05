from pyramid.data.functional.main import Main

def startup():
	main = Main()
	main.args()
	main.start()
	main.stop()
