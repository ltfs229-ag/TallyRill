# TallyRill project state

24 November 2026, Moscow time. Product version 1.0.0. The repository contains the sources, synthetic fixtures, market study, design and architecture notes, bilingual documentation, release tooling and observed test results.

- Implemented, built and verified the local app, per-user Windows MSI and portable ZIP. Exact binary hashes are in docs/PACKAGING.md and release/SHA256SUMS.txt.
- The warehouse example was checked against daff and csv-diff. Both GUI themes and languages were exercised. A separate Windows 10 machine remains to be tested.
- Official website published on 24 November 2026 at https://tallyrill.alexgvsih.chatgpt.site/ru . Verified anonymous HTTPS access to the Russian page, both release binaries and the source archive. All three archive/package hashes matched the published SHA-256 file. A browser ran the hosted warehouse example and displayed 3/1/1/4.
- Public GitHub repository and issue tracker: https://github.com/ltfs229-ag/TallyRill . The v1.0.0 release uses the Windows installer and portable ZIP verified in docs/PACKAGING.md.
- Community catalog intake, adoption metrics and user feedback remain unverified. Publish only at channels that accept the material. Start with the evidence and eligibility checks in MARKETING_PLAN.md.

- WinGet 1.29.380 validated the three package manifests with no warnings. The Scoop manifest passed the upstream JSON schema. Intake by either community catalog remains pending.
- Weekly maintenance is scheduled for Tuesdays at 12:00 Moscow time. On the launch date, audience downloads, public mentions and verified user feedback have no established baseline.
