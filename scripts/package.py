"""Build the Windows installer and portable ZIP using CPython 3.12 on Windows."""

import hashlib
import os
from pathlib import Path
import tempfile
import uuid
import zipfile

from msilib import CAB, PID_TEMPLATE, PID_WORDCOUNT, add_data, init_database, schema, sequence


NAME = "TallyRill"
VERSION = "1.0.0"
NAMESPACE = uuid.UUID("fabb2fee-78dd-4a15-ace3-65d327384abf")
ROOT = Path(__file__).resolve().parents[1]

# Explicitly list public release inputs so private workspace files cannot enter a package.
# Each tuple names the source, installed relative path and unique MSI short file name.
PAYLOAD = (
    ("build/TallyRill.html", "TallyRill.html", "TALLYRIL.HTM"),
    ("LICENSE", "LICENSE", "LICENSE"),
    ("examples/catalog-before.csv", "examples/catalog-before.csv", "BEFORE.CSV"),
    ("examples/catalog-after.csv", "examples/catalog-after.csv", "AFTER.CSV"),
    ("docs/GUIDE.md", "docs/GUIDE.md", "GUIDE.MD"),
)


def guid(label):
    return "{" + str(uuid.uuid5(NAMESPACE, label)).upper() + "}"


def build_msi(path, root):
    product = guid("product/" + VERSION)
    upgrade = guid("upgrade")
    db = init_database(str(path), schema, NAME, product, VERSION, NAME + " contributors")
    summary = db.GetSummaryInformation(2)
    summary.SetProperty(PID_TEMPLATE, "Intel;1033")
    summary.SetProperty(PID_WORDCOUNT, 10)  # Embedded cabinet, long names, no elevation.
    summary.Persist()
    add_data(db, "Property", [
        ("UpgradeCode", upgrade), ("INSTALLLEVEL", "1"), ("ARPNOMODIFY", "1"),
        ("SecureCustomProperties", "PREVIOUSVERSION;NEWERVERSION"),
    ])
    add_data(db, "Upgrade", [
        (upgrade, None, VERSION, None, 0, None, "PREVIOUSVERSION"),
        (upgrade, VERSION, None, None, 2, None, "NEWERVERSION"),
    ])
    add_data(db, "LaunchCondition", [
        ("Installed OR NOT NEWERVERSION", "A newer version of TallyRill is already installed."),
        ("NOT ALLUSERS", "TallyRill uses a per-user installation."),
    ])
    # Use standard actions only. Check related products before evaluating launch conditions.
    for table in ("InstallExecuteSequence", "InstallUISequence"):
        actions = [row for row in getattr(sequence, table) if row[2] > 0 and row[0] != "LaunchConditions"]
        actions.append(("LaunchConditions", None, 250))
        add_data(db, table, actions)
    add_data(db, "Directory", [
        ("TARGETDIR", None, "SourceDir"),
        ("LocalAppDataFolder", "TARGETDIR", "."),
        ("UserPrograms", "LocalAppDataFolder", "Programs"),
        ("APPDIR", "UserPrograms", "TALLYRIL|TallyRill"),
        ("SAMPLES", "APPDIR", "examples"),
        ("DOCS", "APPDIR", "docs"),
        ("ProgramMenuFolder", "TARGETDIR", "."),
    ])
    add_data(db, "Feature", [("Application", None, NAME, None, 1, 1, "APPDIR", 0)])
    cabinet = CAB("payload.cab")
    directory_ids = {".": "APPDIR", "docs": "DOCS", "examples": "SAMPLES"}
    for source, target, short_name in PAYLOAD:
        rel = Path(target)
        filename = rel.name
        identifier = "F_" + target.replace(".", "_").replace("/", "_").replace("-", "_")
        component = "C_" + identifier
        registry_id = "R_" + identifier
        folder = directory_ids[str(rel.parent)]
        file_path = root / source
        seq, _ = cabinet.append(str(file_path), filename, identifier)
        add_data(db, "Component", [(component, guid(target), folder, 4, None, registry_id)])
        add_data(db, "FeatureComponents", [("Application", component)])
        add_data(db, "Registry", [
            (registry_id, 1, r"Software\TallyRill\Components", identifier, VERSION, component),
        ])
        add_data(db, "File", [
            (identifier, component, short_name + "|" + filename, file_path.stat().st_size,
             None, None, 512, seq),
        ])
        if target == "TallyRill.html":
            add_data(db, "Shortcut", [
                ("OpenTallyRill", "ProgramMenuFolder", "TALLYRIL|TallyRill", component,
                 "[#" + identifier + "]", None, "Open TallyRill", None, None, None, 1, "APPDIR"),
            ])
            for directory in ("DOCS", "SAMPLES", "APPDIR"):
                add_data(db, "RemoveFile", [("Remove_" + directory, component, None, directory, 2)])
    cabinet.commit(db)
    db.Commit()


def package(root):
    for source, _, _ in PAYLOAD:
        if not (root / source).is_file():
            raise FileNotFoundError(root / source)
    release = root / "release"
    release.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=release) as staging:
        staging = Path(staging)
        prefix = NAME + "-" + VERSION
        installer = staging / (prefix + "-windows.msi")
        portable = staging / (prefix + "-portable.zip")
        build_msi(installer, root)
        with zipfile.ZipFile(portable, "w") as archive:
            for source, target, _ in PAYLOAD:
                info = zipfile.ZipInfo(prefix + "/" + target)
                info.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(info, (root / source).read_bytes())
        manifest = staging / "SHA256SUMS.txt"
        lines = [hashlib.sha256(file.read_bytes()).hexdigest() + "  " + file.name
                 for file in (installer, portable)]
        manifest.write_text("\n".join(lines) + "\n", encoding="ascii", newline="\n")
        for file in (installer, portable, manifest):
            os.replace(file, release / file.name)
            print(file.name)


if __name__ == "__main__":
    package(ROOT)
