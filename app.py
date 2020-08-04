#!/usr/bin/env python3
from time import sleep
import subhopper_oop
import whois_extractor
import re
from db_functions import remove_rows, get_stats
from flask import Flask, redirect, request, render_template, flash
from os.path import join, dirname, realpath
from logger import log_debug
from tld import get_fld

app = Flask(__name__)
app.secret_key = b'veryuniquepa$$word!'

def verify_tld(domain):
	try:
		get_fld(domain, fix_protocol=True)
		return True
	except Exception as e:
		print(str(e))
		log_debug(str(e))
		return False


@app.route("/", methods=["GET", "POST"])
def testing():
	inp = request.form.get('dom')
	domain = request.form.get('domain')
	ips = request.form.get('ips')
	whois = request.form.get('whois')
	email = request.form.get('email')
	rmtb = request.form.get('rmtb')
	try:
		if request.method == 'GET':
			return render_template('testingscript.html')

		elif request.method == 'POST' and verify_tld(inp):

			if ips:
				try:
					runner = subhopper_oop.Subhopper(inp)
					historicips = runner.run()[1]
					return render_template('testingscript.html', get_domain=historicips)
				except Exception as e:
					return render_template('testingscript.html', error=e)
			if domain:
				try:
					runner = subhopper_oop.Subhopper(inp)
					subdomains = runner.run()[0]
					return render_template('testingscript.html', get_domain=subdomains)
				except Exception as e:
					log_debug(str(e))
					return render_template('testingscript.html', error=e)
			if whois:
				try:
					results = whois_extractor.get_whois_results(inp)
					print(results)
					templist = []
					for i in results[1][0][1:]:
						templist.append([i])
					return render_template('testingscript.html', get_domain=templist)
				except Exception as e:
					return render_template('testingscript.html', error=e)
			if email:
				try:
					results = whois_extractor.get_whois_results(inp)
					return render_template('testingscript.html', get_domain=results[0])
				except Exception as e:
					return render_template('testingscript.html', error=e)
			if rmtb:
				try:
					if remove_rows(inp):
						return render_template('testingscript.html', rmtb="Rows Removed.")
					else:
						return render_template('testingscript.html', rmtb="No rows found for {}.".format(inp))
				except Exception as e:
					return render_template('testingscript.html', error=e)

		else:
			print(request.form.get('domain'))
			flash("Please use only valid domain format.")
			return render_template('testingscript.html')

	except Exception as e:
		log_debug(str(e))
		return redirect('/', 302)


if __name__=="__main__":
	app.run(host="127.0.0.1", port="5000", debug=True)
