from urllib.parse import urlparse
import pathlib
import subprocess
 

def speedtest_using_cli():
  process = subprocess.Popen("speedtest-cli --simple",shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  stdout, stderr = process.communicate()
  return stdout.decode('utf-8')

def extension(fpath):
  return str(pathlib.Path(fpath).suffix)

def is_url(url):
  try:
    result = urlparse(url)
    return all([result.scheme, result.netloc])
  except :
    return False

def progress(current,total):
  bar =""
  current = int(current/10)
  for i in range(0,10):
      if(i < current):
          bar += "■" 
      else:
          bar += "□"
  return f"[{bar}]"