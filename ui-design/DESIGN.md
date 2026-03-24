# Design System Specification: Professional Utility & Tonal Depth

## 1. Overview & Creative North Star: "The Digital Architect"
This design system rejects the "standard dashboard" aesthetic in favor of **The Digital Architect**—a philosophy that treats utility as an art form. While the app serves a functional purpose, the interface must feel like a precision instrument: authoritative, calm, and layered. 

We break the "template" look by abandoning the rigid 1px grid. Instead of boxing content, we use **Intentional Asymmetry** and **Tonal Layering**. High-contrast typography scales are paired with expansive breathing room to ensure that even the most complex utility data feels digestible and premium.

---

### 2. Colors: Tonal Logic over Structural Lines
Our palette is anchored by a deep, authoritative Blue (`primary_container: #2d328f`), balanced by a sophisticated slate spectrum.

*   **The "No-Line" Rule:** Explicitly prohibit 1px solid borders for sectioning. Boundaries are defined solely through background color shifts. For example, a `surface_container_low` section should sit directly on a `surface` background.
*   **Surface Hierarchy & Nesting:** Treat the UI as stacked sheets of fine paper. 
    *   **Level 0 (Base):** `surface` (#faf8ff)
    *   **Level 1 (Sections):** `surface_container_low` (#f2f3ff)
    *   **Level 2 (Interactive Cards):** `surface_container_lowest` (#ffffff)
*   **The "Glass & Gradient" Rule:** To provide "visual soul," use subtle linear gradients for primary actions, transitioning from `primary` (#141779) to `primary_container` (#2d328f) at a 135° angle.
*   **Functional Accents:** 
    *   **Status Green:** Use `tertiary_fixed_dim` (#4edea3) for active states.
    *   **Status Amber:** Use a custom derivation of `on_secondary_container` for warnings.

---

### 3. Typography: Editorial Authority
We use **Inter** as our typographic backbone. The goal is "High-Readability Editorial"—using size and weight rather than color to define importance.

*   **Display & Headline:** Use `display-md` (2.75rem) for critical data points like countdown timers. Keep letter-spacing tight (-0.02em) to maintain a "machined" look.
*   **Title & Body:** `title-lg` (1.375rem) is used for card headers. `body-md` (0.875rem) is the workhorse for utility descriptions.
*   **Labeling:** `label-sm` (0.6875rem) should be used in ALL CAPS with +0.05em tracking for secondary metadata to differentiate it from actionable text.

---

### 4. Elevation & Depth: The Layering Principle
We move away from traditional drop shadows toward **Ambient Depth**.

*   **Tonal Layering:** Depth is achieved by "stacking" tiers. A `surface_container_lowest` card placed on a `surface_container` background creates a soft, natural lift without a shadow.
*   **Ambient Shadows:** For floating elements (like modals), use a diffuse shadow: `box-shadow: 0 12px 40px rgba(19, 27, 46, 0.06)`. The color is a 6% opacity tint of `on_surface`.
*   **The "Ghost Border" Fallback:** If a divider is required for accessibility, use `outline_variant` (#c7c5d4) at **15% opacity**. Never use 100% opaque borders.
*   **Glassmorphism:** For persistent overlays, use `surface_container_low` with a `60%` opacity and a `20px` backdrop-blur. This integrates the component into the environment rather than "pasting" it on top.

---

### 5. Components: Precision Utility

#### **Cards & Lists**
*   **Rule:** Forbid divider lines.
*   **Implementation:** Separate list items using `spacing-4` (1rem) vertical gaps. Use `surface_container_high` (#e2e7ff) on hover to indicate interactivity.
*   **Corners:** All cards use `rounded-lg` (1rem/16px) to soften the professional tone.

#### **Buttons & Toggles**
*   **Primary Action:** A gradient-fill button (`primary` to `primary_container`) with `rounded-md` (0.75rem).
*   **Toggle Switches:** Use `primary_fixed` (#e0e0ff) for the track and `primary` (#141779) for the active thumb. The transition must be a 200ms "ease-in-out" for a tactile feel.

#### **The Confirmation Logic (Countdown Timers)**
*   **Styling:** Timers should use `display-lg` typography in `on_background` color. 
*   **Visual Cue:** Surround the timer with a thin, circular progress track using a "Ghost Border" that fills in `tertiary_fixed_dim` as time elapses.

#### **Input Fields**
*   **State:** Default state is a `surface_container_highest` fill. On focus, the background shifts to `surface_container_lowest` with a 2px `surface_tint` (#4f54b1) bottom-bar only—not a full box outline.

---

### 6. Do’s and Don’ts

#### **Do:**
*   **Do** use `spacing-12` (3rem) or `spacing-16` (4rem) to separate major functional groups. Space is a luxury; use it.
*   **Do** use `tertiary` (#002f1e) for success states to keep the palette sophisticated and dark rather than neon.
*   **Do** nest containers (`lowest` inside `low`) to create natural visual focus.

#### **Don't:**
*   **Don't** use 1px solid black or grey borders. They "trap" the design and make it look dated.
*   **Don't** use standard "drop shadows" (e.g., #000 at 25%). They muddy the clean slate-blue palette.
*   **Don't** cram multiple actions into a single card. One primary intent per container.
*   **Don't** use `Roboto` unless `Inter` is unavailable; Inter’s taller x-height provides the premium editorial feel we require.