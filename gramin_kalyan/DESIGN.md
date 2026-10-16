---
name: Gramin Kalyan
colors:
  surface: '#f0fdf3'
  surface-dim: '#d0ddd4'
  surface-bright: '#f0fdf3'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#eaf7ed'
  surface-container: '#e4f1e7'
  surface-container-high: '#dfebe2'
  surface-container-highest: '#d9e6dc'
  on-surface: '#131e18'
  on-surface-variant: '#404941'
  inverse-surface: '#28332d'
  inverse-on-surface: '#e7f4ea'
  outline: '#707971'
  outline-variant: '#bfc9bf'
  surface-tint: '#256b44'
  primary: '#004526'
  on-primary: '#ffffff'
  primary-container: '#155e39'
  on-primary-container: '#8fd5a6'
  inverse-primary: '#8fd6a7'
  secondary: '#885200'
  on-secondary: '#ffffff'
  secondary-container: '#fea93e'
  on-secondary-container: '#6d4100'
  tertiary: '#632b00'
  on-tertiary: '#ffffff'
  tertiary-container: '#873d00'
  on-tertiary-container: '#ffb68a'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#abf2c2'
  primary-fixed-dim: '#8fd6a7'
  on-primary-fixed: '#002110'
  on-primary-fixed-variant: '#00522e'
  secondary-fixed: '#ffddbb'
  secondary-fixed-dim: '#ffb867'
  on-secondary-fixed: '#2b1700'
  on-secondary-fixed-variant: '#673d00'
  tertiary-fixed: '#ffdbc8'
  tertiary-fixed-dim: '#ffb68b'
  on-tertiary-fixed: '#321200'
  on-tertiary-fixed-variant: '#753400'
  background: '#f0fdf3'
  on-background: '#131e18'
  surface-variant: '#d9e6dc'
typography:
  headline-xl:
    fontFamily: Noto Sans
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 42px
  headline-lg:
    fontFamily: Noto Sans
    fontSize: 26px
    fontWeight: '700'
    lineHeight: 36px
  headline-md:
    fontFamily: Noto Sans
    fontSize: 22px
    fontWeight: '700'
    lineHeight: 30px
  headline-sm:
    fontFamily: Noto Sans
    fontSize: 19px
    fontWeight: '600'
    lineHeight: 28px
  body-xl:
    fontFamily: Noto Sans
    fontSize: 18px
    fontWeight: '500'
    lineHeight: 28px
  body-lg:
    fontFamily: Noto Sans
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 26px
  body-md:
    fontFamily: Noto Sans
    fontSize: 15px
    fontWeight: '400'
    lineHeight: 24px
  label-xl:
    fontFamily: Noto Sans
    fontSize: 18px
    fontWeight: '700'
    lineHeight: 24px
  label-lg:
    fontFamily: Noto Sans
    fontSize: 16px
    fontWeight: '600'
    lineHeight: 22px
  label-md:
    fontFamily: Noto Sans
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
  label-sm:
    fontFamily: Noto Sans
    fontSize: 12px
    fontWeight: '700'
    lineHeight: 16px
    letterSpacing: 0.5px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  gutter: 1rem
  gutter-tablet: 1.5rem
  gutter-desktop: 2rem
  margin: 1rem
  margin-tablet: 2rem
  margin-desktop: 3rem
  space-xs: 0.375rem
  space-sm: 0.75rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2.25rem
  space-2xl: 3.5rem
---

## Brand & Style

This design system is engineered for rural students, first-generation scholars, and their families navigating competitive scholarships and government welfare programs. The aesthetic merges civic trustworthiness with village-rooted warmth. Rather than adopting an austere bureaucratic interface or a slick metro-fintech sheen, the design conveys the dependable, patient dignity of a village council elder and the clarity of a dedicated rural schoolmaster.

