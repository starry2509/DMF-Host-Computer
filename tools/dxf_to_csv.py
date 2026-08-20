"""
开发工具：从 chip_shape.dxf 生成 chip_point.csv。
用法（在项目根目录）:
    python tools/dxf_to_csv.py
依赖: pip install dxfgrabber
"""
import csv
import os
import sys

ELECTRODE_NUM = 120

ELECTRODE_ID_ORDER = [
    115, 25, 24, 23, 22, 21, 20, 19, 105, 104,
    103, 102, 101, 100, 32, 31, 30, 29, 28, 27,
    106, 98, 97, 96, 95, 94, 93, 40, 39, 38,
    37, 36, 35, 34, 90, 89, 88, 87, 86, 85,
    47, 43, 82, 78, 49, 52, 48, 46, 41, 50,
    75, 74, 76, 73, 45, 44, 42, 91, 83, 81,
    80, 79, 26, 18, 33, 77, 84, 92, 99, 107,
    6, 119, 9, 60, 56, 55, 53, 51, 59, 58,
    57, 54, 66, 67, 68, 71, 65, 69, 70, 72,
    4, 116, 10, 17, 11, 13, 14, 15, 16, 114,
    108, 109, 110, 111, 112, 118, 113, 7, 12, 1,
    117, 8, 124, 3, 5, 121, 122, 123, 2, 120,
]


def get_cord_from_one_electrode(polyline, electrode_id):
    coord_list = [electrode_id]
    for (x0, y0) in polyline.points:
        coord_list.append(x0)
        coord_list.append(y0)
    return coord_list


def extract_from_dxf(input_file, electrode_ids):
    import dxfgrabber

    dxf = dxfgrabber.readfile(input_file)
    port_id_list = []
    idx = 0
    for e in dxf.entities:
        if e.dxftype == 'LWPOLYLINE':
            port_id_list.append(get_cord_from_one_electrode(e, electrode_ids[idx]))
            idx += 1
    return port_id_list


def write_csv(output_file, port_id_list):
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for line in port_id_list:
            writer.writerow(line)


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_file = os.path.join(root, 'chip', 'chip_shape.dxf')
    output_file = os.path.join(root, 'chip', 'chip_point.csv')

    if len(ELECTRODE_ID_ORDER) != ELECTRODE_NUM:
        print('Error: electrode id count mismatch')
        sys.exit(1)
    if not os.path.isfile(input_file):
        print(f'Error: missing {input_file}')
        sys.exit(1)

    port_id_list = extract_from_dxf(input_file, ELECTRODE_ID_ORDER)
    write_csv(output_file, port_id_list)
    print(f'Wrote {len(port_id_list)} electrodes to {output_file}')


if __name__ == '__main__':
    main()
