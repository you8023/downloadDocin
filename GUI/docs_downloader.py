import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog
from docs_download import Ui_DocsDownload
import webbrowser
import requests
from fpdf import FPDF
from PIL import Image
from lxml import etree
import re, time, random, os

class Docin_download:
    def  __init__ (self, path, originUrl, QTextBrowser):
        self.path = path
        self.originUrl = originUrl
        self.QTextBrowser = QTextBrowser

    def add_text(self, added_text):
        self.QTextBrowser.append(added_text)
        self.QTextBrowser.moveCursor(self.QTextBrowser.textCursor().End)  #文本框显示到底部
        QtWidgets.QApplication.processEvents()

    def getTiltleUrl(self, originUrl):
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

    def getPictures(self, theurl, path):
        # 获取图片
        pagenum = 1
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36"
        }
        allNum = 0
        while pagenum>0:
            # time.sleep(3*random.random())
            url = theurl + str(pagenum)
            img_req = requests.get(url=url, headers=headers)
            if img_req.content==b'sid error or Invalid!':
                self.add_text('正在下载第' + str(pagenum) + '页...')
                allNum = pagenum-1
                self.add_text('下载结束，文档共有' + str(allNum) + '页')
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

    def combinePictures2Pdf(self, path, pdfName, allNum):
        # 合并图片为pdf
        self.add_text('开始合并页面为PDF：')
        pagenum = 1
        file_name = path + str(pagenum) + '.png'
        cover = Image.open(file_name)
        width, height = cover.size
        pdf = FPDF(unit = "pt", format = [width, height])
        while allNum>=pagenum:
            try:
                self.add_text('正在合并页面' + str(pagenum))
                file_name = path + str(pagenum) + '.png'
                pdf.add_page()
                pdf.image(file_name, 0, 0)
                pagenum += 1
            except Exception as e:
                self.add_text(e)
                break;
        pdf.output(pdfName, "F")

    def removePictures(self, path, allNum):
        # 删除原图片
        pagenum = 1
        while allNum>=pagenum:
            try:
                self.add_text('删除页面源文件' + str(pagenum))
                file_name = path + str(pagenum) + '.png'
                os.remove(file_name)
                pagenum += 1
            except Exception as e:
                self.add_text(e)
                break;

    def docin_download(self):
        result = self.getTiltleUrl(self.originUrl)
        title = result[0].split('.')[0]
        url = result[1]
        # print(title, url)
        self.add_text("文档名：" + str(title))
        allNum = self.getPictures(url, self.path)
        pdfName = title + '.pdf'
        self.combinePictures2Pdf(self.path, pdfName, allNum)
        self.removePictures(self.path, allNum)
        self.add_text("文献下载完成！请到设定的保存目录处查看🍉")

class mywindow(QtWidgets.QWidget, Ui_DocsDownload):
    def  __init__ (self):
        super(mywindow, self).__init__()
        self.setupUi(self) 
        self.radioButton.setChecked(True)
        self.toolButton_2.clicked.connect(self.choose_folder)
        self.toolButton_3.clicked.connect(self.start_download)
        self.toolButton_5.clicked.connect(self.get_source_code)

    def add_text(self, added_text):
        self.textBrowser.append(added_text)
        self.textBrowser.moveCursor(self.textBrowser.textCursor().End)  #文本框显示到底部
        QtWidgets.QApplication.processEvents()

    def choose_folder(self):
        #选取文件夹
        foldername = QFileDialog.getExistingDirectory(self, "选取文件夹", "C:/")
        print(foldername)
        self.lineEdit_2.setText(foldername)

    def get_source_code(self):
        url = "https://github.com/you8023/downloadDocin"
        webbrowser.open_new_tab(url)

    def start_download(self):
        save_folder = self.lineEdit_2.text() # 保存结果的路径
        originUrl = self.lineEdit.text() # url
        if not (save_folder and originUrl):
            self.add_text("请检查上面的参数是否填写完整！")
            return
        else:
            self.add_text("程序已开始运行，请稍等...")

        if self.radioButton.isChecked() == True:
            QTextBrowser = self.textBrowser
            save_folder = save_folder.rstrip('/') + '/'
            if re.findall('https://(www.)?docin.com', originUrl) == []:
                self.add_text("请输入正确的豆丁网文献网址！")
            else:
                downloader = Docin_download(save_folder, originUrl, QTextBrowser)
                downloader.docin_download()
        elif self.radioButton_2.isChecked() == True:
            self.add_text("道客巴巴文档源正在集成中，请等待软件更新😋")
        else:
            self.add_text("请选择下载资料的网站👻")


if __name__=="__main__":
    
    app=QtWidgets.QApplication(sys.argv)
    ui = mywindow()
    ui.show()
    sys.exit(app.exec_())