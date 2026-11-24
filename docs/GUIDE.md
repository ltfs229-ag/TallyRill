# TallyRill

[English guide](#english-guide) · [Русское руководство](#русское-руководство)

## English guide

TallyRill compares two snapshots of a table on your computer. A key identifies the same record in both snapshots. For inventory, a SKU may repeat at multiple depots, so the pair of SKU and depot identifies one stock position.

### Open the app

- **Windows installer.** Open the Windows MSI, then launch TallyRill from Start. The installation belongs to your Windows user. To uninstall, find TallyRill in Windows Settings under Apps and choose Uninstall.
- **Portable ZIP.** Extract the ZIP to a folder and open `TallyRill.html` in a current Microsoft Edge or Google Chrome browser. Keep the extracted `examples` folder for the tutorial. To remove the portable copy, close the tab and delete that extracted folder. Save your reports elsewhere first.
- **Verify a download.** In PowerShell, run `Get-FileHash -Algorithm SHA256` followed by the path to the downloaded MSI or ZIP. Compare the hash with the line for that filename in `SHA256SUMS.txt`. The MSI is unsigned, so Windows may show an unknown-publisher notice.

The local application works offline. Use the language and theme controls to change the interface. Browser zoom scales it for your display. Use Tab and Shift+Tab to move between controls, and the usual Enter or Space key to activate a focused control.

### Your first comparison

1. Load [catalog-before.csv](../examples/catalog-before.csv) as the earlier file (A) and [catalog-after.csv](../examples/catalog-after.csv) as the later file (B). Each contains eight stock positions.
2. Keep automatic decoding and delimiter detection for these files. Select **both SKU and Depot** as the key and run the comparison.
3. Check the summary. Three positions changed, one was added, one was removed and four stayed the same. Search for `CL-101`. At North depot, stock fell from 18 to 15 and the price rose from 34.00 to 36.00. The South position of the same SKU stayed the same.
4. Use a status filter to examine additions or removals. The added carafe has SKU `GL-812`. Export the CSV report to keep all differences. The current search, filter and page affect the view only.

### Prepare your files

The first record contains unique, nonblank column names. Every data record must contain the same number of fields as its header. The import supports comma, semicolon and tab delimiters, including quoted values with embedded delimiters and line breaks. Two adjacent double quotes inside a quoted value represent one literal double quote.

Automatic decoding reads UTF-8 and recognises UTF-16 LE or BE by its byte-order mark. For a legacy Cyrillic export, select Windows-1251 on that file. If all columns appear under a single heading, select the correct delimiter. Export a worksheet as CSV/TSV before opening it. Each input is limited to 12 MiB, 500,000 cells including headers, and 256 columns.

Choose one or more columns with matching names in both files. Every selected key part needs a value, and the resulting key must identify one record in each file in which it occurs. Source values are compared as text. For example, `001` differs from `1`, and `34.0` differs from `34.00`. Letter case and spaces can also change a match. A changed key appears as a removal and an addition. Reordering records or columns does not create differences.

### Read the report

| Result | What it tells you |
|---|---|
| Changed | A matched key has different text in at least one shared data column. |
| Added / removed | The key occurs only in B / only in A. Check A and B if the direction looks reversed. |
| Unchanged | The matched row has identical values in all shared data columns. The summary includes these rows. |
| Column added / removed | A header appears on one side only. This schema change has its own entry. |

The exported CSV uses UTF-8 with BOM and a comma delimiter. It includes a status, the key columns, a field name and the before/after values. Each changed field gets its own record, so four exported field changes can describe three changed stock positions. Added and removed positions include their field values. Schema entries carry the column name. Spreadsheet formula-like text is prefixed with an apostrophe, including some negative numbers. Use the report to review changes before any downstream import.

### If comparison stops

- **Duplicate key.** Check the reported records on the indicated side. In the tutorial, using only SKU makes the two depots collide. Add Depot to the key, then compare again.
- **Empty key.** Check the indicated record for blank or whitespace-only values in a selected key column. Correct the source export or choose another stable identifier.
- **Header, encoding or quoting error.** Check the file's encoding, delimiter, header and quoting. An error refers to a logical record, with the header counted as 1. Embedded line breaks can make editor line numbers differ.
- **Input or report limit.** Split both inputs into matching subsets, for example by depot, keeping the header in each. Keep all rows for each chosen key together. A large field-level report can reach the separate export limit even when both inputs fit.

Closing or reloading the tab clears the loaded tables and comparison. Save the exported report before closing if you need a copy. When reporting a problem, share the version, browser, import settings and a small fictional example that reproduces it. Keep real inventory and personal data out of public issues.

## Русское руководство

TallyRill сравнивает две версии таблицы на вашем компьютере. Ключ определяет одну и ту же запись в обеих выгрузках. Например, артикул может повторяться на нескольких складах. Тогда одну складскую позицию определяет сочетание артикула и склада.

### Запуск

- **Установщик Windows.** Откройте файл MSI и запустите TallyRill из меню «Пуск». Программа устанавливается для текущего пользователя. Для удаления найдите TallyRill в разделе «Приложения» параметров Windows и выберите «Удалить».
- **Переносимая версия.** Распакуйте ZIP в папку и откройте `TallyRill.html` в актуальной версии Microsoft Edge или Google Chrome. В папке `examples` лежат учебные выгрузки. Чтобы удалить переносимую копию, закройте вкладку и удалите распакованную папку. Предварительно перенесите нужные отчёты в другое место.
- **Проверка загрузки.** В PowerShell введите `Get-FileHash -Algorithm SHA256` и путь к MSI или ZIP. Сравните результат со строкой для этого файла в `SHA256SUMS.txt`. Установщик выпущен без цифровой подписи, поэтому Windows может показать уведомление о неизвестном издателе.

Локальная версия работает без интернета. Переключатели языка и темы меняют оформление. Масштаб регулируется средствами браузера. Клавишами Tab и Shift+Tab можно переходить между элементами. Enter или пробел активируют выбранный элемент.

### Первая сверка

1. Откройте [catalog-before.csv](../examples/catalog-before.csv) как предыдущую версию (A), затем [catalog-after.csv](../examples/catalog-after.csv) как новую (B). В каждом файле восемь складских позиций.
2. Оставьте автоматическое определение кодировки и разделителя. Выберите **одновременно SKU и Depot** как ключ и запустите сверку.
3. Проверьте итог. Три позиции изменились, одна добавлена, одна удалена и четыре совпали. Найдите `CL-101`. На складе North остаток упал с 18 до 15, цена выросла с 34.00 до 36.00. На складе South для этого артикула изменений нет.
4. Выберите в фильтре добавленные или удалённые позиции. Среди добавленных найдите графин с артикулом `GL-812`. Сохраните CSV-отчёт, если нужны все отличия. Экспорт охватывает и строки, скрытые текущим поиском, фильтром или страницей.

### Подготовка файлов

Первая запись содержит уникальные непустые заголовки. Число полей в каждой записи должно совпадать с числом заголовков. Разделителем может служить запятая, точка с запятой или табуляция. Внутри значения в двойных кавычках допустимы разделитель и перенос строки. Пара двойных кавычек внутри такого поля обозначает одну кавычку в значении.

В автоматическом режиме распознаются UTF-8 и UTF-16 LE/BE с меткой порядка байтов (BOM). Для старых кириллических выгрузок выберите Windows-1251 отдельно для нужного файла. Если вместо нескольких колонок распознана одна, укажите разделитель вручную. Лист Excel сначала сохраните в CSV/TSV. Предел на один файл — 12 МиБ, 500 000 ячеек вместе с заголовками и 256 колонок.

Выберите одну или несколько колонок с одинаковыми заголовками в двух файлах. Каждая часть ключа должна быть заполнена. Получившееся сочетание должно быть уникальным внутри каждого файла. Значения сравниваются как текст. Например, `001` отличается от `1`, а `34.0` — от `34.00`. Регистр и пробелы также имеют значение. Изменившийся ключ даёт удаление старой записи и добавление новой. Перестановка строк и колонок сохраняет совпадение.

### Чтение отчёта

| Результат | Значение |
|---|---|
| Изменена | Ключ совпадает, а текст хотя бы в одном общем поле отличается. |
| Добавлена / удалена | Ключ встречается только в B / только в A. Если направления перепутаны, проверьте порядок файлов. |
| Без изменений | Совпали ключ и все общие поля. Такие позиции учтены в сводке. |
| Добавлена / удалена колонка | Заголовок присутствует только с одной стороны. Разница структуры отражена отдельно. |

CSV-отчёт использует UTF-8 с BOM и разделитель-запятую. Каждая запись содержит статус, ключевые колонки, имя поля и значения до и после. Одному изменённому полю соответствует одна запись отчёта. Например, четыре изменённых поля могут относиться к трём складским позициям. Для добавленных и удалённых позиций выгружаются значения полей, для изменений структуры — имя колонки. Потенциальные формулы получают начальный апостроф. Он может появиться и перед отрицательным числом. Учитывайте это при последующей обработке.

### Устранение ошибок

- **Повтор ключа.** Проверьте указанные записи в соответствующем файле. В учебной выгрузке один SKU встречается на двух складах. Добавьте Depot в ключ и повторите сверку.
- **Пустой ключ.** В указанной записи одна из ключевых колонок пуста или состоит из пробелов. Исправьте выгрузку или выберите другой устойчивый идентификатор.
- **Ошибка заголовка, кодировки или кавычек.** Проверьте настройки импорта и структуру проблемной записи. Заголовок считается первой логической записью. Номер записи может отличаться от номера строки в редакторе из-за переносов внутри значений.
- **Превышен предел входа или отчёта.** Разбейте обе выгрузки на одинаковые группы, например по складам. Оставьте заголовок в каждой части и храните все записи с одним ключом вместе. У экспорта собственный предел, поэтому большой отчёт по полям может потребовать разбиения даже для двух допустимых входных файлов.

После закрытия или обновления вкладки загруженные таблицы и результаты сверки очищаются. Если отчёт понадобится позже, сохраните CSV заранее. Для сообщения об ошибке укажите версию программы, браузер, настройки импорта и небольшой воспроизводимый пример с вымышленными значениями. Рабочие выгрузки и персональные данные в публичные обращения включать не следует.
