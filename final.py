import requests
import json
import pandas as pd
import sys
import os
import time
from lxml import etree
import re
import msvcrt

NO_secret_json = False  #預設有SECRET.json

def set_working_directory():
    # 獲取執行檔案的路徑
    exe_path = sys.argv[0]
    # 轉換為絕對路徑
    exe_dir = os.path.abspath(os.path.dirname(exe_path))
    # 設置工作目錄
    os.chdir(exe_dir)

#LoadingBar
def ANSI_string(s, color=None, background=None, bold=False):
    colors = {
        'black': '\033[30m',
        'red': '\033[31m',
        'green': '\033[32m',
        'yellow': '\033[33m',
        'blue': '\033[34m',
        'magenta': '\033[35m',
        'cyan': '\033[36m',
        'white': '\033[37m',
        'reset': '\033[0m'
    }
    
    background_colors = {
        'black': '\033[40m',
        'red': '\033[41m',
        'green': '\033[42m',
        'yellow': '\033[43m',
        'blue': '\033[44m',
        'magenta': '\033[45m',
        'cyan': '\033[46m',
        'white': '\033[47m',
        'reset': '\033[0m'
    }
    
    styles = {
        'bold': '\033[1m',
        'reset': '\033[0m'
    }
    color_code = colors[color] if color in colors else ''
    background_code = background_colors[background] if background in colors else ''
    bold_code = styles['bold'] if bold else ''

    return f"{color_code}{background_code}{bold_code}{s}{styles['reset']}"

def getData_loading_bar(duration, k):
    total_ticks = 20
    for i in range(total_ticks + 1):
        if i == total_ticks:
            progress = ANSI_string('[',bold=True) + ANSI_string('=',color='cyan') * total_ticks + ANSI_string('=',color='cyan') + ANSI_string(']',bold=True)
        else:
            progress = ANSI_string('[',bold=True) + ANSI_string('=',color='blue') * i + ANSI_string('>',color='blue') + ' ' * (total_ticks - i) + ANSI_string(']',bold=True)
        sys.stdout.write('\r' + progress + f' 抓取第{k}筆資料中，請等待' + '.' * (i % 4) + ' ' * (4 - i % 4))
        sys.stdout.flush()
        time.sleep(duration / total_ticks)
    sys.stdout.write('\n')

def waiting_loading_bar(duration):
    total_ticks = duration
    for i in range(total_ticks + 1):
        if(i==total_ticks):
            sys.stdout.write('\r' + ANSI_string(f'等待完畢，開始執行下一步',bold=True))
            sys.stdout.flush()
        else:    
            sys.stdout.write('\r' + ANSI_string(f'請等待{duration-i}秒',bold=True) + '.' * (i % 4) + ' ' * (4 - i % 4))
            sys.stdout.flush()
            time.sleep((duration / total_ticks))
    sys.stdout.write('\n')

NOTION_TOKEN = ""
PAGE_ID = ""
DATABASE_ID = ""
#NotionAPI

set_working_directory()
# 檢查是否存在 SECRET.json 檔案
secret_json_path = os.path.join(os.getcwd(), 'SECRET.json')
if os.path.exists(secret_json_path):
    # 讀取 JSON 檔案
    with open(secret_json_path) as file:
        data = json.load(file)
    # 取得 integration 和 Database 資訊
    NOTION_TOKEN = data.get('notion_id')
    PAGE_ID = data.get('page_id')
    file.close()
else:
    NO_secret_json = True


class NotionClient():
    def __init__(self):
        self.notion_key = NOTION_TOKEN
        self.default_headers = {'Authorization': f"Bearer {self.notion_key}",
                                'Content-Type': 'application/json', 'Notion-Version': '2022-06-28'}
        self.session = requests.Session()
        self.session.headers.update(self.default_headers)    

    def create_database(self, data):
        url = "https://api.notion.com/v1/databases"
        response = self.session.post(url, json=data)
        return response.json()

    def create_page(self, data, databaseID):
        url = "https://api.notion.com/v1/pages"
        payload = {"parent": {"database_id": databaseID}, "properties": data}
        response = requests.post(url, headers=self.default_headers, json=payload)
        return response.json(),response.status_code

