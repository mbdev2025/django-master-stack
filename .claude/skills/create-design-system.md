---
name: create-design-system
description: Créer un système de design complet pour le frontend SaaS (typographie, couleurs, animations, style Medium-like)
---

# Skill: Create Design System

Crée un système de design professionnel pour vos applications SaaS avec typographie distinctive, palettes de couleurs, et animations intentionnelles - style Medium.

## Utilisation

```
/create-design-system <style> [options]
```

## Exemples

```bash
# Système de design style Medium
/create-design-system medium

# Système de design style Stripe
/create-design-system stripe

# Système de design personnalisé
/create-design-system custom --colors:vibrant --typography:modern
```

## Styles Disponibles

### **1. Medium Style (Recommandé)**
- Typographie épurée et lisible
- Palette de couleurs minimaliste (noir, blanc, gris)
- Animations fluides et subtiles
- Mise en page aérée
- Focus sur le contenu

### **2. Stripe Style**
- Typographie technique mais élégante
- Palette de couleurs vibrantes (blues, purples)
- Animations micro-interactions
- Design cards et surfaces
- Interface professionnelle

### **3. Linear Style**
- Typographie moderne et géométrique
- Palette de couleurs pastelles
- Animations smooth et easing
- Interface clean et minimaliste
- Focus sur la productivité

## Ce qui est généré

### **1. Système de Typographie**

```css
/* styles/typography.css */
:root {
  /* Font Families */
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-serif: 'Merriweather', Georgia, serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;

  /* Font Sizes */
  --text-xs: 0.75rem;      /* 12px */
  --text-sm: 0.875rem;     /* 14px */
  --text-base: 1rem;       /* 16px */
  --text-lg: 1.125rem;     /* 18px */
  --text-xl: 1.25rem;      /* 20px */
  --text-2xl: 1.5rem;     /* 24px */
  --text-3xl: 1.875rem;   /* 30px */
  --text-4xl: 2.25rem;    /* 36px */

  /* Font Weights */
  --font-light: 300;
  --font-normal: 400;
  --font-medium: 500;
  --font-semibold: 600;
  --font-bold: 700;

  /* Line Heights */
  --leading-tight: 1.25;
  --leading-snug: 1.375;
  --leading-normal: 1.5;
  --leading-relaxed: 1.625;
  --leading-loose: 2;
}
```

### **2. Palette de Couleurs**

```css
/* styles/colors.css */
:root {
  /* Medium Style - Minimaliste */
  --color-primary: #1a1a1a;
  --color-secondary: #757575;
  --color-accent: #2962ff;
  --color-success: #00a698;
  --color-warning: #f5a623;
  --color-error: #e03131;

  /* Neutrals */
  --color-gray-50: #f9f9f9;
  --color-gray-100: #f3f3f3;
  --color-gray-200: #e5e5e5;
  --color-gray-300: #d4d4d4;
  --color-gray-400: #a3a3a3;
  --color-gray-500: #737373;
  --color-gray-600: #525252;
  --color-gray-700: #404040;
  --color-gray-800: #303030;
  --color-gray-900: #1a1a1a;

  /* Semantic Colors */
  --color-bg-primary: #ffffff;
  --color-bg-secondary: #f9f9f9;
  --color-bg-tertiary: #f3f3f3;
  --color-text-primary: #1a1a1a;
  --color-text-secondary: #757575;
  --color-text-tertiary: #a3a3a3;

  /* Borders */
  --color-border-light: #e5e5e5;
  --color-border-medium: #d4d4d4;
  --color-border-dark: #a3a3a3;
}
```

### **3. Spacing System**

```css
/* styles/spacing.css */
:root {
  /* Spacing Scale */
  --space-1: 0.25rem;   /* 4px */
  --space-2: 0.5rem;    /* 8px */
  --space-3: 0.75rem;   /* 12px */
  --space-4: 1rem;      /* 16px */
  --space-5: 1.25rem;   /* 20px */
  --space-6: 1.5rem;    /* 24px */
  --space-8: 2rem;      /* 32px */
  --space-10: 2.5rem;   /* 40px */
  --space-12: 3rem;     /* 48px */
  --space-16: 4rem;     /* 64px */
  --space-20: 5rem;     /* 80px */
  --space-24: 6rem;     /* 96px */
}
```

### **4. Animation System**

