# Instructions
1. Download and install Python (3.12), https://www.python.org/downloads/
   1. Stored (e.g.) here: `C:\Python\Python312\python.exe`
2. Clone GitHub project `https://github.com/lustat/ungdomsserien`
3. Open a command window to create a virtual environment.
   1. Go to project folder 
   2. Execute: `C:\Python\Python312\python.exe -m venv venv`
   3. Activate environment: `venv\Scripts\activate`
   4. Install requirements: `pip install -r requirements.txt`
4. Create Input Excel files
5. Execute runme.py


## Alternative with gui: To create executable, 
#### 1. Start windows command prompt (cmd)
Go to project folder: PATH\ungdomsserien
#### 2. activate virtual environment
PATH\ungdomsserien>venv\Script\activate
#### 3. Go to skofcounter folder
PATH\ungdomsserien\test
#### 4. Run pyinstaller
pyinstaller --onefile --icon=run1.ico --clean skofcounter.py