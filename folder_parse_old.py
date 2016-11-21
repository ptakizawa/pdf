import os
from PyPDF2 import PdfFileWriter, PdfFileReader 

base_folder = 'files/fall2015'

def _separate_slides(doc, slides_folder):
	infile = PdfFileReader(open(doc, 'rb'))
	for i in xrange(infile.getNumPages()):
		page = infile.getPage(i)
		outfile = PdfFileWriter()
		outfile.addPage(page)
		with open('%s/slide_%02d.pdf' % (slides_folder, i+1), 'wb') as f:
			outfile.write(f)

for path, dirs, files in os.walk(base_folder):
    for d in dirs:
        if d == "Lectures_Presentations":
        	print path
        	os.chdir(path+'/'+d)
        	for files in os.listdir(os.getcwd()):
        		folder = files.split('.')[0]
        		if folder is not '':
        		    os.mkdir(folder)
        		    _separate_slides(files, folder)
        	

