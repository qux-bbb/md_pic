# coding:utf8
# author: qux
"""
markdown图片转换相关

图片可能有3种: 在线图片/本地图片/base64编码

脚本有2个功能
1. 将图片直接用base64的形式编码在文件中
2. 将图片保存到pic文件夹中

"""

import os
import sys
import re
import base64
import requests
from hashlib import md5
from optparse import OptionParser


def pic_in(src_path, dst_path):
    """
	将md中涉及到的图片转为内嵌base64的形式
	:param src_path: 原md文件路径
	:param dst_path: 转换后的md文件路径
	:return: None
	"""
    md_folder = os.path.dirname(src_path)

    src_file = open(src_path, 'r')
    md_content = src_file.read()
    src_file.close()

    # 正则 找到图片路径
    matches = re.findall(r'!\[.*]\((.*)\)', md_content)

    for match in matches:
        if match.startswith('data:image'):
            continue
        if match.startswith('http'):
            print(match + ' Converting...')
            pic_content = requests.get(match).content
        else:
            pic_path = os.path.join(md_folder, match)
            print(pic_path + ' Converting...')
            pic_content = open(pic_path, 'rb').read()

        pic_encode = base64.b64encode(pic_content)

        base64_pic = ''
        # 图片类型经过试验没必要区分，所以直接硬编码
        # 可行的类型有: jpeg/png/gif
        # 精准识别需要引入magic库，不方便
        base64_pic += 'data:image/png;base64,'
        base64_pic += pic_encode
        md_content = md_content.replace(match, base64_pic)

    dst_file = open(dst_path, 'w')
    dst_file.write(md_content)
    dst_file.close()


def pic_out(src_path, dst_path):
    """
	将md中涉及到的图片转为本地图片的形式
	:param src_path: 原md文件路径
	:param dst_path: 转换后的md文件路径
	:return: None
	"""
    md_folder = os.path.dirname(src_path)

    src_file = open(src_path, 'r')
    md_content = src_file.read()
    src_file.close()

    # 正则 找到图片路径
    matches = re.findall(r'!\[.*]\((.*)\)', md_content)

    pic_folder_path = os.path.join(md_folder, 'pics')
    if matches and not os.path.exists(pic_folder_path):
        os.mkdir(pic_folder_path)

    for match in matches:
        if match.startswith(('data:image', 'http')):
            if match.startswith('data:image'):
                base64_pic = re.findall(r'data:image/.+?;base64,(.+)', match)[0].strip()
                pic_content = base64_pic.decode('base64')
            if match.startswith('http'):
                pic_content = requests.get(match).content
            pic_md5 = md5(pic_content).hexdigest()
            pic_path = os.path.join(pic_folder_path, '%s.png' % pic_md5)
            with open(pic_path, 'wb') as f:
                f.write(pic_content)
            md_content = md_content.replace(match, './pics/%s.png' % pic_md5)
            print(pic_path + ' Converted.')

    dst_file = open(dst_path, 'w')
    dst_file.write(md_content)
    dst_file.close()


def main():
    parser = OptionParser(
        'Usage:    python md_pic.py [options]\n'
        'Example:\n'
        '  Turn pics into md file: python md_pic.py -f src.md -t pic_in -d dst.md\n'
        '  Turn pics to pic folder: python md_pic.py -f src.md -t pic_out -d dst.md\n')
    parser.add_option('-f', '--file', dest='src_path', help='the source file to turn')
    parser.add_option('-d', '--dest_file', dest='dst_path', help='the destination file processed')
    parser.add_option('-t', '--type', dest='method', help='the method to use, could be one of them: pic_in | pic_out')

    (options, args) = parser.parse_args()

    src_path = options.src_path
    dst_path = options.dst_path
    method = options.method

    if len(sys.argv) == 1:
        parser.print_usage()
        exit(0)

    if not src_path or not os.path.exists(src_path):
        print('Cannot get src file!!!')
        exit(0)
    if not method or method not in ['pic_in', 'pic_out']:
        print('Need type or type is error!!!')
        exit(0)
    if not dst_path:
        dst_path = src_path + '.modify'

    if method == 'pic_in':
        pic_in(src_path, dst_path)
    else:
        pic_out(src_path, dst_path)

    print('Done!')

    return


if __name__ == '__main__':
    main()