def CreateDatabase(page_id,author):
    notion_client = NotionClient()
    print("建立database中，請等待")
    waiting_loading_bar(1)
    # Create a database with some properties
    data = {
        "parent": {
            "type": "page_id",
            "page_id": page_id
        },
        "icon": {
            "type": "emoji",
                "emoji": "📖"
        },
        "title": [
            {
                "type": "text",
                "text": {
                    "content": f"{author}",
                    "link": None
                }
            }
        ],
        "properties": {
            "書名": {
                "title": {}
            },
            "書本封面": {
                 "files": {}
            },
            "書本連結": {
                 "url": {}
            },
            "ISBN": {
                "rich_text": {}
            },
            "作者": {
                "rich_text": {}
            },   
            "出版社": {
                "rich_text": {}
            },
            "出版日期": {
                "date": {}
            }    
        }
    }
    catches_create_response = notion_client.create_database(data)
    json_str = json.dumps(catches_create_response, indent=2)
    # # 寫入到文件
    # with open('catches_database.json', 'w', encoding='utf-8') as f:
    #     f.write(json_str)
    # f.close()
    #print(json_str)
    catches_dict = json.loads(json_str)
    create_database_fail_statement = ""
    if ('status' in json_str) and catches_dict['status']==400:
        create_database_fail_statement = 'Database建立失敗: 無效的Page ID，請再次確認連結無誤'
        print(ANSI_string(s=create_database_fail_statement,color='red'))
        return ""
    elif('status' in json_str) and catches_dict['status']==401: 
        create_database_fail_statement = 'Database建立失敗: 無效的整合密碼，請確認頁面是否成功連結到您的integration，或是再次檢查整合密碼是否有誤'
        print(ANSI_string(s=create_database_fail_statement,color='red'))
        return ""
    elif('status' in json_str) and catches_dict['status']==404:
        create_database_fail_statement = 'Database建立失敗: 此頁面不存在，或是您未成功連結至您的integration上'
        print(ANSI_string(s=create_database_fail_statement,color='red'))
        return ""
    else:
        database_ID = catches_dict["id"]
        return database_ID

def NormalizeDate(date):
    if(not ('/' in date)):
        date = '1000/1/1'  
    date_split = date.split('/')
    year = date_split[0]
    mon =  date_split[1]
    day =  date_split[2]
    if(len(mon)==1):
        mon = '0' + mon
    if(len(day)==1):
        day = '0' + day
    return f'{year}-{mon}-{day}'

def CreatePage(databaseID,title=None,book_img=None,ISBN=None,author=None,publish=None,published_date=None,book_link=None):
    notion_client = NotionClient()
    published_date = NormalizeDate(published_date)
    data = {
        "書名": {"title": [{"text": {"content": title}}]},
        "書本封面": {
                    "id": "V%5E%5Be",
                    "type": "files",
                    "files": [
                        {
                            "name": book_img,
                            "type": "external",
                            "external": {
                                "url": book_img
                            }
                        }
                    ]
                },
        "ISBN": {
                    "rich_text": [
                        {
                            "text": {
                                "content": ISBN,
                            },
                        }
                    ]
                },
        "作者": {
                    "rich_text": [
                        {
                            "text": {
                                "content": author,
                            },
                        }
                    ]
                },
        "出版社": {
                    "rich_text": [
                        {
                            "text": {
                                "content": publish,
                            },
                        }
                    ]
                },
        "出版日期": {"date": {"start": published_date, "end": None}},
        "書本連結": {"url":book_link}
    }
    status_code = notion_client.create_page(data = data,databaseID = databaseID)[1]
    if(status_code==200):
        print(ANSI_string(ANSI_string(f'{title}',bold=True)+'上傳至Notion成功',color='green'))
    else:
        print(ANSI_string(ANSI_string(f'{title}',bold=True)+'上傳至Notion失敗',color='red'))

def EstablishFullDatabase(keyword,df = pd.DataFrame({'書名': [], '書本封面':[], 'ISBN': [], '作者':[], '出版社':[],'出版日期':[], '書本連結': []})):
    databaseID = CreateDatabase(author=keyword,page_id=PAGE_ID)
    if databaseID != "":
        for i in range(len(df['書名'])):
            CreatePage(databaseID=databaseID,title=df['書名'][i],book_img=df['書本封面'][i],ISBN=df['ISBN'][i],author=df['作者'][i],publish=df['出版社'][i],published_date=df['出版日期'][i],book_link=df['書本連結'][i])

#GetBookData
headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
               "AppleWebKit/537.36 (KHTML, like Gecko)"
               "Chrome/63.0.3239.132 Safari/537.36"}

def extract_book_id(url):
    # 使用正則表達式從URL中提取數字部分
    match = re.search(r'/products/(\d+)', url)
    if match:
        return match.group(1)
    else:
        return None

