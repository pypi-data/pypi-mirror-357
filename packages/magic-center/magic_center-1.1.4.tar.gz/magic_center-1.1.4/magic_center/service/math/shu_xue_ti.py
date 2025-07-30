from datetime import datetime
import numpy as np
import xlwt
import random
import os


def auto_num_list(df):
    row, col = df.shape
    outer_data = []
    number = 0
    for row_idx in range(row):
        inner_data = []
        for col_idx in range(col):
            number += 1
            inner_data.append(number)
        outer_data.append(inner_data)

    print(outer_data)
    return outer_data


def auto_num_comparation_less_than_20(tar_path):
    row = 30
    col = 8
    outer_data_1 = []
    outer_data_2 = []
    outer_data_symbol = []
    for row_idx in range(row):
        inner_data_1 = []
        inner_data_2 = []
        inner_data_symbol = []
        for col_idx in range(col):
            if col_idx % 2 == 0:
                first_num = str(np.random.randint(0, 20))
                inner_data_1.append(first_num)
                first_num = str(np.random.randint(0, 20))
                inner_data_2.append(first_num)
                inner_data_symbol.append(" \u3007 ")
            else:
                inner_data_1.append("")
                inner_data_2.append("")
                inner_data_symbol.append("")
        if row_idx % 2 == 0:
            outer_data_1.append(inner_data_1)
            outer_data_2.append(inner_data_2)
            outer_data_symbol.append(inner_data_symbol)
        else:
            outer_data_1.append(col * [""])
            outer_data_2.append(col * [""])
            outer_data_symbol.append(col * [""])
    outer_data_array_1 = np.array(outer_data_1)
    outer_data_array_2 = np.array(outer_data_2)
    outer_data_array_symbol = np.array(outer_data_symbol)
    final_result = np.char.add(outer_data_array_1, outer_data_array_symbol)
    final_result = np.char.add(final_result, outer_data_array_2)
    wb = xlwt.Workbook(encoding="utf-8")
    sheet = wb.add_sheet('sheet1', cell_overwrite_ok=True)
    sheet.write(0, 1, "20以内比较大小", set_style('Times New Roman', 220, True))
    curr_row = 2
    for rows in final_result:
        for col_idx, item in enumerate(rows):
            sheet.write(curr_row, col_idx, item, set_style('Arial', 350))
        curr_row += 1
    if not os.path.exists(tar_path):
        os.makedirs(tar_path)
    version = datetime.strftime(datetime.now(), format="%Y%m%d%H%M%S")
    wb.save(tar_path + f"/20以内比较大小_{version}.xls")
    return tar_path + f"/20以内比较大小_{version}.xls"


def auto_num_comparation_less_than_100(tar_path):
    row = 30
    col = 8
    outer_data_1 = []
    outer_data_2 = []
    outer_data_symbol = []
    for row_idx in range(row):
        inner_data_1 = []
        inner_data_2 = []
        inner_data_symbol = []
        for col_idx in range(col):
            if col_idx % 2 == 0:
                first_num = str(np.random.randint(0, 100))
                inner_data_1.append(first_num)
                first_num = str(np.random.randint(0, 100))
                inner_data_2.append(first_num)
                inner_data_symbol.append(" \u3007 ")
            else:
                inner_data_1.append("")
                inner_data_2.append("")
                inner_data_symbol.append("")
        if row_idx % 2 == 0:
            outer_data_1.append(inner_data_1)
            outer_data_2.append(inner_data_2)
            outer_data_symbol.append(inner_data_symbol)
        else:
            outer_data_1.append(col * [""])
            outer_data_2.append(col * [""])
            outer_data_symbol.append(col * [""])
    outer_data_array_1 = np.array(outer_data_1)
    outer_data_array_2 = np.array(outer_data_2)
    outer_data_array_symbol = np.array(outer_data_symbol)
    final_result = np.char.add(outer_data_array_1, outer_data_array_symbol)
    final_result = np.char.add(final_result, outer_data_array_2)
    wb = xlwt.Workbook(encoding="utf-8")
    sheet = wb.add_sheet('sheet1', cell_overwrite_ok=True)
    sheet.write(0, 1, "100以内比较大小", set_style('Times New Roman', 220, True))
    curr_row = 2
    for rows in final_result:
        for col_idx, item in enumerate(rows):
            sheet.write(curr_row, col_idx, item, set_style('Arial', 350))
        curr_row += 1
    if not os.path.exists(tar_path):
        os.makedirs(tar_path)
    version = datetime.strftime(datetime.now(), format="%Y%m%d%H%M%S")
    wb.save(tar_path + f"/100以内比较大小_{version}.xls")
    return tar_path + f"/100以内比较大小_{version}.xls"


