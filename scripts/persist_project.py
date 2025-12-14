# export_project.py
import sys

from server.lib.ExampleProjManager import persist_projects

"""
A script to export project from the database into JSON files.
The projects will be saved in server/assets/examples directory.
"""

if __name__ == "__main__":
    if len(sys.argv) not in [2, 3]:
        print("Usage: python persist_project.py <project_name> [new_name]")
        sys.exit(1)
    project_name = sys.argv[1]
    new_name = sys.argv[2] if len(sys.argv) == 3 else None
    persist_projects(project_name, new_name)