```css
/* styles/animations.css */
:root {
  /* Easing Functions */
  --ease-in-quad: cubic-bezier(0.55, 0.085, 0.68, 0.53);
  --ease-in-cubic: cubic-bezier(0.55, 0.055, 0.675, 0.19);
  --ease-in-quart: cubic-bezier(0.895, 0.03, 0.685, 0.22);
  --ease-in-quint: cubic-bezier(0.755, 0.05, 0.855, 0.06);
  --ease-in-sine: cubic-bezier(0.47, 0, 0.745, 0.715);

  --ease-out-quad: cubic-bezier(0.25, 0.46, 0.45, 0.94);
  --ease-out-cubic: cubic-bezier(0.215, 0.61, 0.355, 1);
  --ease-out-quart: cubic-bezier(0.165, 0.84, 0.44, 1);
  --ease-out-quint: cubic-bezier(0.23, 1, 0.32, 1);
  --ease-out-sine: cubic-bezier(0.39, 0.575, 0.565, 1);

  --ease-in-out-quad: cubic-bezier(0.455, 0.03, 0.515, 0.955);
  --ease-in-out-cubic: cubic-bezier(0.645, 0.045, 0.355, 1);
  --ease-in-out-quart: cubic-bezier(0.77, 0, 0.175, 1);

  /* Durations */
  --duration-fast: 150ms;
  --duration-normal: 300ms;
  --duration-slow: 500ms;
  --duration-slower: 1000ms;
}

/* Animations */
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideUp {
  from {
    transform: translateY(10px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

@keyframes scaleIn {
  from {
    transform: scale(0.95);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}
```

### **5. Components UI Style Medium**

```tsx
// components/ui/Button.tsx
const buttonVariants = {
  primary: "bg-black text-white hover:bg-gray-800",
  secondary: "bg-gray-100 text-black hover:bg-gray-200",
  ghost: "bg-transparent text-black hover:bg-gray-100",
  link: "bg-transparent text-blue-600 hover:underline",
};

const buttonSizes = {
  sm: "h-8 px-3 text-sm",
  md: "h-10 px-4 text-base",
  lg: "h-12 px-6 text-lg",
};
```

### **6. Cards & Surfaces**

```css
/* styles/components.css */
.card {
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border-light);
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: all var(--duration-normal) var(--ease-in-out-cubic);
}

.card:hover {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transform: translateY(-1px);
}

.surface-elevated {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.surface-flat {
  box-shadow: none;
}
```

### **7. Forms & Inputs**

```css
/* styles/forms.css */
.input {
  font-family: var(--font-sans);
  font-size: var(--text-base);
  line-height: var(--leading-normal);
  color: var(--color-text-primary);
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border-medium);
  border-radius: 6px;
  padding: var(--space-3) var(--space-4);
  transition: all var(--duration-fast) var(--ease-in-out-cubic);
}

.input:focus {
  outline: none;
  border-color: var(--color-accent);
  box-shadow: 0 0 0 3px rgba(41, 98, 255, 0.1);
}

.input::placeholder {
  color: var(--color-text-tertiary);
}
```

### **8. Dashboard Grid**

```css
/* styles/dashboard.css */
.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: var(--space-6);
  padding: var(--space-6);
}

.stat-card {
  grid-column: span 3;
  padding: var(--space-6);
  border-radius: 8px;
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border-light);
}

.chart-container {
  grid-column: span 8;
}

.sidebar {
  grid-column: span 4;
}
```

## Fichiers Générés

```
styles/
├── base.css              /* Reset & base styles */
├── typography.css        /* Système de typographie */
├── colors.css            /* Palette de couleurs */
├── spacing.css           /* Système d'espacement */
├── animations.css        /* Animations & transitions */
├── components.css        /* Components UI */
├── forms.css             /* Styles de formulaires */
├── dashboard.css         /* Dashboard layouts */
└── utilities.css         /* Classes utilitaires */
```

## TypeScript Interfaces

```typescript
// styles/types.ts
export interface DesignSystem {
  colors: ColorPalette;
  typography: TypographySystem;
  spacing: SpacingSystem;
  animations: AnimationSystem;
  breakpoints: Breakpoints;
}

export interface ColorPalette {
  primary: string;
  secondary: string;
  accent: string;
  success: string;
  warning: string;
  error: string;
  neutrals: Record<string, string>;
}

export interface TypographySystem {
  fontFamily: {
    sans: string;
    serif: string;
    mono: string;
  };
  fontSize: Record<string, number>;
  fontWeight: Record<string, number>;
  lineHeight: Record<string, number>;
}
```

## Intégration avec shadcn/ui

```bash
# Installer shadcn/ui avec le design system
npx shadcn-ui@latest init

# Personnaliser les couleurs pour le style Medium
npx shadcn-ui@latest add button
npx shadcn-ui@latest add card
npx shadcn-ui@latest add input
```

## Exemple d'Utilisation

```bash
# Créer un design system style Medium
/create-design-system medium

# Génère automatiquement:
# - CSS variables complet
# - Components React stylés
# - Tailwind config personnalisé
# - Fichiers TypeScript
```

Créez des interfaces professionnelles style Medium, Stripe ou Linear ! 🎨
