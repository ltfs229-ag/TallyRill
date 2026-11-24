"""Capture the built app with an installed Chromium browser and FFmpeg on PATH.

    python -m pip install playwright
    python scripts/capture.py

Set TALLYRILL_BROWSER to a Chromium executable when Edge/Chrome is not in a
standard location. All example data comes from the bundled app.
"""

import argparse
import asyncio
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

from playwright.async_api import async_playwright


ROOT = Path(__file__).resolve().parents[1]
MEDIA = ROOT / "media"
SIZE = {"width": 1360, "height": 960}


def browser_path():
    custom = os.environ.get("TALLYRILL_BROWSER")
    if custom:
        path = Path(custom)
        if not path.is_file():
            raise FileNotFoundError(path)
        return str(path)
    candidates = []
    for env in ("ProgramFiles(x86)", "ProgramFiles", "LOCALAPPDATA"):
        if directory := os.environ.get(env):
            for subpath in ("Microsoft/Edge/Application/msedge.exe",
                            "Google/Chrome/Application/chrome.exe"):
                candidates.append(Path(directory) / subpath)
    for name in ("chromium", "chromium-browser", "google-chrome", "msedge"):
        if path := shutil.which(name):
            candidates.append(Path(path))
    return next((str(path) for path in candidates if path.is_file()), None)


async def collect_frames(page, folder, stop, frames):
    """Record actual viewport frames with their variable capture times."""
    while not stop.is_set():
        started = time.monotonic()
        name = f"frame-{len(frames):04d}.png"
        await page.screenshot(path=folder / name, timeout=12000)
        frames.append((name, started))
        await asyncio.sleep(max(0, 0.13 - (time.monotonic() - started)))


async def capture(app, folder, search):
    epochs = []
    frames = []
    async with async_playwright() as engine:
        browser = await engine.chromium.launch(executable_path=browser_path(), headless=True)
        try:
            context = await browser.new_context(viewport=SIZE, locale="en-US",
                                                color_scheme="light", device_scale_factor=1,
                                                offline=True)
            page = await context.new_page()
            page.set_default_timeout(7000)
            await page.goto(app.as_uri())
            await page.locator("#sample").wait_for()
            await page.evaluate("document.fonts.ready")
            await page.screenshot(path=folder / "start.png")
            stop = asyncio.Event()
            recorder = asyncio.create_task(collect_frames(page, folder, stop, frames))
            try:
                epochs.append((time.monotonic(), "Open the sample to explore two inventory snapshots."))
                await page.wait_for_timeout(1700)
                await page.locator("#sample").focus()
                await page.wait_for_timeout(600)
                await page.keyboard.press("Enter")
                results = page.locator("#result")
                await results.wait_for(state="visible")
                await page.locator("#search").wait_for(state="visible")
                await page.wait_for_timeout(650)
                epochs.append((time.monotonic(), "Review the changes between the two exports."))
                await results.evaluate("e => e.scrollIntoView({block: 'start', behavior: 'instant'})")
                await page.screenshot(path=folder / "report-light.png")
                await page.wait_for_timeout(2450)
                field = page.locator("#search")
                await field.focus()
                epochs.append((time.monotonic(), f"Search for {search} to inspect its inventory changes."))
                await field.press_sequentially(search, delay=230)
                await page.wait_for_timeout(2300)
                await field.fill("")
                await page.locator("#theme").click()
                await page.locator("#lang").click()
                await results.evaluate("e => e.scrollIntoView({block: 'start', behavior: 'instant'})")
                await page.wait_for_timeout(550)
                await page.screenshot(path=folder / "report-dark-ru.png")
                epochs.append((time.monotonic(), "The same comparison in Russian and dark mode."))
                await page.wait_for_timeout(1900)
            finally:
                stop.set()
                await recorder
            end = time.monotonic()
        finally:
            await browser.close()
    return frames, epochs, end


def clock_time(seconds):
    ms = max(0, round(seconds * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def encode(folder, frames, epochs, end):
    if not frames:
        raise RuntimeError("No browser frames captured")
    first = frames[0][1]
    timeline = ["ffconcat version 1.0"]
    for index, (name, start) in enumerate(frames):
        next_start = frames[index + 1][1] if index + 1 < len(frames) else end
        timeline.extend([f"file {name}", f"duration {max(0.04, next_start - start):.4f}"])
    timeline.append(f"file {frames[-1][0]}")
    (folder / "frames.txt").write_text("\n".join(timeline), encoding="ascii")
    captions = []
    for i, (start, line) in enumerate(epochs):
        until = epochs[i + 1][0] if i + 1 < len(epochs) else end
        captions.extend([str(i + 1), f"{clock_time(start - first)} --> {clock_time(until - first)}",
                         line, ""])
    (folder / "captions.srt").write_text("\n".join(captions), encoding="utf-8")

    def ffmpeg(*args):
        subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-y",
                        *args], cwd=folder, check=True)

    # Put captions below the actual viewport so they never cover controls.
    style = "FontName=Arial,FontSize=8,PrimaryColour=&H00FFFFFF,Outline=0,Shadow=0,MarginV=3"
    filters = f"fps=15,pad=iw:ih+68:0:0:color=0x17212c,subtitles=captions.srt:force_style='{style}'"
    ffmpeg("-f", "concat", "-i", "frames.txt", "-vf", filters, "-an", "-c:v", "libx264",
           "-preset", "fast", "-crf", "19", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "demo.mp4")
    palette = "fps=8,scale=1080:-2:flags=lanczos,split[a][b];[a]palettegen=stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=4"
    ffmpeg("-i", "demo.mp4", "-vf", palette, "-loop", "0", "demo.gif")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--app", type=Path, default=ROOT / "build" / "TallyRill.html")
    parser.add_argument("--search", default="CL-101", help="Text matching a key in the built-in sample")
    args = parser.parse_args()
    app = args.app.resolve(strict=True)
    if not shutil.which("ffmpeg"):
        parser.error("FFmpeg with libass, libx264 and GIF encoding is required")
    with tempfile.TemporaryDirectory(prefix="tallyrill-capture-") as temp:
        folder = Path(temp)
        frames, epochs, end = asyncio.run(capture(app, folder, args.search))
        encode(folder, frames, epochs, end)
        MEDIA.mkdir(exist_ok=True)
        for name in ("start.png", "report-light.png", "report-dark-ru.png", "demo.mp4", "demo.gif"):
            shutil.copyfile(folder / name, MEDIA / name)
            print(f"{name}  {(MEDIA / name).stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
