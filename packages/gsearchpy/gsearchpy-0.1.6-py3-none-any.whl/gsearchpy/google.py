
import os
import time
import json
import random
import string
import re
import traceback
import threading

from seleniumbase import SB
from user_agent import generate_user_agent
from curl_cffi import requests
from bs4 import BeautifulSoup
import urllib


DEFAULT_COOKIES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "google_cookies.json")


class CookieManager:
    def __init__(self, cookies_path=DEFAULT_COOKIES_PATH):
        self.cookies_path = cookies_path
        self._cookies_cache = None
        self._lock = threading.Lock()


    def _human_typing(self, sb, selector, text, delay=0.1):
        for char in text:
            sb.send_keys(selector, char)
            time.sleep(random.uniform(delay - 0.05, delay + 0.05))


    def _generate_cookies(self):
        random_keyword = random.choice(self._get_kewords())
        user_agent = generate_user_agent(navigator='chrome')

        with SB(uc=True, headless=True, cft=True) as sb:
            sb.driver.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": user_agent})
            url = "https://www.google.com"
            sb.activate_cdp_mode(url)
            try:
                sb.open(url)

                accept_buttons = [
                    'button:contains("Acceptă tot")',
                    'button:contains("Accept all")',
                    'button:contains("Aceptar todo")',
                    'button:contains("Alle akzeptieren")',
                    'button#L2AGLb'
                ]

                for btn in accept_buttons:
                    try:
                        sb.wait_for_element_visible(btn, timeout=3)
                        sb.click(btn)
                        time.sleep(1)
                        break
                    except:
                        pass

                sb.wait_for_element("textarea.gLFyf", timeout=10)
                self._human_typing(sb, "textarea.gLFyf", random_keyword)

                sb.execute_script("document.querySelector('textarea.gLFyf').form.submit();")
                sb.wait_for_element("#search", timeout=10)
                time.sleep(random.uniform(2, 4))

                ck = sb.get_cookies()
                cookies = {c['name']: c['value'] for c in ck}

                with open(self.cookies_path, "w") as f:
                    json.dump(cookies, f, indent=4)

                return cookies

            except Exception as e:
                traceback.print_exc()
                sb.save_screenshot("debug_screenshot.png")
                print("Cookie generation failed:", e)
                return {}


    def get_cookies(self):
        with self._lock:
            if self._cookies_cache is None:
                print("Generating fresh cookies...")
                self._cookies_cache = self._generate_cookies()
            return self._cookies_cache


    def invalidate(self):
        with self._lock:
            print("Invalidating cookies cache...")
            self._cookies_cache = None


    def _get_kewords(self):
        return [
                "how to build a web scraper in python",
                "best VSCode extensions for productivity",
                "why do cats purr",
                "funniest AI fails",
                "top programming languages 2025",
                "how long can a snail sleep",
                "Python automation",
                "docker vs kubernetes",
                "is cereal a soup",
                "latest AI tools 2025",
                "how to deploy Django on AWS",
                "machine learning vs deep learning",
                "difference between Git and GitHub",
                "how do magnets work",
                "top 10 coding interview questions",
                "why JavaScript is weird",
                "should you learn Rust in 2025",
                "is pineapple on pizza good",
                "best Linux distros for developers",
                "how to contribute to open source",
                "what is quantum computing",
                "top VSCode themes for night coding",
                "build a chatbot with Python",
                "why is regex so hard",
                "what does an AI model see",
                "best keyboard shortcuts in VSCode",
                "how to stay focused while coding",
                "is ChatGPT replacing developers",
                "top 5 Python libraries for automation",
                "how does DNS work"
            ]

