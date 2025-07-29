Amazon Description Scraper
==========================

.. image:: https://img.shields.io/pypi/v/amazon-description-scraper.svg?logo=python&logoColor=white
   :target: https://pypi.org/project/amazon-description-scraper/

.. image:: https://github.com/ryzanbui02/amazon-description-scraper/actions/workflows/test-and-deploy.yaml/badge.svg
    :target: https://github.com/ryzanbui02/amazon-description-scraper/actions/workflows/test-and-deploy.yaml

Webscrape project to get Amazon products' descriptions.


Requirements
------------

This library is compatible with Python >= 3.9 and requires:

- ``bs4``
- ``fake-useragent``
- ``pandas``
- ``requests``
- ``selenium``


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
