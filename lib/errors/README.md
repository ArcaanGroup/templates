# Error Handling Utilities

This directory contains the standardized error handling system for the application.

## Files

- `AppError.ts`: Core error handling utilities including standardized error codes, type guards, and error transformation functions.

## Purpose

The error handling system provides:

1. **Standardization**: Consistent error codes and structures throughout the application
2. **Type Safety**: Proper TypeScript support for error handling
3. **Maintainability**: Centralized error handling logic that's easy to update
4. **User Experience**: Consistent error messages and handling patterns

## Usage

For documentation on how to use this error handling system, see [ERRORS.md](../.docs/ERRORS.md).

## Integration

This system integrates with:
- API clients and axios interceptors
- React components
- Server actions
- Authentication middleware
- Form validation