def auto_less_than_20(tar_path):
    wb = xlwt.Workbook(encoding="utf-8")
    sheet = wb.add_sheet('sheet1', cell_overwrite_ok=True)
    sheet.write(0, 1, "20以内混合加减法", set_style('Times New Roman', 220, True))
    row = 50
    col = 10
    first_nums = list(range(0, 21))
    operators = ["+", "-"]
    curr_row = 3
    for rowIdx in range(0, row):
        if rowIdx % 2 == 0:
            continue
        if rowIdx == 25:
            curr_row += 1
            continue
        for colIdx in range(0, col):
            if colIdx % 2 == 1:
                question_str = ""
            else:
                operator = random.choice(operators)
                first_num = random.choice(first_nums)
                if operator == "+":
                    second_num = random.choice(list(range(0, 20 - first_num + 1)))
                elif operator == "-":
                    second_num = random.choice(list(range(first_num + 1)))
                question_str = str(first_num) + " " + operator + " " + str(second_num) + " = "
            sheet.write(curr_row - 1, colIdx, question_str)
        curr_row += 2
    if not os.path.exists(tar_path):
        os.makedirs(tar_path)
    version = datetime.strftime(datetime.now(), format="%Y%m%d%H%M%S")
    wb.save(tar_path + f"/20以内混合加减法_{version}.xls")
    return tar_path + f"/20以内混合加减法_{version}.xls"


def auto_less_than_100(tar_path):
    wb = xlwt.Workbook(encoding="utf-8")
    sheet = wb.add_sheet('sheet1', cell_overwrite_ok=True)
    sheet.write(0, 1, "100以内混合加减法", set_style('Times New Roman', 220, True))
    row = 50
    col = 10
    first_nums = list(range(0, 101))
    operators = ["+", "-"]
    curr_row = 3
    for rowIdx in range(0, row):
        if rowIdx % 2 == 0:
            continue
        if rowIdx == 25:
            curr_row += 1
            continue
        for colIdx in range(0, col):
            if colIdx % 2 == 1:
                question_str = ""
            else:
                operator = random.choice(operators)
                first_num = random.choice(first_nums)
                if operator == "+":
                    second_num = random.choice(list(range(0, 100 - first_num + 1)))
                elif operator == "-":
                    second_num = random.choice(list(range(first_num + 1)))
                question_str = str(first_num) + " " + operator + " " + str(second_num) + " = "
            sheet.write(curr_row - 1, colIdx, question_str)
        curr_row += 2
    if not os.path.exists(tar_path):
        os.makedirs(tar_path)
    version = datetime.strftime(datetime.now(), format="%Y%m%d%H%M%S")
    wb.save(tar_path + f"/100以内混合加减法_{version}.xls")
    return tar_path + f"/100以内混合加减法_{version}.xls"


def auto_less_than_100_pmm(tar_path):
    wb = xlwt.Workbook(encoding="utf-8")
    sheet = wb.add_sheet('sheet1', cell_overwrite_ok=True)
    sheet.write(0, 1, "100以内混合加减乘法", set_style('Times New Roman', 220, True))
    row = 50
    col = 10
    first_nums = list(range(0, 101))
    operators_p_m = ["+", "-"]
    operators_m_d = ["*"]
    curr_row = 3
    for rowIdx in range(0, row):
        if rowIdx % 2 == 0:
            continue
        if rowIdx == 25:
            curr_row += 3
            continue
        for colIdx in range(0, col):
            if colIdx % 2 == 1:
                question_str = ""
            else:
                if rowIdx >= 13 and rowIdx <= 24 or rowIdx >= 38 and rowIdx <= 49:
                    operator = random.choice(operators_m_d)
                    first_num = random.choice(list(range(1, 10)))
                    if first_num > 5:
                        second_num = random.choice(list(range(1, 6)))
                    else:
                        second_num = random.choice(list(range(1, 10)))
                    question_str = str(first_num) + " " + operator + " " + str(second_num) + " = "
                else:
                    operator = random.choice(operators_p_m)
                    first_num = random.choice(first_nums)
                    if operator == "+":
                        second_num = random.choice(list(range(0, 100 - first_num + 1)))
                    elif operator == "-":
                        second_num = random.choice(list(range(first_num + 1)))
                    question_str = str(first_num) + " " + operator + " " + str(second_num) + " = "
            sheet.write(curr_row - 1, colIdx, question_str)
        curr_row += 2
    if not os.path.exists(tar_path):
        os.makedirs(tar_path)
    version = datetime.strftime(datetime.now(), format="%Y%m%d%H%M%S")
    wb.save(tar_path + f"/100以内混合加减乘法_{version}.xls")
    return tar_path + f"/100以内混合加减乘法_{version}.xls"


