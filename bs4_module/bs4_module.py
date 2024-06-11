import os
import re
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from regex_modules import regex_modules
from requests_module import requests_module
from utils_module import colors

class CoreParser():
    
    def __init__(self, html_doc, url_domain, name_target,
    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X v4lak; rv:42.0) Gecko/20100101 Firefox/42.0'):
        self.html_doc = html_doc
        self.url_domain = url_domain
        self.soup = BeautifulSoup(self.html_doc, 'html.parser')
        self.user_agent = user_agent
        self.urls = []
        self.host = urlparse(url_domain).hostname
        self.name_target = name_target


    def parser_url(self,src_tags):
        parser_url_domain = urlparse(self.url_domain)
        parser_src_tags = urlparse(src_tags)
        
        if parser_src_tags.path[0:1] != '/':
            src_tags = parser_url_domain.scheme + "://" + parser_url_domain.hostname + "/" + parser_src_tags.path
            self.urls.append(src_tags)

        elif parser_src_tags.netloc == '':
            src_tags = parser_url_domain.scheme + "://" + parser_url_domain.hostname + parser_src_tags.path + "?" +\
                parser_src_tags.query
            self.urls.append(src_tags)
        else:
            self.urls.append(src_tags)

    def get_content_js(self):
        test_conn = requests_module.CoreRequests(self.url_domain, self.name_target)
        if test_conn:
            current_dir = os.getcwd()
            path_save = ""
            dir_name = urlparse(self.url_domain).hostname
        else:
            print(f"{self.url_domain} maybe down :/ ?")

        try:
            os.mkdir(str(dir_name))
            print(f">> Create directory {dir_name}")
            print(f">> Files will be saved at {dir_name}")
        except FileExistsError as e:
            print(f">> {e}")
        
        for url_src_tag in self.urls:
            arrays_match = []
            try:
                if url_src_tag[0:2] == "//":
                    url_src_tag = "http:" + url_src_tag
                print(colors.colors.fg.blue + f"[INFO] Getting info from: {url_src_tag}" + colors.colors.reset)
                r = requests.get(url_src_tag, verify=False, data={'User-Agent:': self.user_agent}, stream=True)
                content_save = r.content
                for _,v in regex_modules.REGEX_PATT.items():
                    values_found = re.findall(v, r.text)
                    if values_found:
                        for v in values_found:
                            if v in arrays_match:
                                continue
                            else:
                                arrays_match.append(v) 
                for url in arrays_match:
                    if "aws" in url:
                        print(colors.colors.fg.red + f"[AWS INFO] {url}" + colors.colors.reset)
                    elif self.host in url:
                        print(colors.colors.fg.orange + f"[DOMAIN INFO] {url}" + colors.colors.reset)
                    elif self.name_target in url:
                        print(colors.colors.fg.orange + f"[NAME INFO] {url}" + colors.colors.reset)
                    elif "vtex" in url:
                        print(colors.colors.fg.red + f"[VTEX INFO] {url}" + colors.colors.reset)
                    else:
                        print(colors.colors.fg.blue + f"[INFO URL] {url}" + colors.colors.reset)
                    
            except ConnectionError as e:
                print(f">> Error while save content from \n{url_src_tag} \n {e}")

            try:
                # Extract the filename from the URL
                filename = url_src_tag.split('/')[-1]

                # Construct the path to save the file within the generated folder
                path_save = os.path.join(current_dir, dir_name, filename)

                with open(path_save, 'wb') as f:
                    f.write(content_save)

            except FileNotFoundError as e:
                print(f">> Error while saving JS content to parse \n {e}")
    
    def find_all_script(self):
        for tag in self.soup.find_all("script"):
            if tag.get('src'):
                self.parser_url(tag.get('src'))
