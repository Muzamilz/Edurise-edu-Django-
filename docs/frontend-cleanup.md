# Frontend Cleanup Plan

## Current Structure
```
frontend/src/
├── views/          # Page components
├── stores/         # State management
├── services/       # API services
├── router/         # Vue Router configuration
├── plugins/        # Vue plugins
├── locales/        # Internationalization
├── layout/         # Layout components
├── components/     # Reusable components
└── assets/         # Static assets
```

## Required Changes

### 1. Remove Unnecessary Components ✅
- ✅ Remove any AI-related components
- ✅ Remove form builder components
- ✅ Remove analytics components that aren't part of the core plan

### 2. Reorganize Structure ✅
Create new feature-based structure:
```
frontend/src/
├── features/
│   ├── auth/              # Authentication features ✅
│   │   ├── components/    # Auth-specific components ✅
│   │   ├── services/      # Auth API services ✅
│   │   └── stores/        # Auth state management ✅
│   ├── courses/           # Course management ✅
│   │   ├── components/    # Course components ✅
│   │   ├── services/      # Course API services ✅
│   │   └── stores/        # Course state management ✅
│   ├── blog/             # Blog system ✅
│   │   ├── components/    # Blog components ✅
│   │   ├── services/      # Blog API services ✅
│   │   └── stores/        # Blog state management ✅
│   ├── testimonials/     # Testimonials ✅
│   │   ├── components/    # Testimonial components ✅
│   │   ├── services/      # Testimonial API services ✅
│   │   └── stores/        # Testimonial state management ✅
│   ├── admin/            # Admin dashboard ✅
│   │   ├── components/    # Admin components ✅
│   │   ├── services/      # Admin API services ✅
│   │   └── stores/        # Admin state management ✅
│   ├── payments/         # Payment system ✅
│   │   ├── components/    # Payment components ✅
│   │   ├── services/      # Payment API services ✅
│   │   └── stores/        # Payment state management ✅
│   └── communications/   # Communication system ✅
│       ├── components/    # Communication components ✅
│       ├── services/      # Communication API services ✅
│       └── stores/        # Communication state management ✅
├── shared/               # Shared components and utilities ✅
│   ├── components/       # Global reusable components ✅
│   ├── utils/           # Utility functions ✅
│   └── constants/       # Global constants ✅
├── router/              # Vue Router configuration ✅
├── plugins/             # Vue plugins ✅
├── locales/             # Internationalization ✅
└── assets/              # Static assets ✅
```

### 3. Implementation Steps

1. **Cleanup Phase** ✅
   - ✅ Remove unnecessary components and services
   - ✅ Archive any potentially useful code for future reference
   - ✅ Update imports and dependencies

2. **Reorganization Phase** ✅
   - ✅ Create new directory structure
   - ✅ Move existing components to appropriate feature directories
   - ✅ Update import paths
   - ✅ Update router configuration

3. **Testing Phase** ✅
   - ✅ Verify all components work in new structure
   - ✅ Update tests to match new structure
   - ✅ Ensure all imports are correct

### 4. Files to Remove ✅
- ✅ Any AI-related components
- ✅ Form builder components
- ✅ Unnecessary analytics components
- ✅ Any unused utility functions
- ✅ Deprecated services

### 5. Files to Keep ✅
- ✅ Core authentication components
- ✅ Basic layout components
- ✅ Essential utility functions
- ✅ Internationalization setup
- ✅ Router configuration
- ✅ Plugin configurations

## Next Steps

1. ✅ Create the new directory structure
2. ✅ Move existing components to appropriate feature directories
3. ✅ Remove unnecessary components and services
4. ✅ Update all import paths
5. ✅ Test the application
6. ✅ Update documentation 