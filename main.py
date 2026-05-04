from auth import register, login, get_profile, update_profile, follow, unfollow, get_following, get_followers, get_mutual_connections, get_recommendations, search_users, get_popular_users


def prompt(prompt_text: str) -> str:
    return input(prompt_text).strip()


def main():
    current_user = None
    while True:
        if current_user:
            print(f"\nLogged in as: {current_user['username']}")
        print("\nChoose: register | login | logout | view | edit | follow | unfollow | followers | following | mutual | recommend | search | popular | quit")
        cmd = prompt("> ")

        if cmd == "register":
            name = prompt("Name: ")
            email = prompt("Email: ")
            username = prompt("Username: ")
            password = prompt("Password: ")
            try:
                user = register(name, email, username, password)
                print("Registered:", user)
            except ValueError as e:
                print("Error:", e)

        elif cmd == "login":
            if current_user:
                print("Already logged in")
                continue
            username = prompt("Username: ")
            password = prompt("Password: ")
            user = login(username, password)
            if user:
                current_user = user
                print("Login successful.")
            else:
                print("Invalid credentials.")

        elif cmd == "logout":
            current_user = None
            print("Logged out.")

        elif cmd == "view":
            if not current_user:
                print("Please login first.")
                continue
            profile = get_profile(current_user["userId"])
            print("Profile:", profile)

        elif cmd == "edit":
            if not current_user:
                print("Please login first.")
                continue
            print("Leave blank to keep current value.")
            name = prompt("New name: ") or None
            email = prompt("New email: ") or None
            bio = prompt("New bio: ") or None
            updated = update_profile(current_user["userId"], name=name, email=email, bio=bio)
            print("Updated:", updated)
            current_user["username"] = updated["username"]
            current_user["name"] = updated["name"]
        elif cmd == "follow":
            if not current_user:
                print("Please login first.")
                continue
            target_id = prompt("Follow user (Enter username): ")
            if follow(current_user["userId"], target_id):
                print("Now following", target_id)
            else:
                print("Failed to follow. Check username.")
        elif cmd == "unfollow":
            if not current_user:
                print("Please login first.")
                continue
            target_id = prompt("Unfollow user (Enter username): ")
            if unfollow(current_user["userId"], target_id):
                print("Unfollowed", target_id)
            else:
                print("Failed to unfollow. Check username.")
    
        elif cmd == "search":
            search_text = prompt("Search by name or username: ")
            results = search_users(search_text)

            if not results:
                print("No users found.")
            else:
                print("\nSearch Results:")
                for user in results:
                    print(f"- {user['name']} (@{user['username']}) | Email: {user['email']}")

        elif cmd == "popular":
            users = get_popular_users()

            if not users:
                print("No users found.")
            else:
                print("\nPopular Users:")
                for user in users:
                    print(f"- {user['name']} (@{user['username']}) | Followers: {user['followerCount']}")
        elif cmd == "following":
            if not current_user:
                print("Please login first.")
                continue
            users = get_following(current_user["userId"])
            if users:
                print(f"You are following ({len(users)}):")
                for u in users:
                    print(f"  @{u['username']} — {u['name']}")
            else:
                print("You are not following anyone.")

        elif cmd == "followers":
            if not current_user:
                print("Please login first.")
                continue
            users = get_followers(current_user["userId"])
            if users:
                print(f"Your followers ({len(users)}):")
                for u in users:
                    print(f"  @{u['username']} — {u['name']}")
            else:
                print("You have no followers yet.")

        elif cmd == "mutual":
            if not current_user:
                print("Please login first.")
                continue
            target = prompt("Check mutual connections with (username): ")
            users = get_mutual_connections(current_user["userId"], target)
            if users:
                print(f"Mutual connections with @{target} ({len(users)}):")
                for u in users:
                    print(f"  @{u['username']} — {u['name']}")
            else:
                print(f"No mutual connections with @{target}.")

        elif cmd == "recommend":
            if not current_user:
                print("Please login first.")
                continue
            users = get_recommendations(current_user["userId"])
            if users:
                print("People you may want to follow:")
                for u in users:
                    print(f"  @{u['username']} — {u['name']} ({u['commonConnections']} common connection(s))")
            else:
                print("No recommendations available yet.")

        elif cmd == "quit":
            print("Bye")
            break

        else:
            print("Unknown command")


if __name__ == "__main__":
    main()