Amazon Description Scraper
==========================

.. image:: https://img.shields.io/pypi/v/keepa.svg?logo=python&logoColor=white
   :target: https://pypi.org/project/keepa/

.. image:: https://readthedocs.org/projects/keepaapi/badge/?version=latest
    :target: https://keepaapi.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://app.codacy.com/project/badge/Grade/9452f99f297c4a6eac14e2d21189ab6f
  :target: https://www.codacy.com/gh/akaszynski/keepa/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=akaszynski/keepa&amp;utm_campaign=Badge_Grade

Webscrape project to get suppliers' catalogs.


Features
--------

- Uses Selenium and BeautifulSoup
- Modular scraping system


Installation
------------
Module can be installed from `PyPI <https://pypi.org/project/amazon-scraper>`_ with:

.. code::

  pip install amazon-scraper


Brief Example
-------------

.. code:: python

  from zendom import AmazonScraper
  
  proxy_key = "XXXXXXXXXXX" # enter real proxy key here
  client = AmazonScraper(proxy_key=proxy_key, jsonl_output_path="data/output.jsonl")
  asins = ["B07WC4TDJJ"]
  results = client.scrape(asins=asins, marketplace="US")
  print(results)
