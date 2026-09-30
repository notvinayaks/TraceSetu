# How TraceSetu works — in-app user guide

**Current steering (25 September):** the user explicitly requested the real public-case recording, then approved TraceSetu and asked to continue. That authorization supersedes earlier UI-approval holds below. Current delivery and live-case facts are in `docs/TRACESETU_SUBMISSION.md`; older measurements below remain historical evidence.

Added and verified on 25 September 2026. The user requested a complete plain-language explanation that a newcomer can use without prior project context.

## Open the guide

- Before signing in: choose **New to TraceSetu? See how it works** below the sign-in form.
- In the workspace: select **How it works** in the sidebar, or **First time here? How it works** on the Investigations page.
- Use the seven contents links to jump to a topic. **Back to workspace** returns to the existing case when one is open.
- An investigator or administrator can choose **Open a training case** inside the guide. It creates a separate, explicitly synthetic case; reviewers see instructions for opening a shared case instead.

## What the guide explains

1. **What it does:** a wallet-to-service investigation, a plain explanation of VASPs and an explicitly illustrative transfer diagram. The first supported custody boundary is distinct from the nearest actual service, which may remain unknown.
2. **Your first investigation:** create a case, add a reviewer, choose the correct chain and UTC window, distinguish live/imported/training inputs, set hop/request limits, run and inspect the result.
3. **Understand the results:** supported receiving service, no answer, path counts versus entity counts, hops, unresolved branches, nearestness certificate, evidence grades, risk signals and completed-with-gaps status. Graph controls and Bitcoin input/output ambiguity are explained.
4. **Find the next step:** challenge a source; plan a request budget; review and execute eligible queries; distinguish fresh live acquisition from reassessment of recorded evidence. Narrowly supported bridge proof review and unsupported mixer/swap paths remain explicit.
5. **Reports and reviewed requests:** PDF and signed-bundle export; hash/signature/replay checks; current matching recipient; a separate reviewer; payload-bound request approval; supported signed-response imports, corrections, monitoring and audit activity.
6. **Live data and limitations:** recorded retrieval time, successful bounded Bitcoin sample, remaining six-chain validation, configured provider access and the difference between real acquisition, a fixed imported snapshot and synthetic training. Official SAHYOG remains unconnected.
7. **Common questions:** prerequisites, empty graphs, missing review/request buttons, public data versus ownership intelligence, the intended differentiation and an honest prototype presentation.

The guide does not claim to identify customers, prove criminality, guarantee nearestness or recover/freeze funds. It preserves the visible NOT_SENT / NOT_CONNECTED request distinction. This guide revision preceded the later explicit recording authorization. The approved TraceSetu public-case recording is documented in docs/TRACESETU_SUBMISSION.md.

## Implementation and verification

The authoritative displayed copy is `frontend/src/HowItWorks.tsx`, with presentation in `frontend/src/help.css`. App entry points are in `frontend/src/App.tsx`. The guide does not require authentication to read and does not disclose private case data. Only its training shortcut creates a case, through the existing authenticated workflow.

TypeScript and Vite builds passed. `tmp/check_help.cjs` checked unauthenticated access, all seven section targets, FAQ expansion, home/sidebar entry points, the training shortcut, return to the existing case and desktop/390px mobile layout. There were zero browser page errors and no horizontal overflow. Evidence: `output/help-review/results.json` and five screenshots. Desktop, result-definition and mobile-step screenshots were visually inspected. Backend behavior was unchanged; the earlier 107-test baseline remains a historical verification record, not a freshly repeated suite.
