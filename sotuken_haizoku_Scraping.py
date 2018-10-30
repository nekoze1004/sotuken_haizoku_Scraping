import requests
from bs4 import BeautifulSoup
import prettytable
from tqdm import tqdm

url = "http://portal.fun.ac.jp/course/graduationStudy/2019/JP/essay.html"

"""
teacher : 検索したい先生の名前。文字列。and検索をしたい場合は ["角", "康"]のようにList型で書く。
teemas  : 検索したいテーマたち。List型として書く。
"""

"""teacher = ["角", "康"]
teemas = ["コミュニケーション", "メディア", "Cyber Physical Space"]"""

teacher = "村井"
teemas = ["小説・映画・アニメ・マンガ・ゲームなど作品と物語に関する研究", "言葉のレトリックや感性的な側面、より深い意味解釈に関する研究", "社会的な言語データに関する研究"]


def find_word_and(page, words, n=0):
    if len(words) == 0:
        return -1
    if words is str:
        result = page[n:].find(words)
        return result
    elif len(words) == 1:
        result = page[n:].find(str(words[0]))
        return result
    else:
        result = page.find(words[0])
        return find_word_and(page, words[1:], n=result)


def find_word_or(page, words, n=0):
    if len(words) == 0:
        return -1
    if words is str:
        result = page[n:].find(words)
        return result
    elif len(words) == 1:
        result = page[n:].find(str(words[0]))
        return result
    else:
        for word in words:
            result = page[n:].find(word)
            if result > -1:
                return result
            else:
                result = find_word_or(page, words[1:], n=n)
                return result


def find_word_number(page, words, n=0):
    if len(words) == 0:
        return []
    result_list = []
    if type(words) == str:
        result = page[n:].find(words)
        if result > 0:
            result_list.append(words)
    elif len(words) == 1:
        result = page[n:].find(str(words[0]))
        if result > 0:
            result_list.append(str(words[0]))
    else:
        for word in words:
            result = page[n:].find(word)
            if result > 0:
                result_list.append(word)
    return result_list


def get_student_ID(link):
    u = link.get("href")
    # print(u)
    student_ID = u[u.find("b") + 1:u.find("b") + 8]
    # print(student_ID)
    return student_ID


def get_student_name(page, student_ID):
    f = page.find(student_ID)
    # print(f)
    lf = page[f + 8:].find("\n")
    # print(lf)
    name = page[f + 8:f + 8 + lf]
    return name


if __name__ == '__main__':

    r = requests.get(url)
    r.encoding = r.apparent_encoding
    # print(r.text)
    s = BeautifulSoup(r.text, "lxml")
    title = s.title.string
    # print(title)
    links = s.findAll("a")
    y_sumi = 0
    teema = 0
    count404 = 0
    students = {}
    for link in tqdm(links[:-1]):  # 戻るリンク回避のため最後を除く
        # print(link.get("href"))
        res = requests.get(link.get("href"))
        res.encoding = res.apparent_encoding

        if res.status_code == 404:
            count404 += 1
            continue

        soup = BeautifulSoup(res.text, "lxml")
        if find_word_and(soup.text, teacher) > 0:
            ID = get_student_ID(link)
            name = get_student_name(s.text, ID)
            students[ID] = (name, teacher)
            y_sumi += 1
        results = find_word_number(soup.text, teemas)
        if len(results) > 0:
            ID = get_student_ID(link)
            name = get_student_name(s.text, ID)
            students[ID] = (name, results)
            teema += 1

    table = prettytable.PrettyTable(["学籍番号", "氏名", "キーワード", "URL"])
    tem = "http://portal.fun.ac.jp/~b{}/essay.html"
    print("\n")
    for ID in students:
        table.add_row([ID, students[ID][0], students[ID][1], tem.format(ID)])
        # print(f"{ID}, {students[ID][0]}, {students[ID][1]}, {tem.format(ID)}")

    print(table)
    print()
    print(f"総人数:{len(links)}")
    print(f"404エラー:{count404}")
    print(f"{teacher}が含まれる人数:{y_sumi}")
    print(f"{teemas}が含まれる人数:{teema}")
    print(f"{teacher}研を希望していると思われる人数:{len(students)}")
