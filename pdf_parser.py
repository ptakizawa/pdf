# -*- coding: utf-8 -*-
from pdfminer.pdfparser import PDFParser 
from pdfminer.pdfdocument import PDFDocument, PDFNoOutlines
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine, LTFigure, LTImage, LTChar
from PyPDF2 import PdfFileWriter, PdfFileReader 
import sys
import os
from binascii import b2a_hex

def with_pdf(pdf_doc, pdf_pwd, fn, *args):
	"""Open the pdf document, apply the function, return the results"""
	result = None
	try:
		# open the pdf file
		fp = open(pdf_doc, 'rb')
		# create a parser object associated with the file opbject
		parser = PDFParser(fp)
		# create a PDFDocument object that stores the document structure; supply the password for initialization
		doc = PDFDocument(parser, pdf_pwd)
		# connect the parser and document objects
		#parser.set_document(doc)

		if doc.is_extractable:
			# apply the function and return the result
			result = fn(doc, *args)

		# close the pdf file
		fp.close()
	except IOError():
		# the file doesn't exist of similar problem
		print "There was a problem opening or processing the file"
	return result

def _parse_pages(doc, images_folder):
	"""With an open PDFDocument object, get the pages and parse and each one"""
	rsrcmgr = PDFResourceManager()
	laparams = LAParams()
	device = PDFPageAggregator(rsrcmgr, laparams=laparams)
	interpreter = PDFPageInterpreter(rsrcmgr, device)

	text_content = [] # a list of strings, each representing text collected from each page of the doc

	for i, page in enumerate(PDFPage.create_pages(doc)):
		interpreter.process_page(page)
		# receive the LTPage object for this page
		layout = device.get_result()
		# layout is an LTPage object which may contain child objects like LTTextBox, LTFigure, LTImage, etc.
		text_content.append(parse_lt_objs(layout, (i+1), images_folder))
	return text_content

def _separate_slides(doc, slides_folder):
	infile = PdfFileReader(open(doc, 'rb'))
	for i in xrange(infile.getNumPages()):
		page = infile.getPage(i)
		outfile = PdfFileWriter()
		outfile.addPage(page)
		with open('%s/slide_%02d.pdf' % (slides_folder, i+1), 'wb') as f:
			outfile.write(f)

def parse_lt_objs(lt_objs, page_number, images_folder, text=[]):
	"""Iterate through the list of LT* objects and capture the text or image data contained in each"""
	text_content = []
	for lt_obj in lt_objs:
		if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine):
			# text
			text_content.append(lt_obj.get_text())
		elif isinstance(lt_obj, LTImage):
			# an image, so save it to the designmated folder and note it's place in the text
			saved_file = save_image(lt_obj, page_number, images_folder)
			if saved_file:
				# use html style <img /> tag to mark the position of the image within the text
				text_content.append('<img src="'+os.path.join(images_folder, saved_file)+'" />')
			else:
				print >> sys.stderr, "Error saving image on page", page_number, lt_obj.__repr__
		elif isinstance(lt_obj, LTFigure):
			# LTFigure objects are containers for other LT* objects, so recurse through the children
			text_content.append(parse_lt_objs(lt_obj, page_number, images_folder, text_content))
	return '\n'.join(text_content)

def write_file (folder, filename, filedata, flags='w'):
    """Write the file data to the folder and filename combination
    (flags: 'w' for write text, 'wb' for write binary, use 'a' instead of 'w' for append)"""
    result = False
    if os.path.isdir(folder):
        try:
            file_obj = open(os.path.join(folder, filename), flags)
            file_obj.write(filedata)
            file_obj.close()
            result = True
        except IOError:
            pass
    return result

def save_image(lt_image, page_number, images_folder):
	"""Try to save the image data from this LTImage object, and return the file name, if successful"""
	result = None
	if lt_image.stream:
		file_stream = lt_image.stream.get_rawdata()
		if file_stream:
			file_ext = determine_image_type(file_stream[0:4])
			if file_ext:
				file_name = ''.join([str(page_number), '_', lt_image.name, file_ext])
				if write_file(images_folder, file_name, file_stream, flags='wb'):
					result = file_name
	return result

def save_slide(slide, page_number, slides_folder):
	"""Try to save the slide and return file name, if succcessful"""
	result = None
	if slide.stream:
		file_stream = slide.stream.get_rawdata()
		if file_stream:
			file_name = ''.join(['slide', '_', page_number])
			if write_file(slides_folder, file_name, file_stream, flags='wb'):
				return file_name

def determine_image_type (stream_first_4_bytes):
    """Find out the image file type based on the magic number comparison of the first 4 (or 2) bytes"""
    file_type = None
    bytes_as_hex = b2a_hex(stream_first_4_bytes)
    if bytes_as_hex.startswith('ffd8'):
        file_type = '.jpeg'
    elif bytes_as_hex == '89504e47':
        file_type = '.png'
    elif bytes_as_hex == '47494638':
        file_type = '.gif'
    elif bytes_as_hex.startswith('424d'):
        file_type = '.bmp'
    return file_type

def get_pages(pdf_doc, pdf_pwd='', images_folder='tmp/', slides_folder='slides/'):
	"""Process each of these pages in this pdf file and print the entire text to stdout"""
	#print '\n\n'.join(with_pdf(pdf_doc, pdf_pwd, _parse_pages, *tuple([images_folder])))
	#print '\n\n'.join(with_pdf(pdf_doc, pdf_pwd, _separate_slides, *tuple([slides_folder])))
	_separate_slides(pdf_doc, slides_folder)

if __name__ == '__main__':
	get_pages(str(sys.argv[1]))