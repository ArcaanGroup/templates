"use client";

import { useTranslations } from "next-intl";
import { useForm } from "react-hook-form";
import useLoginForm from "./useLoginForm";

type FormData = {
  username: string;
  password: string;
};

export default function LoginForm() {
  const t = useTranslations("auth");
  const form = useForm<FormData>();

  const { onSubmit, isPending, isError } = useLoginForm();

  return (
    <div className="w-full max-w-md p-8 space-y-6 bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700">
      <h2 className="text-2xl font-bold text-center text-gray-800 dark:text-white mb-6">
        {t("login.title")}
      </h2>

      <form
        onSubmit={form.handleSubmit(onSubmit)}
        className="flex flex-col space-y-4"
      >
        {isError && (
          <div className="p-3 text-sm text-red-700 bg-red-100 rounded-lg dark:bg-red-900/30 dark:text-red-200">
            {isError}
          </div>
        )}

        <div>
          <label
            htmlFor="username"
            className="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300"
          >
            {t("login.usernameLabel")}:
          </label>
          <input
            type="text"
            id="username"
            dir="auto"
            className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:outline-none ${
              form.formState.errors.username
                ? "border-red-500 focus:ring-red-200 dark:focus:ring-red-800"
                : "border-gray-300 focus:border-blue-500 focus:ring-blue-200 dark:focus:ring-blue-800 dark:border-gray-600"
            } bg-white dark:bg-gray-700 dark:text-white`}
            {...form.register("username", {
              required: t("validation.username.required"),
              minLength: {
                value: 3,
                message: t("validation.username.minLength"),
              },
            })}
          />
          {form.formState.errors.username && (
            <span className="mt-1 text-xs text-red-600 dark:text-red-400">
              {form.formState.errors.username.message?.toString()}
            </span>
          )}
        </div>

        <div>
          <label
            htmlFor="password"
            className="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300"
          >
            {t("login.passwordLabel")}:
          </label>
          <input
            type="password"
            id="password"
            className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:outline-none ${
              form.formState.errors.password
                ? "border-red-500 focus:ring-red-200 dark:focus:ring-red-800"
                : "border-gray-300 focus:border-blue-500 focus:ring-blue-200 dark:focus:ring-blue-800 dark:border-gray-600"
            } bg-white dark:bg-gray-700 dark:text-white`}
            {...form.register("password", {
              required: t("validation.password.required"),
              minLength: {
                value: 6,
                message: t("validation.password.minLength"),
              },
            })}
          />
          {form.formState.errors.password && (
            <span className="mt-1 text-xs text-red-600 dark:text-red-400">
              {form.formState.errors.password.message?.toString()}
            </span>
          )}
        </div>

        <button
          type="submit"
          disabled={isPending}
          className="w-full py-3 px-4 bg-blue-600 hover:bg-blue-700 focus:ring-4 focus:outline-none focus:ring-blue-300 text-white font-medium rounded-lg transition duration-300 ease-in-out transform hover:scale-[1.02] disabled:opacity-70 disabled:cursor-not-allowed dark:bg-blue-700 dark:hover:bg-blue-800 dark:focus:ring-blue-900 flex items-center justify-center"
        >
          {isPending ? (
            <>
              <svg
                className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                ></circle>
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
              {t("login.loading")}
            </>
          ) : (
            t("login.submitButton")
          )}
        </button>
      </form>
    </div>
  );
}
