Set objShell = CreateObject("WScript.Shell")
objShell.Run "powershell -command ""& {cd..; .\venv\Scripts\Activate; python app.py}""", 0, True