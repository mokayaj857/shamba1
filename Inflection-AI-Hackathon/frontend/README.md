# 🌾 Agri-Adapt AI Frontend

> **Next.js 15 + React 18 + TypeScript Frontend for Agricultural AI Platform**

## 🚀 Quick Start

### Prerequisites
- Node.js 16+ 
- npm, yarn, or pnpm

### Installation
```bash
# Install dependencies
npm install
# or
yarn install
# or
pnpm install
```

### Development
```bash
# Start development server
npm run dev
# or
yarn dev
# or
pnpm dev
```

The frontend will run on `http://localhost:3000`

### Production Build
```bash
# Build for production
npm run build

# Start production server
npm start
```

## 🏗️ Project Structure

```
frontend/
├── 📁 app/                    # Next.js 15 App Router
│   ├── page.tsx              # Main dashboard page
│   ├── layout.tsx            # Root layout with providers
│   ├── loading.tsx           # Loading component
│   └── globals.css           # Global Tailwind CSS styles
├── 📁 components/             # React components
│   ├── ui/                   # Reusable UI components (Radix UI)
│   │   ├── button.tsx        # Button component
│   │   ├── card.tsx          # Card component
│   │   ├── input.tsx         # Input field component
│   │   └── ...               # Other UI components
│   ├── resilience-gauge.tsx  # Drought resilience score gauge
│   ├── recommendations-panel.tsx # Farming recommendations
│   ├── data-visualization.tsx    # Charts and data display
│   ├── weather-integration.tsx   # Weather data integration
│   ├── crop-recommendation-engine.tsx # Crop suggestions
│   ├── input-cost-calculator.tsx # Cost analysis tool
│   └── theme-provider.tsx    # Dark/light theme provider
├── 📁 lib/                    # Utility libraries
│   └── utils.ts              # Helper functions
├── 📁 public/                 # Static assets
│   ├── placeholder-logo.png  # Logo placeholder
│   ├── placeholder-logo.svg  # SVG logo
│   └── ...                   # Other static files
├── 📁 styles/                 # Additional styles
│   └── globals.css           # Global CSS (legacy)
├── package.json               # Dependencies and scripts
├── tsconfig.json              # TypeScript configuration
├── next.config.mjs            # Next.js configuration
├── postcss.config.mjs         # PostCSS configuration
└── components.json            # UI components configuration
```

## 🎨 Key Features

### 🌱 Agricultural Dashboard
- **County Selection**: Interactive dropdown with 47 Kenyan counties
- **Resilience Scoring**: Visual gauge showing drought resilience (0-100%)
- **Data Visualization**: Interactive charts for weather and yield data
- **Recommendations**: AI-powered farming advice based on scores
- **Weather Integration**: Real-time weather data for selected counties

### 🎯 Technical Features
- **Mobile-First Design**: Responsive layout optimized for smartphones
- **Accessibility**: WCAG 2.1 compliant with Radix UI components
- **Performance**: Optimized with Next.js 15 and React 18
- **Type Safety**: Full TypeScript implementation
- **Modern Styling**: Tailwind CSS 4 with custom components

## 🔧 Technology Stack

### Core Framework
- **Next.js 15**: React framework with App Router
- **React 18**: Latest React with concurrent features
- **TypeScript 5**: Type-safe JavaScript

### UI & Styling
- **Tailwind CSS 4**: Utility-first CSS framework
- **Radix UI**: Accessible component primitives
- **Lucide React**: Beautiful icon library
- **Class Variance Authority**: Component variant management

### Data & Forms
- **React Hook Form**: Performant form handling
- **Zod**: TypeScript-first schema validation
- **Recharts**: Composable charting library

### Development Tools
- **ESLint**: Code linting
- **PostCSS**: CSS processing
- **Autoprefixer**: CSS vendor prefixing

## 🔌 API Integration

The frontend connects to the FastAPI backend running on `http://localhost:8000`:

### Key Endpoints
- `GET /api/counties` - List of Kenya counties
- `POST /api/predict` - Single prediction request
- `POST /api/predict/batch` - Batch predictions
- `GET /api/model/status` - Model performance info
- `GET /api/metrics` - Usage statistics

### Example API Call
```typescript
const predictResilience = async (data: PredictionRequest) => {
  const response = await fetch('http://localhost:8000/api/predict', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  
  return response.json();
};
```

## 🎨 Component Architecture

### Core Components
1. **ResilienceGauge**: Circular progress indicator for resilience scores
2. **RecommendationsPanel**: Farming advice and best practices
3. **DataVisualization**: Interactive charts and graphs
4. **WeatherIntegration**: Real-time weather data display
5. **CropRecommendationEngine**: AI-powered crop suggestions
6. **InputCostCalculator**: Financial analysis tool

### UI Components
- **Button**: Primary, secondary, and ghost button variants
- **Card**: Content containers with headers and actions
- **Input**: Form input fields with validation
- **Select**: Dropdown selection components
- **Tabs**: Tabbed interface for content organization

## 🚀 Development Workflow

### Adding New Components
1. Create component file in `components/` directory
2. Use TypeScript interfaces for props
3. Implement with Radix UI primitives
4. Style with Tailwind CSS classes
5. Add to main dashboard page

### Styling Guidelines
- Use Tailwind CSS utility classes
- Follow mobile-first responsive design
- Maintain consistent spacing and typography
- Ensure accessibility compliance

### State Management
- Use React hooks for local state
- Context API for theme and global state
- React Hook Form for form state
- Optimistic updates for better UX

## 🧪 Testing

### Running Tests
```bash
# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run specific test file
npm test -- components/resilience-gauge.test.tsx
```

### Testing Strategy
- Unit tests for individual components
- Integration tests for component interactions
- E2E tests for critical user flows
- Accessibility testing with axe-core

## 📱 Mobile Optimization

### Responsive Design
- **Mobile First**: Designed for 320px+ screens
- **Touch Friendly**: Large touch targets and gestures
- **Offline Ready**: Service worker for offline functionality
- **Performance**: Optimized bundle size and loading

### Progressive Web App
- Installable on mobile devices
- Offline functionality
- Push notifications (future)
- App-like experience

## 🌐 Internationalization

### Language Support
- English (primary)
- Swahili (planned)
- Local dialects (future)

### Cultural Considerations
- Kenyan farming practices
- Local crop varieties
- Traditional knowledge integration
- Community feedback loops

## 🚀 Deployment

### Vercel (Recommended)
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

### Other Platforms
- **Netlify**: Static site hosting
- **AWS Amplify**: Full-stack hosting
- **Docker**: Containerized deployment
- **Self-hosted**: Custom server setup

## 🔒 Security

### Best Practices
- Input validation with Zod
- XSS protection
- CSRF protection
- Secure API communication
- Environment variable management

### Privacy
- No personal data collection
- Anonymous usage analytics
- GDPR compliance ready
- Data encryption in transit

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create feature branch
3. Install dependencies
4. Make changes
5. Run tests
6. Submit pull request

### Code Standards
- TypeScript strict mode
- ESLint configuration
- Prettier formatting
- Conventional commits
- Component documentation

---

## 📞 Support

- **Documentation**: [API Docs](http://localhost:8000/docs)
- **Issues**: [GitHub Issues](https://github.com/your-username/agri-adapt-ai/issues)
- **Frontend Team**: frontend@agri-adapt-ai.com

---

**Built with ❤️ for sustainable agriculture in Kenya**

*Frontend powered by Next.js 15, React 18, and Tailwind CSS*
