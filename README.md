# Instructions
1. Download and install Python (3.12)
2. 
3. Create a virtual environment
   1. Go to project folder 
   2. C:\Python\Python312\python.exe -m venv venv
4. Activate venv
   1. venv\Scripts\activate
5. Install requirements
   1. pip install -r requirements.txt
6. Create Input Excel files
7. Execute runme.py



## Alternative with gui: To create executable, 
#### 1. Start windows command prompt (cmd)
Go to project folder: PATH\ungdomsserien
#### 2. activate virtual environment
PATH\ungdomsserien>venv\Script\activate
#### 3. Go to skofcounter folder
PATH\ungdomsserien\test
#### 4. Run pyinstaller
pyinstaller --onefile --icon=run1.ico --clean skofcounter.py