# Two snapshots of a ceramics catalogue

This reproducible comparison uses the two fictional inventory exports in [examples](../examples). Read the earlier snapshot first. Each file contains eight inventory positions and five columns. A position is identified by the pair `SKU` and `Depot`. The same pour-over is stocked at two depots, and only the North position changed. The after file also uses a different row order.

## Inventory changes

| SKU | Depot | Difference | Before | After |
| --- | --- | --- | --- | --- |
| CL-101 | North | Stock | 18 | 15 |
| CL-101 | North | Price | 34.00 | 36.00 |
| GL-204 | North | Stock | 48 | 43 |
| WD-417 | North | Price | 42.00 | 39.00 |
| GL-812 | South | Added | — | Smoke glass carafe, 11 units at 38.00 |
| CL-638 | North | Removed | Ochre bud vase, 7 units at 26.00 | — |

There are three modified positions, four modified fields, one addition, one removal and four unchanged positions. The comma in the item name `Linen napkins, set of 2` belongs inside a single CSV field.

## Independent result with daff

On 24 November 2026, daff 1.4.2 ran on Windows 11 Pro, build 26300, with Python 3.12.3. To repeat the run in PowerShell, start in the TallyRill project directory. The temporary virtual environment keeps the benchmark separate from the application.

```powershell
$benchDir = Join-Path ([IO.Path]::GetTempPath()) ('tallyrill-benchmark-' + [guid]::NewGuid().ToString('N'))
py -3.12 -m venv $benchDir
& "$benchDir\Scripts\python.exe" -m pip install daff==1.4.2
$daff = "$benchDir\Scripts\daff.exe"
& $daff version
& $daff diff --id SKU --id Depot --unordered --no-color --all-columns --context 0 --output-format csv examples/catalog-before.csv examples/catalog-after.csv
```

Captured standard output from the diff command:

```csv
@@,SKU,Depot,Item,Stock,Price
---,CL-638,North,Ochre bud vase,7,26.00
->,CL-101,North,Porcelain pour-over,18->15,34.00->36.00
->,GL-204,North,Ripple tumbler,48->43,14.50
->,WD-417,North,Ash serving board,9,42.00->39.00
+++,GL-812,South,Smoke glass carafe,11,38.00
```

The two key flags disambiguate the pour-over. Unordered comparison skips moves, so a change of sort order generates no extra inventory events. The two fields changed on CL-101/North appear together on one output row. Daff also supports applying patches and three-way merges. [daff documentation](https://github.com/paulfitz/daff)

To check the same case in TallyRill, load both sample files, select `SKU` and `Depot` together, run the comparison and check the identifiers and values against the table above. A single-column SKU key is ambiguous for this catalogue. The result with that key is a separate test case.

On 24 November 2026, the TallyRill 1.0.0 portable ZIP was extracted into a fresh directory. In Microsoft Edge on Windows 11, both extracted CSVs were selected through the file inputs, the two key checkboxes were selected, and the comparison and export buttons were activated. The four summary counts read **3 changed, 1 added, 1 removed, 4 unchanged**. The downloaded CSV contained 14 detail records: four changed fields, five fields for the removed vase, and five for the new carafe. The keys and before/after values matched the daff run above.
