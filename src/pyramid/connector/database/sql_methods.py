from connector.database.methods.add_update import SQLMethodsAddUpdate
from connector.database.methods.delete import SQLMethodsDelete
from connector.database.methods.find import SQLMethodsFind


class SQLMethods(SQLMethodsAddUpdate, SQLMethodsFind, SQLMethodsDelete):
	__abstract__ = True