### Aesthetic & Design Style
The system employs a **Tactile High-Contrast Civic** style:
- **Resilience under harsh sunlight:** High-luminance paper-cream backdrops replace blinding stark whites, reducing glare while maintaining maximum readable contrast outdoors.
- **Physical tangibility:** Structural components rely on distinct structural outlines, warm card surfaces, and chunky, physically pressable tap targets rather than floating ethereal shadows. Low-end LCD and TFT displays with low viewing angles or crushed dynamic range can clearly distinguish card boundaries and interactable zones.
- **Multilingual and Voice-First Accommodations:** The layout recognizes varying literacy levels and linguistic diversity across India. Audio playouts, voice-dictation mic anchors, and dual-script reading ergonomics take visual precedence over abstract iconography.

## Colors

The palette draws directly from public welfare credibility and agricultural abundance: deep crop greens, sun-baked earth, turmeric/mustard markers, and warm saffron urgency indicators.

### Key Roles & Semantic Application
- **Primary (`#155E39`):** Represents institutional authority, stability, and growth. Used for primary CTA containers, validated step markers, official stamp badges, and sticky bottom completion bars. Pairs strictly with `#FFFFFF` text to achieve a WCAG AAA rating (> 8:1 contrast).
- **Secondary (`#C27803`):** Ochre/Mustard for informational callouts, upcoming deadlines, status tags (e.g., "Verification Pending"), and active tab highlights.
- **Tertiary (`#E06D10`):** Saffron/Terracotta reserved for high-salience actions: audio playback indicators, microphone listening states, critical document alerts, and deadline warnings.
- **Neutral Surface & Canvas (`#FBF9F5` base, `#F5F1EA` container):** Off-white parchment and clay wash that prevents screen glare in bright field environments and grounds white surface cards.
- **Neutral Foreground (`#1E2923` primary text, `#46534B` secondary text):** Forest-tinted charcoal ensuring 100% legibility on cream surfaces without the harsh vibrating edge of synthetic pure black.
- **Structural Borders (`#DCD3C4` active, `#E5DFD5` resting):** Earthy clay outlines that demarcate cards, form inputs, and sections regardless of display hardware limitations.

## Typography

Typography relies on **Noto Sans** to guarantee structural parity, rendering fidelity, and identical visual weight across Latin characters, Devanagari (Hindi/Marathi), and regional Indian scripts.

### Baseline Rules & Ergonomics
- **No Body Text Under 15px:** To accommodate varying visual acuity and budget device screen resolutions, the minimum readable size for narrative content is set to 15px, with standard instructional body at 16px (`body-lg`) and 18px (`body-xl`).
- **Generous Vertical Metrics:** Line heights are maintained between 1.45x and 1.6x font size to prevent complex matras, conjuncts, and vowel diacritics in Indian scripts from clipping or overlapping adjacent lines.
- **Prominent Primary Buttons:** Core user decision points use `label-xl` (18px Bold) to ensure instant readability from arm's length.

## Layout & Spacing

The layout is built primarily for single-hand, thumb-driven mobile interaction, scaling seamlessly into tablet kiosks at Common Service Centers (CSC) or village panchayat offices.

### Grid & Responsiveness
- **Mobile (Base to 599px):** 4-column fluid layout with `1rem` (16px) margins and gutters. Single-column stacked cards ensure straightforward vertical scanning without cognitive overload. Critical actions are anchored to a sticky bottom dock.
- **Tablet (600px to 1023px):** 8-column layout with `1.5rem` (24px) margins and gutters. Forms switch to a 2-column format while scheme detail views adopt a 5-column / 3-column split (scheme criteria vs. application checklist).
- **Desktop / CSC Kiosk (1024px+):** 12-column layout maxed at 1120px container width to avoid excessively long line lengths.

### Spatial Rhythm
Padding inside interactive cards is pinned to `space-md` (16px) or `space-lg` (24px) to ensure user tap zones are separated from neighbouring controls, eliminating accidental taps during field operation.

## Elevation & Depth

