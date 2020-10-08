from ipwhois import IPWhois
import email_grabber
import socket
from logger import log_debug
from db_functions import update_emails_table, update_whois_table, reset_emails_table, reset_whois_table, check_emails, check_asns, validate_existing_records_in_emails_table

def get_whois_results(target):
    if not validate_existing_records_in_emails_table(target):
        resolve = socket.gethostbyname(target)
        obj = IPWhois(resolve)
        results = obj.lookup_whois()
        emails_whois = (results['nets'][0]['emails'])
        emails = list(set(emails_whois + email_grabber.get_emails(target)))
        cidr = (results['nets'][0]['cidr'])
        asn_num = (results['asn'])
        asn_disc = (results['asn_description'])
        asn_country = (results['asn_country_code'])
        try:
            update_whois_table(asn_disc, target, asn_num, asn_country, cidr)
            for email in emails:
                update_emails_table(email, target)
            return check_emails(target), check_asns(target)
        except Exception as e:
            log_debug('Error while getting WHOIS results ' + str(e))
            pass
    elif validate_existing_records_in_emails_table(target):
        return check_emails(target), check_asns(target)
    else:
        log_debug("Record {} exist in DB".format(target))
        exit()