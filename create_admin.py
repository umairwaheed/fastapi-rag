import sys
from app.helpers import get_password_hash, get_user_by_username
from app.models import Role, User
from app.db import engine
from app.oso import add_role
from sqlmodel import Session


if __name__ == "__main__":
    try:
        password = sys.argv[1]
    except IndexError:
        password = "admin"

    user = User(
        username="admin",
        email="admin@example.com",
        password=get_password_hash(password),
        role=Role.USER,
    )

    with Session(engine) as session:
        current_user = get_user_by_username(session, "admin")
        if current_user:
            session.delete(current_user)
            session.commit()

        session.add(user)
        session.commit()
        session.refresh(user)
        add_role(user, Role.USER)
