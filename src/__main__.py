from pyramid.data.functional.main import Main

def startup():
	main = Main()

	main.args()
	main.logs()
	main.git_info()
	main.config()
	main.clean_data()

	main.open_socket()
	main.start()
	main.stop()

if __name__ == "__main__":
	startup()
