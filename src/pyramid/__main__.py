from data.functional.main import Main
from tools.test_dev import TestDev

main = Main()

main.logs()
main.git_info()
main.config()
main.database()
main.clean_data()

test_dev = TestDev(main._config, main.logger)
# test_dev.test_db()

main.start()
main.stop()
