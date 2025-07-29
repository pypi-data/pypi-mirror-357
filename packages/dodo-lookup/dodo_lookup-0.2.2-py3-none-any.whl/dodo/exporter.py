import json
import csv
import io
from prettytable import PrettyTable
from termcolor import colored

def export_json(results):
    return json.dumps([
        {"domain": domain, "status": ("available" if available is True else "taken" if available is False else "unknown")}
        for domain, available in results
    ], indent=2)

def export_csv(results):
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["domain", "status"])
    for domain, available in results:
        status = "available" if available is True else "taken" if available is False else "unknown"
        writer.writerow([domain, status])
    return buffer.getvalue()

def print_results(results):
    table = PrettyTable()
    table.field_names = ["Domain", "Status"]

    for domain, available in results:
        if available is True:
            status = colored("✅ Available", "green")
        elif available is False:
            status = colored("❌ Taken", "red")
        else:
            status = colored("⚠️ Unknown", "yellow")

        table.add_row([domain, status])

    print(table)