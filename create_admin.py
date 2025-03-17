import sys

from sqlmodel import Session

from app.helpers import get_password_hash, get_user_by_username
from app.models import Role, User, engine
from app.oso import add_oso_role, delete_oso_user

if __name__ == "__main__":
    try:
        password = sys.argv[1]
    except IndexError:
        password = "admin"

    user = User(
        username="admin",
        email="admin@example.com",
        password=get_password_hash(password),
        role=Role.ADMIN,
    )

    with Session(engine) as session:
        current_user = get_user_by_username(session, "admin")
        if current_user:
            session.delete(current_user)
            delete_oso_user(current_user)
            session.commit()

        session.add(user)
        session.commit()
        session.refresh(user)
        add_oso_role(user, Role.ADMIN)
