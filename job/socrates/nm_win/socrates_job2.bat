set PATH=%PATH%;C:\Users\mille\Anaconda3;C:\Users\mille\Anaconda3\Scripts;C:\Users\mille\Anaconda3\Library\bin
call C:\Users\mille\Anaconda3\Scripts\activate.bat
call conda activate siads-orbital
python.exe "./socrates_scrapper_nm.py" >> log.log 2> error.log
