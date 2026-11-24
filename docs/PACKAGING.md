# Windows distribution

TallyRill opens a self-contained HTML file in a modern browser. Both Windows packages contain the application, its MIT license, a bilingual guide, and the two synthetic sample exports.

| Download | How to use it |
| --- | --- |
| `TallyRill-1.0.0-windows.msi` | Double-click the installer, then open **TallyRill** from Start. To uninstall, open Settings → Apps, select TallyRill and choose Uninstall. |
| `TallyRill-1.0.0-portable.zip` | Extract the entire folder, then open `TallyRill.html` in Edge, Chrome or another supported browser. Keep the folder on a disk or USB drive. Removing the extracted folder removes the portable copy. |
| `SHA256SUMS.txt` | Compare the SHA-256 digest of your download against the corresponding entry. |

The MSI is unsigned. Windows may identify the publisher as unknown. The MSI registers the application for the current user, installs in `%LOCALAPPDATA%\Programs\TallyRill`, and places a shortcut in that user's Start menu. The installation includes no services or browser extensions. The Windows Installer implementation uses standard actions for files, a shortcut and HKCU component markers. [Windows Installer installation context](https://learn.microsoft.com/en-us/windows/win32/msi/installation-context)

### Установка на Windows

Запустите MSI и откройте **TallyRill** из меню «Пуск». Windows может показать предупреждение о неизвестном издателе, поскольку у файла нет цифровой подписи. Установка действует для текущего пользователя. Для удаления откройте «Параметры» → «Приложения», найдите TallyRill и выберите «Удалить». Для запуска с флешки распакуйте portable ZIP и откройте файл `TallyRill.html` в современном браузере. В обеих поставках папка `examples` содержит два примера для сверки.

## Build on Windows

Build `build/TallyRill.html` using the source instructions in the project README first. The packaging script requires the standard Windows CPython 3.12 distribution, which includes `msilib`. Run these commands from the repository root.

```powershell
py -3.12 scripts/package.py
Get-FileHash -Algorithm SHA256 release/*.msi,release/*.zip
Get-Content release/SHA256SUMS.txt
```

The package payload is allowlisted in the script. Each MSI build receives its own Windows Installer package code. Release checksums refer to the distributed artifacts. Users can verify the downloaded bytes with `Get-FileHash`.

## Installation checks

The per-user installation can be tested in a clean account with Windows Installer. Check the target directory and existing apps first so the test does not disturb an existing installation. PowerShell users can pass the absolute package path to `msiexec.exe /i` for installation or `msiexec.exe /x` for removal. Add `/qn /norestart` for unattended operation, use `Start-Process -Wait -PassThru`, and inspect the process exit code. Product code for version 1.0.0 is `{7E87D659-51CC-5E14-A758-762ED6CA226E}`.

### Observed on 24 November 2026

Windows 11 Pro build 26300, CPython 3.12.3 x64. A clean-target check preceded the installation. The tester compared both package digests to the manifest and all five files in each distribution to the build inputs. Windows Installer returned 0 for installation and registered TallyRill as installed. The Start menu shortcut resolved to the installed HTML. An isolated Edge session opened that target, displayed the localized TallyRill title and rendered the controls. Windows Installer then returned 0 for removal. The install directory, shortcut, HKCU component key and product registration were gone. PowerShell reported the MSI's Authenticode status as `NotSigned`. A separate Windows 10 installation test is outstanding.

Verified SHA-256 digests for the final packages:

```text
3dde71ae8d94300cdd7df4e1beccb570f5551f1d70462d94805e3d419219d2f7  TallyRill-1.0.0-windows.msi
969537f6a9baec7129163f83fef4636666ad506363b04aba46e9137b9084ca8e  TallyRill-1.0.0-portable.zip
```
