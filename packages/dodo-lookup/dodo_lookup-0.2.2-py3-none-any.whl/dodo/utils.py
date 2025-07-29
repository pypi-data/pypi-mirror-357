import whois
import logging

def suppress_whois_logs():
    logging.getLogger("whois.whois").setLevel(logging.CRITICAL)

def check_domain_availability(domain):
    try:
        w = whois.whois(domain)
        return not bool(w.domain_name), None
    except Exception as e:
        return None, str(e)