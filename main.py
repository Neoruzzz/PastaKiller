import subprocess
import sys
libraries = [["selenium", "selenium"], ["requests", "requests"], ["PIL", "pillow"], ["twocaptcha", "2captcha-python"]]
for library in libraries:
    try:
        __import__(library[0])
        print(f"[@] {library[0]} Already installed")
    except ImportError:
        print(f"[!] {library[0]} Not found. Install...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", library[1]])
from json import JSONDecodeError
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import requests
from io import BytesIO
from PIL import Image
import random
import os
from twocaptcha import TwoCaptcha
import threading
from urllib.parse import quote
import json
from proxy import getProxyPlugin
from proxy import deleteProxyPlugin

totalreports = 0
configuration = dict()
lock = threading.Lock()

def telegramSend(text):
	requests.get(f"https://api.telegram.org/bot{configuration['telegram_token']}/sendMessage?chat_id={configuration['telegram_chatid']}&text={quote(text)}&parse_mode=Markdown")

class Worker(threading.Thread):
	def __init__(self, id, threadid, reports, proxy = None):
		super().__init__()
		self.reports = reports
		self.id = id
		self.url = f"http://pastebin.com/report/{id}"
		self.threadid = threadid
		if proxy:
			self.proxy = proxy
		else:
			self.proxy = None

	def report(self):
		global totalreports
		global configuration
		global lock
		solver = TwoCaptcha(configuration['api_key'])
		chrome_options = Options()
		if self.proxy:
			if len(self.proxy.split(":")) == 2:
				chrome_options.add_argument(f'--proxy-server=http://{self.proxy[0]}')
			else:
				print("[@] Creating proxy auth plugin...")
				chrome_options.add_extension(getProxyPlugin(self.proxy.split(":")[0], self.proxy.split(":")[1], self.proxy.split(":")[2], self.proxy.split(":")[3], self.threadid))
		chrome_options.add_argument("--headless")
		chrome_options.add_argument("--disable-logging")
		chrome_options.add_argument("--log-level=3")
		chrome_options.add_argument("--no-sandbox")
		chrome_options.add_argument("--disable-dev-shm-usage")
		service = Service(log_path="NUL")
		driver = webdriver.Chrome(service=service, options=chrome_options)
		driver.get(self.url)
		print(f'[THREAD/{self.threadid}] [@] Start report')
		name = random.choice(configuration['names'])
		report_text = random.choice(configuration['reports'])
		email = f"{name}{random.randint(0, 9)}{random.randint(0, 9)}{random.randint(0, 9)}{random.randint(0, 9)}@yopmail.com"
		print(f"[THREAD/{self.threadid}] [@] Report text: " + report_text)
		driver.find_element(By.ID, "reportform-text").send_keys(report_text)
		driver.find_element(By.ID, "reportform-user_full_name").send_keys(name)
		driver.find_element(By.ID, "reportform-email").send_keys(email)
		captcha_element = driver.find_element(By.ID, "reportform-verifycode-image")
		image_data = captcha_element.screenshot_as_png
		image = Image.open(BytesIO(image_data))
		image.save(f'captcha{self.threadid}.png')
		print(f'[THREAD/{self.threadid}] [@] Solving captcha...')
		result = solver.normal(f'captcha{self.threadid}.png')
		os.remove(f'captcha{self.threadid}.png')
		print(f'[THREAD/{self.threadid}] [@] Captcha is ' + result['code'].upper())
		driver.find_element(By.ID, "reportform-verifycode").send_keys(result['code'].upper())

		driver.find_element(By.CSS_SELECTOR, "button.btn.-big").click()
		time.sleep(2)
		try:
			with lock:
				totalreports = totalreports + 1
			print(
				f'[THREAD/{self.threadid}] [@] [{totalreports}] {driver.find_element(By.CSS_SELECTOR, "div.notice.-success").text}')
			if self.proxy:
				telegramSend(f"🟥 *[{totalreports}] REPORT SENT! — PastaKiller* 🟥\n🌐 *Proxy:* `{self.proxy}`\n🔴 *Paste:* https://pastebin.com/{self.id}\n👤 *Sender:* `{name}`\n📧 *Email:* `{email}`\n💬 *Report Text:* `{report_text}`\n💸 *Remaining balance:* `{getBalance()}₽`")
			else:
				telegramSend(f"🟥 *[{totalreports}] REPORT SENT! — PastaKiller* 🟥\n🌐 *Proxy:* Don't use proxy\n🔴 *Paste:* https://pastebin.com/{self.id}\n👤 *Sender:* `{name}`\n📧 *Email:* `{email}`\n💬 *Report Text:* `{report_text}`\n💸 *Remaining balance:* `{getBalance()}₽`")
		except:
			print(f"[THREAD/{self.threadid}] [@] Stupid RuCaptcha couldn't solve the captcha...")
			pass
		print(f'[THREAD/{self.threadid}] [@] Remaining balance on RuCaptcha: {getBalance()}₽')
		deleteProxyPlugin(self.threadid)
		driver.quit()

	def run(self):
		print(f'[@] [THREAD/{self.threadid}] Started')
		for _ in range(0, self.reports):
			try:
				self.report()
			except KeyboardInterrupt:
				print(f'[@] [THREAD/{self.threadid}] Stopped')
			except Exception as e:
				print(f'[@] [THREAD/{self.threadid}] Failed to start report. {str(e).split("(Session info")[0].strip()}')