This design system avoids blurry drop-shadows and translucent glass effects, which fail in bright outdoor glare and perform inconsistently on budget phone processors. Depth is articulated purely through **layered tonal planes** combined with **tactile solid borders**.

### Layering Hierarchy
1. **Canvas (Ground Floor):** Deep off-white (`#FBF9F5`).
2. **Container Level 1 (Resting Cards & Sheets):** Solid `#FFFFFF` fill framed by a crisp 1.5px solid border (`#E5DFD5`). This ensures complete separation against the cream canvas.
3. **Container Level 2 (Selected, Focused, or Urgent Cards):** `#FFFFFF` fill supported by a 2.5px solid outline in Primary Green (`#155E39`) or Ochre (`#C27803`), plus an earthy contact shadow: `box-shadow: 0 4px 0 0 #D0C6B8`. This creates a tactile, physical "click-down" presence.
4. **Active Sticky Elements (Bottom CTA Bar, Mic Prompts):** `#FFFFFF` with a thick top border (`2px solid #E5DFD5`) and a deep protective shadow (`0 -4px 16px rgba(30, 41, 35, 0.08)`).

## Shapes

The roundedness tier is set to **2 (Rounded)** with purposeful variations across scales:
- Standard cards, input fields, and banners utilize `rounded-lg` (16px / 1rem) for an approachable, friendly visual presence that remains orderly and structured.
- Interactive controls, status badges, voice microphone triggers, and primary action buttons utilize full pills (`rounded-full`) or `rounded-xl` (24px / 1.5rem), providing a smooth, thumb-inviting form factor.

## Components

### Buttons
- **Touch Standard:** All interactive buttons possess an uncompromising minimum touch height of **56px** (up to 64px for primary mobile actions).
- **Primary CTA:** Background `#155E39`, text `#FFFFFF` (18px Bold), border radius 16px or full pill. When pressed, shifts 2px downward to provide tangible tactile feedback. Always features an accompanying directional icon (e.g., rightward arrow or document check).
- **Secondary Action:** Background `#FFFFFF`, 2px solid `#155E39`, text `#155E39`.
- **Audio / Speak CTA:** Tertiary Ochre/Saffron tint (`#FFF7ED`), 2px solid `#E06D10`, featuring a high-visibility speaker icon and bilingual label (e.g., *"बोलकर सुनें / Listen"*).

### Voice & Assistance Anchor
- Floating or persistent sticky microphone button with a minimum touch zone of **64px × 64px**, clad in Tertiary Saffron (`#E06D10`) with pure white microphone iconography and a subtle pulse wave for non-text-proficient users.

### Cards & Scheme Tiles
- Pure `#FFFFFF` surface with a 1.5px `#E5DFD5` border and 16px corner radius.
- Includes a prominent header zone featuring scheme logo / government insignia placeholder, bilingual title, a clear category tag (e.g., "Pre-Matric", "Merit-Based"), and a prominent highlighted badge for benefit amounts (e.g., *"₹25,000 / year"* highlighted in an Ochre pill).

### Input Fields & Selectors
- Minimum vertical height of **56px**.
- Border is 2px solid `#DCD3C4`, elevating to 2.5px solid `#155E39` on focus with an off-white inner glow.
- Labels are persistently visible above the field in 16px bold (no floating labels that disappear or become unreadable).
- An integrated microphone icon is embedded inside every text input to permit instantaneous local dialect speech-to-text.

### Checkboxes & Radio Selection Cards
- Checkboxes and radio discs measure a minimum of **28px × 28px** with thick 3px indicator marks.
- Option lists are rendered as selectable full-width cards: tapping any area of the row activates the selection state, transitioning the border to 2px solid `#155E39` with a soft green background wash (`#F0F7F3`).

### Chips & Filter Pills
- Minimum height **44px**, pill-shaped, enclosed with 1.5px solid earthy border `#DCD3C4`.
- Selected state adopts `#155E39` with `#FFFFFF` text and a visible checkmark icon.