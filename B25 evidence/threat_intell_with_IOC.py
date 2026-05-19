from datetime import datetime, timezone
from enum import Enum
import json
import re


class ThreatLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class IOCType(Enum):
    IP = "IP"
    DOMAIN = "DOMAIN"
    HASH = "HASH"
    URL = "URL"

# creating a class to hold indicator of compromised information
class IOC:
    def __init__(self, value: str, ioc_type: IOCType, threat_level: ThreatLevel, description: str, source: str, added_at: str):
        self.value = value
        self.ioc_type = ioc_type
        self.threat_level = threat_level
        self.description = description
        self.source = source
        self.added_at = added_at


class ThreatIntelligence:
    def __init__(self):

        self.ioc_array = []


    def add_ioc(self, value: str, ioc_type: IOCType, threat_level: ThreatLevel, description: str, source: str, time_added: timezone):
        # create the object and store it
        ioc = IOC(value, ioc_type, threat_level, description, source, time_added)
        self.ioc_array.append(ioc)

    def remove_ioc(self, value: str):

        value = value.lower()

        for ioc_object in self.ioc_array:
            if ioc_object.value == value:
                self.ioc_array.remove(ioc_object)
                return True, ioc_object

        return False, None

    def list_all_ioc(self):
        # simply tidy up for list presentation
        result_list = []
        for ioc in self.ioc_array:

            ioc_dict = {
                "value": ioc.value,
                "ioc_type": ioc.ioc_type.value,
                "threat_level": ioc.threat_level.value,
                "description": ioc.description,
                "source": ioc.source,
                "added_at": ioc.added_at
            }

            result_list.append(ioc_dict)

        return result_list
            

    def check_indicator(self, indicator: str):
        indicator_array = []
        indicator = indicator.lower()

        for ioc in self.ioc_array:
            if ioc.value == indicator:
                indicator_array.append(ioc.value)
        
        if len(indicator_array) == 0:
            return None
        return indicator_array

    def scan_text(self, text: str):

        matches = []
        text = text.lower()

        for ioc in self.ioc_array:
            if ioc.value in text:
                matches.append(ioc)

        return matches

    @staticmethod
    def extract_ip(text: str):

        pattern = r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b"
        return re.findall(pattern, text)

    @staticmethod
    def extract_domain(text: str):

        pattern = r"\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b"
        return re.findall(pattern, text)

    @staticmethod
    def extract_hash(text: str):

        pattern = r"\b[a-fA-F0-9]{32,64}\b"
        return re.findall(pattern, text)


    def save_to_file(self, filename: str):

        data= self.list_all_ioc()

        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    def load_from_file(self, filename: str):

        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)

        self.ioc_array.clear()

        for item in data:
            self.ioc_array.append( IOC(item["value"], IOCType(item["ioc_type"]), ThreatLevel(item["threat_level"]), item["description"], item["source"], item["added_at"]))

    def generate_report(self):
        """Generate a formatted intelligence report."""

        report = []
        report.append("=" * 60)
        report.append("CURRENT THREAT INTELLIGENCE REPORT FOR ALL KNOWN THREAT")
        report.append("=" * 60)
        # better to add time, as the threat intelligence data base grows over time.
        report.append(f"Generated: {datetime.now(timezone.utc).isoformat()} UTC")
        report.append(f"Total IOCs: {len(self.ioc_array)}")
        report.append("")

        for ioc in self.ioc_array:
            report.append(f"Indicator     : {ioc.value}")
            report.append(f"Type          : {ioc.ioc_type.value}")
            report.append(f"Threat Level  : {ioc.threat_level.value}")
            report.append(f"Description   : {ioc.description}")
            report.append(f"Source        : {ioc.source}")
            report.append(f"Added At      : {ioc.added_at}")
            report.append("-" * 60)

        return "\n".join(report)



if __name__ == "__main__":
    threat_intell = ThreatIntelligence()

    # add data that have collected
    # add malicious IP
    threat_intell.add_ioc("192.168.1.100", IOCType.IP, ThreatLevel.HIGH, "command-and-control server ip address ", "industry blogs", "2026-05-19T01:42:18.701591+00:00")

    # add malicious domain
    threat_intell.add_ioc("cits2006.com.au", IOCType.DOMAIN, ThreatLevel.CRITICAL,"phishing website", "threat Feed","2026-05-19T01:42:18.701591+00:00")

    # check indicator
    result = None
    
    while True:
        check = input('[0] to quit; [1] to check:')
        if check == '1':
            info = input("IOC value to check:") # ie) cits2006.com.au, 192.168.1.100 
            result = threat_intell.check_indicator(info)
        elif check == '0':
            break 
        else:
            print('[!] Error, please enter [0] or [1]')
            continue
    
    if result:
        print("Threat Found:")
        print(result)

    # scan a sample log
    sample_log = " User A380 connected to 194.168.1.100 and accessed example.com/login"

    matches = threat_intell.scan_text(sample_log)

    if matches:
        print("\nDetected Indicators:")
        for match in matches:
            print(f"- {match.value} ({match.threat_level.value})")

    # report
    print("\n")
    print(threat_intell.generate_report())

    # save to database
    threat_intell.save_to_file("ioc_database.json")
