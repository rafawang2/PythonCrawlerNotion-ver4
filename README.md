# The-Python-Crawler-for-Blogging-Notion-Automation
利用Python抓取博客來的資料，並自動存入指定的Notion database

# 打包流程
1. pip install pipenv -i https://pypi.tuna.tsinghua.edu.cn/simple/	#安裝pip虛擬環境

2. pipenv install							#建立虛擬環境

3. pipenv shell								#進入虛擬環境(若沒有建立過虛擬環境會自行建立)

4. pip install -r require.txt						#安裝程式會用到的套件

5. pip install pyinstaller						#在虛擬環境安裝打包套件

6. pyi-makespec -F -i favicon.ico final.py				#建立final.spec用於下一步打包，-i favicon.ico表示使用favicon.ico作為exe檔的縮圖

7. pyinstaller final.spec						#根據final.spec文件打包包含檔案成exe檔

# 打包方法
我已經把打包該用的指令都放在Makefile，這樣只需要在目前資料夾開啟cmd，並輸入make指令，就可以自動包裝成exe
檔案存在 {當前目錄}\dist\final.exe