"""
Seed script for populating the database with initial data.

This script creates:
- One role 'Admin' with permission 'super:user'
- One user 'admin' with password 'Secret123' assigned to the Admin role
"""

import asyncio
import os
import sys
from typing import List

from app.application.use_cases.role_use_cases import RoleUseCase

# Add the project root to the path
sys.path.insert(0, os.path.abspath("."))

from fastapi_pagination import Params

from app.domain.entities import RoleEntity, UserEntity
from app.infrastructure.core.database import get_db_session
from app.infrastructure.repositories.permission_repository import (
    JSONPermissionRepository,
)
from app.infrastructure.repositories.role_repository import RoleRepository
from app.infrastructure.repositories.user_repository import UserRepository
from app.interface.repository.role_repository_interface import IRoleRepository
from app.interface.repository.user_repository_interface import IUserRepository


async def create_roles(role_repository: IRoleRepository):
    """Create initial roles in the database."""
    print("Creating roles...")

    roles_data = [{"name": "Admin"}]

    roles: List[RoleEntity] = []
    for role_data in roles_data:
        try:
            # Check if role already exists - get all roles and check if one exists with that name
            params = Params(page=1, size=100)  # Assuming we won't exceed 100 roles
            existing_roles_page = await role_repository.get_all(params)
            existing_role_names = [r.name for r in existing_roles_page.items]

            if role_data["name"] not in existing_role_names:
                # Create role domain directly instead of using DTO
                role_domain = RoleEntity.create(name=role_data["name"])
                role = await role_repository.create(role_domain)
                print(f"Created role: {role.name}")

                # Create permission repository and service to get the 'super:user' permission
                permission_repo = JSONPermissionRepository()

                # Get the 'super:user' permission
                super_user_permission = await permission_repo.get_by_title("super:user")
                if super_user_permission:
                    # Create role service to assign permission
                    role_service = RoleUseCase(role_repository, permission_repo)
                    await role_service.assign_permission_to_role(
                        role.id, super_user_permission.id
                    )
                    print(f"Assigned permission 'super:user' to role: {role.name}")
                else:
                    print("Warning: 'super:user' permission not found")

                roles.append(role)
            else:
                print(f"Role '{role_data['name']}' already exists")
        except Exception as e:
            print(f"Error creating role '{role_data['name']}': {e}")

    return roles


async def create_users(
    user_repository: IUserRepository, role_repository: IRoleRepository
):
    """Create sample users in the database."""
    print("Creating users...")

    users_data = [
        {
            "first_name": "Admin",
            "last_name": "User",
            "email": "admin@example.com",
            "username": "admin",
            "password": "Secret123",
        },
    ]

    users: List[UserEntity] = []
    for user_data in users_data:
        try:
            # Check if user already exists
            existing_user = await user_repository.get_by_email(user_data["email"])
            if existing_user is None:
                # Create user domain directly instead of using DTO
                user_domain = UserEntity.create(
                    first_name=user_data["first_name"],
                    last_name=user_data["last_name"],
                    email=user_data["email"],
                    username=user_data["username"],
                    password=user_data["password"],
                )
                user = await user_repository.create(user_domain)
                print(f"Created user: {user.username}")

                # Find the Admin role and assign it to the user
                params = Params(page=1, size=100)  # Assuming we won't exceed 100 roles
                roles_page = await role_repository.get_all(params)
                admin_role = next(
                    (r for r in roles_page.items if r.name == "Admin"), None
                )

                if admin_role:
                    # Assign admin role to the user
                    updated_user = await user_repository.assign_role(
                        user_id=user.id, role_id=admin_role.id
                    )
                    print(f"Assigned admin role to user: {updated_user.username}")

                # Activate the user
                user.activate()  # Set is_active to True and update timestamp
                activated_user = await user_repository.update(user)
                if activated_user is not None:
                    print(f"Activated user: {activated_user.username}")

                users.append(user)
            else:
                print(f"User with email '{user_data['email']}' already exists")
        except Exception as e:
            print(f"Error creating user '{user_data['username']}': {e}")

    return users


async def main():
    """Main function to run the seed script."""
    print("Starting database seeding...")

    try:
        # Get database session
        async for session in get_db_session():
            # Initialize repositories
            user_repo: IUserRepository = UserRepository(session)
            role_repo: IRoleRepository = RoleRepository(session)

            # Create roles
            await create_roles(role_repo)

            # Create users
            await create_users(user_repo, role_repo)

            print("Database seeding completed successfully!")
            break

    except Exception as e:
        print(f"Error during seeding: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
