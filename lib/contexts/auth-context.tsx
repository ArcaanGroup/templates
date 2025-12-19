"use client";

import {
  AppErrorCode,
  newAppError,
  isAppError,
  isAxiosError,
} from "@/errors/AppError";
import { getFastAPIServer } from "@/gen/api";
import { User, UserLogin } from "@/gen/schema";
import { Key } from "@/utils/key.enum";
import Cookies from "js-cookie";
import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

interface AuthContextType {
  user: User | null;
  isPending: boolean;
  login: (credentials: UserLogin) => Promise<void>;
  logout: () => Promise<void>;
  isAuthenticated: () => boolean;
  checkUserPermissions: (requiredPermissions: string[]) => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{
  children: React.ReactNode;
  initialUser?: User;
}> = ({ children, initialUser }) => {
  const [user, setUser] = useState<User | null>(initialUser ?? null);
  const [isPending, setIsPending] = useState<boolean>(false);
  const api = useMemo(() => getFastAPIServer(), []);

  const _setUser = useCallback((user: User) => {
    setUser(user);
  }, []);

  const _removeTokens = useCallback(() => {
    Cookies.remove(Key.AccessToken);
  }, []);

  const _removeUser = useCallback(() => {
    setUser(null);
  }, []);

  const _setIsPending = useCallback((to: boolean) => {
    setIsPending(to);
  }, []);

  const _setTokens = useCallback(async (accessToken: string) => {
    Cookies.set(Key.AccessToken, accessToken);
  }, []);

  const _getMe = useCallback(async () => {
    let me;
    try {
      me = await api.getMeApiAuthMeGet();
      if (!me.success) {
        throw newAppError(AppErrorCode.AUTH_UNAUTHORIZED, "Not authenticated.");
      }
    } catch (err) {
      console.error("failed to get user info:", err);
      if (
        (isAxiosError(err) && err.response?.status === 401) ||
        (isAppError(err) && err.code === AppErrorCode.AUTH_UNAUTHORIZED)
      ) {
        _removeUser();
        throw newAppError(AppErrorCode.AUTH_UNAUTHORIZED, "Not authenticated");
      }
    }
    if (me) {
      _setUser(me.payload as User);
    } else {
      throw newAppError(AppErrorCode.AUTH_UNAUTHORIZED, "Failed to get me.");
    }
  }, [_removeUser, _setUser, api]);

  const login = useCallback(
    async (credentials: UserLogin) => {
      _setIsPending(true);
      try {
        // Check if user is already logged in by getting user info
        await _getMe();
      } catch (err) {
        console.error("failed to get me:", err);
        if (isAppError(err) && err.code === AppErrorCode.AUTH_UNAUTHORIZED) {
          try {
            // If not logged in, perform login with credentials
            const res = await api.loginApiAuthLoginPost(credentials);
            if (!res.success || !res.payload?.token)
              throw newAppError(AppErrorCode.AUTH_LOGIN_FAILED, "Login failed");

            _setTokens(res.payload.token);

            // Then get user info
            await _getMe();
          } catch (err) {
            console.error("failed to login with credentials:", err);
            throw newAppError(AppErrorCode.AUTH_LOGIN_FAILED, "Login failed");
          }
        }
      } finally {
        _setIsPending(false);
      }
    },
    [_setIsPending, _getMe, api, _setTokens],
  );

  const logout = useCallback(async () => {
    await api.logoutApiAuthLogoutPost();
    _removeTokens();
    _removeUser();
  }, [_removeTokens, _removeUser, api]);

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
    [_getUserPermissions],
  );

  // Check if user is authenticated on initial load
  useEffect(() => {
    const checkAuthStatus = async () => {
      if (!user) {
        try {
          await _getMe();
        } catch (err) {
          console.error("failed to get initial user info:", err);
          // User is not authenticated, which is fine
        }
      }
    };

    checkAuthStatus();
  }, [_getMe, user]);

  const value = {
    user,
    isPending,
    login,
    logout,
    isAuthenticated,
    checkUserPermissions,
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
