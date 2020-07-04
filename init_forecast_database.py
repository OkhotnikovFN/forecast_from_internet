import peewee

DATABASE_PATH = "files/forecast_database.db"

database = peewee.SqliteDatabase(DATABASE_PATH)
database_proxy = peewee.DatabaseProxy()
database_proxy.initialize(database)
