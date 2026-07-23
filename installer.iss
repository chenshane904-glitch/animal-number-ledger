; 十二动物号码归纳器安装脚本
[Setup]
AppName=十二动物号码归纳器
AppVersion=1.1.0
DefaultDirName={autopf}\十二动物号码归纳器
DefaultGroupName=十二动物号码归纳器
OutputDir=C:\Users\2SS2\Documents\Codex\2026-07-22\cloud\outputs
OutputBaseFilename=十二动物号码归纳器-安装包-v1.1.0-优化版
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "chinesesimplified"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "附加任务:"; Flags: unchecked

[Files]
Source: "C:\Users\2SS2\animal-number-ledger\dist\十二动物号码归纳器-v1.1.0.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\十二动物号码归纳器"; Filename: "{app}\十二动物号码归纳器-v1.1.0.exe"
Name: "{group}\卸载十二动物号码归纳器"; Filename: "{uninstallexe}"
Name: "{autodesktop}\十二动物号码归纳器"; Filename: "{app}\十二动物号码归纳器-v1.1.0.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\十二动物号码归纳器-v1.1.0.exe"; Description: "启动十二动物号码归纳器"; Flags: nowait postinstall skipifsilent
