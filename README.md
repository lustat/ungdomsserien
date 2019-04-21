## To create executable, 
#### 1. Start windows command prompt (cmd)
Go to project folder: PATH\ungdomsserien
#### 2. activate virtual environment
PATH\ungdomsserien>venv\Script\activate
#### 3. Go to skofcounter folder
PATH\ungdomsserien\test
#### 4. Run pyinstaller
pyinstaller --onefile --icon=run1.ico --clean skofcounter.py
