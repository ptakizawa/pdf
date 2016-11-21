import os
BASE_FOLDER = '/Users/ptakizawa/curriculum_pdfs'

def get_files(folder):
    file_list = []
    for path, dirs, files in os.walk(BASE_FOLDER):
        for f in files:
            path_array = path.split('/')
            document = {}
            document['course'] = path_array[-2]
            document['pedagogy'] = path_array[-1]
            document['session_title'] = f.strip('.pdf')
            document['url'] = '/'.join([path, f])
            file_list.append(document)
    return file_list

pdf_list = get_files(BASE_FOLDER)
for item in pdf_list:
    for key, value in item.iteritems():
        print key + ': ' + value

        	

