import {
  getMeApiAuthMeGet,
  loginApiAuthLoginPost,
  logoutApiAuthLogoutPost,
  refreshTokensApiAuthRefreshPost,
} from "@/lib/gen/hook";
import { User, UserLogin } from "@/lib/gen/schema";
import { create } from "zustand";
import { devtools } from "zustand/middleware";
import { immer } from "zustand/middleware/immer";

interface AuthStore {
  user: User | null;
  isPending: boolean; // Indicates that the login/logout operation is in progress
  login: (credentials: UserLogin) => Promise<void>;
  logout: () => Promise<void>;
  _getMe: () => Promise<void>;
  _setUser: (user: User) => void;
  _removeUser: () => void;
  _setIsPending: (to: boolean) => void;
  _refreshTokens: () => Promise<void>;
  isAuthenticated: () => boolean;
}

export const useAuthStore = create<AuthStore>()(
  devtools(
    immer((set, get) => ({
      user: null,
      isPending: false,
      async login(credentials: UserLogin) {
        get()._setIsPending(true);
        try {
          // Check if user is already logged in by getting user info
          await get()._getMe();
        } catch {
          // If not logged in, perform login with credentials
          await loginApiAuthLoginPost(credentials);
          // Then get user info
          await get()._getMe();
        } finally {
          get()._setIsPending(false);
        }
      },
      async logout() {
        await logoutApiAuthLogoutPost();
        get()._removeUser();
      },
      async _getMe() {
        const me = await getMeApiAuthMeGet();
        get()._setUser(me.payload as User);
      },
      _setUser: (user) =>
        set((state) => {
          state.user = user;
        }),
      _removeUser: () =>
        set((state) => {
          state.user = null;
        }),
      _setIsPending(to: boolean) {
        set((state) => {
          state.isPending = to;
        });
      },
      async _refreshTokens() {
        try {
          // This will trigger the refresh mechanism in the axios interceptor
          await refreshTokensApiAuthRefreshPost();
          // Get updated user data after refresh
          await get()._getMe();
        } catch (error) {
          // If refresh fails, remove user from store
          get()._removeUser();
          throw error;
        }
      },
      isAuthenticated() {
        return !!get().user;
      },
    })),
    { name: "zustand-store" },
  ),
);
