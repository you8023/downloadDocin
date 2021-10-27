import requests
from fpdf import FPDF
from PIL import Image
from lxml import etree
import re, time, random, os

def getTiltleUrl(originUrl):
	# 获取资料的标题和通用的url链接
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

def getPictures(theurl, path):
	# 获取图片
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

def combinePictures2Pdf(path, pdfName, allNum):
	# 合并图片为pdf
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

def removePictures(path, allNum):
	# 删除原图片
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

if __name__ == '__main__':
	# 文件存储的路径
	path = 'E:\\test\\Docin\\'
	# 需要的资料的网址
	# originUrl = 'https://www.docin.com/p-977106193.html?docfrom=rrela'
	originUrl = input('input the url: ')
	result = getTiltleUrl(originUrl)
	title = result[0].split('.')[0]
	url = result[1]
	print(title, url)
	allNum = getPictures(url, path)
	pdfName = path + title + '.pdf'
	combinePictures2Pdf(path, pdfName, allNum)
	removePictures(path, allNum)
