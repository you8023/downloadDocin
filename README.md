# downloadDocin
免费自动下载豆丁网的资料Download materials in Docin freely and automatically
如遇图片显示不全，请到我的[博客](https://www.jianshu.com/p/3817e06d6a92)观看，欢迎点赞留言！

最近在查找资料时，在[豆丁网](https://www.docin.com/)上找到不少有用的资料，比如说一些课程的PPT之类的，但是只能在线看，而且还有广告，但是下载下来要钱，而且要价不菲，于是动起了歪脑筋，寻思着搞一个爬虫直接下载下来就可以离线看了，也方便资料的存储管理。本教程已完结，请放心食用，效果如下（该效果图采用[screentogif](https://www.screentogif.com/)软件录制，特此鸣谢）：
![豆丁网资料自动下载效果展示](https://upload-images.jianshu.io/upload_images/5714082-ab2ee2ea09375988.gif?imageMogr2/auto-orient/strip)


本代码免费开源，不想了解原理的可以跳过到使用部分直接使用，希望能给我点个赞以支持开发，如果方便的话，github来一颗星星更好啦！
开源代码地址：[https://github.com/you8023/downloadDocin](https://github.com/you8023/downloadDocin)，直接下载按照使用方法使用即可，如遇问题，欢迎在文章下方留言或在[github](https://github.com/you8023/downloadDocin/issues)上提issue。

## 开发环境
* Windows 10
* Sublime Text 3
* Python 3.8
* python库：lxml、fpdf、requests

## 环境搭建
1. 首先安装Python，直接到官网下载安装即可
2. 安装Python库
键盘同时按下`win`+`R`，在弹出的对话框中输入`cmd`按回车
在弹出的黑框中输入命令安装python库：
```
pip install lxml
pip install fpdf
pip install requests
```
至此，环境搭建完毕

## 分析&设计
在编写代码前，需要对需求及网页进行分析，明确我们需要的东西的位置

### 需求分析
首先明确需求，我们需要将豆丁网上我们需要的资料爬取下来，通过对页面元素进行观察，发现上面的资料，无论何种格式，均是以图片的形式进行展示，因此，考虑将其保存为pdf以方便查看。提取的输入输出如下：
* 输入：所需资料的网址
* 输出：资料的pdf文件，其中包含：
  * 资料的每张图片
  * 资料标题

### 页面分析
#### 页面标题
打开想要的资料的网页，这里以[这个网页](https://www.docin.com/p-456842624.html)为例，首先，鼠标右键检查，找到标题元素：
![标题](https://upload-images.jianshu.io/upload_images/5714082-979f491a36c290e4.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
可以发现，标题所属的为`span`标签，class为`doc_title fs_c_76`，因此，可以据此定位标题所在

#### 页面资料内容
再以此方法找到资料所属的标签：
![网页元素](https://upload-images.jianshu.io/upload_images/5714082-7c2b9fa4dd351d65.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
发现网页的资料均是以图片形式显示，因此，目标确定，我们仅需要找到这个链接即可
复制链接，直接用浏览器打开，发现果然就是我们要找的这张图片
接着，分析链接`https://docimg1.docin.com/docinpic.jsp?file=456842624&width=942&sid=LE-fLs-BXk4g4mtVLS2D8apgA9Z5X3NNeoZbh0mHZkW*C1Zz1LvKe8xey1BsO1BG&pageno=1&pcimg=1`，发现其中有三个关键字段，分别是：
* file
* sid
* pageno

其中，经过观察，发现`file`字段的数字和网页链接`https://www.docin.com/p-456842624.html`的数字一致；
`pageno`字段则是第几页；
而`sid`经过打开另一个资料的网页测试，发现不同的资料具有不同的`sid`，观察其编码，没发现规律，最终，经过仔细分析，在`source`页面源码中找到了一个关键字段`flash_param_hzq`：
![flash_param_hzq字段的发现](https://upload-images.jianshu.io/upload_images/5714082-6173e3a5c0281b38.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

虽然和`sid`字段并不完全一致，但使用该字段作为`sid`也能得到图片，因此，提取该网页的`flash_param_hzq`字段即可；

## 代码实现
页面分析完毕，即可开始编写代码。

### 获取资料标题和内容的通用url
首先，使用`requests`获取网页内容，并使用`lxml`将其封装为一个HTML对象方便后续解析：
```python
html = etree.HTML(requests.get(originUrl).text)
```
然后使用`xpath`提取标题：
```python
title = html.xpath('//span[@class="doc_title fs_c_76"]/text()')[0]
```
其中，`//span`表示匹配任意`span`标签，使用`[@class=""]`匹配`class`属性，使用`/text()`提取标签内的内容，由于返回的内容为一个元祖，因此使用`[0]`取第一个元素

使用正则表达式匹配`file`字段：
```python
fileId = re.findall('\-\d+\.',originUrl)[0][1:-1]
```
其中，`\d`代表匹配数字，`+`表示匹配一次或多次，`[1:-1]`表示取结果的第二个字符到倒数第二个字符

将HTML对象转为字符串：
```python
theHTML = etree.tostring(html).decode('utf-8')
```
使用正则表达式匹配`flash_param_hzq`字段：
```python
sid = re.findall('flash_param_hzq:\"[\w\*\-]+\"', theHTML)[0][17:-1]
```
其中，`\w`表示匹配数字或字母
至此，该部分函数书写完毕，完整代码为：
```python
def getTiltleUrl(originUrl):
	html = etree.HTML(requests.get(originUrl).text)
	theHTML = etree.tostring(html).decode('utf-8')
	# print(theHTML)
	try:
		title = html.xpath('//span[@class="doc_title fs_c_76"]/text()')[0]
	except:
		title = html.xpath('//title/text()')
	fileId = re.findall('\-\d+\.',originUrl)[0][1:-1]

	sid = re.findall('flash_param_hzq:\"[\w\*\-]+\"', theHTML)[0][17:-1]
	url = 'https://docimg1.docin.com/docinpic.jsp?file=' + fileId + '&width=1000&sid=' + sid + '&pcimg=1&pageno='
	return title, url
```
### 获取图片
通过上面的函数获取到通用的链接后，仅需要更改`pageno`字段即可获取所有图片，使用`requests`获取到图片后，直接将文件流写入到文件中即可。但在后续代码运行过程中发现图片格式报错，因此，使用`PIL`标准化图片。完整代码如下：
```python
def getPictures(theurl, path):
	pagenum = 1
	headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36"
	}
	allNum = 0
	while pagenum>0:
		# time.sleep(3*random.random())
		print('Downloading picture ' + str(pagenum))
		url = theurl + str(pagenum)
		img_req = requests.get(url=url, headers=headers)
		if img_req.content==b'sid error or Invalid!':
			allNum = pagenum-1
			print('Downloading finished, the count of all pictures is ' + str(allNum))
			pagenum = -1
			break;
		file_name = path + str(pagenum) + '.png'
		f = open(file_name, 'wb')
		f.write(img_req.content)
		f.close()
		# 将图片保存为标准png格式
		im = Image.open(file_name)
		im.save(file_name)
		pagenum += 1
	return allNum
```

### 合并图片为pdf
这里主要使用`fpdf`库合并图片为pdf，代码如下：
```python
def combinePictures2Pdf(path, pdfName, allNum):
	print('Start combining the pictures...')
	pagenum = 1
	file_name = path + str(pagenum) + '.png'
	cover = Image.open(file_name)
	width, height = cover.size
	pdf = FPDF(unit = "pt", format = [width, height])
	while allNum>=pagenum:
		try:
			print('combining picture ' + str(pagenum))
			file_name = path + str(pagenum) + '.png'
			pdf.add_page()
			pdf.image(file_name, 0, 0)
			pagenum += 1
		except Exception as e:
			print(e)
			break;
	pdf.output(pdfName, "F")
```

其中：
* `pdf = FPDF(unit = "pt", format = [width, height])`规定了pdf的尺寸
* `pdf.add_page()`将为pdf添加一张空白页面
* `pdf.image(file_name, 0, 0)`则是将图片绘制到该空白页面上，后两个参数为绘制的起始xy坐标
* `pdf.output(pdfName, "F")`则是生成pdf文件

### 删除原图片
pdf生成完毕之后，之前保存到本地的图片就没有用武之地了，这时需要删去所有图片，删去某个文件的语句为：
```python
os.remove(file_name)
```
完整代码如下：
```python
def removePictures(path, allNum):
	pagenum = 1
	while allNum>=pagenum:
		try:
			print('deleting picture ' + str(pagenum))
			file_name = path + str(pagenum) + '.png'
			os.remove(file_name)
			pagenum += 1
		except Exception as e:
			print(e)
			break;
```

### 主函数
最后，书写语句依次调用函数，自动化下载图片，合并为pdf，并删去原文件：
```python
if __name__ == '__main__':
	path = 'E:\\test\\Docin\\'
	# originUrl = 'https://www.docin.com/p-977106193.html?docfrom=rrela'
	originUrl = input('input the url: ')
	result = getTiltleUrl(originUrl)
	title = result[0].split('.')[0]
	url = result[1]
	print(title, url)
	allNum = getPictures(url, path)
	pdfName = title + '.pdf'
	combinePictures2Pdf(path, pdfName, allNum)
	removePictures(path, allNum)
```
其中：
* `path`为保存文件的路径，注意，必须为转义`\`后的绝对路径
* 原网址使用`input`函数以让用户自行输入

## 代码使用
源码在[GitHub](https://github.com/you8023/downloadDocin)上，直接下载即可使用。
1. 进入到源码所在的文件夹，使用编辑器（记事本亦可）打开源码文件，修改最下方`main`函数中的`path`路径为你想要保存文件的路径
2. 在文件所在的文件夹的地址栏输入`cmd`，按下回车，在出现的黑框中输入以下命令：
```python
python downloadPPT.py
```
3. 按下回车，当出现提示语句时输入网址，按下回车
4. 静等程序跑完即可，下载的资料在第一步输入的路径里面

如图所示：
![豆丁网资料自动下载效果展示](https://upload-images.jianshu.io/upload_images/5714082-ab2ee2ea09375988.gif?imageMogr2/auto-orient/strip)
