# Interface review using Emil Kowalski’s design-engineering skill

20 November 2026. Applied the upstream `emil-design-eng` skill, pinned and retained with its license in `.agents/skills/emil-design-eng/`. The user’s explicit ban on decorative UI and custom replacement components takes precedence over generic animation examples. No motion was added.

| Before | After | Why |
|---|---|---|
| Arrow tile in the recommendations heading with no destination | Removed | A visible affordance must correspond to a real action. |
| Decorative crew icons, dialogue icon tiles, sun illustration, brand ornament and privacy chip | Removed | They added visual weight without helping a task. |
| Repeated weather symbols and offset strings in each hourly cell | Time, temperature and severity labels; full source timezone remains available | Remove repeated clutter while keeping risk information. |
| Handwritten notification div and timer | Installed UI SDK Toast | Library owns announcement, dismissal and lifetime behavior. |
| Forecast controls recreated on every poll | Compare stable forecast content and retain unchanged DOM | Keyboard focus and selection survive polling. |
| Crew cards recreated by each age tick | Reuse unchanged content and show the last reading timestamp | Stable reading and text selection, with the two-minute stale boundary still enforced. |
| Labels as small as 8–10px | Minimum 12px metadata, 14px recommendation text, 16px inputs | Readability and reduced mobile input zoom. |
| Global hover styles | Hover-capable pointer media query | Avoid persistent hover presentation after touch. |
| Long crew/site names could crowd narrow cards | Wrapping, constrained flex children and a two-column phone count layout | Actual values remain available without horizontal page overflow. |
| Unnecessary server receipt details repeated in crew cards | Last sample time and freshness status | Show the information relevant to the supervisor. |
| Minified styling with obsolete decoration rules | Formatted CSS and removed obsolete selectors | Make the design rules inspectable and easier to maintain. |

## Verification

- `npm test`: exit 0, 72 tests passed.
- `npm run test:browser`: exit 0, 27 checks passed. Includes keyboard focus retention across polling, 99-character unbroken names at 360px, empty-site switching, source labels, SDK-owned controls, 16px inputs, durable acknowledgement behavior and desktop/tablet/mobile layouts.
- Strict Cloudflare TypeScript checking: exit 0.
- Screenshots and machine-readable results: `docs/evidence/emil-review/`.

The browser checks use Chromium. Real iOS/Android keyboard, safe-area and touch behavior was not physically tested. This interface review does not close missing weather/gateway/hardware work in the engineering audit.
