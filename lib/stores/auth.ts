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
  login: (credentials: UserLogin) => Promise<User>;
  logout: () => Promise<void>;
  _getMe: () => Promise<User>;
  _setUser: (user: User) => void;
  _removeUser: () => void;
}

export const useAuthStore = create<AuthStore>()(
  devtools(
    immer((set, get) => ({
      user: null,
      async login(credentials: UserLogin) {
        await loginApiAuthLoginPost(credentials);
        const me = await get()._getMe();
        get()._setUser(me);
        return get().user as User;
      },
      async logout() {
        await logoutApiAuthLogoutPost();
        get()._removeUser();
      },
      async _getMe() {
        const me = await getMeApiAuthMeGet();
        set((state) => {
          state.user = me.payload as User;
        });
        return me.payload as User;
      },
      _setUser: (user) =>
        set((state) => {
          state.user = user;
        }),
      _removeUser: () =>
        set((state) => {
          state.user = null;
        }),
    })),
    { name: "zustand-store" },
  ),
);
