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
} from "@/lib/gen/hook";
import { User, UserLogin } from "@/lib/gen/schema";

interface AuthContextType {
  user: User | null;
  isPending: boolean;
  login: (credentials: UserLogin) => Promise<void>;
  logout: () => Promise<void>;
  _getMe: () => Promise<void>;
  _setUser: (user: User) => void;
  _removeUser: () => void;
  _setIsPending: (to: boolean) => void;
  _refreshTokens: () => Promise<void>;
  isAuthenticated: () => boolean;
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

  const login = useCallback(async (credentials: UserLogin) => {
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
  }, []);

  const logout = useCallback(async () => {
    await logoutApiAuthLogoutPost();
    _removeUser();
  }, [_removeUser]);

  const _getMe = useCallback(async () => {
    const me = await getMeApiAuthMeGet();
    _setUser(me.payload as User);
  }, [_setUser]);

  const _refreshTokens = useCallback(async () => {
    try {
      // This will trigger the refresh mechanism in the axios interceptor
      await refreshTokensApiAuthRefreshPost();
      // Get updated user data after refresh
      await _getMe();
    } catch (error) {
      // If refresh fails, remove user from store
      _removeUser();
      throw error;
    }
  }, [_getMe, _removeUser]);

  const isAuthenticated = useCallback(() => {
    return !!user;
  }, [user]);

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
    _getMe,
    _setUser,
    _removeUser,
    _setIsPending,
    _refreshTokens,
    isAuthenticated,
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
