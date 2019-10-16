# md_pic  
markdown图片转换相关  

## 简单介绍

对markdown的图片一直很纠结，放在图床是很简单，但是有可能图床失效，然后就有了这个脚本，用来将图片转成自己想要的形式

转换可以有2种结果:
1. 将图片直接用base64的形式编码在文件中，结果为单个文件，缺点是大段的base64串影响看源文件效果
3. 将图片保存到pic文件夹中，md文件引用本地文件夹中的图片，内容简练，缺点是有另外的图片文件

因为图床不确定，就不写转成图床形式的逻辑了

## 使用命令  
```bat
Usage:    python md_pic.py [options]                                                                                                                  Example:
  Turn pics into md file: python md_pic.py -f src.md -t pic_in -d dst.md
  Turn pics to pic folder: python md_pic.py -f src.md -t pic_out -d dst.md


Options:
  -h, --help            show this help message and exit
  -f SRC_PATH, --file=SRC_PATH
                        the source file to turn
  -d DST_PATH, --dest_file=DST_PATH
                        the destination file processed
  -t METHOD, --type=METHOD
                        the method to use, could be one of them: pic_in |
                        pic_out
```
