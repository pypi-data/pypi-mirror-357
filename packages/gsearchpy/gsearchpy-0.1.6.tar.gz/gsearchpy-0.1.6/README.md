## 📦 gsearchpy 
**gsearchpy** is a lightweight Python package that allows you to perform Google Search queries programmatically and retrieve raw search result pages with ease.

It is built for developers, researchers, and automation enthusiasts who need a flexible interface to Google Search.

---

## Table of Contents

- [Features](#-features)
- [Installation](#-installation)
- [Example Usage](#-example-usage)


## 🚀 Features

- 🔍 Perform Google searches using customizable parameters  
- 📄 Retrieve raw HTML content and filtered data of Google search results  
- 🔁 Built-in pagination support  
---


## 📦 Installation

```
pip install gsearchpy
```

### Using Github
```
pip install git+https://@github.com/itsguptaaman/gsearchpy.git
```

### After Installation run this command to setup the drivers and dependency
```
gsearchpy
```


## 📦 Example Usage

### For raw data response 
```python
from gsearchpy import GoogleScraper

scraper = GoogleScraper()
html = scraper.google_search(query)
```

### For clean data
```python
from gsearchpy import GoogleScraper

query = "best VSCode extensions for productivity"
scraper = GoogleScraper()
html = scraper.google_search(query)
print(scraper.google_search_clean_data(html))
```

### To get google maps data or any other data use tbm paramter
```python
from gsearchpy import GoogleScraper

google = GoogleScraper()
query = "coffee shop in dubai"
html = google.google_search(query, tbm="lcl")
print(google.local_search_clean_data(html))
```

### Also you can use v2 except for google search you can use this for lcl, images, news, and etc.
```python
from gsearchpy import GoogleScraper

google = GoogleScraper()
query = "coffee shop in dubai"
html = google.google_search_v2("plumbers", page_number=2, gl="ahemdabad")
print(google.local_search_clean_data(html))
```