def get_BookTitle(html):
    title_x = html.xpath('/html/body/div[4]/div/div[1]/div/div/div/div[1]/h1/text()')
    #title_x = html.xpath('/html/body/div/div/div/div/div/div/div/h1/text()')
    if(title_x != []):
        title = title_x[-1]
        return title
    else:
        title_x = html.xpath('/html/body/div[4]/div/div[1]/div[2]/div[1]/h1/text()')
        if(title_x != []):
            title = title_x[-1]
            return title
        else:
            return '未找到資料'

def get_ISBN(html):
    ISBN_x = html.xpath('/html/body/div[4]/div/div/div[1]/div/div/ul[1]/li[1]/text()')
    #ISBN_x = html.xpath('/html/body/div/div/div/div/div/div/ul/li[1]/text()')
    if(ISBN_x != []):
        has_isbn = any(item.startswith('ISBN') or item.startswith('條碼') for item in ISBN_x)
        has_Eisbn = any(item.startswith('EISBN') for item in ISBN_x)
        if(has_isbn or has_Eisbn):
            ISBN = ISBN_x[-1].split("：")[1]
            return ISBN
        else:
            return '未找到ISBN'
    else:
        ISBN_x = html.xpath('/html/body/div[4]/div[3]/div[1]/section[5]/div/ul[1]/li[1]/text()')
        if(ISBN_x != []):
            ISBN = ISBN_x[-1].split("：")[1]
            return ISBN
        else:
            return '未找到資料'

def get_Author(html):
    author_x = html.xpath("/html/body/div/div/div/div/div/ul/li[contains(., '作者')]/a/text()")
    if(author_x == []):
        author_x = html.xpath("/html/body/div/div/div/div/div/ul/li[contains(., '編者')]/a/text()")
    if(author_x!=[]):
        if(' ' in author_x[0]):
            author = re.sub(r'\s+', '，', author_x[0])
            return author
        return author_x[0]
    else:
        author_x = html.xpath("/html/body/div/div/div/div/div/div/div/div/ul/li[contains(., '作者')]/a/text()")
        if(author_x == []):
            author_x = html.xpath("/html/body/div/div/div/div/div/div/div/div/ul/li[contains(., '編者')]/a/text()")
        if(author_x!=[]):
            if(' ' in author_x[0]):
                author = re.sub(r'\s+', '，', author_x[0])
                return author
            return author_x[0]
        else:
            return '未找到資料'
        
def get_Publishing(html):
    publish_x = html.xpath('/html/body/div/div/div/div/div/ul/li[contains(., "出版社")]/a/span/text()')
    if(publish_x != []):
        publish = publish_x[-1]
        return publish
    else:
        publish_x = html.xpath('/html/body/div/div/div/div/div/ul/li[contains(., "出版社")]/a/text()')
        if(publish_x != []):
            publish = publish_x[-1]
            return publish
        else:
            return '未找到資料'
        
def get_PublishDate(html):
    date_x = html.xpath('/html/body/div/div/div/div/div/ul/li[contains(., "出版日期")]/text()')
    if(date_x!=[]):
        return date_x[0].split("：")[1]
    else:
        date_x = html.xpath("/html/body/div/div/div/div/div/div/div/div/ul/li[contains(., '出版日期')]/text()")
        if(date_x!=[]):
            return date_x[0].split("：")[1]
        else:
            return '未找到資料'

def get_bookImg(html):
    img_x = html.xpath('/html/body/div[4]/div/div[1]/div[1]/div/div/img/@src')
    if(img_x != []):
        img_link = img_x[0].split('&')[0]
        img_link = img_link.split('?i=')[-1]
        return img_link
    else:
        img_x = html.xpath('/html/body/div[4]/div[1]/div[1]/div/div/div[1]/div[1]/div/img/@src')
        if(img_x != []):
            img_link = img_x[0].split('&')[0]
            img_link = img_link.split('?i=')[-1]
            return img_link
        else:
            return '未找到資料'
    
def get_book_data(url):
    res = requests.get(url,headers=headers, timeout=10)
    bookID = extract_book_id(url)
    if(res.status_code==requests.codes.ok):
        content = res.content.decode()
        html = etree.HTML(content)    
        title = get_BookTitle(html)
        ISBN = get_ISBN(html)
        author = get_Author(html)
        publish = get_Publishing(html)
        date = get_PublishDate(html)
        bookImglink = get_bookImg(html)
        book_data = [title, ISBN, author, publish, date, bookImglink]
        return book_data
    else:
        return 'fail',res.status_code

