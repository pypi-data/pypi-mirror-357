import concurrent.futures
from tqdm import tqdm
from dodo.utils import suppress_whois_logs, check_domain_availability
from importlib.resources import read_text

suppress_whois_logs()

def load_tlds():
    content = read_text("dodo", "../tlds.txt")
    return sorted(set(line.strip() for line in content.splitlines() if line.strip()))

def check_all_domains(name, tlds):
    domains = [f"{name}.{tld}" for tld in tlds]
    results = []

    def check(domain):
        available, _ = check_domain_availability(domain)
        return domain, available

    with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(tlds), 10)) as executor:
        for domain, available in tqdm(executor.map(check, domains), total=len(domains), desc="Progress", colour="cyan"):
            results.append((domain, available))

    return results