def auto_less_than_100_pmmd(tar_path):
    wb = xlwt.Workbook(encoding="utf-8")
    sheet = wb.add_sheet('sheet1', cell_overwrite_ok=True)
    sheet.write(0, 1, "100以内混合加减乘除法", set_style('Times New Roman', 220, True))
    row = 50
    col = 10
    first_nums = list(range(0, 101))
    operators_p_m = ["+", "-"]
    operators_m_d = ["*", "÷"]
    md_list_1 = get_md_list()
    md_list_2 = get_md_list()
    curr_row = 3
    for rowIdx in range(curr_row, row):
        if rowIdx % 2 == 0:
            continue
        if rowIdx == 25:
            curr_row += 3
            continue
        for colIdx in range(0, col):
            if colIdx % 2 == 1:
                question_str = ""
            else:
                if rowIdx >= 13 and rowIdx <= 24:
                    question_str = get_random_md(md_list_1)
                elif rowIdx >= 38 and rowIdx <= 49:
                    question_str = get_random_md(md_list_2)
                else:
                    operator = random.choice(operators_p_m)
                    first_num = random.choice(first_nums)
                    if operator == "+":
                        second_num = random.choice(list(range(0, 100 - first_num + 1)))
                    elif operator == "-":
                        second_num = random.choice(list(range(first_num + 1)))
                    question_str = str(first_num) + " " + operator + " " + str(second_num) + " = "
            sheet.write(curr_row - 1, colIdx, question_str)
        curr_row += 2
    if not os.path.exists(tar_path):
        os.makedirs(tar_path)
    version = datetime.strftime(datetime.now(), format="%Y%m%d%H%M%S")
    wb.save(tar_path + f"/100以内混合加减乘除法_{version}.xls")
    return tar_path + f"/100以内混合加减乘除法_{version}.xls"


def auto_shushi_less_than_100(tar_path):
    wb = xlwt.Workbook(encoding="utf-8")
    sheet = wb.add_sheet('sheet1', cell_overwrite_ok=True)
    sheet.write(0, 1, "100以内列竖式混合加减法", set_style('Times New Roman', 220, True))
    col = 8
    first_nums = list(range(0, 101))
    operators = ["+", "-"]
    curr_row = 3
    data_rows_wrote_count = 1
    while data_rows_wrote_count <= 6:
        for colIdx in range(0, col):
            if colIdx % 3 != 0:
                question_str = ""
            else:
                proper_formular = False
                while not proper_formular:
                    first_operator = random.choice(operators)
                    first_num = random.choice(first_nums)
                    if first_operator == "+":
                        second_num = random.choice(list(range(0, 100 - first_num + 1)))
                    elif first_operator == "-":
                        second_num = random.choice(list(range(first_num + 1)))
                    second_operator = random.choice(operators)
                    result = eval(str(first_num) + " " + first_operator + " " + str(second_num))
                    if not (0 <= result <= 100):
                        continue
                    if second_operator == "+":
                        third_num = random.choice(list(range(0, 100 - result + 1)))
                    elif second_operator == "-":
                        third_num = random.choice(list(range(result + 1)))
                    final_result_str = (str(first_num) + " " + first_operator + " " + str(second_num) + " " +
                                        second_operator + str(third_num))
                    result = eval(final_result_str)
                    if all(map(lambda x: 0 if x - 10 < 0 else 1,
                               random.sample([first_num, second_num, third_num], 2))) and 0 <= result <= 100:
                        proper_formular = True
                question_str = str(final_result_str) + " = "
            sheet.write(curr_row - 1, colIdx, question_str)
        curr_row += 9
        data_rows_wrote_count += 1
    if not os.path.exists(tar_path):
        os.makedirs(tar_path)
    version = datetime.strftime(datetime.now(), format="%Y%m%d%H%M%S")
    wb.save(tar_path + f"/100以内列竖式混合加减法_{version}.xls")
    return tar_path + f"/100以内列竖式混合加减法_{version}.xls"


