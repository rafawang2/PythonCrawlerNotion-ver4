# 打包第三版成exe執行檔
利用Python抓取博客來的資料，並自動存入指定的Notion database

## 打包流程
1. 安裝pip虛擬環境: ```pip install pipenv -i https://pypi.tuna.tsinghua.edu.cn/simple/```

2. 建立虛擬環境: ```pipenv install```

3. 進入虛擬環境: ```pipenv shell```

4. 安裝程式會用到的套件: ```pip install -r require.txt```

5. 在虛擬環境安裝打包套件: ```pip install pyinstaller```

6. 建立final.spec用於下一步打包，-i favicon.ico表示使用favicon.ico作為exe檔的縮圖:  ```pyi-makespec -F -i favicon.ico final.py```

7. 根據final.spec文件打包包含檔案成exe檔: ```pyinstaller final.spec```

## 打包方法(makefile)
我已經把打包該用的指令都放在Makefile，若有安裝make的程式(我是使用minGW裡面的make套件)，可以使用此Makefile來自動打包成exe

`只需要在目前資料夾開啟cmd，並輸入make指令，就可以自動包裝成exe`
    
exe執行檔會存在 {當前目錄}\dist\final.exe
