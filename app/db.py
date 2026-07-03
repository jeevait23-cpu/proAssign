from pymongo import MongoClient

from .repositories import MongoProjectRepository, MongoUserRepository


def create_user_repository(config):
    client = MongoClient(config["MONGO_URI"])
    database = client[config["MONGO_DB"]]
    repository = MongoUserRepository(database.users)
    repository.ensure_indexes()
    return repository


def create_project_repository(config):
    client = MongoClient(config["MONGO_URI"])
    database = client[config["MONGO_DB"]]
    repository = MongoProjectRepository(database.projects)
    repository.ensure_indexes()
    return repository
