# TraceSetu method review - 29 September 2026

This review addresses cryptocurrency nearest-VASP attribution. It does not concern ATM withdrawal forecasting or claim completion of the paused full-product build.

## Read first

1. `TraceSetu_Forensic_Method_Research_Paper.md`: eight-page paper source, including ten primary references and an honest current/proposed requirement map.
2. `../../output/pdf/TraceSetu_Forensic_Method_Research_Paper.pdf`: rendered, visually checked paper with fictional example and algorithm diagram.
3. `../../output/submission/TraceSetu_ANANTHA_SIH2026_Research_Revision.pptx`: revised six-slide deck preserving the user's exact selected source design.
4. `reference/README.md`: precise experiment contract, assumptions, reproduction and limitations.

## Verified result

Run `python research/method-review-20260929/reference/run_experiment.py` from the project root. The recorded run passed 64 synthetic functional/adversarial tests, with zero failures/errors and zero API calls. Independent review reproduced the suite and checked source hashes. Test count is not attribution accuracy.

The reference recognises a strict account-based token sweep/gas motif as an unconfirmed hypothesis. It uses externally supplied operator/role assertions and complete-coverage attestations. A perfectly imitating customer remains indistinguishable. Bitcoin cluster expansion, real-world evaluation and integration into the MVP are not part of this implementation.

Review found and fixed temporal address-revisit pruning, stale event/anchor snapshot reuse, and gas-feeder-only stopping. The snapshot digest covers events/anchors, not coverage/balances or detector policy. Those changes require rerunning detection. General path results are chronological connectivity, not amount-preserving fund provenance.

## Delivery checks

`verification/design-preservation.json` records original/final hashes and package invariants. `verification/final-validation.json` records native-table, font, slide-size, package and first-party import checks. Native PowerPoint renders cover all six final slides. `verification/delivery-qa.json` records paper page/content checks and artefact hashes. Original PPT bytes are unchanged. No generated imagery or watermark was added.

No application source, UI, case database, real disclosure workflow, GitHub repository or Drive folder was changed by this research task.

Publication note (30 September 2026): this folder and the selected project documents are now authorised for the existing private TraceSetu repository. Statements above describing no GitHub changes refer to the research task itself. `build_paper.py` preserves the original Windows/Calibri rendering assumptions; the standard-library reference tests are portable and require no network.
