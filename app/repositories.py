from datetime import datetime, timezone

from bson import ObjectId


class MongoUserRepository:
    def __init__(self, collection):
        self.collection = collection

    def ensure_indexes(self):
        self.collection.create_index("email", unique=True)

    def find_by_email(self, email):
        return self.collection.find_one({"email": email})

    def create(self, user):
        now = datetime.now(timezone.utc)
        document = {
            "name": user["name"],
            "email": user["email"],
            "password_hash": user["password_hash"],
            "created_at": now,
            "last_login_at": None,
        }
        result = self.collection.insert_one(document)
        document["_id"] = result.inserted_id
        return document

    def mark_login(self, email):
        self.collection.update_one(
            {"email": email},
            {"$set": {"last_login_at": datetime.now(timezone.utc)}},
        )


class MongoProjectRepository:
    def __init__(self, collection):
        self.collection = collection

    def ensure_indexes(self):
        self.collection.create_index([("owner_email", 1), ("created_at", -1)])

    def list_for_user(self, owner_email):
        return list(
            self.collection.find({"owner_email": owner_email}).sort("created_at", -1)
        )

    def find_for_user(self, project_id, owner_email):
        object_id = self._object_id(project_id)
        if object_id is None:
            return None
        return self.collection.find_one({"_id": object_id, "owner_email": owner_email})

    def create(self, owner_email, project):
        now = datetime.now(timezone.utc)
        document = {
            **project,
            "owner_email": owner_email,
            "created_at": now,
            "updated_at": now,
        }
        result = self.collection.insert_one(document)
        document["_id"] = result.inserted_id
        return document

    def update(self, project_id, owner_email, project):
        object_id = self._object_id(project_id)
        if object_id is None:
            return False

        result = self.collection.update_one(
            {"_id": object_id, "owner_email": owner_email},
            {"$set": {**project, "updated_at": datetime.now(timezone.utc)}},
        )
        return result.matched_count == 1

    def delete(self, project_id, owner_email):
        object_id = self._object_id(project_id)
        if object_id is None:
            return False

        result = self.collection.delete_one({"_id": object_id, "owner_email": owner_email})
        return result.deleted_count == 1

    @staticmethod
    def _object_id(project_id):
        if not ObjectId.is_valid(project_id):
            return None
        return ObjectId(project_id)
