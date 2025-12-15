import { User } from "@/lib/gen/schema";
import React, { useCallback } from "react";
import { useAuth } from "@/lib/contexts/auth-context";
import { useTranslations } from "next-intl";

interface UserProfileProps {
  user: User;
}

const UserProfile: React.FC<UserProfileProps> = ({ user }) => {
  const { logout } = useAuth();
  const t = useTranslations("UserProfile");

  const handleLogout = useCallback(async () => {
    try {
      await logout();
    } catch (error) {
      console.error("Logout failed:", error);
      // Optionally show an error message to the user
    }
  }, [logout]);

  return (
    <div className="bg-white rounded-lg shadow-md p-6 max-w-md w-full">
      <div className="flex items-center space-x-4 mb-4">
        {/* Placeholder for user avatar */}
        <div className="bg-gray-200 border-2 border-dashed rounded-xl w-16 h-16" />
        <div>
          <h2 className="text-xl font-bold text-gray-800">
            {user.first_name} {user.last_name}
          </h2>
          <p className="text-gray-600">@{user.username}</p>
        </div>
      </div>

      <div className="space-y-3">
        <div>
          <label className="text-sm font-medium text-gray-500">
            {t("email")}
          </label>
          <p className="text-gray-800">{user.email}</p>
        </div>

        <div>
          <label className="text-sm font-medium text-gray-500">
            {t("userId")}
          </label>
          <p className="text-gray-800">{user.id}</p>
        </div>

        <div>
          <label className="text-sm font-medium text-gray-500">
            {t("status")}:{" "}
          </label>
          <span
            className={`px-2 py-1 rounded-full text-xs font-medium ${
              user.is_active
                ? "bg-green-100 text-green-800"
                : "bg-red-100 text-red-800"
            }`}
          >
            {user.is_active ? t("active") : t("inactive")}
          </span>
        </div>

        <div>
          <label className="text-sm font-medium text-gray-500">
            {t("roles")}:
          </label>
          <div className="flex flex-wrap gap-2 mt-1">
            {user.roles && user.roles.length > 0 ? (
              user.roles.map((role, index) => (
                <span
                  key={index}
                  className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs"
                >
                  {role.name}
                </span>
              ))
            ) : (
              <span className="text-gray-500 italic">
                {t("noRolesAssigned")}
              </span>
            )}
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4 pt-4 border-t border-gray-200">
          <div>
            <label className="text-sm font-medium text-gray-500">
              {t("created")}
            </label>
            <p className="text-gray-800 text-sm">
              {new Date(user.created_at).toLocaleDateString()}
            </p>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-500">
              {t("updated")}
            </label>
            <p className="text-gray-800 text-sm">
              {new Date(user.updated_at).toLocaleDateString()}
            </p>
          </div>
        </div>

        <div className="pt-4 border-t border-gray-200">
          <button
            onClick={handleLogout}
            className="w-full bg-red-500 hover:bg-red-600 text-white font-medium py-2 px-4 rounded-md transition duration-200"
          >
            {t("logoutButton")}
          </button>
        </div>
      </div>
    </div>
  );
};

export default UserProfile;
