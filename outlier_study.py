import requests
import metric
random_url = "https://en.wikipedia.org/wiki/Special:Random"

for x in range(0,50):
	actual_url = requests.head(random_url, timeout=100.0 , headers={'Accept-Encoding': 'identity'}).headers.get('location', random_url)
	split_url = actual_url.split('/')
	article_name = split_url[-1]
	metric.wiki2color(article_name, True, True, True, True, None, None, False, 'Outlier_Study')
	

