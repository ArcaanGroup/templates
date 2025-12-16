"use client";

import React, { Component, ErrorInfo, ReactNode } from "react";
import { useTranslations } from "next-intl";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

// Wrapper component to use the hook inside the class component
const ErrorBoundaryContent: React.FC<{ error?: Error }> = ({ error }) => {
  const t = useTranslations("common");

  return (
    <div className="p-6 text-center">
      <h2 className="text-xl font-bold text-red-600 mb-2">
        {t("somethingWentWrong")}
      </h2>
      <p className="text-gray-600">
        {error?.message || t("unexpectedErrorOccurred")}
      </p>
      <button
        className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        onClick={() => window.location.reload()}
      >
        {t("reloadPage")}
      </button>
    </div>
  );
};

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("Error caught by boundary:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return <ErrorBoundaryContent error={this.state.error} />;
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
