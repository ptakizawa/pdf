from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
import re
from io import StringIO
from io import open

def readPDF(pdfFile):
    fp = open(pdfFile, 'rb') 
    parser = PDFParser(fp)

    document = PDFDocument(parser)

    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    laparams = LAParams()
    codec = 'utf-8'
    device = TextConverter(rsrcmgr, retstr, codec=codec,  laparams=laparams)
    intepreter = PDFPageInterpreter(rsrcmgr, device)

    for page in PDFPage.create_pages(document):
        interpreter.process_page(page)
        data = retstr.getvalue()

    device.close()
    return data

pdfFile = open('BC1_LE003N_Proteins.pdf')
outputString = readPDF(pdfFile)
print outputString
pdfFile.close()

