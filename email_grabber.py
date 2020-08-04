import requests
import re
import random
import time
import subprocess

def get_emails(target_domain):
	if target_domain == None:
		print("Missing target. Use --> python email_grabber.py -d domain.com")
		exit(0)
	cmd = subprocess.check_output(["sudo","service","tor","start"])
	print(str(cmd.decode()))

	s = requests.Session()
	capturedEmails = []

	proxies = {
		"https": "socks5://127.0.0.1:9050"
	}

	target_domain = target_domain

	user_agents = [
		"Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.96 Mobile Safari/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
		"Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Googlebot/2.1; +http://www.google.com/bot.html) Safari/537.36",
		"Mozilla/5.0 (iPhone; CPU iPhone OS 8_3 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12F70 Safari/600.1.4 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
		"SentiBot www.sentibot.eu (compatible with Googlebot)",
		"Mozilla/5.0 (iPhone; CPU iPhone OS 6_0 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/6.0 Mobile/10A5376e Safari/8536.25 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
		"Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0",
		"Mozilla/5.0 (Android 4.4; Tablet; rv:41.0) Gecko/41.0 Firefox/41.0",
		"Mozilla/5.0 (Windows NT x.y; Win64; x64; rv:10.0) Gecko/20100101 Firefox/10.0",
		"Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:10.0) Gecko/20100101 Firefox/10.0",
		"Mozilla/5.0 (X11; Linux i686; rv:10.0) Gecko/20100101 Firefox/10.0",
		"Mozilla/5.0 (Android; Mobile; rv:40.0) Gecko/40.0 Firefox/40.0"
	]

	headers = {
		"Host": "duckduckgo.com",
		"User-Agent": user_agents[random.randint(0,len(user_agents)-1)],
		"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
		"Accept-Language": "en-US,en;q=0.5",
		"Accept-Encoding": "gzip",
		"Referer": "https://duckduckgo.com/",
		"Content-Type": "application/x-www-form-urlencoded",
		"Content-Length": str(37),
		"DNT": str(1),
		"Connection": "keep-alive",
		"Upgrade-Insecure-Requests": "1"
	}

	data = {
		"q":'"@{}"'.format(target_domain),
		"b":"",
		"kl":"us-en"
	}

	nextParam = {
		"q":'"@{}"'.format(target_domain),
		"s":30,
		"nextParams":"",
		"v":"l",
		"o":"json",
		"dc":11,
		"api":"/d.js",
		"kl":"us-en"
	}

	print("Running first request...")
	url = "https://duckduckgo.com/html/"
	error_check = True
	while error_check == True:
		req = s.post(url, headers=headers, data=data, proxies=proxies)
		if "If this error persists" in req.text:
			cmd = subprocess.check_output(["sudo","service","tor","restart"])
			print(str(cmd.decode()))
		else:
			error_check = False

	catch_re = re.findall(r"(\w+|\w+\.\w+|\w+\-\w+)(?=<b>{})".format(data["q"].replace('"',"")), req.text)
	for email in catch_re:
			if email not in capturedEmails:
				capturedEmails.append(email)

	print("First emails added...")
		
	time.sleep(random.randint(2,4))

	while nextParam["s"] < 530:
		try:
			print("Running next requests...")
			req = s.post(url, headers=headers, data=nextParam, proxies=proxies)
			catch_re = re.findall(r"(\w+|\w+\.\w+|\w+\-\w+)(?=<b>{})".format(data["q"].replace('"',"")), req.text)
			print("Adding email batch...")
			for email in catch_re:
				if email+"@{}".format(target_domain) not in capturedEmails:
					capturedEmails.append(email+"@{}".format(target_domain))
			nextParam["s"] += 50
			print("nextParam changed to " + str(nextParam["s"]))
			nextParam["dc"] += 20
			time.sleep(random.randint(2,4))
		except Exception as e:
			print(str(e))
			break
	
	with open("emails_of_{}.txt".format(target_domain),"a+") as file:
		for email in capturedEmails:
			file.writelines(email+"\n")
		file.close()
	s.close()
	cmd = subprocess.check_output(["sudo","service","tor","stop"])
	print(str(cmd.decode()))
	return capturedEmails
