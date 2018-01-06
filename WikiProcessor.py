
import io
import os
from contextlib import closing
import requests
from tqdm import tqdm
import WikiExtractor
from cElementTree import iterparse


DOWNLOAD_ROOT = 'https://dumps.wikimedia.org/'

class WikiDump():

	def __init__(self, data_dir, title = None, page = 0):
		self.data_dir = data_dir
		self.stub_dict = {}
		for stub in os.listdir(self.download_dir):
		    s = stub.split("p")
	    	self.stub_dict[stub] = (s[2], s[3])
	    self.title = title
	    self.page = 0

	def __iter__(self):
        """
        Iterate over the pages of a Wikipedia articles database dump,
        yielding one (page id, page title, page content) 3-tuple at a time.

        Yields:
            Tuple[str, str, str]: page id, title, content as plaintext
        """
        filepath = None
        end = False

        while not end:
	        for stub, (first, last) in self.stub_dict:
	        	if last >= self.page and first <= self.page:
	        		filepath = os.path.join(clean_dir, stub)

		    if filepath != None:
	        	for event, elem in iterparse(io.open(filepath)):
	        		if elem.tag = "doc":
	        			page_id = elem.tag["id"]
	        			if page_id < self.page:
	        				elem.clear()
	        				continue()
	        			title, content = elem.text.split(".", 1)
	        			if self.title != None and title.lower() != self.title.lower():
	        				elem.clear()
	        				continue()	
		        		elem.clear()
		        		self.page++
		        		yield page_id, title, content

				filepath = None
			else:
				end = True

		#TODO: change to spit out timestamp


class WikiProcessor():

    def __init__(self, data_dir, lang='en', version='latest'):
        self.lang = lang
        self.version = version
    	self.data_dir = os.path.join(data_dir, '{lang}wiki/{version}/'.format(version=self.version, lang=self.lang))
    	self.download_dir = os.path.join(data_dir + 'downloads')
    	self.clean_dir = os.path.join(data_dir + 'clean')
    	self.corpus_dir = os.path.join(data_dir + 'corpus')
		self.dump_url = compat.urljoin(DOWNLOAD_ROOT, self.data_dir)


	def write_streaming_download_file(url, filepath, mode='wt', encoding=None,
	                                  chunk_size=1024):
	    """
	    Download content from ``url`` in a stream; write successive chunks of size
	    ``chunk_size`` bytes to disk at ``filepath``. Files with appropriate extensions
	    are compressed with gzip or bz2 automatically. Any intermediate folders
	    not found on disk may automatically be created.
	    """
	    decode_unicode = True if 't' in mode else False
        if not os.path.exists(self.download_dir):
			os.makedirs(self.download_dir)
	    # always close the connection
	    with closing(requests.get(url, stream=True)) as r:
	        # set fallback encoding if unable to infer from headers
	        if r.encoding is None:
	            r.encoding = 'utf-8'
	        with io.open(filepath, mode=mode, encoding=encoding) as f:
	            pbar = tqdm(
	                unit='B', unit_scale=True,
	                total=int(r.headers.get('content-length', 0)))
	            chunks = r.iter_content(
	                chunk_size=chunk_size, decode_unicode=decode_unicode)
	            for chunk in chunks:
	                # needed (?) to filter out "keep-alive" new chunks
	                if chunk:
	                    pbar.update(len(chunk))
	                    f.write(chunk)


    def download(self, force=False):
    	dump_page = requests.get(self.dump_url)
    	soup = BeautifulSoup(dump_page, 'html.parser')
    	stub_list = []
    	for link in soup.find_all('a'):
    		stub = link.get('href')
    		if 'pages-meta-history' in stub 
    			and '.7z' in stub 
    			and 'rss' not in stub:
    			stub_list.append(stub)

    	for stub, _ in self.stub_dict:
	    	fname = os.path.join(self.download_dir, stub)
	    	url = compat.urljoin(self.dump_url, stub)
			if os.path.isfile(fname) and force is False:
			    LOGGER.warning(
			        'File %s already exists; skipping download...', fname)
			    return
		    LOGGER.info(
		        'Downloading data from %s and writing it to %s', url, fname)
		    fileio.write_streaming_download_file(
		        url, fname, mode='wb', encoding=None,
		        chunk_size=1024)

	def process_dumps(self, force = False, template_file = None, file_compress = False, process_count = 1):
		if not os.path.exists(self.clean_dir):
			os.makedirs(self.clean_dir)
		for filename in os.listdir(self.download_dir):
			if os.path.exists(os.path.join(self.clean_dir, filename)) and not force:
				continue;
			WikiExtractor.process_dump(os.path.join(self.download_dir, filename), template_file,
				os.path.join(self.clean_dir, stub), file_compress, process_count)


	def generate_graphs(self, force = False, title = None):
		
		current_title = None

		for id, iter_title, content in WikiDump(self.clean_dir, title = title):
			
			if current_title = None:
				current_title = iter_title
			
			if iter_title == current_title:

				textacy.Doc(content)
				#corpus
				
			#generate models


			#score docs

			#generate graphs

			#serialize everything? mebbe not lol











