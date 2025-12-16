# Nextjs template

This is a comprehensive [Next.js](https://nextjs.org) application bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app). This project showcases modern web development practices with TypeScript, internationalization, authentication, and API client generation.

## Features

- **Next.js 16** with App Router
- **TypeScript** for type safety
- **Tailwind CSS** for styling
- **Internationalization (i18n)** support with RTL/LTR capabilities
- **Authentication & Authorization** with middleware protection
- **Orval** for API client generation from OpenAPI specs
- **Redux Toolkit** for client state management
- **TanStack Query** for server state management and caching
- **ESLint** for code quality
- **Geist Font** optimization with `next/font`
- **Modern Package Management** with pnpm
- **Proxy Configuration** for API requests
- **Theme Switching** with dark/light mode support

## Project Structure

```
nextjs-template/
├── app/                    # Next.js App Router pages and layouts
├── lib/                    # Shared utilities, components, and helpers
│   ├── auth/               # Authentication and authorization logic
│   ├── axios/              # Axios configuration and interceptors
│   ├── components/         # Reusable React components
│   ├── contexts/           # React context providers
│   ├── gen/                # Generated API clients and schemas (by Orval)
│   └── i18n/               # Internationalization configuration
├── messages/               # Localization message files
├── public/                 # Static assets
├── .docs/                  # Project documentation
├── .git/
├── .next/                  # Next.js build directory
├── next.config.ts          # Next.js configuration
├── tsconfig.json           # TypeScript configuration
├── eslint.config.mjs       # ESLint rules
├── orval.config.js         # API client generation config
├── proxy.ts                # Internationalized authentication middleware
├── package.json            # Dependencies and scripts
└── pnpm-lock.yaml          # Lock file
```

## Getting Started

### Prerequisites

- Node.js 18+ recommended
- pnpm package manager

### Installation

First, install the dependencies:

```bash
pnpm install
# or
npm install
# or
yarn install
```

### Development

Run the development server:

```bash
pnpm dev
# or
npm run dev
# or
yarn dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

### API Client Generation

This project uses Orval to generate typed API clients from OpenAPI specifications. To regenerate clients:

```bash
pnpm run orval
# or check package.json for the specific script
```

### Building for Production

Create a production build:

```bash
pnpm build
# or
npm run build
# or
yarn build
```

Serve the production build:

```bash
pnpm start
# or
npm run start
# or
yarn start
```

## Internationalization (i18n)

This project includes internationalization support with both English (en) and Persian (fa) locales. RTL (right-to-left) support is included for Persian. Configuration is located in the `lib/i18n/` directory, and translation files are stored in the `messages/` folder. The application uses `next-intl` for locale detection via URL routing.

## Authentication & Authorization

The application includes a comprehensive authentication system with:
- Custom middleware for authentication and authorization (`proxy.ts`)
- Context-based authentication management (`lib/contexts/auth-context`)
- Protected route components (`lib/components/Protected.tsx`)
- Login form with form validation (`lib/components/login-form/`)
- User profile display component (`lib/components/UserProfile.tsx`)

## Project Conventions

- Components follow PascalCase naming convention
- TypeScript is used throughout the application
- Tailwind CSS classes are used for styling
- Component composition is favored over inheritance
- Hooks are placed in the `lib/` directory or co-located with components
- Authentication state is managed through React Context
- API clients are auto-generated from OpenAPI specs using Orval

## Code Quality

- ESLint enforces code style and catches potential issues
- TypeScript provides static type checking
- Orval ensures API contracts are type-safe
- TanStack Query provides type-safe data fetching and caching
- Prettier ensures consistent code formatting

## Learn More

To learn more about the technologies used in this project, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial
- [TypeScript Documentation](https://www.typescriptlang.org/docs/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Orval Documentation](https://orval.dev/) - for API client generation

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deployment

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
