Amazon Description Scraper
==========================

.. image:: https://img.shields.io/pypi/v/amazon-description-scraper.svg?logo=python&logoColor=white
   :target: https://pypi.org/project/amazon-description-scraper/

Webscrape project to get suppliers' catalogs.


Features
--------

- Uses Selenium and BeautifulSoup
- Modular scraping system


Installation
------------
Module can be installed from `PyPI <https://pypi.org/project/amazon-description-scraper>`_ with:

.. code::

  pip install amazon-description-scraper


Brief Example
-------------

.. code:: python

  from amzsc import AmazonScraper
  
  proxy_key = "XXXXXXXXXXX" # enter real proxy key here
  client = AmazonScraper(proxy_key=proxy_key, jsonl_output_path="data/output.jsonl")
  asins = ["B07WC4TDJJ"]
  results = client.scrape(asins=asins, marketplace="US")
  print(results)
