from pg_db_connection import pg_db, database
from models import (
    Coin, Duty, Knowledge, Skill, Behaviour,
    DutyCoin, DutyKnowledge, DutySkill, DutyBehaviour,
    User, RequestLog
)

def create_tables():
    if database.obj is None:
        database.initialize(pg_db)

    database.connect()

    tables = [
        Coin, Duty, Knowledge, Skill, Behaviour,
        DutyCoin, DutyKnowledge, DutySkill, DutyBehaviour,
        User, RequestLog
    ]

    database.create_tables(tables, safe=True)
    print("All tables created!")

    database.close()


if __name__ == "__main__":
    create_tables()