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

def follow(follower_id: str, followed_username: str) -> bool:
    followed_id = get_user_id_by_username(followed_username)
    if follower_id == followed_id:
        return False
    
    with driver.session() as session:
        result = session.run(
            """
            MATCH (a:User {userId: $followerId}), (b:User {userId: $followedId})
            MERGE (a)-[relationship:FOLLOWS]->(b)
            RETURN COUNT(relationship) > 0 AS followed
            """,
            followerId=follower_id, followedId=followed_id,
        ).single()
        
    return result["followed"] > 0

def unfollow(follower_id: str, followed_username: str) -> bool:
    followed_id = get_user_id_by_username(followed_username)
    if follower_id == followed_id:
        return False
    
    with driver.session() as session:
        result = session.run(
            """
            MATCH (a:User {userId: $followerId})-[relationship:FOLLOWS]->(b:User {userId: $followedId})
            DELETE relationship
            RETURN COUNT(relationship) = 0 AS unfollowed
            """,
            followerId=follower_id, followedId=followed_id,
        ).single()
    return result["unfollowed"] > 0

def get_user_id_by_username(username: str) -> Optional[str]:
    with driver.session() as session:
        result = session.run(
            "MATCH (u:User {username: $username}) RETURN u.userId AS userId",
            username=username,
        ).single()
    return result["userId"] if result else None


def get_following(user_id: str) -> list:
    with driver.session() as session:
        result = session.run(
            """MATCH (u:User {userId: $userId})-[:FOLLOWS]->(f:User)
            RETURN f.username AS username, f.name AS name""",
            userId=user_id,
        )
        return [{"username": r["username"], "name": r["name"]} for r in result]


def get_followers(user_id: str) -> list:
    with driver.session() as session:
        result = session.run(
            """MATCH (f:User)-[:FOLLOWS]->(u:User {userId: $userId})
            RETURN f.username AS username, f.name AS name""",
            userId=user_id,
        )
        return [{"username": r["username"], "name": r["name"]} for r in result]


def get_mutual_connections(user_id: str, target_username: str) -> list:
    target_id = get_user_id_by_username(target_username)
    if not target_id:
        return []
    with driver.session() as session:
        result = session.run(
            """MATCH (a:User {userId: $userId})-[:FOLLOWS]->(m:User)<-[:FOLLOWS]-(b:User {userId: $targetId})
            RETURN m.username AS username, m.name AS name""",
            userId=user_id, targetId=target_id,
        )
        return [{"username": r["username"], "name": r["name"]} for r in result]


def get_recommendations(user_id: str) -> list:
    with driver.session() as session:
        result = session.run(
            """MATCH (me:User {userId: $userId})-[:FOLLOWS]->(a:User)-[:FOLLOWS]->(rec:User)
            WHERE rec.userId <> $userId
              AND NOT (me)-[:FOLLOWS]->(rec)
            RETURN rec.username AS username, rec.name AS name, COUNT(a) AS commonCount
            ORDER BY commonCount DESC
            LIMIT 10""",
            userId=user_id,
        )
        return [{"username": r["username"], "name": r["name"], "commonConnections": r["commonCount"]} for r in result]