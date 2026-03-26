; MyVCE Certificacion - Script para Inno Setup
; Genera un instalador .exe profesional para Windows

#define MyAppName "MyVCE Certificacion"
#define MyAppVersion "1.0"
#define MyAppPublisher "MyVCE"
#define MyAppExeName "MyVCE_Certificacion.bat"
#define MyAppDir "MyVCE_Certificacion"

[Setup]
AppId={{8F2D4A1-5B3C-4D9E-A1F0-7C2B8E9D3A6F}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL=https://github.com/myvce
AppSupportURL=https://github.com/myvce
AppUpdatesURL=https://github.com/myvce
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=installer
OutputBaseFilename=MyVCE_Certificacion_Setup_v{#MyAppVersion}
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Crear icono en el escritorio"; GroupDescription: "Accesos directos:"; Flags: unchecked

[Files]
Source: "dist\{#MyAppDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"
Name: "{group}\Desinstalar {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Ejecutar {#MyAppName}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{localappdata}\MyVCE_Certificacion"

[Code]
var
  PythonInstalled: Boolean;
  TempDir: String;

function IsPythonInstalled(): Boolean;
var
  ResultCode: Integer;
begin
  Result := False;
  if FileExists(ExpandConstant('{pf}\Python312\python.exe')) then
  begin
    Result := True;
    Exit;
  end;
  if FileExists(ExpandConstant('{pf}\Python311\python.exe')) then
  begin
    Result := True;
    Exit;
  end;
  if FileExists(ExpandConstant('{pf}\Python310\python.exe')) then
  begin
    Result := True;
    Exit;
  end;
  if Exec('cmd.exe', '/c python --version', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
  begin
    Result := (ResultCode = 0);
  end;
end;

function DownloadFile(URL: String; OutputFile: String): Boolean;
var
  ResultCode: Integer;
begin
  Result := False;
  if Exec('powershell', '-Command "Invoke-WebRequest -Uri ''' + URL + ''' -OutFile ''' + OutputFile + '''"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
  begin
    Result := (ResultCode = 0) and FileExists(OutputFile);
  end;
end;

function InstallPythonSilent(InstallerPath: String): Boolean;
var
  ResultCode: Integer;
begin
  Result := False;
  if not FileExists(InstallerPath) then
  begin
    Exit;
  end;
  if Exec(InstallerPath, '/quiet InstallAllUsers PrependPath=1 Include_pip=1', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
  begin
    Result := (ResultCode = 0) or (ResultCode = 3010);
  end;
end;

procedure WaitForPython(MaxSeconds: Integer);
var
  Counter: Integer;
  ResultCode: Integer;
begin
  Counter := 0;
  while Counter < MaxSeconds do
  begin
    if Exec('cmd.exe', '/c python --version', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
    begin
      if ResultCode = 0 then Exit;
    end;
    Sleep(2000);
    Counter := Counter + 2;
  end;
end;

function InitializeSetup(): Boolean;
var
  DownloadSuccess: Boolean;
  InstallSuccess: Boolean;
  UserChoice: Integer;
  DownloadURL: String;
  InstallerFile: String;
begin
  Result := True;
  PythonInstalled := IsPythonInstalled();
  TempDir := ExpandConstant('{tmp}');
  DownloadURL := 'https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe';
  InstallerFile := TempDir + '\python-installer.exe';
  
  if not PythonInstalled then
  begin
    UserChoice := MsgBox('Python no esta instalado. Esta aplicacion requiere Python 3.10 o superior. Desea que el instalador descargue e instale Python automaticamente?', mbConfirmation, MB_YESNO);
    
    if UserChoice = IDYES then
    begin
      DownloadSuccess := DownloadFile(DownloadURL, InstallerFile);
      
      if DownloadSuccess then
      begin
        InstallSuccess := InstallPythonSilent(InstallerFile);
        if InstallSuccess then
        begin
          WaitForPython(120);
        end;
      end;
    end;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    if FileExists(TempDir + '\python-installer.exe') then
    begin
      DeleteFile(TempDir + '\python-installer.exe');
    end;
  end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usPostUninstall then
  begin
    if MsgBox('Desea eliminar los datos de configuracion de la aplicacion?', mbConfirmation, MB_YESNO) = IDYES then
    begin
      DelTree(ExpandConstant('{localappdata}\MyVCE_Certificacion'), True, True, True);
    end;
  end;
end;
