[Setup]
AppName=PDF Merger
AppVersion=1.0
DefaultDirName={pf}\PDFMerger
DefaultGroupName=PDF Merger
OutputDir=.
OutputBaseFilename=PDFMergerInstaller
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\main\main.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\main\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "python\python-3.12.8-amd64.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall
Source: "src\requirements.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\PDF Merger"; Filename: "{app}\main.exe"
Name: "{group}\Uninstall PDF Merger"; Filename: "{uninstallexe}"

[Run]
Filename: "{tmp}\python-3.12.8-amd64.exe"; Parameters: "/quiet InstallAllUsers=1 PrependPath=1"; StatusMsg: "Installing Python..."
Filename: "{app}\install_dependencies.bat"; Parameters: ""; StatusMsg: "Installing dependencies..."; Flags: runhidden
Filename: "{app}\main.exe"; Description: "{cm:LaunchProgram,PDF Merger}"; Flags: nowait postinstall skipifsilent

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
var
  BatchFilePath: String;
  BatchContent: String;
  PythonDir: String;
begin
  if CurStep = ssPostInstall then
  begin
    // Get the Python installation directory
    PythonDir := ExpandConstant('{pf}\Python312'); // Adjust this to match the installed Python version

    // Create the batch file to install dependencies
    BatchFilePath := ExpandConstant('{app}\install_dependencies.bat');
    BatchContent := PythonDir + '\python.exe -m pip install --upgrade pip' + #13#10 +
                    PythonDir + '\python.exe -m pip install -r ' + ExpandConstant('{app}\requirements.txt');
    SaveStringToFile(BatchFilePath, BatchContent, False);
  end;
end;