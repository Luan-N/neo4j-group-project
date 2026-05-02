from typing import Optional, Dict
import uuid
from db import driver


def register(name: str, email: str, username: str, password: str) -> Dict:
    with driver.session() as session:
        res = session.run(
            "MATCH (u:User) WHERE u.username = $username OR u.email = $email RETURN u LIMIT 1",
            username=username, email=email,
        )
        if res.single() is not None:
            raise ValueError("Username or email already exists")

        user_id = str(uuid.uuid4())
        r = session.run(
            """CREATE (u:User {userId: $userId, name: $name, email: $email,
            username: $username, bio: $bio, password: $password})
            RETURN u.userId AS userId, u.name AS name, u.email AS email, u.username AS username""",
            userId=user_id, name=name, email=email, username=username, bio="", password=password,
        )
        row = r.single()
        return {"userId": row["userId"], "name": row["name"], "email": row["email"], "username": row["username"]}


def login(username: str, password: str) -> Optional[Dict]:
    with driver.session() as session:
        r = session.run(
            """MATCH (u:User {username: $username, password: $password})
            RETURN u.userId AS userId, u.username AS username, u.name AS name, u.email AS email""",
            username=username, password=password,
        )
        row = r.single()
        if row is None:
            return None
        return {"userId": row["userId"], "username": row["username"], "name": row["name"], "email": row["email"]}


def get_profile(user_id: str) -> Optional[Dict]:
    with driver.session() as session:
        r = session.run(
            """MATCH (u:User {userId: $userId})
            RETURN u.userId AS userId, u.username AS username,
            u.name AS name, u.email AS email, u.bio AS bio""",
            userId=user_id,
        )
        row = r.single()
        if row is None:
            return None
        return {"userId": row["userId"], "username": row["username"], "name": row["name"], "email": row["email"], "bio": row["bio"]}


def update_profile(user_id: str, name: Optional[str] = None, email: Optional[str] = None, bio: Optional[str] = None) -> Dict:
    sets = []
    params = {"userId": user_id}
    if name is not None:
        sets.append("u.name = $name")
        params["name"] = name
    if email is not None:
        sets.append("u.email = $email")
        params["email"] = email
    if bio is not None:
        sets.append("u.bio = $bio")
        params["bio"] = bio

    if not sets:
        return get_profile(user_id)

    set_clause = ", ".join(sets)
    with driver.session() as session:
        session.run(f"MATCH (u:User {{userId: $userId}}) SET {set_clause}", **params)
    return get_profile(user_id)