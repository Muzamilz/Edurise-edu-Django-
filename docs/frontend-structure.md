# Frontend Structure Reorganization

## New Directory Structure

```
src/
├── features/                    # Feature-based modules
│   ├── auth/                   # Authentication features
│   │   ├── components/        # Auth-specific components
│   │   ├── services/          # Auth API services
│   │   └── stores/            # Auth state management
│   ├── courses/               # Course management
│   │   ├── components/        # Course components
│   │   ├── services/          # Course API services
│   │   └── stores/            # Course state management
│   ├── blog/                  # Blog system
│   │   ├── components/        # Blog components
│   │   ├── services/          # Blog API services
│   │   └── stores/            # Blog state management
│   ├── testimonials/          # Testimonials
│   │   ├── components/        # Testimonial components
│   │   ├── services/          # Testimonial API services
│   │   └── stores/            # Testimonial state management
│   ├── admin/                 # Admin dashboard
│   │   ├── components/        # Admin components
│   │   ├── services/          # Admin API services
│   │   └── stores/            # Admin state management
│   ├── payments/              # Payment system
│   │   ├── components/        # Payment components
│   │   ├── services/          # Payment API services
│   │   └── stores/            # Payment state management
│   └── communications/        # Communication system
│       ├── components/        # Communication components
│       ├── services/          # Communication API services
│       └── stores/            # Communication state management
├── shared/                    # Shared resources
│   ├── components/           # Global reusable components
│   ├── utils/               # Utility functions
│   └── constants/           # Global constants
├── router/                   # Vue Router configuration
├── plugins/                  # Vue plugins
├── locales/                  # Internationalization
└── assets/                   # Static assets
```

## Migration Steps

1. **Create New Structure**
   - Create all feature directories
   - Create shared directories
   - Create subdirectories for components, services, and stores

2. **Move Existing Files**
   - Move authentication-related files to `features/auth/`
   - Move course-related files to `features/courses/`
   - Move blog-related files to `features/blog/`
   - Move testimonial-related files to `features/testimonials/`
   - Move admin-related files to `features/admin/`
   - Move payment-related files to `features/payments/`
   - Move communication-related files to `features/communications/`

3. **Update Imports**
   - Update all import paths in components
   - Update all import paths in services
   - Update all import paths in stores
   - Update router configurations

4. **Clean Up**
   - Remove old directories
   - Remove unused files
   - Update documentation

## Current to New Structure Mapping

### Components
- `components/auth/*` → `features/auth/components/*`
- `components/courses/*` → `features/courses/components/*`
- `components/blog/*` → `features/blog/components/*`
- `components/testimonials/*` → `features/testimonials/components/*`
- `components/admin/*` → `features/admin/components/*`
- `components/payments/*` → `features/payments/components/*`
- `components/communications/*` → `features/communications/components/*`
- `components/common/*` → `shared/components/*`

### Services
- `services/auth.js` → `features/auth/services/index.js`
- `services/courses.js` → `features/courses/services/index.js`
- `services/blog.js` → `features/blog/services/index.js`
- `services/testimonials.js` → `features/testimonials/services/index.js`
- `services/admin.js` → `features/admin/services/index.js`
- `services/payments.js` → `features/payments/services/index.js`
- `services/communications.js` → `features/communications/services/index.js`

### Stores
- `stores/auth.js` → `features/auth/stores/index.js`
- `stores/courses.js` → `features/courses/stores/index.js`
- `stores/blog.js` → `features/blog/stores/index.js`
- `stores/testimonials.js` → `features/testimonials/stores/index.js`
- `stores/admin.js` → `features/admin/stores/index.js`
- `stores/payments.js` → `features/payments/stores/index.js`
- `stores/communications.js` → `features/communications/stores/index.js`

## Next Steps

1. Create the new directory structure
2. Move files to their new locations
3. Update import paths
4. Test the application
5. Update documentation 