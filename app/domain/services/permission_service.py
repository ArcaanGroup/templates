"""Permission service to handle permissions data"""
import json
import os
from typing import List
import uuid

from app.application.dto.permission_dto import PermissionDTO


class PermissionService:
    """Service for handling permissions data"""

    @staticmethod
    def get_permissions() -> List[PermissionDTO]:
        """Get all permissions from the permissions.json file"""
        try:
            # Get the path to the permissions.json file
            permissions_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "permissions.json")

            with open(permissions_path, "r") as file:
                permissions_data = json.load(file)

            permissions = []
            for perm_data in permissions_data:
                permission = PermissionDTO(
                    id=uuid.UUID(perm_data["id"]),
                    title=perm_data["title"],
                    description=perm_data["description"],
                    policies=perm_data["policies"]
                )
                permissions.append(permission)

            return permissions
        except FileNotFoundError:
            # If the file doesn't exist, return an empty list
            return []
        except Exception:
            # If there's any error reading the file, return an empty list
            return []
