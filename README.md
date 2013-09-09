This project does a search into TPB, looking for results for a given query string.

It returns a list of search results, each having the following data:
* torrent name
* magnet URL
* no. of seeders
* set of files
  * name
  * approx. size in bytes

The list is ordered by decreasing number of seeders.


Usage:

scrapy crawl tpb -o out.json -t jsonlines -a query="enter your query here"

The command above will write a set of JSON results in a file called out.json.

