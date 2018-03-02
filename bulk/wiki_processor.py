
import io
import os
from contextlib import closing
import requests
from tqdm import tqdm
import wiki_extractor
from pymongo import MongoClient


DOWNLOAD_ROOT = 'https://dumps.wikimedia.org/'

##
# Mongo options
HOST = 'localhost'
PORT = 27017

class WikiProcessor():

    def __init__(self, data_dir, lang='en', version='latest', db_name='wikihistory_db',collection_name='plaintext_articles'):
        self.lang = lang
        self.version = version
    	self.data_dir = os.path.join(data_dir, '{lang}wiki/{version}/'.format(version=self.version, lang=self.lang))
    	self.download_dir = os.path.join(data_dir + 'downloads')
    	self.clean_dir = os.path.join(data_dir + 'clean')
    	self.corpus_dir = os.path.join(data_dir + 'corpus')
		self.dump_url = compat.urljoin(DOWNLOAD_ROOT, self.data_dir)
		self.mongo_collection = MongoClient(HOST, PORT)[db_name][collection_name]

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
			WikiExtractor.process_dump(os.path.join(self.download_dir, filename), template_file, process_count, mongo_collection)

	def full_article_iterator():
		cursor = mongo_collection.find({}, {_id: 0, page: 1}).noCursorTimeout()
		for item in cursor:
  			yield item

	def articles_by_title_aggregator():
		




class WikiProcessor():

    def __init__(self, data_dir, lang='en', version='latest'):
        self.lang = lang
        self.version = version
    	self.data_dir = os.path.join(data_dir, '{lang}wiki/{version}/'.format(version=self.version, lang=self.lang))
    	self.download_dir = os.path.join(data_dir + 'downloads')
    	self.clean_dir = os.path.join(data_dir + 'clean')
    	self.corpus_dir = os.path.join(data_dir + 'corpus')
		self.dump_url = compat.urljoin(DOWNLOAD_ROOT, self.data_dir)


	

	def getRemlist(title):


	def applyModel(title = None, remove = True):
	    """
	        Applies PatchModel to the history for Wikipedia page, title.
	        Returns the full history tranformed into a graph according to the model,
	            the PatchModel, and the most recent content.
	    """

	    title=title.replace(" ", "_")

	    # Make folders for model, graph, and content files
	    if not os.path.isdir('GMLs'):
	        os.mkdir('GMLs')
	    if not os.path.isdir('models'):
	        os.mkdir('models')
	    if not os.path.isdir('content'):
	        os.mkdir('content')

	    print "Setting up distance comparison . . ."

	    # Set up semantic distance comparison
	    if not os.path.isdir("dictionaries") or not os.path.isfile('dictionaries/'+title+'.dict'):
	        proc.saveDictionary(title)
	    dictionary=proc.readDictionary(title)
	    
	    if not os.path.isdir("corpus") or not os.path.isfile('corpus/'+title+'.mm'):
	        proc.saveCorpus(title, dictionary)
	    corpus=proc.readCorpus(title)
	    
	    if not os.path.isdir("tfidf") or not os.path.isfile('tfidf/'+title+'.tfidf'):
	        proc.saveTfidf(title, corpus, True)
	    tfidf=proc.loadTfidf(title)
	    
	    if not os.path.isdir("lsi") or not os.path.isfile('lsi/'+title+'.lsi'):
	        proc.saveLsi(title, tfidf, corpus, dictionary, 300)
	    lsi=proc.loadLsi(title)


	    # Get the list of vertices to remove
	    if remove:
	        remList = getRemlist(title)
	       

	    print "Applying model . . ."

	    model = PatchModel()
	    prev = ""
	    pid=0
	    offset='0'
	    wikiit=proc.WikiIter()
	    
	    for (rvid, timestamp, content) in wikiit.__iter__(title, offset):
	       
	        # Apply to the PatchModel and write dependencies to graph.
	        if remove and rvid in remList:
	            remList.remove(rvid)
	    
	        else:
	            # Get semantic distance
	            dist = 1-proc.scoreDoc(title, prev, content, dictionary, tfidf, lsi)[0][1]
	            
	            # Apply PatchModel
	            content=content.encode("ascii", "replace")
	            contentList=content.split()
	            prevList=prev.split()
	            ps = PatchSet.psdiff(pid, prevList, contentList)
	            pid+=len(ps.patches)
	            for p in ps.patches:
	                model.apply_patch(p, timestamp, dist) #list of out-edges from rev
	            
	            prev = content
	        
	        
	    if remove:
	        cachefile = title.replace(" ", "_")+'_rem.txt'
	    else:
	        cachefile = title.replace(" ", "_")+'.txt'

	    # Writes graph to file
	    nx.write_gml(model.graph, "GMLs/"+cachefile)
	        
	    # Write model to file
	    modelFile = open("models/"+ cachefile, "w")
	    line = ""
	    for patch in model.model:
	        line+= str(patch[0])+' '+str(patch[1])+'\n'
	    modelFile.write(line)
	    modelFile.close()

	    # Write content to file
	    contentFile = open("content/"+ cachefile, "w")
	    contentFile.write(content)
	    contentFile.close()
	    
    	return model.graph, content, model.model











