# -*- coding:utf-8 -*-
import requests
import re
import xlwt
import numpy


# 编码转换
def filter_u_code(string):
    u_codes = re.findall(r'(\\u\w{4})', string)
    for u_code in u_codes:
        string = string.replace(u_code, u_code.encode("utf-8").decode("unicode_escape"))
    return string


# 获取专业
def get_zhuanye(i):
    resp_zhuanye = requests.get(url=f'https://gkcx.eol.cn/school/{i}/professional',
                                headers={'User-Agent': 'BaiduSpider', })
    resp_zhuanye.encoding = "utf-8"
    computer = re.compile(r"计算机")
    computer = computer.findall(resp_zhuanye.text)
    software = re.compile(r"软件工程")
    software = software.findall(resp_zhuanye.text)
    if computer and software:
        return ["计算机", "软件工程"]
    elif not computer and software:
        return ["无", "软件工程"]
    elif computer and not software:
        return ["计算机", "无"]
    elif not computer and not software:
        return ["无", "无"]

#检测985 211
def is_985_211(i):
    resp_is = requests.get(url=f'https://static-data.eol.cn/www/2.0/school/{i}/info.json',
                           headers={'User-Agent': 'BaiduSpider', })
    resp_is.encoding = "utf-8"
    resp_is = resp_is.json()
    resp_is = resp_is["data"]
    if resp_is["f985"] == "1":
        return "985"
    elif resp_is["f211"] == "1":
        return "211"
    else:
        return ""


# 获取大学名称
def get_name(resp):
    # resp:request获取的网址
    # 正则表达式获取包含大学名称的字符串
    resp_data = resp.json()
    name = resp_data["data"]["name"]
    results_name = filter_u_code(name)
    return results_name


# 获取大学成绩
def get_score(resp):
    # 通过正则表达式获取分数线的字符串
    resp_data = resp.json()
    results_score = []
    try:
        for index in range(0, len(resp_data["data"]["pro_type_min"]["13"])):
            scores = resp_data["data"]["pro_type_min"]["13"][index]["type"]["1"]
            results_score.append(int(float(scores)))
        return results_score
    except (KeyError):
        pass


# 打印excel
def output(scores_dic, output_file_name):
    # scores_dic:包含名称 成绩 学课的字典
    # output_file_name:输出excel名称
    name_score = xlwt.Workbook()
    print(scores_dic)
    sheet = name_score.add_sheet('分数线')
    titles = ("名称", "2020分数线平均", "2019分数线平均", "2018分数线平均", "1号专业", "2号专业")
    row = 1
    # 创建标题
    for index, title in enumerate(titles):
        sheet.write(0, index, title)
    for key in scores_dic:
        # 有分数的话
        if scores_dic[key]:
            # 书写学校名称
            sheet.write(row, 0, key)
            # 依次打印
            sheet.write(row, 4, scores_dic[key][-2])
            sheet.write(row, 5, scores_dic[key][-1])
            for line in range(len(scores_dic[key]) - 2):
                sheet.write(row, line + 1, scores_dic[key][line])
            row += 1
    name_score.save(f'{output_file_name}.xls')


def main():
    scores_dic = {}
    # 30,3602
    # 3329
    for i in range(30, 51):

        resp = requests.get(url=f'https://static-data.eol.cn/www/2.0/school/{i}/info.json',
                            headers={'User-Agent': 'BaiduSpider'})
        resp_json=resp.json()
        # 判断是不是一个空的网址id
        try:
            resp_json["data"]
        except(KeyError):
            continue
        # 获取名称~
        results_name = get_name(resp) + is_985_211(i)
        results_score = get_score(resp)
        # 排除技校和没有分的大学
        if results_score and not "职业" in results_name:
            # 获取专业情况并拼接列表
            results_score = results_score + get_zhuanye(i)
            # 检测是否具有计算机和软件工程专业
            if results_score[-1] == "软件工程" or results_score[-2] == "计算机":
                # 创建字典并更新~
                new_name_score = {results_name: results_score}
                scores_dic.update(new_name_score)
                # 打印一下进度条
                print(new_name_score)
                print(i, "号大学       ", round(i * 100 / 3680, 2), "%")
    return scores_dic


if __name__ == '__main__':
    scores_dic = main()
    # numpy.save('分数线字典(包含专业.npy', scores_dic)
    output(scores_dic, "测试1.xls")
