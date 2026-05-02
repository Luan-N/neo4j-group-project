import gzip, csv

users = set()
edges = []

with gzip.open("gplus_combined.txt.gz", "rt") as f:
    for line in f:
        a, b = line.strip().split()
        users.add(a)
        users.add(b)
        edges.append((a, b))
        if len(edges) >= 10000:
            break

# users.csv
with open("users.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["userId", "name", "username", "email", "bio", "password"])
    for uid in users:
        w.writerow([uid, f"User_{uid}", f"user_{uid}", f"{uid}@example.com", f"Bio for user_{uid}", "password"])

# follows.csv
with open("follows.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["followerId", "followedId"])
    for a, b in edges:
        w.writerow([a, b])