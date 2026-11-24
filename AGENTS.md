# TallyRill maintenance

This directory is a standalone project. Work only inside this repository. Keep all user exports and credentials out of source, releases, screenshots and bug reports. Use invented examples.

Read PROGRESS.md before continuing. Build with scripts/build.py, run the Node suite and tests/browser.py, then package with CPython 3.12 on Windows. Rebuild every distributable after content changes. Verify SHA-256, the installed shortcut, uninstall and the portable example before publishing a new release. Do not overwrite an already distributed asset under the same version.

The comparison contract preserves exact text, rejects ambiguous keys and reports schema drift separately. Keep both languages, download instructions, packaging documentation and the example oracle in sync.

Record the actual URLs, observed release metrics and open feedback in PROGRESS.md. The site's registered service checkout lives separately under website/. Never publish its Git configuration or local machine state as project source.