class GoogleScraper:
    def __init__(self, cookies_path=DEFAULT_COOKIES_PATH):
        self.cookies_path = cookies_path
        self.cookie_manager = CookieManager()


    def _read_cookies_from_file(self):
        with open(self.cookies_path, "r") as f:
            cookies = json.load(f)
        return cookies


    def _get_headers(self):
        return {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9',
            'downlink': '10',
            'priority': 'u=0, i',
            'referer': 'https://www.google.com/',
            'rtt': '50',
            'sec-ch-prefers-color-scheme': 'dark',
            'sec-ch-ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
            'sec-ch-ua-arch': '"x86"',
            'sec-ch-ua-bitness': '"64"',
            'sec-ch-ua-form-factors': '"Desktop"',
            'sec-ch-ua-full-version': '"135.0.7049.114"',
            'sec-ch-ua-full-version-list': '"Google Chrome";v="135.0.7049.114", "Not-A.Brand";v="8.0.0.0", "Chromium";v="135.0.7049.114"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-model': '""',
            'sec-ch-ua-platform': '"Linux"',
            'sec-ch-ua-platform-version': '"6.11.0"',
            'sec-ch-ua-wow64': '?0',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'upgrade-insecure-requests': '1',
            'user-agent': generate_user_agent(navigator='chrome'),
            'x-browser-channel': 'stable',
        }


    def _get_response(self, params, retry=3):
        try:
            if os.path.exists(self.cookies_path):
                cookies = self._read_cookies_from_file()
            else:
                self.cookie_manager.invalidate()
                cookies = self.cookie_manager.get_cookies()

            headers = self._get_headers()
            time.sleep(random.uniform(1, 3))

            response = requests.get(
                "https://www.google.com/search",
                params=params,
                headers=headers,
                cookies=cookies
            )

            data = response.content.decode("utf-8")
            if "SearchResultsPage" in data:
                return data, response
            else:
                if retry > 0:
                    print("Retrying after cookie refresh...")
                    self.cookie_manager.invalidate()
                    return self._get_response(params, retry - 1)
                return None, response
        except Exception as e:
            traceback.print_exc()
            print("Error during request:", e)
            return None, None


    def google_search(self, query, hl="en", gl="in", num=20, start=0, safe="active", unique="0", tbm=None, tbs=None, **kwargs):
        """
        Perform a Google search and return the search results.

        Parameters:
        ----------
        query : str
            The search query to be submitted to Google.
        hl : str, optional
            Interface language of the search results (default is "en").
        gl : str, optional
            Geolocation or country code for localizing search results (default is "in").
        num : int, optional
            Number of results to fetch per page (default is 20; max allowed is 100).
        start : int, optional
            The index of the first result to return (used for pagination; default is 0).
        safe : str, optional
            Enables or disables Google's SafeSearch (default is "active").
        unique : str, optional
            Enables duplicate content filtering ("1") or disables it ("0") (default is "0").
        tbm : str, optional
            Specifies the type of search (e.g., "isch" for images, "vid" for videos, "lcl" for local search).
        tbs : str, optional
            Applies additional search filters such as date range.
        **kwargs : dict
            Any additional parameters to be included in the search request.

        Returns:
        -------
        dict
            A dictionary of query parameters to be used in a Google search URL.
        """
        params = {
            "q": query,
            "hl": hl,
            "gl": gl,
            "num": num,
            "start": start,
            "safe": safe,
            "filter": unique,
        }

        if tbm:
            params["tbm"] = tbm
        if tbs:
            params["tbs"] = tbs

        params.update(kwargs)
        data, response = self._get_response(params)
        return data


    def _get_sponsor_data(self, sp_data):
        data = {}
        
        header = None
        a_tag = None
        title = None
        link = None
        logo = None

        sponsor_data = sp_data.find('div', {'class': 'v5yQqb'})

        if sponsor_data:
            span = sponsor_data.find("span", {'class': 'OSrXXb'})
            header = span.text if span else None
            a_tag = sponsor_data.find('a')
        
        if header:
            data.update({"header": header})

        description_data = sp_data.find('div', {'class': 'p4wth'})
        description = description_data.text if description_data else None
        
        if description:
            data.update({"description": description})
        

        if a_tag:
            link = a_tag.get('href')
            title = a_tag.find('span').text if a_tag.find('span') else None
            logo = a_tag.find("img").get("src") if a_tag.find("img") else None

        if link:
            data.update({"link": link})
        
        # if logo:
        #     data.update({"logo_link": logo})
        
        if title:
            data.update({"title": title})

        return data
    

    def _get_box_data(self, box):
        data = {}
        box_data = box.find("span", {"class": "V9tjod"})
        if not box_data:
            return data
        
        link = box_data.find("a").get("href")
        if link:
            data.update({"link": link})
        
        logo = box_data.find("img").get("src")
        # if logo:
        #     data.update({"logo_link": logo})
        
        title = box_data.find("h3").text if box_data.find("h3") else None
        if title:
            data.update({"title": title})

        header_data = box_data.find('div', {'class': "CA5RN"})
        header = None
        header_details = None
        if header_data:
            header = header_data.find('span').text if header_data.find('span') else None
            header_div = header_data.find('div', {'class': 'byrV5b'})
            header_details = header_div.text if header_div else None

        if header:
            data.update({"header": header})

        if header_details:
            data.update({"header_details": header_details})

        description_data = box.find('div', {'class': 'kb0PBd A9Y9g'})
        description = None
        if description_data:
            description = description_data.find('span').text if description_data.find('span') else None

        if description:
            data.update({"description": description})

        return data
    

    def google_search_clean_data(self, html):
        """
        Filters Google search data based on the provided HTML content.

        Parameters:
        -----------
        html : str
            The HTML content to filter.

        Returns:
        -------
        dict
            A dictionary containing the filtered Google search data.
        """
        if not html:
            return {"error": "Please pass proper html data"}
        
        soup = BeautifulSoup(html, "lxml")
        
        searchs = soup.find('div', {"id": "search"})
        containers = searchs.find_all("div", {"class": "MjjYud"})
        if not containers:
            return {"error": "No data found in google search! Please check the data!"}

        final_data = []

        taw = soup.find('div', {'id': 'taw'})
        if taw:
            dt = self._get_sponsor_data(taw)
            final_data.append(dt)
            
        for box in containers:
            if not box.find(True):
                continue
            dt = self._get_box_data(box)
            if dt:
                final_data.append(dt)
        
        return {"data": final_data}


    def google_search_v2(self, query, page_number=1, num=15, gl="in", tbm="lcl", tbs="0", hl="en",  **kwargs):
    
        def random_string(length=10):
            return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

        page_number = page_number - 1
        start_index = page_number * num

        params = {
            "sca_esv": random_string(16),
            "hl": hl,
            "gl": gl,
            "tbm": tbm,
            "sxsrf": random_string(64) + ":" + str(random.randint(1000000000000, 9999999999999)),
            "q": query,
            "rflfq": str(random.randint(1, 10)),
            "num": str(num),
            "start": str(start_index),
            "sa": random.choice(["X", "Y", "Z"]),
            "ved": random_string(50),
            "biw": str(random.randint(800, 2000)),
            "bih": str(random.randint(600, 1200)),
            "dpr": round(random.uniform(1.0, 2.0), 2),
            "tbs": random_string(20),
            "lf": str(random.choice([1, 2, 3])),
            "lf_ui": str(random.choice([5, 6, 7, 8, 9])),
        }

        params.update(kwargs)

        encoded_params = urllib.parse.urlencode(params)
        url = f"https://www.google.com/search?{encoded_params}"
        headers = self._get_headers()

        res = requests.get(url, headers=headers, impersonate="chrome101")
        if res.status_code != 200:
            return None
        return res.text
    

    def _extract_bussiness_box_data(self, box):
        data = {}
        div = box.find('div', {'class': 'VkpGBb'})
        if not div:
            return data
        
        part_one = div.find('div', {'class': 'cXedhc'})
        title_data = part_one.find('span', {'class': 'OSrXXb'})
        title = title_data.text if title_data else None
        if title:
            data.update({'title': title})

        rating_data = part_one.find('span', {'class': 'Y0A0hc'})
        review_rating = rating_data.text if rating_data else None
        if review_rating:
            rating, reviews_count= review_rating.split('(')
            data.update({'rating': rating})
            reviews_count = reviews_count.replace(')', '')
            data.update({'reviews_count': reviews_count})

        raw_data = part_one.text
        pattern = r"(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{3,4}\)?[-.\s]?)?\d{3,4}[-.\s]?\d{4}"
        numbers = re.findall(pattern, raw_data)
        if numbers:
            data.update({'phone numbers': numbers})

        data.update({"raw_data": raw_data})

        a_tags = div.find_all('a')
        a_tags = [a.get('href') for a in a_tags if a.get('href')]
        
        maps_link = None
        link = None

        if len(a_tags) == 1:
            if "maps" in a_tags[0]:
                maps_link = a_tags[0]
        elif len(a_tags) == 2:
            for tag in a_tags:
                if "maps" in tag:
                    maps_link = tag
                else:
                    link = tag

        if maps_link:
            data["map_link"] = 'https://www.google.com/' + maps_link
        if link:
            data["link"] = link
            
        return data
    

    def local_search_clean_data(self, html):
        soup = BeautifulSoup(html, 'lxml')
        data = soup.find('div', {'jscontroller': 'EfJGEe'})
        if not data:
            return {"error": "bussiness data is empty"}
        containers = soup.find_all('div', {'jscontroller': 'AtSb'})
        final_data = []
        for box in containers:
            dt = self._extract_bussiness_box_data(box)
            if dt:
                final_data.append(dt)
        
        return {"data": final_data}
    
