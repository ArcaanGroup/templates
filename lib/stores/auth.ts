import {
  getMeApiAuthMeGet,
  loginApiAuthLoginPost,
  logoutApiAuthLogoutPost,
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
}

export const useAuthStore = create<AuthStore>()(
  devtools(
    immer((set, get) => ({
      user: null,
      isPending: false,
      async login(credentials: UserLogin) {
        get()._setIsPending(true);
        try {
          await get()._getMe();
        } catch {
          await loginApiAuthLoginPost(credentials);
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
    })),
    { name: "zustand-store" },
  ),
);