#GetPageData
def generate_author_url(keyword):   #輸入作者後產生作者頁面之連結
    link = "https://search.books.com.tw/search/query/key/"+keyword+"/adv_author/1/"
    print(link)
    return link

def generate_book_url(bookID): #利用書本ID產生該書連結
    return "https://www.books.com.tw/products/" + bookID + "?sloc=main"

def get_bookID(book_links): #取得書本ID，為產生書本連結用
    book_ids = []
    for link in book_links:
        book_id_match = re.search(r'/item/([^/]+?)/', link)
        if book_id_match:
            book_id = book_id_match.group(1)
            book_ids.append(book_id)
        else:
            print(f"No book ID found in link: {link}")
    return book_ids

headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
               "AppleWebKit/537.36 (KHTML, like Gecko)"
               "Chrome/63.0.3239.132 Safari/537.36"}

def page_crawel(page_url):
    res = requests.get(page_url,headers=headers)
    if(res.status_code==requests.codes.ok):
        print("連接成功!")
        print("抓取資料...")
        
        content = res.content.decode()  #解碼網頁
        html = etree.HTML(content)
        
        book_link = html.xpath('/html/body/div/div/div/div/div/div/div/div/h4/a/@href') #將此頁面所有書籍連結都放進book_link[]
        bookIDs = get_bookID(book_link) #把ID從連結擷取出來
        
        #產生書籍連結陣列，可以遍歷這個陣列來達成此頁面所有書籍的訪問
        booklinks = []
        for id in bookIDs:
            booklinks.append(generate_book_url(id))
        
        print(f"抓取到{len(bookIDs)}筆書本連結資料")
        
        titles                  = []    #書名陣列 
        ISBNs                   = []    #ISBN
        authors                 = []    #作者
        publishs                = []    #出版社
        dates                   = []    #出版日期
        bookImglinks            = []    #書本封面圖片連結
        Successful_books_links  = []    #成功抓到的書籍連結    
        Failed_books_links      = []    #存取被拒的書籍連結
        
        cnt = 0 #計數器，可以知道抓到的資料數
        for link in booklinks:  #開始第一次訪問所有書籍連結
            getData_loading_bar(2,cnt+1)     #間隔兩秒請求一次以免因為過量請求而被伺服器拒絕
            BookData = get_book_data(link)  #利用自訂函式求得此單本書籍的基本資料
            
            if(BookData[0]!='fail'):   #書本連結存取正常
                if BookData[0] == '未找到資料':     #網路異常導致抓取錯誤，放進失敗陣列，之後反覆檢查
                    print(ANSI_string('資料未正確抓取',color='red'))
                    Failed_books_links.append(link)
                else:
                    print(ANSI_string('成功抓取資料',color='green') + ANSI_string(f'　{BookData}',bold=True))
                    titles.append(BookData[0])
                    ISBNs.append(BookData[1])
                    authors.append(BookData[2])
                    publishs.append(BookData[3])
                    dates.append(BookData[4])
                    bookImglinks.append(BookData[5])
                    Successful_books_links.append(link)
                    BookData = []
            else:   #書籍連結存取被拒，放進失敗陣列等待重複檢查跟請求
                print(ANSI_string(f'連接失敗，錯誤代碼{BookData[1]}',color='red'))
                Failed_books_links.append(link)
            cnt=cnt+1
        df = pd.DataFrame({'書名': titles, '書本封面':bookImglinks, 'ISBN': ISBNs, '作者':authors, '出版社':publishs,'出版日期':dates, '書本連結': Successful_books_links})
        
        if(Failed_books_links!=[]):
            print('抓取失敗的資料連結如下')
            df_failed = pd.DataFrame({'連結':Failed_books_links})
            print(df_failed,end="\n<====================================================>\n")
        
        fail_cnt = 1
        while Failed_books_links:   #走訪失敗陣列，成功抓取目前索引的資料則將此索引之書籍連結移出失敗陣列，直到失敗陣列裡的連結都被成功抓取
            fail_book_cnt = 1
            print('重新抓取失敗之資料，請等待5秒:')
            waiting_loading_bar(5)
            print(f'第{fail_cnt}次重新嘗試抓取失敗連結，還剩{len(Failed_books_links)}筆失敗資料，請等待')
            for link in Failed_books_links[:]:  # 使用切片[:]以便在迴圈中修改原始串列
                getData_loading_bar(2,fail_book_cnt)
                fail_book_cnt = fail_book_cnt + 1
                BookData = get_book_data(link)
                if BookData[0] != 'fail':
                    if BookData[0] == '未找到資料':
                        print(ANSI_string('資料未正確抓取',color='red'))
                    else:
                        print(ANSI_string('成功抓取資料',color='green') + ANSI_string(f'　{BookData}',bold=True))
                        titles.append(BookData[0])
                        ISBNs.append(BookData[1])
                        authors.append(BookData[2])
                        publishs.append(BookData[3])
                        dates.append(BookData[4])
                        bookImglinks.append(BookData[5])
                        Successful_books_links.append(link)
                        Failed_books_links.remove(link)  # 從失敗連結串列中移除成功處理的連結
                else:
                    print(ANSI_string(f'連結失敗：{link}，錯誤代碼{BookData[1]}',color='red'))
            fail_cnt = fail_cnt+1
            print("<====================================================>")
        print("此頁資料全部抓取完畢!")
        
        df = pd.DataFrame({'書名': titles, '書本封面':bookImglinks, 'ISBN': ISBNs, '作者':authors, '出版社':publishs,'出版日期':dates, '書本連結': Successful_books_links})
        return df
    else:
        print(ANSI_string(f"連接失敗，錯誤代碼{res.status_code}",color='red'))

