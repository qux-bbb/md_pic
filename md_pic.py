# coding:utf8
# author: qux
"""
markdown图片转换相关

图片可能有3种: 在线图片/本地图片/base64编码

脚本有2个功能
1. 将图片直接用base64的形式编码在文件中(参考式)
2. 将图片保存到pics文件夹中

"""
import argparse
import base64
import os
import re
import shutil
import textwrap
from hashlib import md5

import requests


class MdPic:
    refer_resource_re = re.compile(r'\[(?P<refer_id>.+?)\]:\s+(?P<refer_content_with_title>.+)\n*')
    inline_re = re.compile(r'!\[(?P<alt_text>.+)]\((?P<content_with_title>.*)\)')
    refer_re = re.compile(r'!\[(?P<alt_text>.+)]\[(?P<refer_id>.*)\]')
    base64_img_re = re.compile(r'data:image/.+?;base64,(.+)')

    def __init__(self, file_path, pic_folder_name='pics'):
        self.pic_folder_name = pic_folder_name  # 转换后的图片文件夹
        self.md_folder = os.path.dirname(file_path)  # 原md文件所在文件夹
        self.file_path = file_path  # md文件路径
        self.md_content = None  # 原md文件内容
        self.existing_references = {}  # 所有已存在的引用
        self.inline_matches = None  # 行内式图片集
        self.refer_matches = None  # 引用式图片集

        src_file = open(file_path, 'r')
        self.md_content = src_file.read()
        src_file.close()

        for match in re.finditer(MdPic.refer_resource_re, self.md_content):
            refer_id = match.group('refer_id')
            if refer_id in self.existing_references:
                continue
            match_content, match_title = MdPic.split_content_title(match.group('refer_content_with_title'))
            self.existing_references[refer_id] = {
                'raw': match.group(),
                'content': match_content,
                'title': match_title,
                'changed': False,
                'used': False
            }

        # ![Alt text](/path/to/img.jpg "Optional title")
        self.inline_matches = re.finditer(MdPic.inline_re, self.md_content)
        # ![Alt text][id]
        self.refer_matches = re.finditer(MdPic.refer_re, self.md_content)

    @staticmethod
    def split_content_title(content_title):
        """
        拆分content和title
        :param content_title: 可能包含title的内容
        :return: str,str or str,None
        """
        if re.search(r'\s', content_title):
            return content_title.split(None, 1)
        else:
            return content_title, None

    def get_base64_pic_and_pic_content(self, match_content):
        if match_content.startswith('http'):
            pic_content = requests.get(match_content).content
        else:
            pic_path = os.path.join(self.md_folder, match_content)
            pic_content = open(pic_path, 'rb').read()
        pic_encoded = base64.b64encode(pic_content)
        # 图片类型经过试验没必要区分，所以直接硬编码
        # 可行的类型有: jpeg/png/gif
        # 精准识别需要引入magic库，不方便
        base64_pic = 'data:image/png;base64,' + pic_encoded
        return base64_pic, pic_content

    def pic_in(self):
        """
        将md中涉及到的图片转为内嵌base64的形式, base64放在文件末尾
        :return: None
        """

        reference_ids = self.existing_references.keys()

        new_references = {}

        for match in self.inline_matches:
            alt_text = match.group('alt_text')
            match_content, match_title = MdPic.split_content_title(match.group('content_with_title'))
            if match_content.startswith('data:image'):
                base64_pic = match_content
                pic_encoded = re.search(MdPic.base64_img_re, match_content).group(1).strip()
                pic_content = pic_encoded.decode('base64')
            else:
                base64_pic, pic_content = self.get_base64_pic_and_pic_content(match_content)
            pic_md5 = md5(pic_content).hexdigest()

            self.md_content = self.md_content.replace(match.group(),
                                                      '![{alt_text}][{pic_md5}]'.format(alt_text=alt_text,
                                                                                        pic_md5=pic_md5)
                                                      )

            if pic_md5 in reference_ids:
                if not new_references[pic_md5]['title'] and match_title:
                    new_references[pic_md5]['title'] = match_title
            else:
                reference_ids.append(pic_md5)
                new_references[pic_md5] = {
                    'content': base64_pic,
                    'title': match_title
                }

        for match in self.refer_matches:
            alt_text = match.group('alt_text')
            if match.group('refer_id'):
                refer_id = match.group('refer_id')
            else:
                refer_id = alt_text
            if self.existing_references[refer_id]['content'].startswith('data:image'):
                pass
            else:
                self.existing_references[refer_id]['content'], _ = self.get_base64_pic_and_pic_content(self.existing_references[refer_id]['content'])
                self.existing_references[refer_id]['changed'] = True
        for k in self.existing_references:
            if self.existing_references[k]['changed']:
                if self.existing_references[k]['title']:
                    self.md_content = self.md_content.replace(self.existing_references[k]['raw'],
                                                              '[{refer_id}]: {refer_content} {refer_title}\n'.format(
                                                                  refer_id=k,
                                                                  refer_content=self.existing_references[k]['content'],
                                                                  refer_title=self.existing_references[k]['title']
                                                              ))
                else:
                    self.md_content = self.md_content.replace(self.existing_references[k]['raw'],
                                                              '[{refer_id}]: {refer_content}\n'.format(
                                                                  refer_id=k,
                                                                  refer_content=self.existing_references[k]['content'])
                                                              )
                print(k + ' Converted.')

        if self.existing_references:
            if not self.md_content.endswith('\n'):
                self.md_content += '\n'
        else:
            # 保证引用出现前至少有2个回车符
            if self.md_content.endswith('\n\n'):
                pass
            elif self.md_content.endswith('\n'):
                self.md_content += '\n'
            else:
                self.md_content += '\n\n'

        for refer_id in new_references:
            if new_references[refer_id]['title']:
                self.md_content += '[{refer_id}]: {refer_content} {refer_title}\n'.format(
                    refer_id=refer_id,
                    refer_content=new_references[refer_id]['content'],
                    refer_title=new_references[refer_id]['title']
                )
            else:
                self.md_content += '[{refer_id}]: {refer_content}\n'.format(
                    refer_id=refer_id,
                    refer_content=new_references[refer_id]['content']
                )
            print(refer_id + ' Converted.')

        dst_file = open(self.file_path, 'w')
        dst_file.write(self.md_content)
        dst_file.close()

    def pic_out(self):
        """
        将md中涉及到的图片转为本地图片的形式, 放在图片文件夹中
        :return: None
        """

        pic_folder_path = os.path.join(self.md_folder, self.pic_folder_name)
        if not os.path.exists(pic_folder_path):
            os.mkdir(pic_folder_path)
        if re.search(r'!\[.*]\(.*\)', self.md_content) and not os.path.exists(pic_folder_path):
            os.mkdir(pic_folder_path)

        for match in self.inline_matches:
            alt_text = match.group('alt_text')
            match_content, match_title = MdPic.split_content_title(match.group('content_with_title'))
            if match_content.startswith(('data:image', 'http')):
                if match_content.startswith('data:image'):
                    base64_pic = re.findall(MdPic.base64_img_re, match_content)[0].strip()
                    pic_content = base64_pic.decode('base64')
                else:
                    pic_content = requests.get(match_content).content
                pic_md5 = md5(pic_content).hexdigest()
                pic_path = os.path.join(pic_folder_path, '%s.png' % pic_md5)
                with open(pic_path, 'wb') as f:
                    f.write(pic_content)
                if match_title:
                    self.md_content = self.md_content.replace(match.group(),
                                                              '![{alt_text}](./{pic_folder_name}/{pic_md5}.png {title})'.format(
                                                                  alt_text=alt_text,
                                                                  pic_folder_name=self.pic_folder_name,
                                                                  pic_md5=pic_md5,
                                                                  title=match_title)
                                                              )
                else:
                    self.md_content = self.md_content.replace(match.group(),
                                                              '![{alt_text}](./{pic_folder_name}/{pic_md5}.png)'.format(
                                                                  alt_text=alt_text,
                                                                  pic_folder_name=self.pic_folder_name,
                                                                  pic_md5=pic_md5)
                                                              )
                print(pic_path + ' Converted.')

        for match in self.refer_matches:
            alt_text = match.group('alt_text')
            if match.group('refer_id'):
                refer_id = match.group('refer_id')
            else:
                refer_id = alt_text
            if self.existing_references[refer_id]['content'].startswith(('data:image', 'http')):
                if self.existing_references[refer_id]['content'].startswith('data:image'):
                    base64_pic = re.findall(MdPic.base64_img_re,
                                            self.existing_references[refer_id]['content'])[0].strip()
                    pic_content = base64_pic.decode('base64')
                else:
                    pic_content = requests.get(self.existing_references[refer_id]['content']).content
                pic_md5 = md5(pic_content).hexdigest()

                if self.existing_references[refer_id]['title']:
                    self.md_content = self.md_content.replace(match.group(),
                                                              '![{alt_text}](./{pic_folder_name}/{pic_md5}.png {title})'.format(
                                                                  alt_text=alt_text,
                                                                  pic_folder_name=self.pic_folder_name,
                                                                  pic_md5=pic_md5,
                                                                  title=self.existing_references[refer_id]['title'])
                                                              )
                else:
                    self.md_content = self.md_content.replace(match.group(),
                                                              '![{alt_text}](./{pic_folder_name}/{pic_md5}.png)'.format(
                                                                  alt_text=alt_text,
                                                                  pic_folder_name=self.pic_folder_name,
                                                                  pic_md5=pic_md5)
                                                              )
                pic_path = os.path.join(pic_folder_path, '%s.png' % pic_md5)
                if not os.path.exists(pic_path):
                    with open(pic_path, 'wb') as f:
                        f.write(pic_content)
                    print(pic_path + ' Converted.')

                self.existing_references[refer_id]['used'] = True

        # 移除已经使用的reference
        for k in self.existing_references:
            if self.existing_references[k]['used']:
                self.md_content = self.md_content.replace(self.existing_references[k]['raw'], '')

        dst_file = open(self.file_path, 'w')
        dst_file.write(self.md_content)
        dst_file.close()


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''
        Convert markdown pictures.
        Example:
            Turn pictures into md file: python md_pic.py pic_in hello.md
            Turn pictures to folder: python md_pic.py pic_out hello.md'''))
    parser.add_argument('type', choices=['pic_in', 'pic_out'], help='the method to use')
    parser.add_argument('path', help='the path of the file to be converted')
    args = parser.parse_args()

    if not os.path.exists(args.path):
        print('The file does not exist!!!')
        exit(0)
    
    shutil.copyfile(args.path, args.path+'.bak')

    md_pic = MdPic(args.path)
    if args.type == 'pic_in':
        md_pic.pic_in()
    else:
        md_pic.pic_out()

    print('Done!')
    return


if __name__ == '__main__':
    main()
