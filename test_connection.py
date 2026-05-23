import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise SystemExit("DATABASE_URL not found in .env")

engine = create_engine(database_url)

with engine.connect() as conn:
    result = conn.execute(text("SELECT version();"))
    print("Connected!")
    print(result.scalar())