def getBalance():
	res = requests.post("https://api.rucaptcha.com/getBalance", json={"clientKey": configuration['api_key']})
	return res.json()['balance']

def getProxies():
	proxies = list()
	if os.path.exists("proxy.txt"):
		try:
			with open("proxy.txt", "r") as f:
				data = f.read()
				for proxy in data.splitlines():
					if len(proxy.split(":")) == 2 or len(proxy.split(":")) == 4:
						proxies.append(proxy)
						print(f"[+] Successfully loaded {proxy}")
					else:
						raise Exception
		except Exception:
			print("[!] Incorrect proxy file")
			exit()
	else:
		print('[!] Proxies not found')
		with open("proxy.txt", 'w+') as f:
			f.write("EXAMPLE\nONLY HTTP PROXY\nIP:PORT\nIP:PORT:USERNAME:PASSWORD")
		print('[+] Created proxies.txt')
		exit()
	return proxies

def getReports():
	reports = list()
	if os.path.exists("reports.txt"):
		with open("reports.txt", "r") as f:
			data = f.read()
			if len(data.splitlines()) != 0:
				for report in data.splitlines():
					print(f'[+] Successfully loaded {report}')
					reports.append(report)
	else:
		print('[!] Reports not found')
		with open("reports.txt", 'w+') as f:
			f.write("EXAMPLE\nThis paste contains a information for malware\nThis paste is a very harmfull")
		print('[+] Created reports.txt')
		exit()
	return reports

def getNames():
	names = list()
	if os.path.exists("names.txt"):
		with open("names.txt", "r") as f:
			data = f.read()
			if len(data.splitlines()) != 0:
				for name in data.splitlines():
					print(f'[+] Successfully loaded {name}')
					names.append(name)
	else:
		print('[!] Names not found')
		with open("names.txt", 'w+') as f:
			f.write("EXAMPLE\nJohn\nArthur")
		print('[+] Created names.txt')
		exit()
	return names

def createConfiguration():
	global configuration
	print('[@] Creating configuration...')
	if input("[$] Use proxies? (Y/N): ").lower() == 'y':
		use_proxies = True
	else:
		use_proxies = False
	apikey = input("[$] Input RuCaptcha API Key: ")
	pastebin_id = input("[$] Input Pastebin ID: ")
	telegram_token = input("[$] Input Telegram Token: ")
	telegram_chatid = input("[$] Input Telegram Chat ID: ")
	data = {'use_proxies': use_proxies, 'api_key': apikey, 'pastebin_id': pastebin_id, 'telegram_token': telegram_token, 'telegram_chatid': telegram_chatid}
	with open('config.json', 'w+') as f:
		f.write(json.dumps(data))
	print('[+] Configuration created!')
	configuration = data

def loadConfiguration():
	global configuration
	if os.path.exists("config.json"):
		try:
			with open("config.json", "r") as f:
				data = json.loads(f.read())
				if all(key in data for key in ['use_proxies', 'api_key', 'pastebin_id', 'telegram_token', 'telegram_chatid']):
					configuration = data
		except JSONDecodeError:
			print('[!] Incorrect configuration file')
			createConfiguration()
	else:
		print('[!] Configuration not found')
		createConfiguration()

