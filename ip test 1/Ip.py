#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Advanced Penetration Testing Tool
# Author: Your Name

import os
import subprocess
import socket
import time
import concurrent.futures
from datetime import datetime
import logging
from libnmap.parser import NmapParser
import pdfkit  # برای تولید گزارش PDF
import requests  # برای ارسال نتایج به API

# تنظیمات لاگ‌گیری
logging.basicConfig(
    filename='pentest.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class AdvancedPentestTool:
    def __init__(self, target_ip):
        self.target_ip = target_ip
        self.results = {}
        self.required_tools = {
            'nmap': 'اسکن شبکه و آسیب‌پذیری‌ها',
            'hydra': 'حملات بروت‌فورس',
            'nikto': 'اسکن آسیب‌پذیری‌های وب',
            'sqlmap': 'تست تزریق SQL',
            'metasploit': 'اکسپلویت‌های پیشرفته',  # اختیاری
            'whatweb': 'شناسایی تکنولوژی‌های وب'
        }

    def print_banner(self):
        banner = """
        ██████╗ ███████╗███╗   ██╗████████╗███████╗██████╗ 
        ██╔══██╗██╔════╝████╗  ██║╚══██╔══╝██╔════╝██╔══██╗
        ██████╔╝█████╗  ██╔██╗ ██║   ██║   █████╗  ██████╔╝
        ██╔═══╝ ██╔══╝  ██║╚██╗██║   ██║   ██╔══╝  ██╔══██╗
        ██║     ███████╗██║ ╚████║   ██║   ███████╗██║  ██║
        ╚═╝     ╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚═╝  ╚═╝
        """
        print(banner)
        print("=" * 70)
        print(f"آزمون نفوذ پیشرفته - هدف: {self.target_ip}")
        print(f"زمان شروع: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        print("هشدار: این ابزار فقط برای تست قانونی با مجوز قابل استفاده است!")
        print("=" * 70 + "\n")

    def check_tools(self):
        missing_tools = []
        for tool in self.required_tools:
            try:
                subprocess.check_output(['which', tool])
            except subprocess.CalledProcessError:
                missing_tools.append(tool)
        
        if missing_tools:
            print("[!] ابزارهای ضروری نصب نیستند:")
            for tool in missing_tools:
                print(f"- {tool} ({self.required_tools[tool]})")
            print("\nنصب با دستورات زیر:")
            print("sudo apt install nmap hydra nikto sqlmap whatweb")
            exit(1)

    def nmap_scan(self, port, scripts):
        try:
            command = f"nmap -p {port} --script {scripts} {self.target_ip} -oX scan_{port}.xml"
            subprocess.run(command, shell=True, check=True)
            
            # پردازش نتایج با libnmap
            report = NmapParser.parse_fromfile(f"scan_{port}.xml")
            return report.hosts[0].services
        except Exception as e:
            logging.error(f"خطا در اسکن پورت {port}: {str(e)}")
            return None

    def web_scan(self):
        print("\n[+] در حال اسکن آسیب‌پذیری‌های وب...")
        try:
            # اسکن با Nikto
            subprocess.run(f"nikto -h {self.target_ip} -output nikto_scan.html", shell=True)
            
            # اسکن با sqlmap (اگر پورت 80/443 باز است)
            subprocess.run(f"sqlmap -u http://{self.target_ip} --batch --output-dir=sqlmap_scan", shell=True)
        except Exception as e:
            logging.error(f"خطا در اسکن وب: {str(e)}")

    def brute_force_attack(self, service, port):
        print(f"\n[+] اجرای بروت‌فورس روی {service} (پورت {port})...")
        try:
            if service == "ssh":
                subprocess.run(f"hydra -L users.txt -P passwords.txt {self.target_ip} ssh -t 4", shell=True)
            elif service == "ftp":
                subprocess.run(f"hydra -L users.txt -P passwords.txt {self.target_ip} ftp", shell=True)
        except Exception as e:
            logging.error(f"خطا در بروت‌فورس: {str(e)}")

    def run_advanced_tests(self):
        tests = {
            22: ("ssh", "ssh-brute,ssh-auth-methods"),
            80: ("http", "http-vuln*,http-sql-injection"),
            443: ("https", "http-vuln*,http-sql-injection"),
            21: ("ftp", "ftp-anon,ftp-brute"),
            445: ("smb", "smb-vuln*"),
            3306: ("mysql", "mysql-empty-password"),
            3389: ("rdp", "rdp-ntlm-info")
        }

        print("\n[+] شروع اسکن پیشرفته با قابلیت چندنخی...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = {}
            for port, (service, scripts) in tests.items():
                futures[executor.submit(self.nmap_scan, port, scripts)] = (port, service)
            
            for future in concurrent.futures.as_completed(futures):
                port, service = futures[future]
                result = future.result()
                if result:
                    self.results[port] = result
                    print(f"[+] پورت {port} ({service}) اسکن شد.")
                    
                    # اجرای بروت‌فورس اگر سرویس آسیب‌پذیر باشد
                    if "brute" in str(result).lower():
                        self.brute_force_attack(service, port)

        # اسکن وب اگر پورت 80/443 باز است
        if 80 in self.results or 443 in self.results:
            self.web_scan()

    def generate_report(self):
        print("\n[+] در حال تولید گزارش...")
        
        # گزارش HTML
        html_report = f"""
        <html>
        <body>
            <h1>گزارش آزمون نفوذ - {self.target_ip}</h1>
            <p>تاریخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <hr>
            <h2>نتایج اسکن:</h2>
            <pre>{self.results}</pre>
            <h2>لاگ‌ها:</h2>
            <pre>{open('pentest.log').read()}</pre>
        </body>
        </html>
        """
        
        with open("report.html", "w") as f:
            f.write(html_report)
        
        # تبدیل به PDF
        pdfkit.from_file("report.html", "report.pdf")
        
        print("[+] گزارش در قالب HTML و PDF ذخیره شد.")

    def send_to_telegram(self, bot_token, chat_id):
        """ارسال نتایج به تلگرام"""
        try:
            text = f"نتایج آزمون نفوذ برای {self.target_ip}\n"
            text += f"زمان: {datetime.now()}\n"
            text += f"نتایج کلی:\n{str(self.results)[:1000]}..."
            
            requests.post(
                f"https://api.telegram.org/bot{bot_token}/sendMessage",
                json={"chat_id": chat_id, "text": text}
            )
            print("[+] نتایج به تلگرام ارسال شد.")
        except Exception as e:
            logging.error(f"خطا در ارسال به تلگرام: {str(e)}")

    def cleanup(self):
        """پاک‌سازی فایل‌های موقت"""
        for f in os.listdir():
            if f.startswith("scan_") or f.endswith(".xml"):
                os.remove(f)

if __name__ == "__main__":
    # دریافت آدرس IP از کاربر
    target_ip = input("آدرس IP هدف را وارد کنید: ")
    
    # بررسی معتبر بودن IP
    try:
        socket.inet_aton(target_ip)
    except socket.error:
        print("آدرس IP نامعتبر است!")
        exit(1)
    
    # اجرای ابزار
    tool = AdvancedPentestTool(target_ip)
    tool.print_banner()
    tool.check_tools()
    tool.run_advanced_tests()
    tool.generate_report()
    tool.cleanup()
    
    # ارسال نتایج به تلگرام (اختیاری)
    # tool.send_to_telegram("YOUR_BOT_TOKEN", "YOUR_CHAT_ID")