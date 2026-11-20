# Exaclim — Deel-inspired interface reference

Recorded 19 November 2026. The user supplied four Deel/Mobbin screenshots showing account-access settings, a sensitive-information dialog, unchecked/checked states, and a saved confirmation. These references are sufficient to establish a visual direction. They do not supply every dashboard screen or constitute a new functional specification.

## Installed guidance

Project skill: `.agents/skills/deel/SKILL.md`, with its upstream `metadata.json` and a local `provenance.json` recording the source commit and verified Git blob hashes. The skill's frontmatter name is `deel-ui-skills`, version 1.0.0, and declares MIT. It was installed from the repository linked by the requested MCP Market listing, not by executing its CLI or installing unrelated skills.

- Listing: https://mcpmarket.com/tools/skills/deel-ui-design-system-1
- Community source: https://github.com/goharabbas321/zeoel-framework
- Pinned commit: `cd671c85f04a2fdc067dd583feea0d6e71431789`

This is a third-party design-guidance skill. It does not install Deel's internal components or establish endorsement, access to private documentation, or licensing of Deel's assets.

## Visual direction from the user's screenshots

These are visual observations, not measured color or pixel specifications:

- Horizontal application navigation with an organization/workspace switcher, leading product identity, and trailing utility controls.
- Pale lavender treatment near the header, fading toward a warm, light page surface.
- Clear page title followed by secondary tabs with a dark underline for the selected section.
- Large white cards with generous internal spacing and rounded corners; subdued inset rows for individual settings/actions.
- Near-black primary text, readable gray secondary text, thin neutral dividers and simple line icons.
- Dark primary buttons; a visibly distinct disabled state; black checked-checkbox treatment.
- Centered white dialogs with rounded corners, a dimmed backdrop, close control, explanatory text and a full-width action where appropriate.
- Clear empty/unchecked, changed/checked and saved states. A compact dark toast confirms completion.

Use Exaclim identity and heat-related content. The Deel logo, Mobbin watermark, HR navigation and financial examples are reference context, not Exaclim assets or requirements.

## Resolve contradictions before implementation

The upstream skill describes a light interface but gives `surface-raised` as `#141414` and `text-primary` as `#909090`. Several text/surface pairings would fail its own stated contrast requirement. Its pale-blue focus color also needs contrast review on light surfaces. It mixes a strict 4px grid with a 2px default gap and has very large extracted heading sizes.

Do not apply that table verbatim. The user's screenshot references and readable, accessible states take priority. Preserve the original installed skill for provenance; define any approved Exaclim tokens separately. Favor a coherent 4px-based spacing system, responsive typography, clear focus treatment and genuine contrast checks over incidental extracted values.

## Implementation boundary

Keep `@ui-sdk/core` and `@ui-sdk/web` as the interaction foundation. The reference changes the visual language; it does not require React or MUI. SDK components continue to own tabs, control semantics, focus management, popup dismissal and keyboard interaction. Any new UI pattern should use the SDK where it provides one.

Keep heat warning colors meaningful, and pair them with words/icons. Preserve synthetic-data labeling, emergency latching, separate acknowledgement, stale-data fallback and crew privacy behavior. Reference styling must not turn a help action into an ordinary notification or hide data-quality problems.

Installation and reference documentation do not themselves redesign the live dashboard. The next implementation should apply these references to the agreed Exaclim screens, then run the relevant browser, keyboard, responsive and contrast checks.
