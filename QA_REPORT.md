# Release QA · 1.0.0

Test date 24 November 2026. Windows 11 Pro build 26300, Intel Core i5-11260H, CPython 3.12.3 x64. Final HTML SHA-256 `082a46166230fb6a403c62b30ed03103f77e48e443527dcc9f6cd099856acf24`.

| Check | Observation |
| --- | --- |
| Engine suite | 8 Node test groups passed. Includes multiline quoted records, CRLF, header-only tables, reordering, schema drift, duplicate and blank keys, exact text, tuple delimiters, malformed quotes, encoding and size guards. |
| Full workflow | Headless Edge 158.0.4370.33 and Chrome 158.0.8127.38 each loaded two files, rejected an ambiguous key, recovered after a second key was selected, searched, filtered and downloaded the complete CSV in offline mode. |
| Independent oracle | Both TallyRill and daff 1.4.2 returned 3 changed rows (4 fields), 1 addition, 1 removal and 4 unchanged rows. Repeated SKUs belonged to distinct depots. [Inputs and comparison](docs/COMPARISON.md). |
| Russian import | Recovered from invalid automatic decoding by selecting Windows-1251 for A. Compared with BOM-marked UTF-16 for B. |
| Safety checks | Source resembling HTML rendered literally. The exported CSV quoted fields and neutralized tested spreadsheet formula prefixes. The browser test recorded zero HTTP(S) requests and zero uncaught page errors. Input changes invalidated the previous report on a subsequent parsing error. This was a scoped code review and automated test. |
| Keyboard and visual checks | Executed comparison using Enter. Inspected real screenshots in two themes. Corrected a clipped statistic on narrow Russian layouts and an extra focus outline. Verified the counters on a 320 × 800 viewport for both languages and themes. |
| Installation | MSI per-user install and uninstall both returned 0. Verified 5/5 payload hashes in the MSI and ZIP, Start menu shortcut and cleanup. Opened the packed app and repeated the comparison/export from its ZIP. [Packaging report](docs/PACKAGING.md). |

## Performance observation

The integration suite generated two 50,000-row, three-column inputs of 938,902 and 938,906 bytes. Every quantity changed. It measured time from selecting the files to showing the first page of twelve differences. On the final build one Edge run and one Chrome run each took 0.562 seconds, with both suites running concurrently. Summed browser-child working sets before and after the operation were 557.5 → 642.1 MiB for Edge and 547.3 → 636.0 MiB for Chrome. These are process-tree samples including browser overhead. Peak memory and a cross-machine percentile were not measured.

Reproduce with `node --test tests/engine.test.js` and `python tests/browser.py` using the README's environment. The test prints versions, timing, inputs and process-tree memory. Measurements will vary with background activity and browser version.

## Outstanding coverage

A separate Windows 10 installation, ARM hardware, assistive-technology sessions and testing against independently supplied real-world data remain open. Both release packages are unsigned. Only the supplied synthetic data was used in screenshots and public comparisons. Browser formula handling and policies can vary across spreadsheet programs.

