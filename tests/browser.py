"""End-to-end checks against the built application in a clean, offline browser."""
import csv
import io
import json
import os
import tempfile
import time
from pathlib import Path
import psutil
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
BROWSER = os.environ.get("TALLYRILL_BROWSER", r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")

def payload(name, data):
    return {"name": name, "mimeType":"text/csv", "buffer":data}

def run():
    with sync_playwright() as p, tempfile.TemporaryDirectory() as tmp:
        browser = p.chromium.launch(executable_path=BROWSER)
        ctx = browser.new_context(locale="en-US", offline=True, accept_downloads=True)
        page = ctx.new_page()
        failed, remote = [], []
        page.on("pageerror", lambda e: failed.append(str(e)))
        page.on("request", lambda r: remote.append(r.url) if r.url.startswith(("http:","https:")) else None)
        page.goto((ROOT/"build/TallyRill.html").as_uri())
        q=page.locator
        for i, side in enumerate(["before","after"]):
            q(f"#file{i}").set_input_files(ROOT/f"examples/catalog-{side}.csv")
        expect(q("#run")).to_be_enabled()
        q("#run").click()
        expect(q("#notice")).to_contain_text("share a key")
        q("#keys").get_by_label("Depot",exact=True).check()
        q("#run").click()
        expect(q(".entry")).to_have_count(5)
        assert q(".stat b").all_text_contents()==["3","1","1","4"]
        q("#search").fill("CL-101")
        expect(q(".entry")).to_have_count(1)
        expect(q(".entry")).to_contain_text("36.00")
        q("#filter").select_option("removed")
        expect(q("#entries")).to_contain_text("No changes match")
        with page.expect_download() as info:
            q("#export").click()
        dest=Path(tmp)/"report.csv"
        info.value.save_as(dest)
        rows=list(csv.DictReader(io.StringIO(dest.read_text(encoding="utf-8-sig"))))
        assert sum(r["status"]=="changed" for r in rows)==4
        q("#theme").click()
        q("#lang").click()
        expect(q("html")).to_have_attribute("lang","ru")
        q("#reset").click()
        expect(q("#result")).to_be_hidden()
        q("#file0").set_input_files(payload("old.csv","Код;Цена\nА;1".encode("cp1251")))
        expect(q("#notice")).to_contain_text("кодировку")
        q(".file summary").first.click()
        q("#enc0").select_option("windows-1251")
        q("#file1").set_input_files(payload("new.csv","Код;Цена\nА;2".encode("utf-16")))
        expect(q("#run")).to_be_enabled()
        q("#run").click()
        expect(q(".entry")).to_have_count(1)
        expect(q(".entry")).to_contain_text("Цена")
        q("#lang").click()
        q("#reset").click()
        q("#file0").set_input_files(payload("old.csv",b"k,v\n1,x"))
        q("#file1").set_input_files(payload("new.csv",b'k,v,meta\n1,<img src=x onerror=alert(1)>,tag'))
        q("#run").click()
        expect(q("#entries")).to_contain_text("<img src=x")
        expect(q("#entries img")).to_have_count(0)
        expect(q("#schema")).to_contain_text("meta")
        q("#file1").set_input_files(payload("bad.csv",b'k,v\n1,"broken'))
        expect(q("#notice")).to_contain_text("quotation")
        expect(q("#result")).to_be_hidden()
        q("#reset").click()
        # 50k entries per side, 50k changed fields, ~1.1 MiB per input.
        n=50000
        files=[("id,qty,zone\n"+"".join(f"{i:06},{i+s},North\n" for i in range(n))).encode() for s in (0,1)]
        process=psutil.Process()
        def rss():
            return sum(p.memory_info().rss for p in process.children(recursive=True) if p.is_running() and p.name().lower() in ("msedge.exe","chrome.exe"))
        mem0=rss()
        start=time.perf_counter()
        for i, data in enumerate(files):
            q(f"#file{i}").set_input_files(payload("snapshot.csv",data))
        expect(q("#run")).to_be_enabled()
        q("#run").focus()
        page.keyboard.press("Enter")
        expect(q(".entry")).to_have_count(12, timeout=20000)
        duration=time.perf_counter()-start
        mem1=rss()
        assert q(".stat b").first.inner_text()=="50000"
        q("#next").click()
        expect(q("#pageinfo")).to_contain_text("13–24")
        page.set_viewport_size({"width":360,"height":800})
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        q("#sample").click()
        expect(q("#entries .entry")).to_have_count(5)
        assert not failed,failed
        assert not remote,remote
        print(json.dumps({"browser":browser.version,"rows_per_file":n,"input_bytes":[len(x) for x in files],
            "elapsed_seconds":round(duration,3),"browser_working_set_mib_before":round(mem0/2**20,1),
            "browser_working_set_mib_after":round(mem1/2**20,1),"page_errors":failed,"remote_requests":remote}))
        browser.close()
if __name__=="__main__":
    run()

