"use client";

import React, {
  createContext,
  useContext,
  useState,
  useCallback,
  useEffect,
} from "react";
import {
  getMeApiAuthMeGet,
  loginApiAuthLoginPost,
  logoutApiAuthLogoutPost,
  refreshTokensApiAuthRefreshPost,
} from "@/gen/hook";
import { User, UserLogin } from "@/gen/schema";
import { transformError, AppErrorCode } from "@/errors/AppError";

interface AuthContextType {
  user: User | null;
  isPending: boolean;
  login: (credentials: UserLogin) => Promise<void>;
  logout: () => Promise<void>;
  isAuthenticated: () => boolean;
  checkUserPermissions: (requiredPermissions: string[]) => boolean;
  _getUserPermissions: () => string[] | undefined;
  _getMe: () => Promise<void>;
  _setUser: (user: User) => void;
  _removeUser: () => void;
  _setIsPending: (to: boolean) => void;
  _refreshTokens: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{
  children: React.ReactNode;
  initialUser?: User;
}> = ({ children, initialUser }) => {
  const [user, setUser] = useState<User | null>(initialUser ?? null);
  const [isPending, setIsPending] = useState<boolean>(false);

  const _setUser = useCallback((user: User) => {
    setUser(user);
  }, []);

  const _removeUser = useCallback(() => {
    setUser(null);
  }, []);

  const _setIsPending = useCallback((to: boolean) => {
    setIsPending(to);
  }, []);

  const _getMe = useCallback(async () => {
    const me = await getMeApiAuthMeGet();
    _setUser(me.payload as User);
  }, [_setUser]);

  const login = useCallback(
    async (credentials: UserLogin) => {
      _setIsPending(true);
      try {
        // Check if user is already logged in by getting user info
        await _getMe();
      } catch {
        // If not logged in, perform login with credentials
        await loginApiAuthLoginPost(credentials);
        // Then get user info
        await _getMe();
      } finally {
        _setIsPending(false);
      }
    },
    [_getMe],
  );

  const logout = useCallback(async () => {
    await logoutApiAuthLogoutPost();
    _removeUser();
  }, [_removeUser]);

  const _refreshTokens = useCallback(async () => {
    try {
      // This will trigger the refresh mechanism in the axios interceptor
      await refreshTokensApiAuthRefreshPost();
      // Get updated user data after refresh
      await _getMe();
    } catch (error) {
      // If refresh fails, remove user from store
      _removeUser();
      // Transform and re-throw the error
      const appError = transformError(error, AppErrorCode.AUTH_REFRESH_FAILED);
      // Only throw the error, don't handle redirects here
      throw appError;
    }
  }, [_getMe, _removeUser]);

  const isAuthenticated = useCallback(() => {
    return !!user;
  }, [user]);

  const _getUserPermissions = useCallback(() => {
    return user?.roles
      ?.map((role) => role.permission_ids)
      .filter(Boolean)
      .flat() as string[] | undefined;
  }, [user]);

  const checkUserPermissions = useCallback(
    (requiredPermissions: string[]) => {
      const userPermissions = _getUserPermissions();
      return (
        requiredPermissions?.every((permId) =>
          userPermissions?.includes(permId),
        ) ?? false
      );
    },
    [user],
  );

  // Check if user is authenticated on initial load
  useEffect(() => {
    const checkAuthStatus = async () => {
      try {
        await _getMe();
      } catch (error) {
        // User is not authenticated, which is fine
      }
    };

    checkAuthStatus();
  }, [_getMe]);

  const value = {
    user,
    isPending,
    login,
    logout,
    isAuthenticated,
    checkUserPermissions,
    _getUserPermissions,
    _getMe,
    _setUser,
    _removeUser,
    _setIsPending,
    _refreshTokens,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
