#!/usr/bin/python
import re

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
from pdfminer.layout import LAParams
from pdfminer.converter import PDFPageAggregator
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine, LTFigure, LTImage, LTChar, LTAnno, LTText, LTTextBoxHorizontal

def to_bytestring (s, enc='utf-8'):
    """Convert the given unicode string to a bytestring, using the standard encoding,
    unless it's already a bytestring"""
    if s:
        if isinstance(s, str):
            return s
        else:
            return s.encode(enc)

def update_page_text_hash (h, lt_obj, pct=0.2):
    """Use the bbox x0,x1 values within pct% to produce lists of associated text within the hash"""
    x0 = lt_obj.bbox[0]
    x1 = lt_obj.bbox[2]
    key_found = False
    str1 = to_bytestring(lt_obj.get_text())
    for k, v in h.items():
        hash_x0 = k[0]
        if x0 >= (hash_x0 * (1.0-pct)) and (hash_x0 * (1.0+pct)) >= x0:
            hash_x1 = k[1]
            if x1 >= (hash_x1 * (1.0-pct)) and (hash_x1 * (1.0+pct)) >= x1:
                # the text inside this LT* object was positioned at the same
                # width as a prior series of text, so it belongs together
                key_found = True
                v.append(str1)
                h[k] = v
    if not key_found:
        # the text, based on width, is a new series,
        # so it gets its own series (entry in the hash)
        h[(x0,x1)] = [str1]
    return h


def dataparse_lt_objs(line_text):
     cuttext = re.sub(r'.*u\'',"", line_text)
     rstrip1 = cuttext.rstrip('>')
     rstrip2 = rstrip1.rstrip('\'')
     #print rstrip2, "\n"

     data = rstrip2.split("\\n")
     for datapoints in data:
        print datapoints


     return


def parse_lt_objs (lt_objs, page_number, text=[]):
    """Iterate through the list of LT* objects and capture the text or image data contained in each"""
    text_content = [] 

    page_text = {} # k=(x0, x1) of the bbox, v=list of text strings within that bbox width (physical column)
    
    for lt_obj in lt_objs:
        if isinstance(lt_obj, LTTextBoxHorizontal): 
            #print "All OBJS:",  lt_objs,  "\t Obj:",  lt_obj,  "\n"
            dataparse_lt_objs(str(lt_obj))

        #print "More Details"
        #print(lt_obj.__class__.__name__)
        #print(lt_obj.bbox)

        # if isinstance(lt_obj, LTTextBox):             
        #     print "LTTextBox:\n"
        #     # text, so arrange is logically based on its column width
        #     # page_text = update_page_text_hash(page_text, lt_obj)
        #     text_content = to_bytestring(lt_obj.get_text())
        #     print text_content
        #     parse_lt_objs(lt_obj, page_number)
        # elif isinstance(lt_obj, LTTextLine):
        #     print "LTTextLine:\n"
        #     text_content = to_bytestring(lt_obj.get_text())
        #     print text_content
        #     parse_lt_objs(lt_obj, page_number)
        # elif isinstance(lt_obj, LTChar) or isinstance(lt_obj, LTAnno):
        #     print "LTChar or LTAnno!\n"
        #     text_content = to_bytestring(lt_obj.get_text())
        #     print text_content            
        # elif isinstance(lt_obj, LTFigure) or isinstance(lt_obj, LTImage):
        #     print "LTFigure or LTImage!\n"
        # elif isinstance(lt_obj, LTLine):
        #     print "LTLine!\n"
        #     text_content = to_bytestring(lt_obj.get_text())
        #     print text_content
        #     parse_lt_objs(lt_obj, page_number)
        # elif isinstance(lt_obj, LTRect):
        #     print "LTRect!\n"
        # elif isinstance(lt_obj, LTCurve):
        #     print "LTCurve!\n"
        # elif isinstance(lt_obj, LTText):
        #     print "LTText!\n"
        #     text_content = to_bytestring(lt_obj.get_text())
        #     print text_content
        #     parse_lt_objs(lt_obj, page_number)
        # else:
        #     print "\nZZZZZZZZZZZZZZ\n"


        if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine):
            # text, so arrange is logically based on its column width
            page_text = update_page_text_hash(page_text, lt_obj)
            #print page_text, "\n"

    for k, v in sorted([(key,value) for (key,value) in page_text.items()]):
        # sort the page_text hash by the keys (x0,x1 values of the bbox),
        # which produces a top-down, left-to-right sequence of related columns
        text_content.append("\n".join(v))

	# return '\n'.join(text_content)
	return

# Open a PDF file.
fp = open('/home/nzc5047/Documents/admin_processing_dates.pdf', 'rb')
# Create a PDF parser object associated with the file object.
parser = PDFParser(fp)
# Create a PDF document object that stores the document structure.
# Supply the password for initialization.
document = PDFDocument(parser)
# Check if the document allows text extraction. If not, abort.
if not document.is_extractable:
    raise PDFTextExtractionNotAllowed
# Create a PDF resource manager object that stores shared resources.
rsrcmgr = PDFResourceManager()
# Create a PDF device object.
device = PDFDevice(rsrcmgr)
# Create a PDF interpreter object.
interpreter = PDFPageInterpreter(rsrcmgr, device)
# Process each page contained in the document.
for page in PDFPage.create_pages(document):
    interpreter.process_page(page)


# Set parameters for analysis.
laparams = LAParams()
# Create a PDF page aggregator object.
device = PDFPageAggregator(rsrcmgr, laparams=laparams)
interpreter = PDFPageInterpreter(rsrcmgr, device)
i = 0
text_content = [] # a list of strings, each representing text collected from each page of the doc
for page in PDFPage.create_pages(document):
    i += 1;
    print "New Page : " + str(i) + "\n"
    interpreter.process_page(page)
    # receive the LTPage object for the page.
    layout = device.get_result()
    parse_lt_objs(layout, (i+1))
    if i > 0:
        break
print text_content
