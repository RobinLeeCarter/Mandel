import os


def find_project_dir():
    file_path = os.path.abspath(__file__)
    file_dir = os.path.dirname(file_path)
    parent_path = os.path.dirname(file_dir)
    return parent_path + r"/"


# file_path = os.path.abspath(__file__)
PROJECT_DIR = find_project_dir()


def full_path(project_path: str):
    return PROJECT_DIR + project_path
