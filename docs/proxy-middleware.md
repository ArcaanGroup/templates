# Extensible Proxy/Middleware System

This project implements an extensible proxy/middleware system that allows adding custom request processing handlers while maintaining the internationalization functionality.

## Features

- **Internationalization**: Maintains locale detection and routing via `next-intl`
- **Extensible**: Easily add custom middleware handlers for authentication, logging, rate limiting, etc.
- **Proxy Capability**: Includes utilities to forward requests to external services
- **Chainable**: Multiple handlers can be registered and will be executed in order

## Usage

### Adding Custom Handlers

```typescript
import { addMiddlewareHandler } from './proxy';

const customHandler = async (request: NextRequest) => {
  // Your custom logic here
  if (someCondition) {
    return NextResponse.redirect(new URL('/somewhere', request.url));
  }
  
  // Return undefined to continue to the next handler
  return undefined;
};

addMiddlewareHandler(customHandler);
```

### Using Provided Helper Functions

The `lib/proxy-helpers.ts` file provides utility functions for common middleware tasks:

```typescript
import { registerExampleMiddlewareHandlers } from './lib/proxy-helpers';

// Register multiple example handlers at once
registerExampleMiddlewareHandlers();
```

### Creating a Proxy Handler

To forward requests to an external service:

```typescript
import { createProxyHandler, addMiddlewareHandler } from './lib/proxy-helpers';

// Create a proxy to forward /api/external/* requests to https://api.example.com/*
const externalApiProxy = createProxyHandler('https://api.example.com/', '/api/external');

addMiddlewareHandler(externalApiProxy);
```

## Architecture

The middleware system works as a chain of handlers:

1. Request comes in
2. Each registered handler gets a chance to process the request
3. If a handler returns a `NextResponse`, the chain stops and that response is returned
4. If a handler returns `undefined`, the chain continues to the next handler
5. Finally, the internationalization middleware processes the request

## Best Practices

- Always return `undefined` if you want the request to continue through the chain
- Return a `NextResponse` (redirect, rewrite, etc.) when you want to intercept the request
- Register handlers in the order you want them to execute
- Handle errors appropriately in your custom handlers