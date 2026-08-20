"""从 CSV 读取电极几何定义（运行时布局数据源）。"""
import csv


def read_defination_from_csv_file(filename):
    electrode_list = {}
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or not row[0].isdigit():
                continue
            electrode_list[int(row[0])] = []
            for loc in row:
                try:
                    loc_num = float(loc)
                except ValueError:
                    break
                electrode_list[int(row[0])].append(loc_num)
    return electrode_list
