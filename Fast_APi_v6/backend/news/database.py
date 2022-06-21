from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

DATABASE_URL = "mysql+mysqlconnector://newssum:qkrrkddls@ssac.ctsolbee3mtl.us-west-2.rds.amazonaws.com/news_data"
# DATABASE_URL = "mysql//admin:12345678@ssac.ctsolbee3mtl.us-west-2.rds.amazonaws.com/news_data?charset=utf8"
ENGINE = create_engine(
    DATABASE_URL,
    encoding = "utf-8",
    echo = True
)

SessionLocal = scoped_session(
    sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=ENGINE)
)
Base = declarative_base()
Base.query = SessionLocal.query_property()


# from databases import Database
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy import create_engine, MetaData
# import json
# import os
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# SECRET_FILE = os.path.join(BASE_DIR, "secrets.json")
# secrets = json.loads(open(SECRET_FILE).read())
# DB = secrets["DB"]
#
# DB_URL = f"mysql://{DB['user']}:{DB['password']}@{DB['host']}:{DB['port']}/{DB['database']}?charset=utf8"
#
# engine = create_engine(
#     DB_URL, encoding = 'utf-8'
# )
#
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
#
# Base = declarative_base()