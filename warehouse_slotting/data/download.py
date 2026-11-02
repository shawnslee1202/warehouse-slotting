"""Download pinned public mirror; verify length and SHA-256 before accepting."""
import argparse,hashlib,json,urllib.request
from pathlib import Path
BASE='https://huggingface.co/datasets/attik/Instacart-Market-Basket-Analysis/resolve/ff7fd3515d570a606635dfc263cf65216af57713/'
FILES={
 'aisles.csv':(2603,'2c5f4677761907d3a3ca01edd2d2abe67c147cc60e4905e68736d5f9f3046067'),
 'departments.csv':(270,'e6829cea3da95ec22eeb4e0294094a68b929f3bcfda48fdd7d1e33403110fc43'),
 'products.csv':(2166953,'abc61fdd748003d280ae49cc5d71b65380805ab1ca55dba96fd9a49295ea78b9'),
 'orders.csv':(108968645,'92a60ced67ac33bd82271f66ff9675374f69482d17a0e1442ba42caa8b3bff89'),
 'order_products__prior.csv':(577550706,'27b59dc9cf0d485f55e64e0bc9c5d6fb077ae167f8dfeab9246a03b5b0186359')}
def digest(p):
    with p.open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()
def download(out):
    out=Path(out); out.mkdir(exist_ok=True,parents=True); manifest=[]
    for name,(size,sha) in FILES.items():
        p=out/name; url=BASE+name+'?download=true'
        if not p.exists() or p.stat().st_size!=size or digest(p)!=sha:
            temp=p.with_suffix('.partial')
            with urllib.request.urlopen(url,timeout=120) as response,temp.open('wb') as f:
                while block:=response.read(1024*1024): f.write(block)
            if temp.stat().st_size!=size or digest(temp)!=sha: raise ValueError('Integrity check failed: '+name)
            temp.replace(p)
        manifest.append(dict(file=name,bytes=size,sha256=sha,url=url)); print(name,'verified',flush=True)
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2))
if __name__=='__main__':
    a=argparse.ArgumentParser(); a.add_argument('--out',default='data/raw'); download(a.parse_args().out)
