"""Prepare a buildless bilingual site using only tracked source and explicit release files."""
import hashlib
import shutil
import subprocess
import zipfile
from pathlib import Path
from html import escape

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/"website/dist"
WORDS = {
"scoop":("Scoop manifest","Манифест Scoop"),"winget":("WinGet manifests","Манифесты WinGet"),
"lang":("en","ru"),"otherlang":("ru","en"),"home":("index.html","ru.html"),"other":("ru.html","index.html"),"switch":("Русский","English"),
"title":("TallyRill — offline CSV comparison by composite key","TallyRill — сверка CSV по составному ключу"),
"desc":("Compare two warehouse exports, find changed fields and save a full CSV report offline. Free open-source Windows installer and portable HTML.","Сравните две складские выгрузки, найдите отличия по полям и скачайте отчёт. Открытое приложение для Windows с автономной portable-версией."),
"heading":("What changed in your inventory?","Что изменилось на складе?"),
"intro":("Open two CSV exports. Match each item to its depot and see exactly where the quantity or price changed.","Откройте две CSV-выгрузки. Сопоставьте артикул со складом и проверьте, где изменились остаток или цена."),
"open":("Open TallyRill","Открыть приложение"),"offline":("Download for offline use","Скачать для работы офлайн"),"tag":("Changed","Изменено"),
"field":("Field","Поле"),"before":("Before","Было"),"after":("After","Стало"),"caption":("From the included warehouse example.","Из складского примера в комплекте."),
"watch":("Follow one stock change","Одна позиция в двух выгрузках"),
"how":("Open the warehouse example and search for CL-101. The North position has two changed fields. The South position keeps its original values. Both share the same SKU.","Откройте складской пример и найдите CL-101. В строке склада North изменились два поля. На складе South у того же артикула остались прежние значения."),
"guide":("Download the EN / RU guide","Скачать руководство на русском и английском"),"downloads":("Downloads","Скачать"),
"unsigned":("Version 1.0.0. The per-user Windows installer is unsigned. The portable edition opens directly in a current Edge or Chrome browser.","Версия 1.0.0. Установщик для текущего пользователя Windows поставляется без цифровой подписи. Portable-версия открывается в современном Edge или Chrome."),
"msi":("Install with a Start menu shortcut","Установить с ярлыком в меню «Пуск»"),"zip":("Extract and open the HTML file","Распаковать и открыть HTML-файл"),"source":("Source code","Исходный код"),"qa":("Test results","Результаты тестов"),
"privacy":("Your exports stay on your device","Ваши выгрузки остаются на устройстве"),
"local":("The comparison runs in your browser. The offline download contains the complete application, including its example data. Only your language and theme preferences are saved between sessions.","Сверка выполняется в браузере. Скачанная версия включает приложение и учебные файлы. Между сеансами сохраняются только выбранные язык и тема."),
"policy":("Read the privacy policy","Политика конфиденциальности")}
def build():
    OUT.mkdir(parents=True,exist_ok=True)
    template=(ROOT/"web/page.html").read_text(encoding="utf-8")
    for i,name in enumerate(("index.html","ru.html")):
        body=template
        import re
        body=re.sub(r"@@(\w+)",lambda m:escape(WORDS[m[1]][i]),body)
        (OUT/name).write_text(body,encoding="utf-8")
    names=["TallyRill-1.0.0-portable.zip","TallyRill-1.0.0-windows.msi"]
    assets={"web/site.css":"site.css","media/mark.svg":"mark.svg","build/TallyRill.html":"TallyRill.html",
            "media/report-light.png":"report.png","media/demo.mp4":"demo.mp4","docs/GUIDE.md":"guide.md",
            "docs/COMPARISON.md":"docs/COMPARISON.md","docs/PACKAGING.md":"docs/PACKAGING.md",
            "distribution/scoop/tallyrill.json":"tallyrill.json","QA_REPORT.md":"qa.md","PRIVACY.md":"privacy.md"}
    for name in names:
        assets["release/"+name]=name
    for side in ("before","after"):
        name=f"examples/catalog-{side}.csv"
        assets[name]=name
    for source,dest in assets.items():
        (OUT/dest).parent.mkdir(exist_ok=True,parents=True)
        shutil.copyfile(ROOT/source,OUT/dest)
    srcname="TallyRill-1.0.0-source.zip"
    immutable = ROOT/"release"/srcname
    if not immutable.exists():
        tracked=subprocess.check_output(["git","ls-files","-z"],cwd=ROOT).decode().split("\0")
        if "src/engine.js" not in tracked:
            raise RuntimeError("Run inside the initialized project with its sources tracked.")
        with zipfile.ZipFile(immutable,"x",compression=zipfile.ZIP_DEFLATED) as z:
            for path in sorted(filter(None,tracked)):
                z.write(ROOT/path,"TallyRill-1.0.0/"+path)
    shutil.copyfile(immutable, OUT/srcname)
    with zipfile.ZipFile(OUT/"winget-manifests.zip","w",compression=zipfile.ZIP_DEFLATED) as z:
        for yaml in sorted((ROOT/"distribution/winget").glob("*.yaml")):
            z.write(yaml,yaml.name)
    lines=[hashlib.sha256((OUT/n).read_bytes()).hexdigest()+"  "+n for n in [*names,srcname]]
    (OUT/"SHA256SUMS.txt").write_text("\n".join(lines)+"\n",encoding="ascii")
if __name__=="__main__":
    build()

