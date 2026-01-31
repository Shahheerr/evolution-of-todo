---
name: frontend-maestro
description: This skill serves as the Lead UI/UX Designer for the project. USE IT whenever the user asks for frontend code, component design, styling, or layout improvements. It enforce premium, modern aesthetics (Glassmorphism, gradients, micro-interactions) using TailwindCSS.
disable-model-invocation: false
---

# Frontend Maestro Skill

This skill transforms functional code into a visual masterpiece. It enforces strict design guidelines to ensure the application feels premium, modern, and polished.

## 🎨 Design Philosophy: "Premium Dark"
The application uses a coherent "Premium Dark" theme.
- **Backgrounds**: Deep, rich blues/grays (`bg-slate-900`, `bg-[#0f172a]`) instead of pure black.
- **Accents**: Vibrant gradients (Indigo -> Purple -> Pink).
- **Depth**: Heavy use of Glassmorphism (blur), shadows, and layering.
- **Typography**: Inter or similar modern sans-serif. ample whitespace.

## 🤖 When to Use This Skill
Activate this skill when the user asks:
1.  "Make this look better."
2.  "Create a dashboard component."
3.  "Fix the CSS."
4.  "Add animations."

## 🛠️ Tailwind Mastery Rules (STRICT)

### 1. The "No Boring Colors" Rule
- **NEVER** use default colors like `bg-blue-500` or `text-red-500` without purpose.
- **ALWAYS** use semantic naming or refined palettes (e.g., `text-indigo-400`, `bg-rose-500/10` for badges).
- **Gradient Text**: Use `bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 to-cyan-400` for headings.

### 2. Glassmorphism Protocol
For cards, modals, and sidebars, use the specific glass effect:
```tsx
className="backdrop-blur-xl bg-white/5 border border-white/10 shadow-2xl rounded-2xl"
```

### 3. Interactive Polish
Every interactive element MUST have state styles:
- **Hover**: Scale up slightly (`hover:scale-[1.02]`), brighten border.
- **Active**: Scale down (`active:scale-[0.98]`).
- **Focus**: Ring with offset (`focus:ring-2 focus:ring-indigo-500/50`).
- **Transition**: `transition-all duration-300 ease-out`.

### 4. Layout & Spacing
- **Padding**: generous padding (`p-6` or `p-8` for cards).
- **Grid**: Use `grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6`.
- **Responsive**: Mobile-first approach. Always test `sm:` and `lg:` breakpoints.

## 🚀 Component Patterns

### The "Hero" Card
```tsx
<div className="relative group overflow-hidden rounded-3xl bg-slate-800 p-1">
  <div className="absolute inset-0 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 opacity-20 group-hover:opacity-100 transition-opacity duration-500 blur-xl" />
  <div className="relative bg-slate-900 rounded-[22px] p-6 h-full border border-slate-700/50">
    {/* Content */}
  </div>
</div>
```

### The "Glow" Button
```tsx
<button className="relative px-6 py-3 rounded-lg bg-indigo-600 text-white font-medium shadow-[0_0_20px_rgba(79,70,229,0.3)] hover:shadow-[0_0_30px_rgba(79,70,229,0.5)] hover:-translate-y-0.5 transition-all">
  Action
</button>
```

## 🧪 Verification Checklist
Before outputting code, ask:
1.  Is there a hover state?
2.  Is the background pure black (avoid!) or rich dark gray?
3.  Is there a subtle border or shadow to create depth?
4.  Did I add `transition-all`?
