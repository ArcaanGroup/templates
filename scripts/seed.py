"""
Seed script for populating the database with initial data.

This script creates:
- Initial roles (Admin, User, Moderator)
- Sample users with different roles
- Assigns roles to users as needed
"""

import asyncio
import os
import sys
from typing import List

# Add the project root to the path
sys.path.insert(0, os.path.abspath("."))

from fastapi_pagination import Params

from app.core.database import get_db_session
from app.interface.repositories.role_repository_interface import IRoleRepository
from app.interface.repositories.user_repository_interface import IUserRepository
from app.models.role.domain import RoleDomain
from app.models.user.domain import UserDomain
from app.repository.role_repository import RoleRepository
from app.repository.user_repository import UserRepository


async def create_roles(role_repository: IRoleRepository):
    """Create initial roles in the database."""
    print("Creating roles...")

    roles_data = [{"name": "Admin"}, {"name": "User"}, {"name": "Moderator"}]

    roles: List[RoleDomain] = []
    for role_data in roles_data:
        try:
            # Check if role already exists - get all roles and check if one exists with that name
            params = Params(page=1, size=100)  # Assuming we won't exceed 100 roles
            existing_roles_page = await role_repository.get_all(params)
            existing_role_names = [r.name for r in existing_roles_page.items]

            if role_data["name"] not in existing_role_names:
                # Create role domain directly instead of using DTO
                role_domain = RoleDomain.create(name=role_data["name"])
                role = await role_repository.create(role_domain)
                print(f"Created role: {role.name}")
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
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "username": "johndoe",
            "password": "Password123",
        },
        {
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane.smith@example.com",
            "username": "janesmith",
            "password": "Password123",
        },
        {
            "first_name": "Bob",
            "last_name": "Johnson",
            "email": "bob.johnson@example.com",
            "username": "bobjohnson",
            "password": "Password123",
        },
        {
            "first_name": "Alice",
            "last_name": "Williams",
            "email": "alice.williams@example.com",
            "username": "alicewilliams",
            "password": "Password123",
        },
    ]

    users: List[UserDomain] = []
    for user_data in users_data:
        try:
            # Check if user already exists
            existing_user = await user_repository.get_by_email(user_data["email"])
            if existing_user is None:
                # Create user domain directly instead of using DTO
                user_domain = UserDomain.create(
                    first_name=user_data["first_name"],
                    last_name=user_data["last_name"],
                    email=user_data["email"],
                    username=user_data["username"],
                    password=user_data["password"],
                )
                user = await user_repository.create(user_domain)
                print(f"Created user: {user.username}")
                users.append(user)
            else:
                print(f"User with email '{user_data['email']}' already exists")
        except Exception as e:
            print(f"Error creating user '{user_data['username']}': {e}")

    return users


async def assign_roles_to_users(
    user_repository: IUserRepository, role_repository: IRoleRepository
):
    """Assign roles to users."""
    print("Assigning roles to users...")

    # Get all roles and users
    params = Params(page=1, size=100)  # Assuming we won't exceed 100 roles/users
    roles_page = await role_repository.get_all(params)
    users_page = await user_repository.get_all(params)

    roles = roles_page.items
    users = users_page.items

    # Find specific roles by name
    admin_role = next((r for r in roles if r.name == "Admin"), None)
    user_role = next((r for r in roles if r.name == "User"), None)
    mod_role = next((r for r in roles if r.name == "Moderator"), None)

    # Assign roles to specific users
    if admin_role and users:
        try:
            # Assign admin role to the first user
            updated_user = await user_repository.assign_role(
                user_id=users[0].id, role_id=admin_role.id
            )
            print(f"Assigned admin role to user: {updated_user.username}")
        except Exception as e:
            print(f"Error assigning admin role to user: {e}")

    if user_role and len(users) > 1:
        try:
            # Assign user role to the second user
            updated_user = await user_repository.assign_role(
                user_id=users[1].id, role_id=user_role.id
            )
            print(f"Assigned user role to user: {updated_user.username}")
        except Exception as e:
            print(f"Error assigning user role to user: {e}")

    if mod_role and len(users) > 2:
        try:
            # Assign moderator role to the third user
            updated_user = await user_repository.assign_role(
                user_id=users[2].id, role_id=mod_role.id
            )
            print(f"Assigned moderator role to user: {updated_user.username}")
        except Exception as e:
            print(f"Error assigning moderator role to user: {e}")

    # Assign user role to the last user as well
    if user_role and len(users) > 3:
        try:
            updated_user = await user_repository.assign_role(
                user_id=users[3].id, role_id=user_role.id
            )
            print(f"Assigned user role to user: {updated_user.username}")
        except Exception as e:
            print(f"Error assigning user role to user: {e}")

    # Make the first user (johndoe) active
    if users:
        try:
            # Get the first user (johndoe) and update their is_active status to True
            first_user = users[0]
            first_user.activate()  # Set is_active to True and update timestamp
            activated_user = await user_repository.update(first_user)
            if activated_user is not None:
                print(f"Activated user: {activated_user.username}")
            else:
                raise Exception()
        except Exception as e:
            print(f"Error activating user: {e}")


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

            # Assign roles to users
            await assign_roles_to_users(user_repo, role_repo)

            print("Database seeding completed successfully!")
            break

    except Exception as e:
        print(f"Error during seeding: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
