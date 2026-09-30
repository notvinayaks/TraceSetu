# TraceSetu GitHub source release — 26 September 2026

Repository: https://github.com/notvinayaks/TraceSetu

Visibility: **private**. Default branch: `main`. Initial commit: `fac605d5e9d8688b561933790a571c65f6e704b3`.

The Git-managed publication copy is **`output/repository/TraceSetu`** relative to this development workspace. The original application source and existing private `.local` installation remain here unchanged. Future app changes made in this original workspace must be deliberately synchronised to the publication copy and verified before committing/pushing; the two folders are not automatically synchronised.

The repository contains 79 source/documentation/configuration files: the complete backend and frontend, synthetic fixtures, all backend tests, browser workflow checks, launch and evidence-verification scripts, lockfiles, API schemas, CI/Docker recipes and portable setup/capability documentation. All 42 application/public-asset/test files compared during the release audit matched their original bytes.

Excluded: real `.env`, credentials, keys, case databases, live provider responses, local signed evidence, installed dependencies, build output, videos, narration/recording scripts, PPTs, PDFs, Word files and the large presentation/research handover. Training fixtures embedded in the app remain included and clearly synthetic. A clone starts with no original case records and generates new local bootstrap passwords.

Verification in the clean copy: fresh locked Python and frontend dependency installs; `pip check`; **116 passing backend tests** with one upstream test-client deprecation warning; Ruff; TypeScript/Vite production build; local startup and health; and the existing main browser smoke workflow, including training analysis, source challenge, bundle integrity/replay and mobile overflow, with zero page errors. The temporary test server used port 8790 and has been stopped; it did not replace the original installation.

The staged-file audit found no prohibited files, detected credential patterns, personal paths or broken local Markdown links. Local `HEAD`, GitHub's commit API and remote `main` all returned the initial commit above. **Both GitHub Actions jobs passed**: fresh backend install/tests/Ruff and fresh frontend install/build on Ubuntu. Verified run: https://github.com/notvinayaks/TraceSetu/actions/runs/36221054101.

No new live-provider validation, institutional integration, deployment or asset-freezing capability is implied by repository publication.
