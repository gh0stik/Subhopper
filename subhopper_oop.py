import re, time, requests, json
from logger import log_debug
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from concurrent.futures import ThreadPoolExecutor
from db_functions import update_sub_domains_table, update_historical_ips_table, reset_historic_ips_table, reset_subhopper_table, validate_existing_records_in_sub_domains_table, check_subdomain, check_historical_ips


class Subhopper():

    def __init__(self, target):

        self.ids = ['E', 'I', 'M', 'Q', 'U', 'Y', 'c', 'g', 'k']  # VirusTotal SubIDs
        self.targeturl = target
        self.Session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko'
        }
        self.ip_regex = r'\d+\.\d+\.\d+\.\d+'
        self.subdomain_regex = r"(?:[\w\-\_]+\.)+(?:)"

    def virus_total(self):
        subdomains = set()

        try:
            firstBatch = self.Session.get("https://www.virustotal.com/ui/domains/{}/subdomains?relationships=resolutions".format(self.targeturl)).text
            for subdomain in range(0, len(json.loads(firstBatch)["data"])):
                subdomains.add(json.loads(firstBatch)["data"][subdomain]["id"])

            for id_letter in self.ids:
                time.sleep(0.5)
                restBatch = self.Session.get("https://www.virustotal.com/ui/domains/{}/subdomains?relationships=resolutions&cursor=ST{}wCi4%3D&limit=10".format(self.targeturl, id_letter)).text
                for subdomain in range(0, len(json.loads(restBatch)["data"])):
                    subdomains.add(json.loads(restBatch)["data"][subdomain]["id"])
        except Exception as e:
            print(str(e))
            log_debug(str(e))
            pass

        return list(subdomains)


    def google_dork(self):
        subdomain_list = set()

        for num in range(1, 4):
            req = self.Session.get("https://www.google.com/search?q=site:{}+-site:www.{}&start={}0".format(self.targeturl, self.targeturl, str(num))).text
            try:
                time.sleep(0.5)
                for sub in re.findall(r"(\w+|\w+-\w+|\w+\.\w+)\.{}".format(self.targeturl), req):
                    subdomain_list.add("{}.{}".format(sub, self.targeturl))
            except Exception as e:
                print(str(e))
                log_debug(str(e))
                pass

        print(subdomain_list)
        return list(subdomain_list)


    def pkey_sub_search(self):

        url = 'https://www.pkey.in/tools-i/search-subdomains/'
        payload = {
            'zone': self.targeturl,
            'submit': ""
        }
        req4 = self.Session.post(url, data=payload, verify=False)
        pKeydomains = re.findall("\w+\."+self.targeturl, req4.text)
        return pKeydomains


    def dns_dumpster(self):
        try:
            dnsdumpster_url = "https://dnsdumpster.com/"
            req = self.Session.get(dnsdumpster_url)
            csrf = re.search(r'(?<=name="csrfmiddlewaretoken" value=").*?(?=")', req.text).group(0)
            headers = {'Referer': dnsdumpster_url}
            data = {'csrfmiddlewaretoken': csrf, 'targetip': self.targeturl}
            req = self.Session.post(dnsdumpster_url, data=data, headers=headers)
            domains = re.findall(self.subdomain_regex + self.targeturl, req.text)
            return domains

        except Exception as e:
            print(str(e))
            log_debug(str(e))
            pass


    def findsubdomains(self):
            url = 'https://findsubdomains.com/subdomains-of/' + self.targeturl
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
            }
            req = self.Session.get(url, headers=headers)
            domains = re.findall(self.subdomain_regex + self.targeturl, req.text)
            return domains


    def crt_sh(self):
        results = set()
        url = "https://crt.sh/"
        req = self.Session.get(url, params={"q": self.targeturl})
        re_get = re.findall("(?<=<TD>|<BR>).*?(?={})".format(self.targeturl), req.text)
        for i in re_get:
            if "*" not in str(i) and "<BR>" not in str(i) and str(i) + "{}".format(self.targeturl) not in results:
                if "<BR>" in str(i):
                    clean = re.findall("(?<=<BR>).*(?=\.)", str(i))
                    if clean and "<BR>" not in clean and clean[0] + ".{}".format(self.targeturl) not in results:
                        results.add(clean[0] + ".{}".format(self.targeturl))
            else:
                if "*" in str(i):
                    i = i.replace("*.", "")
                results.add(str(i) + "{}".format(self.targeturl))
        return list(results)


    def ssl_mate(self):
        subdomains = set()
        try:
            json_data = self.Session.get("https://api.certspotter.com/v1/issuances?domain={}&include_subdomains=true&expand=dns_names".format(self.targeturl)).text
            for dns_name in json.loads(json_data):
                for dns in dns_name['dns_names']:
                    try:
                        subdomain = re.search(".*?(?={})".format(self.targeturl), dns).group(0)
                        if "*" in subdomain:
                            subdomain = subdomain.replace("*.", "")
                            subdomains.add(subdomain+self.targeturl)
                        else:
                            subdomains.add(subdomain+self.targeturl)
                    except:
                        continue
            return list(subdomains)
        except Exception as e:
            print(str(e))
            pass


    def historical_ips_func(self):
        url = "https://viewdns.info/iphistory/?domain=" + self.targeturl
        historical_data = "https://www.virustotal.com/ui/domains/" + self.targeturl + "/resolutions"
        req = self.Session.get(historical_data)
        data = json.loads(req.text)
        getIP_from_data = re.findall(self.ip_regex, str(data))
        req = self.Session.get(url, headers=self.headers)
        getIP_from_req = re.findall(self.ip_regex, req.text)
        return list(set().union(getIP_from_req, getIP_from_data))


    def run(self):
        if self.targeturl != None:
            if not validate_existing_records_in_sub_domains_table(self.targeturl):
                executors_list = []

                start = time.time()
                print("starting...")
                with ThreadPoolExecutor(max_workers=6) as executor:
                    print("[+]Collecting Subdomains from VirusTotal.")
                    executors_list.append(executor.submit(self.virus_total))
                    print("[+]Collecting Subdomains from Google.")
                    executors_list.append(executor.submit(self.google_dork))
                    print("[+]Collecting Subdomains from DNS Dumpster.")
                    executors_list.append(executor.submit(self.dns_dumpster))
                    print("[+]Collecting Subdomains from FindSubdomains.")
                    executors_list.append(executor.submit(self.findsubdomains))
                    print("[+]Collecting Subdomains from Crt_sh.")
                    executors_list.append(executor.submit(self.crt_sh))
                    print("[+]Collecting Subdomains from ssl_mate.")
                    executors_list.append(executor.submit(self.ssl_mate))
                subdomain_list_final = []
                for x in executors_list:
                    subdomain_list_final = list(set(subdomain_list_final + x.result()))
                executor.shutdown()
                print("==========================================================\nDomains:\t\t\tIPs\n==========================================================")
                print("\nUpdating DB...\n")
                for subdomain in subdomain_list_final:
                    update_sub_domains_table(subdomain, self.targeturl)


                print("\n==========================================================\nHistorical IPs:\n==========================================================")
                print("\nUpdating DB...\n")
                for ip in self.historical_ips_func():
                    update_historical_ips_table(ip, self.targeturl)

                end = time.time()
                print("\nTask ended after: " + str(int(end - start)))

                return check_subdomain(self.targeturl), check_historical_ips(self.targeturl)

            elif validate_existing_records_in_sub_domains_table(self.targeturl):
                return check_subdomain(self.targeturl), check_historical_ips(self.targeturl)

            else:
                log_debug("Record {} exist in DB".format(self.targeturl))
                exit()
        else:
            log_debug("Target cannot be None. Check that target domain has been provided with -d or --domain.")
            pass

