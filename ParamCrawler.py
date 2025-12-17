#!/usr/bin/env python3

import re
import argparse
import time
from urllib.parse import urljoin, urlparse, parse_qs
from collections import deque

import cloudscraper
from bs4 import BeautifulSoup

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.1 Safari/605.1.15',
]

JS_RESERVED = {
    # — Language Keywords (ECMAScript)
    'break', 'case', 'catch', 'class', 'const', 'continue', 'debugger', 'default',
    'delete', 'do', 'else', 'export', 'extends', 'finally', 'for', 'function',
    'if', 'import', 'in', 'instanceof', 'let', 'new', 'return', 'super', 'switch',
    'this', 'throw', 'try', 'typeof', 'var', 'void', 'while', 'with', 'yield',

    # — Future/Strict-mode-only Keywords
    'enum', 'implements', 'interface', 'package', 'private', 'protected',
    'public', 'static',

    # — Literals & Types
    'null', 'true', 'false', 'NaN', 'Infinity', 'undefined', 'BigInt',

    # — Global Functions
    'eval', 'isFinite', 'isNaN', 'parseFloat', 'parseInt', 'decodeURI',
    'decodeURIComponent', 'encodeURI', 'encodeURIComponent', 'escape', 'unescape',

    # — Console & Debug
    'console', 'console.log', 'console.error', 'console.warn', 'console.info',
    'console.debug', 'console.table', 'console.dir', 'console.trace',

    # — Timers
    'setTimeout', 'clearTimeout', 'setInterval', 'clearInterval', 'queueMicrotask',

    # — Data Types / Constructors
    'Object', 'Function', 'Boolean', 'Symbol', 'Error', 'EvalError', 'RangeError',
    'ReferenceError', 'SyntaxError', 'TypeError', 'URIError', 'Number', 'BigInt',
    'Math', 'Date', 'String', 'RegExp', 'Array', 'Int8Array', 'Uint8Array',
    'Uint8ClampedArray', 'Int16Array', 'Uint16Array', 'Int32Array', 'Uint32Array',
    'Float32Array', 'Float64Array', 'BigInt64Array', 'BigUint64Array',
    'Map', 'Set', 'WeakMap', 'WeakSet', 'ArrayBuffer', 'SharedArrayBuffer',
    'Atomics', 'DataView', 'Promise', 'Generator', 'GeneratorFunction',

    # — Reflect & Proxy
    'Reflect', 'Proxy',

    # — JSON
    'JSON', 

    # — URL / Networking
    'URL', 'URLSearchParams', 'fetch', 'Request', 'Response', 'Headers',
    'XMLHttpRequest', 'WebSocket', 'EventSource',

    # — DOM (Browser globals)
    'window', 'document', 'navigator', 'location', 'history', 'screen',
    'frames', 'self', 'parent', 'top', 'alert', 'confirm', 'prompt',
    'open', 'close', 'print', 'dispatchEvent', 'addEventListener',
    'removeEventListener', 'getComputedStyle',

    # — BOM / Web APIs
    'localStorage', 'sessionStorage', 'IndexedDB', 'openDatabase',
    'performance', 'Worker', 'SharedWorker', 'ServiceWorker', 'caches',
    'Cache', 'Notification', 'Geolocation', 'history', 'fetch', 'crypto',
    'CustomEvent', 'Event', 'MouseEvent', 'KeyboardEvent', 'TouchEvent',
    'PointerEvent', 'DragEvent', 'ClipboardEvent', 'InputEvent', 'StorageEvent',

    # — Canvas & Multimedia
    'CanvasRenderingContext2D', 'WebGLRenderingContext', 'AudioContext',
    'HTMLCanvasElement', 'HTMLVideoElement', 'HTMLAudioElement', 'MediaSource',
    'MediaRecorder', 'MediaStream', 'Image', 'ImageData',

    # — CSSOM
    'CSS', 'CSSRule', 'CSSStyleSheet', 'CSSStyleRule', 'CSSMediaRule',

    # — Service & Web Workers
    'importScripts', 'postMessage', 'onmessage', 'onerror', 'skipWaiting',
    'clients', 'self', 'registration',

    # — Intl (Internationalization)
    'Intl', 'Intl.Collator', 'Intl.DateTimeFormat', 'Intl.NumberFormat',
    'Intl.PluralRules', 'Intl.RelativeTimeFormat', 'Intl.ListFormat',
    'Intl.Locale',

    # — WebAssembly
    'WebAssembly', 'WebAssembly.Module', 'WebAssembly.Instance',
    'WebAssembly.Memory', 'WebAssembly.Table', 'WebAssembly.CompileError',
    'WebAssembly.LinkError', 'WebAssembly.RuntimeError',

    # — Typed Arrays Helpers
    'atob', 'btoa', 'TextEncoder', 'TextDecoder',

    # — Array.prototype Methods
    'concat', 'copyWithin', 'entries', 'every', 'fill', 'filter', 'find',
    'findIndex', 'flat', 'flatMap', 'forEach', 'includes', 'indexOf',
    'join', 'keys', 'lastIndexOf', 'map', 'pop', 'push', 'reduce', 'reduceRight',
    'reverse', 'shift', 'slice', 'some', 'sort', 'splice', 'toLocaleString',
    'toString', 'unshift', 'values', '[@@iterator]',

    # — String.prototype Methods
    'charAt', 'charCodeAt', 'codePointAt', 'concat', 'endsWith', 'includes',
    'indexOf', 'lastIndexOf', 'localeCompare', 'match', 'matchAll', 'padEnd',
    'padStart', 'repeat', 'replace', 'replaceAll', 'search', 'slice', 'split',
    'startsWith', 'substr', 'substring', 'toLocaleLowerCase', 'toLocaleUpperCase',
    'toLowerCase', 'toUpperCase', 'trim', 'trimStart', 'trimEnd', 'valueOf',
    '[@@iterator]',

    # — Object methods & statics
    'assign', 'create', 'defineProperties', 'defineProperty', 'entries',
    'freeze', 'fromEntries', 'getOwnPropertyDescriptor',
    'getOwnPropertyDescriptors', 'getOwnPropertyNames',
    'getOwnPropertySymbols', 'getPrototypeOf', 'is', 'isExtensible',
    'isFrozen', 'isSealed', 'keys', 'preventExtensions', 'seal',
    'setPrototypeOf', 'values',

    # — Math methods
    'abs', 'acos', 'acosh', 'asin', 'asinh', 'atan', 'atan2', 'atanh',
    'cbrt', 'ceil', 'clz32', 'cos', 'cosh', 'exp', 'expm1', 'floor',
    'fround', 'hypot', 'imul', 'log', 'log1p', 'log2', 'log10',
    'max', 'min', 'pow', 'random', 'round', 'sign', 'sin', 'sinh',
    'sqrt', 'tan', 'tanh', 'trunc',

    # — Number methods & statics
    'isFinite', 'isInteger', 'isNaN', 'isSafeInteger', 'parseFloat',
    'parseInt', 'toExponential', 'toFixed', 'toLocaleString', 'toPrecision',
    'EPSILON', 'MAX_SAFE_INTEGER', 'MIN_SAFE_INTEGER', 'MAX_VALUE',
    'MIN_VALUE', 'NaN', 'NEGATIVE_INFINITY', 'POSITIVE_INFINITY',

    # — Promise methods
    'all', 'allSettled', 'race', 'reject', 'resolve',

    # — Symbol
    'Symbol', 'Symbol.asyncIterator', 'Symbol.hasInstance',
    'Symbol.isConcatSpreadable', 'Symbol.iterator', 'Symbol.match',
    'Symbol.matchAll', 'Symbol.replace', 'Symbol.search',
    'Symbol.species', 'Symbol.split', 'Symbol.toPrimitive',
    'Symbol.toStringTag', 'Symbol.unscopables',

    # — Reflect API
    'Reflect.apply', 'Reflect.construct', 'Reflect.defineProperty',
    'Reflect.deleteProperty', 'Reflect.get', 'Reflect.getOwnPropertyDescriptor',
    'Reflect.getPrototypeOf', 'Reflect.has', 'Reflect.isExtensible',
    'Reflect.ownKeys', 'Reflect.preventExtensions', 'Reflect.set',
    'Reflect.setPrototypeOf',

    # — Proxy Traps
    'get', 'set', 'has', 'deleteProperty', 'apply', 'construct',
    'defineProperty', 'getOwnPropertyDescriptor', 'getPrototypeOf',
    'isExtensible', 'ownKeys', 'preventExtensions', 'setPrototypeOf',

    # — Generator & Async
    'async', 'await', 'yield', 'next', 'throw', 'return',

    # — DOM Element Prototypes (örnek)
    'getElementById', 'getElementsByClassName', 'getElementsByTagName',
    'querySelector', 'querySelectorAll', 'createElement', 'createTextNode',
    'appendChild', 'removeChild', 'replaceChild', 'cloneNode',
    'addEventListener', 'removeEventListener', 'dispatchEvent',
    'setAttribute', 'getAttribute', 'removeAttribute', 'classList',
    'style', 'innerHTML', 'textContent',

    # — EventTarget methods
    'onload', 'onclick', 'onerror', 'onsubmit', 'onkeydown', 'onkeyup',

    # — Other useful globals
    'alert', 'confirm', 'prompt', 'matchMedia', 'requestAnimationFrame',
    'cancelAnimationFrame', 'atob', 'btoa', 'postMessage', 'import',
    'arguments', 'globalThis'
}

