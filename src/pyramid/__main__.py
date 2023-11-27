from data.functional.main import Main


main = Main()

main.args()
main.logs()
main.git_info()
main.config()
main.open_socket()
main.clean_data()

# test_dev = TestDev(main._config, main.logger)
# test_dev.test_deezer()

main.start()
main.stop()
