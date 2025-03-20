Powershell Command to get history from all Powershell sessions

```
cat (Get-PSReadlineOption).HistorySavePath
```

Powershell Command to install Docker CLI in windows

```
Invoke-WebRequest -UseBasicParsing "https://raw.githubusercontent.com/microsoft/Windows-Containers/Main/helpful_tools/Install-DockerCE/install-docker-ce.ps1" -o install-docker-ce.ps1`
.\install-docker-ce.ps1
```
