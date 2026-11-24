# Architecture

The release entry point is one HTML document. Python combines the layout, stylesheet, original inline icon, dictionaries, two synthetic CSV fixtures, application controller and worker at build time. The delivered file runs on file:// in Edge and Chrome. Windows Installer places the same HTML on disk and registers a per-user shortcut.

| Module | Responsibility |
| --- | --- |
| src/engine.js | Strict byte decoding, delimited records, key indexes, schema comparison, filtering and CSV serialization. Exposes the same functions to Node tests. |
| src/worker.js | Owns source tables, index results and cached query matches. Returns small pages of 12 differences or the exported Blob. |
| src/app.js | File selection, import overrides, key selection, view state, status, localization, accessible controls and object URL lifetime. |
| src/strings.js, layout.html, style.css | Interface language, semantic structure and theme tokens. |
| scripts/build.py, scripts/package.py | Combine first-party sources and create the ZIP and per-user MSI from an explicit payload list. |

Each input change terminates the previous worker. The UI discards the previous report and starts with the replacement snapshot. Within one worker the two header maps align fields by exact name. The key index uses JSON-encoded arrays of strings in a Map, preserving boundaries between components. Empty and duplicate keys fail before results are committed. A full outer comparison visits every key and compares shared non-key fields. Schema changes use their own records. Filtering retains row references, and field expansion is performed for displayed rows and export. Query sequence numbers suppress stale views.

With R rows and C columns, the comparison takes O(R × C) work after header alignment, which takes O(C²). Tables, key indexes and diff references live in browser memory. Size and shape limits bound inputs. Export has a separate limit of 24 Mi UTF-16 code units including CSV quoting. A failed export keeps the report available.

Source values reach the DOM as text nodes. A content security policy disallows network connections and plugins. Only a worker assembled from bundled source can be created by the app. Project code contains no remote imports, telemetry, dynamic evaluation, native commands or filesystem write API. Browser downloads are explicitly initiated by the user. The application persists only language and theme if browser storage is available.