class Crawler:
    def __init__(self, start_url, max_depth=2):
        self.start_url = start_url
        self.parsed_start = urlparse(start_url)
        self.domain = self.parsed_start.netloc
        self.max_depth = max_depth
        self.visited = set()
        self.queue = deque([(start_url, 0)])
        self.all_words = set() 
        self.scraper = cloudscraper.create_scraper()
        self.scraper.headers.update({'User-Agent': USER_AGENTS[0]})

    def is_valid_url(self, url):
        parsed = urlparse(url)
        return bool(parsed.netloc) and (parsed.netloc == self.domain or parsed.netloc == '')

    def extract_keywords_from_text(self, text):
        keywords = set()
        string_literals = re.findall(r"(?:'([^']+)')|(?:\"([^\"]+)\")|(?:`([^`]+)`)", text)
        for match in string_literals:
            for val in match:
                if val and len(val) > 2:
                    keywords.update(re.split(r"[^a-zA-Z0-9_-]", val))

        keywords.update(re.findall(r"\.([\w-]+)\b", text))
        
        raw_words = re.findall(r"\b[a-zA-Z0-9_-]+\b", text)
        for w in raw_words:
            if w not in JS_RESERVED and not w.isdigit() and len(w) > 2:
                keywords.add(w)
        return keywords

    def extract_params_from_html(self, soup):
        params = set()
        for tag in soup.find_all(['input', 'textarea', 'select']):
            if tag.get('name'):
                params.add(tag['name'])
        for tag in soup.find_all(id=True):
            params.add(tag['id'])
        return params

    def extract_params_from_url(self, url):
        parsed = urlparse(url)
        qs = parse_qs(parsed.query)
        return set(qs.keys())

    def fetch_and_analyze(self, url):
        try:
            print(f"[*] Crawling: {url}")
            resp = self.scraper.get(url, timeout=10)
            if resp.status_code != 200:
                return []

            content_type = resp.headers.get('Content-Type', '')
            text_content = resp.text

            self.all_words.update(self.extract_params_from_url(url))
            self.all_words.update(self.extract_keywords_from_text(text_content))

            if 'javascript' in content_type or 'json' in content_type or url.endswith('.js'):
                return []

            soup = BeautifulSoup(text_content, 'html.parser')
            self.all_words.update(self.extract_params_from_html(soup))

            new_links = set()
            
            for a in soup.find_all('a', href=True):
                full_url = urljoin(url, a['href'])
                if self.is_valid_url(full_url):
                    self.all_words.update(self.extract_params_from_url(full_url))
                    path_parts = urlparse(full_url).path.split('/')
                    self.all_words.update([p for p in path_parts if p])
                    new_links.add(full_url)

            for script in soup.find_all('script', src=True):
                js_url = urljoin(url, script['src'])
                if self.is_valid_url(js_url):
                    new_links.add(js_url)

            return list(new_links)

        except Exception as e:
            print(f"[!] Error processing {url}: {e}")
            return []

    def start(self):
        print(f"--- Starting Crawl on {self.domain} (Max Depth: {self.max_depth}) ---")
        
        while self.queue:
            current_url, depth = self.queue.popleft()
            
            parsed_clean = urlparse(current_url)
            clean_url = f"{parsed_clean.scheme}://{parsed_clean.netloc}{parsed_clean.path}"

            if clean_url in self.visited:
                continue
            
            if depth > self.max_depth:
                continue

            self.visited.add(clean_url)
            
            found_links = self.fetch_and_analyze(current_url)
            
            for link in found_links:
                self.queue.append((link, depth + 1))
            
            time.sleep(0.5)

    def save_results(self):
        safe_domain = self.domain.replace(':', '_')
        file_wordlist = f"{safe_domain}_wordlist.txt"
        file_urls = f"{safe_domain}_crawled_urls.txt"

        print(f"\n[✓] Crawl Finished for {self.domain}")
        print(f"    - Total Unique Words/Params: {len(self.all_words)}")
        print(f"    - Total Pages/Files Visited: {len(self.visited)}")

        with open(file_wordlist, 'w', encoding='utf-8') as f:
            for word in sorted(self.all_words):
                f.write(f"{word}\n")
        
        with open(file_urls, 'w', encoding='utf-8') as f:
            for url in sorted(self.visited):
                f.write(f"{url}\n")
                
        print(f"[+] Files saved:\n    -> {file_wordlist}\n    -> {file_urls}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Advanced Parameter & Keyword Crawler')
    parser.add_argument('-u', '--url', required=True, help='Target URL to start crawling')
    parser.add_argument('-d', '--depth', type=int, default=2, help='Crawling depth (default: 2)')
    
    args = parser.parse_args()
    
    crawler = Crawler(args.url, max_depth=args.depth)
    crawler.start()
    crawler.save_results()