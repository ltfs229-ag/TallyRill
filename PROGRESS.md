# TallyRill project state

24 November 2026, Moscow time. Version 1.0.0 compares two CSV or TSV snapshots locally and ships with a bilingual guide and synthetic warehouse examples.

## Public release

- The [GitHub repository](https://github.com/ltfs229-ag/TallyRill) contains the MIT-licensed sources, tests, documentation and a [bug report form](https://github.com/ltfs229-ag/TallyRill/issues/new?template=bug.yml).
- The [v1.0.0 release](https://github.com/ltfs229-ag/TallyRill/releases/tag/v1.0.0) contains the per-user unsigned Windows MSI, a portable ZIP and SHA256SUMS.txt. All three files downloaded anonymously from GitHub matched the original files byte for byte. The expected package digests are in [the packaging guide](docs/PACKAGING.md).
- The [GitHub Pages app](https://ltfs229-ag.github.io/TallyRill/) serves the same HTML as the packaged application. Its SHA-256 is `082a46166230fb6a403c62b30ed03103f77e48e443527dcc9f6cd099856acf24`. The live warehouse example showed 3 changed, 1 added, 1 removed and 4 unchanged records.
- The original [bilingual launch site](https://tallyrill.alexgvsih.chatgpt.site/ru) also serves the application and versioned downloads.

## Verification and distribution

- Eight Node tests passed. The browser suite covered the two languages and themes, encodings, composite keys, invalid files, CSV export and a 50,000-row comparison. The warehouse case was compared with daff and csv-diff. Windows 11 installation and removal were verified. A separate Windows 10 test is outstanding. See [QA results](QA_REPORT.md).
- A [clean Windows runner](https://github.com/ltfs229-ag/TallyRill/actions/runs/45435081904) validated the current WinGet manifest, installed the release MSI through WinGet, matched the installed HTML to a fresh source build and verified removal.
- [WinGet submission #488218](https://github.com/microsoft/winget-pkgs/pull/488218) is open. Microsoft [requested the account owner's CLA](https://github.com/microsoft/winget-pkgs/pull/488218#issuecomment-7137476290). Central catalog publication depends on that response and upstream review.
- The [versioned Scoop manifest](https://raw.githubusercontent.com/ltfs229-ag/TallyRill/v1.0.0/distribution/scoop/tallyrill.json) passed upstream JSON schema validation. Scoop Extras requests evidence of established use. The repository had zero stars and forks at launch, so an Extras submission is deferred. See [the Extras intake form](https://github.com/ScoopInstaller/Extras/blob/master/.github/ISSUE_TEMPLATE/package-request.yml).

Weekly maintenance is scheduled for Tuesdays at 12:00 Moscow time. Review upstream feedback, reproduce user reports with synthetic data and distinguish verification downloads from actual adoption. Audience downloads and independent mentions have no established baseline.
