import tkinter as tk
import json
import os
import sys

def set_working_directory():
    # 獲取執行檔案的路徑
    exe_path = sys.argv[0]
    # 轉換為絕對路徑
    exe_dir = os.path.abspath(os.path.dirname(exe_path))
    # 設置工作目錄
    os.chdir(exe_dir)

class NotionConfigApp:
    def __init__(self, master):
        self.master = master
        master.title("Notion 設定")
        master.geometry("300x150")  # 設置視窗大小

        self.label1 = tk.Label(master, text="請輸入整合密碼:")
        self.label1.pack()

        self.entry1 = tk.Entry(master)
        self.entry1.pack()

        self.label2 = tk.Label(master, text="請輸入Page連結:")
        self.label2.pack()

        self.entry2 = tk.Entry(master)
        self.entry2.pack()

        self.submit_button = tk.Button(master, text="儲存", command=self.save_config)
        self.submit_button.pack()

    def save_config(self):
        integration_key = self.entry1.get()
        page_id = self.entry2.get()

        if '/' in page_id:
            page_id = page_id.split('/')[3]
        if '?' in page_id:
            page_id = page_id.split('?')[0]
        
        
        config = {
            "notion_id": integration_key,
            "page_id": page_id
        }
        
        set_working_directory()
        
        current_directory = os.getcwd()
        config_path = os.path.join(current_directory, "SECRET.json")

        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)

        self.entry1.delete(0, tk.END)
        self.entry2.delete(0, tk.END)
        self.master.destroy()  # 關閉視窗

if __name__ == "__main__":
    root = tk.Tk()
    app = NotionConfigApp(root)
    root.mainloop()