def generate_author_url(keyword):   #輸入作者後產生作者頁面之連結
    link = "https://search.books.com.tw/search/query/cat/1/v/1/adv_author/1/key/" + keyword
    print(link)
    return link

def generate_page_link(keyword,page):
    link = "https://search.books.com.tw/search/query/cat/all/sort/1/v/1/adv_author/1/spell/3/ms2/ms2_1/page/" + str(page) + "/key/" + keyword
    return link

def generate_book_url(bookID): #利用書本ID產生該書連結
    return "https://www.books.com.tw/products/" + bookID + "?sloc=main"

if __name__ == "__main__":
    headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
               "AppleWebKit/537.36 (KHTML, like Gecko)"
               "Chrome/63.0.3239.132 Safari/537.36"}
    keyword=str(input("請輸入作者:"))
    print("建立連結中...")
    res = requests.get(generate_author_url(keyword),headers=headers)
    set_working_directory()
    # 現在工作目錄已經設置為執行檔案所在的目錄
    print("當前工作目錄:", os.getcwd())
    if(res.status_code == requests.codes.ok):
        content = res.content.decode()  #解碼網頁
        html = etree.HTML(content)
        pages_cnt_list = html.xpath('/html/body/div/div/div/div/div/ul/li/select/option/text()')
        if(pages_cnt_list!=[]):
            pages_cnt = re.search(r'\d+', pages_cnt_list[0])
            pages_cnt = int(pages_cnt.group())
        else:
            pages_cnt = 1
        print(f'共{pages_cnt}頁')
        df = pd.DataFrame({'書名': [], '書本封面':[], 'ISBN': [], '作者':[], '出版社':[],'出版日期':[], '書本連結': []})
        for i in range(1,pages_cnt+1):
            page_link = generate_page_link(keyword,i)
            print(ANSI_string(f'抓取第{i}頁資料中',bold=True))
            df = pd.concat([df, page_crawel(page_link)], ignore_index=True, axis=0)
        
        print('所有書籍抓取完畢!')
        print(df)
        set_working_directory()
        current_directory = os.getcwd()
        csv_directory = os.path.join(current_directory, "作者csv")
        if not os.path.exists(csv_directory):
            os.makedirs(csv_directory)
        file_path = os.path.join(csv_directory, keyword + ".csv")
        df.to_csv(file_path,index=False,encoding='utf-8-sig')
        
        if(NOTION_TOKEN != "" or PAGE_ID != ""):
            upload = input('是否要將資料匯入Notion(y/n)\n')
            if(upload=='y'):
                EstablishFullDatabase(keyword=keyword,df=df)
            else:
                print('未啟用自動上傳，可以使用Notion的匯入csv功能建立database')
        elif(NO_secret_json):
            print(ANSI_string(s='SECRET.json不存在，請確保有使用SetUp.exe輸入您的整合密碼及Page連結',color='red'))
        elif(NOTION_TOKEN == ""):
            print(ANSI_string(s='無效的整合密碼，請確認頁面是否成功連結到您的integration，或是再次檢查整合密碼是否有誤',color='red'))
        elif(PAGE_ID == ""):
            print(ANSI_string(s='無效的Page ID，請再次確認連結無誤',color='red'))
            
        print("Press any key to exit...")
        msvcrt.getch()
    else:
        print(f'失敗，錯誤代碼{res.status_code}')
        print("Press any key to exit...")
        msvcrt.getch()