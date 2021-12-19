# md_pic
markdown图片转换相关  

## 简单介绍
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

如果要保存网络图片，需要安装requests: `pip install requests`  

## 使用命令  
```r
usage: md_pic.py [-h] {pic_in,pic_out} path

Convert markdown pictures.
Example:
    Turn pictures into md file: python md_pic.py pic_in hello.md
    Turn pictures to folder: python md_pic.py pic_out hello.md

positional arguments:
  {pic_in,pic_out}  the method to use
  path              the path of the file to be converted

optional arguments:
  -h, --help        show this help message and exit
```

## 使用示例
test目录下有测试用的例子  
```r
# 把图片放到readme.md中
py -3 md_pic_py3.py pic_in test/readme.md

# 把所有图片都存成文件的形式
py -3 md_pic_py3.py pic_out test/readme.md
```

## 参考链接
markdown官网: https://daringfireball.net/projects/markdown/  

## 后感
虽然功能很简单, 但格式稍微多几样, 如果没有搞清楚就随便写脚本, 就可能会漏掉一些情况  
所以一定要尽可能把各种情况考虑到, 先把大概的逻辑整理清楚, 按照整理好的逻辑实现, 才不会越写越乱  

python2和python3兼容太麻烦了，所以分成了2个脚本  


---
20191218  
