# Plasma Physics Frontend - React Application

Modern React frontend for the Plasma Physics Literature Search system. Built with TypeScript, Vite, TailwindCSS, and React Query.

## 🚀 Features

- **Modern Stack**: React 18, TypeScript, Vite
- **Responsive Design**: TailwindCSS with mobile-first approach
- **Data Fetching**: React Query for caching and state management
- **Routing**: React Router v6 for navigation
- **Type Safety**: Full TypeScript coverage
- **Charts**: Recharts for data visualization
- **Fast Development**: Vite HMR for instant updates

## 📋 Prerequisites

- Node.js >= 18.0.0
- npm >= 9.0.0
- Backend API running on http://localhost:8000

## 🛠️ Installation

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
```

## 🏃 Development

```bash
# Start development server
npm run dev

# Open browser to http://localhost:3000
```

The development server includes:
- Hot Module Replacement (HMR)
- Proxy to backend API at `/api`
- TypeScript checking
- Fast refresh

## 🏗️ Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

## 🧪 Testing

```bash
# Run tests
npm test

# Run tests with UI
npm run test:ui

# Run tests with coverage
npm run test:coverage
```

## 📁 Project Structure

```
frontend/
├── public/                 # Static assets
├── src/
│   ├── components/         # Reusable React components
│   │   └── Layout.tsx      # Main layout component
│   ├── pages/              # Page components
│   │   ├── HomePage.tsx    # Dashboard/home page
│   │   ├── PapersPage.tsx  # Papers list
│   │   ├── PaperDetailPage.tsx
│   │   ├── TemperaturesPage.tsx
│   │   ├── DensitiesPage.tsx
│   │   └── StatisticsPage.tsx
│   ├── lib/                # Utilities and libraries
│   │   └── api.ts          # API client
│   ├── App.tsx             # Main app component
│   ├── main.tsx            # Entry point
│   └── index.css           # Global styles
├── index.html              # HTML template
├── package.json            # Dependencies
├── tsconfig.json           # TypeScript config
├── vite.config.ts          # Vite config
├── tailwind.config.js      # TailwindCSS config
└── README.md               # This file
```

## 🎨 UI Components

### Layout
- Responsive header with navigation
- Main content area
- Footer

### Pages
1. **Home Page** - Dashboard with statistics cards and quick actions
2. **Papers Page** - Searchable list of papers with pagination
3. **Paper Detail** - Full paper details with measurements
4. **Temperatures Page** - Filter and view temperature measurements
5. **Densities Page** - Filter and view density measurements
6. **Statistics Page** - Charts and visualizations

## 🔌 API Integration

The frontend connects to the FastAPI backend using axios:

```typescript
import { ApiService } from './lib/api';

// Get papers
const papers = await ApiService.getPapers(limit, offset);

// Search papers
const results = await ApiService.searchPapers('tokamak');

// Filter temperatures
const temps = await ApiService.getTemperatures(minTemp, maxTemp);

// Get statistics
const stats = await ApiService.getStatistics();
```

## 🎯 Key Features

### React Query Integration
- Automatic caching (5-minute stale time)
- Background refetching
- Optimistic updates
- Error handling

### Type Safety
- Full TypeScript coverage
- API response types
- Component props validation
- Build-time type checking

### Responsive Design
- Mobile-first approach
- TailwindCSS utilities
- Responsive grid layouts
- Touch-friendly interactions

### Performance
- Code splitting by route
- Lazy loading
- Optimized bundle size
- Fast refresh in development

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the frontend directory:

```bash
VITE_API_URL=http://localhost:8000
```

### Vite Configuration

The Vite config includes:
- API proxy to avoid CORS issues
- Path aliases (`@/` for `src/`)
- React plugin with Fast Refresh

### TailwindCSS

Customized theme with:
- Primary color palette
- Custom components (buttons, cards, inputs)
- Utility classes

## 📦 Dependencies

### Core
- react: ^18.2.0
- react-dom: ^18.2.0
- react-router-dom: ^6.21.0

### Data Fetching
- @tanstack/react-query: ^5.17.9
- axios: ^1.6.5

### UI & Styling
- tailwindcss: ^3.4.1
- recharts: ^2.10.3
- clsx: ^2.1.0

### Development
- vite: ^5.0.11
- typescript: ^5.3.3
- @vitejs/plugin-react: ^4.2.1
- vitest: ^1.2.0

## 🚀 Deployment

### Build for Production

```bash
npm run build
```

This creates an optimized build in the `dist/` directory.

### Deploy to Static Hosting

The built application can be deployed to:
- Vercel
- Netlify
- GitHub Pages
- AWS S3 + CloudFront
- Any static file server

### Example: Vercel

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
cd dist
vercel --prod
```

### Docker Deployment

```dockerfile
# Build stage
FROM node:18-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## 🎨 Customization

### Colors

Edit `tailwind.config.js` to change the color scheme:

```javascript
theme: {
  extend: {
    colors: {
      primary: {
        // Your custom colors
      },
    },
  },
}
```

### Components

All components are in `src/components/`. Create new components:

```typescript
// src/components/MyComponent.tsx
export default function MyComponent() {
  return <div>My Component</div>;
}
```

## 🐛 Troubleshooting

### API Connection Issues

**Problem**: Cannot connect to backend API

**Solution**:
```bash
# Check backend is running
curl http://localhost:8000/health

# Check proxy configuration in vite.config.ts
# Ensure VITE_API_URL is correct
```

### Build Errors

**Problem**: TypeScript errors during build

**Solution**:
```bash
# Check TypeScript errors
npx tsc --noEmit

# Fix type errors in your code
```

### Styling Issues

**Problem**: Tailwind classes not working

**Solution**:
```bash
# Rebuild CSS
npm run dev

# Check tailwind.config.js content paths
```

## 📚 Learn More

- [React Documentation](https://react.dev/)
- [Vite Guide](https://vitejs.dev/guide/)
- [TailwindCSS](https://tailwindcss.com/docs)
- [React Query](https://tanstack.com/query/latest)
- [React Router](https://reactrouter.com/)

## 🤝 Contributing

1. Follow TypeScript best practices
2. Use TailwindCSS for styling
3. Write tests for new components
4. Use React Query for data fetching
5. Follow the existing component structure

## 📝 License

MIT

## 🔗 Related

- [Backend API Documentation](../backend/README.md)
- [Phase 4 Documentation](../PHASE4_COMPLETE.md)
- [Main README](../README.md)