if __name__ == "__main__":
	try:
		os.system('cls')
		os.system('title PastaKiller by @sv1zx')
		loadConfiguration()
		print("[@] Loading names...")
		configuration['names'] = getNames()
		print("[@] Loading reports...")
		configuration['reports'] = getReports()
		if configuration['use_proxies']:
			print('[@] Loading proxies...')
			configuration['proxies'] = getProxies()
		os.system("cls")
		print("\n" +
			  "░░░░░░░░░░░░░░░░▄▄████▄▄▄▄░░░░░░░░░░░\n" +
			  "░░░░░░░░░░░▄▄▄██████████████▄▄░░░░░░░\n" +
			  "░░░░░░░░░██████░░▀█████████████▄░░░░░\n" +
			  "░░░░░░░▄██▄░▀░░░░▀▄▀████▀████████▄░░░\n" +
			  "░░░░░░░██░░░░███░░░░░▀░░░░▀███████▄░░\n" +
			  "░░░░░░░█░░░░░░▀░░░░░░▄▄▄▄░░░░██████░░\n" +
			  "░░░░░░░█░░░░░░░░░░▄▀░░░░░▀▄░░▀█████░░\n" +
			  "░░░░░▄█░░░░███▄▄░░█▄▀█████▄▄░░█████░░\n" +
			  "░░░░░█░░▄▄▄░░░░█░░▀▀▀░░▀▄▄█▄▀▀▀▀███░░\n" +
			  "░░░░░█░░░▄▀▀░▄█▀░░░▀█▄▄░▀▀█▄▀█▄░█▀█░░\n" +
			  "░░░░░▀█░██▄▄░░▀▄░░▀▀█▄▄▀▀▀█▄▄█░░░▄▀░░\n" +
			  "░░░░░░█░███▄▀▀▀▀▀█▀▀░█▄▄██▀▄▀░░░█░░░░\n" +
			  "░░░░░░█░██████▀█████▀▀█░░▄█░░░░█░░░░░\n" +
			  "░░▄░░░█░░█▀███░█░░█░░▄██▀░░▄░▄▀░░░░░░\n" +
			  "█████░█▄▄█▀▀▀▀▀▀▀▀▀▀▀░▄░░▄▄▀█▄░░░░░░░\n" +
			  "███████▀░░░░░░░░░░░░░░▄▀▀░░░███▄░░░░░\n" +
			  "░▀▀▀▀░▀▄▄░░░░░▄▄▄▄▀▀▀░░░░█░▄██████▄░░\n" +
			  "░░░░░░░░▄█▀▀▀▀░░░░░░░░█░▀░▄██████████\n" +
			  "░░░░░▄▄███░░░▄░░░░░░▄▀░░░░██████████▀\n" +
			  "     	PastaKiller — V1.0          \n" +
			  "            dev -> @sv1zx          \n\n" +
			 f"Target: https://pastebin.com/{configuration['pastebin_id']}\n" +
			 f"RuCaptcha api key: {configuration['api_key']}\n" +
			 f"Proxies: {len(configuration['proxies']) if configuration['use_proxies'] else 'Don\'t use'}\n" +
			 f"Names: {len(configuration['names'])}\n" +
			 f"Reports: {len(configuration['reports'])}\n")
		reportsc = int(input('[$] Reports count: '))
		threadsc = int(input('[$] Threads count: '))
		if threadsc > len(configuration['proxies']):
			print(f'[!] Warning: Proxy is greater than the number of threads. Will be started {len(configuration['proxies'])} threads.')
		os.system(f'title PastaKiller by @sv1zx - https://pastebin.com/{configuration['pastebin_id']}')

		threads = list()
		if configuration['use_proxies']:
			thdc = 0
			for proxy in configuration['proxies'][:threadsc]:
				thdc = thdc + 1
				try:
					thd = Worker(configuration['pastebin_id'], thdc, reportsc, proxy)
					thd.start()
				except KeyboardInterrupt:
					print(f'[@] [THREAD/{thdc}] Stopped')
		else:
			for i in range(0, threadsc):
				i = i + 1
				thd = Worker(configuration['pastebin_id'], i, reportsc)
				thd.start()

		for thd in threads:
			thd.join()
	except KeyboardInterrupt:
		print('\n[@] Exit...')
