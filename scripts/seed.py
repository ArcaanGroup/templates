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

from fastapi_pagination import Params

# Add the project root to the path BEFORE importing from app
sys.path.insert(0, os.path.abspath("."))

from app.application.use_cases.role import (
    AssignPermissionRequest,
    AssignPermissionToRoleUseCase,
    CreateRoleRequest,
    CreateRoleUseCase,
)
from app.application.use_cases.user import (
    AssignRoleRequest,
    AssignRoleToUserUseCase,
    CreateUserRequest,
    CreateUserUseCase,
)
from app.domain.entities import RoleEntity, UserEntity
from app.infra.repositories.json.permission_repository import (
    JSONPermissionRepository,
)
from app.infra.repositories.in_memory.role_repository import InMemoryRoleRepository
from app.infra.repositories.in_memory.user_repository import InMemoryUserRepository
from app.interface.repository.role_repository_interface import IRoleRepository
from app.interface.repository.user_repository_interface import IUserRepository


async def create_roles(
    role_repository: IRoleRepository,
    permission_repository: JSONPermissionRepository,
):
    """Create initial roles in the database."""
    print("Creating roles...")

    roles_data = [{"name": "Admin"}]

    roles: List[RoleEntity] = []
    for role_data in roles_data:
        try:
            # Check if role already exists
            existing_roles = await role_repository.get_all(Params(page=1, size=100))
            existing_role_names = [r.name for r in existing_roles]

            if role_data["name"] not in existing_role_names:
                # Create role using use case
                create_role_usecase = CreateRoleUseCase(
                    role_repository, permission_repository
                )
                result = await create_role_usecase.execute(
                    CreateRoleRequest(name=role_data["name"])
                )
                role = result.role
                print(f"Created role: {role.name}")

                # Get the 'super:user' permission
                super_user_permission = await permission_repository.get_by_title(
                    "super:user"
                )
                if super_user_permission:
                    # Assign permission to role using use case
                    assign_perm_usecase = AssignPermissionToRoleUseCase(
                        role_repository, permission_repository
                    )
                    await assign_perm_usecase.execute(
                        AssignPermissionRequest(
                            role_id=role.id,
                            permission_id=super_user_permission.id,
                        )
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
                # Create user using use case
                create_user_usecase = CreateUserUseCase(user_repository)
                result = await create_user_usecase.execute(
                    CreateUserRequest(
                        first_name=user_data["first_name"],
                        last_name=user_data["last_name"],
                        email=user_data["email"],
                        username=user_data["username"],
                        password=user_data["password"],
                    )
                )
                user = result.user
                print(f"Created user: {user.username}")

                # Find the Admin role and assign it to the user
                existing_roles = await role_repository.get_all(Params(page=1, size=100))
                admin_role = next(
                    (r for r in existing_roles if r.name == "Admin"), None
                )

                if admin_role:
                    # Assign admin role to the user using use case
                    assign_role_usecase = AssignRoleToUserUseCase(
                        user_repository, role_repository
                    )
                    await assign_role_usecase.execute(
                        AssignRoleRequest(user_id=user.id, role_id=admin_role.id)
                    )
                    print(f"Assigned admin role to user: {user.username}")

                # Activate the user
                user.activate()  # Set is_active to True and update timestamp
                updated_user = await user_repository.update(user)
                if updated_user is not None:
                    print(f"Activated user: {updated_user.username}")

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
        # Initialize repositories
        user_repo: IUserRepository = InMemoryUserRepository()
        role_repo: IRoleRepository = InMemoryRoleRepository()
        perm_repo: JSONPermissionRepository = JSONPermissionRepository()

        # Create roles
        await create_roles(role_repo, perm_repo)

        # Create users
        await create_users(user_repo, role_repo)

        print("Database seeding completed successfully!")

    except Exception as e:
        print(f"Error during seeding: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
