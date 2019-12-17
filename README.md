# md_pic  
markdown图片转换相关  

## 简单介绍

python环境为2.7  
对markdown的图片一直很纠结，放在图床是很简单，但是有可能图床失效，然后就有了这个脚本，用来将图片转成自己想要的形式  

markdown图片分为2种形式: 行内式, 参考式  
行内式可以有3种形式(注意title可选):
1. `![Alt text](/path/to/img.jpg "Optional title")`
2. `![Alt text](web_img_path "Optional title")`
3. `![Alt text](base64编码图片 "Optional title")`

参考式在文中只有1种形式:  
`![Alt text][id]`  
在文中任何位置都可以放参考内容(这里只实现放在最后)  
`[id]: url/to/image  "Optional title attribute"`  
`url/to/image`其实也类似行内式的3种, 所以其实也是3种  

转换可以有2种结果:
1. 将图片直接用base64的形式编码在文件中(参考式)，结果为单个文件, 缺点是单个文件体积过大
2. 将图片保存到pics文件夹中，md文件引用本地文件夹中的图片，内容简练，缺点是有另外的图片文件

## 使用命令  
```bat
Usage: md_pic.py [-h] -t {pic_in,pic_out} -s SRC_PATH [-d DST_PATH]

Convert markdown pictures.
Example:
    Turn pictures into md file: python md_pic.py -s src.md -t pic_in -d dst.md
    Turn pictures to folder: python md_pic.py -s src.md -t pic_out -d dst.md

optional arguments:
  -h, --help            show this help message and exit
  -t {pic_in,pic_out}, --type {pic_in,pic_out}
                        the method to use
  -s SRC_PATH, --src_path SRC_PATH
                        the path of the source file to be converted
  -d DST_PATH, --dst_path DST_PATH
                        the path of the converted file


```

## 参考链接
markdown官网: https://daringfireball.net/projects/markdown/  

## 后感
虽然功能很简单, 但格式稍微多几样, 如果没有搞清楚就随便写脚本, 就可能会漏掉一些情况  
所以一定要尽可能把各种情况考虑到, 先把大概的逻辑整理清楚, 按照整理好的逻辑实现, 才不会越写越乱  

20191218