def auto_less_than_100_pmmdv(tar_path, pages):
    wb = xlwt.Workbook(encoding="utf-8")
    sheet = wb.add_sheet('sheet1', cell_overwrite_ok=True)
    total_rows_in_an_area = 62
    for page in range(0, pages):
        rows_offset = page * total_rows_in_an_area
        sheet.write(rows_offset, 1, "100以内混合加减乘除法和竖式", set_style('Times New Roman', 220, True))
        row = 25 + rows_offset
        col = 10
        first_nums = list(range(0, 101))
        operators_p_m = ["+", "-"]
        md_list_1 = get_md_list()
        curr_row = 3 + rows_offset
        for rowIdx in range(curr_row, row):
            if rowIdx % 2 == 0:
                continue
            if rowIdx == 25:
                curr_row += 3
                continue
            for colIdx in range(0, col):
                if colIdx % 2 == 1:
                    question_str = ""
                else:
                    if rowIdx >= 13 + rows_offset and rowIdx <= 24 + rows_offset:
                        question_str = get_random_md(md_list_1)
                    elif rowIdx >= 2 + rows_offset and rowIdx <= 12 + rows_offset:
                        operator = random.choice(operators_p_m)
                        first_num = enhance_number_selection(random.choice(first_nums))
                        if operator == "+":
                            second_num = random.choice(list(range(0, 100 - first_num + 1)))
                        elif operator == "-":
                            second_num = random.choice(list(range(first_num + 1)))
                        if second_num <= 10:
                            if operator == "+":
                                operator = "-"
                                second_num = random.choice(list(range(int(first_num/2), first_num + 1)))
                            if operator == "-":
                                operator = "+"
                                second_num = random.choice(list(range(int((100 - first_num)/2), 100 - first_num + 1)))
                        question_str = str(first_num) + " " + operator + " " + str(second_num) + " = "
                sheet.write(curr_row - 1, colIdx, question_str)
            curr_row += 3
        curr_row += 2
        data_rows_wrote_count = 1
        while data_rows_wrote_count <= 2:
            for colIdx in range(0, col):
                if colIdx % 3 != 0:
                    question_str = ""
                else:
                    proper_formular = False
                    while not proper_formular:
                        first_operator = random.choice(operators_p_m)
                        first_num = random.choice(first_nums)
                        if first_operator == "+":
                            second_num = random.choice(list(range(0, 100 - first_num + 1)))
                        elif first_operator == "-":
                            second_num = random.choice(list(range(first_num + 1)))
                        second_operator = random.choice(operators_p_m)
                        result = eval(str(first_num) + " " + first_operator + " " + str(second_num))
                        if not (0 <= result <= 100):
                            continue
                        if second_operator == "+":
                            third_num = random.choice(list(range(0, 100 - result + 1)))
                        elif second_operator == "-":
                            third_num = random.choice(list(range(result + 1)))
                        if third_num <= 10:
                            if second_operator == "+":
                                second_operator = "-"
                                third_num = random.choice(list(range(int(result/3), result + 1)))
                            if second_operator == "-":
                                second_operator = "+"
                                third_num = random.choice(list(range(int((100 - result)/3), 100 - result + 1)))
                        final_result_str = (
                                str(first_num) + " " + first_operator + " " + str(second_num) + " " +
                                second_operator + str(third_num))
                        result = eval(final_result_str)
                        if all(map(lambda x: 0 if x - 10 < 0 else 1,
                                   random.sample([first_num, second_num, third_num],
                                                 2))) and 0 <= result <= 100:
                            proper_formular = True
                    question_str = str(final_result_str) + " = "
                sheet.write(curr_row - 1, colIdx, question_str)
            curr_row += 11
            data_rows_wrote_count += 1
    if not os.path.exists(tar_path):
        os.makedirs(tar_path)
    version = datetime.strftime(datetime.now(), format="%Y%m%d%H%M%S")
    wb.save(tar_path + f"/100以内混合加减乘除法和竖式_{version}.xls")
    return tar_path + f"/100以内混合加减乘除法和竖式_{version}.xls"


def set_style(name, height, bold=False):
    style = xlwt.XFStyle()  # 初始化样式
    font = xlwt.Font()  # 为样式创建字体
    font.name = name
    font.bold = bold
    font.color_index = 4
    font.height = height
    style.font = font
    return style


def get_common_divisor(num: int) -> list[int]:
    divisors = []
    for i in range(1, num + 1):
        if num % i == 0:
            divisors.append(i)
    return divisors


def get_md_list():
    m_list = []
    d_list = []
    m_d_list = []
    for i in range(15):
        first_num = random.choice(list(range(2, 10)))
        if first_num > 5:
            second_num = random.choice(list(range(2, 6)))
        else:
            second_num = random.choice(list(range(2, 10)))
        m_list.append(str(first_num) + " * " + str(second_num) + " = ")
        d_list.append(str(first_num * second_num) + " ÷ " + str(random.choice([first_num, second_num])) + " = ")
    m_d_list.extend(m_list)
    m_d_list.extend(d_list)
    random.shuffle(m_d_list)
    return m_d_list


def get_random_md(md_list):
    return md_list.pop()


def enhance_number_selection(num: int, weight: float = 0.2):
    if num <= 10:
        num = num + int(random.choice(range(20, 101)) * weight)
    return num


