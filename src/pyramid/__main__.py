from data.functional.main import Main
from test_dev import TestDev

main = Main()

main.logs()
main.git_info()
main.config()
main.open_socket()
main.database()
main.clean_data()

test_dev = TestDev(main._config, main.logger)
# test_dev.test_db()

main.start()
main.stop()
