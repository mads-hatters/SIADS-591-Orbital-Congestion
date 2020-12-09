set PATH=%PATH%;C:\ProgramData\Anaconda3;C:\ProgramData\Anaconda3\Scripts;C:\ProgramData\Anaconda3\Library\bin
call C:\ProgramData\Anaconda3\Scripts\activate.bat
call conda activate siads-orbital
python.exe "./socrates_scrapper_nm.py" >> log.log 2> error.log
