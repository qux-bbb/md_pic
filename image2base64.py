#! python3
# coding:utf8
# author: qux
'''
将md中的图片转为base64，硬编码于md中，方便转移保存
可以处理本地和网络上的图片
'''

import sys
import re
import base64
import requests


def main(file_name):
	# 读取原md文件
	md_content = open(file_name,'r').read()

	# 正则 找到图片路径
	matches = re.findall(r"!\[.*]\((.*)\)",md_content)

	# 逐张图片处理
	for match in matches:
		print(match + " Converting...")

		if match.startswith("http"):
			img_content = requests.get(match).content
		else:
			img_content = open(match,"rb").read()
		# 直接用encode转过来的base64会有回车，所以用base64模块
		img_encode = base64.b64encode(img_content)

		base64_img = ""
		# 图片类型经过试验没必要区分，所以直接硬编码
		base64_img += "data:image/jpeg;base64,"
		base64_img += img_encode
		md_content = md_content.replace(match,base64_img)

	open(file_name,'w').write(md_content)

	print("Done!")


if __name__ == '__main__':
	if(len(sys.argv) == 1):
		print('\nusage example:')
		print(' python image2base64.py a.md\n')
	else:
		para = sys.argv
		main(para[1])
