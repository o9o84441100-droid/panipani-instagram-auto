"""Run locally to reauthorize the existing Canva app; never paste secrets in chat."""
import base64,getpass,hashlib,json,os,secrets,sys,webbrowser
from pathlib import Path
from urllib.parse import urlencode,urlparse,parse_qs
from urllib.request import Request,urlopen
from urllib.error import HTTPError
def main():
 client=input("Existing Canva Client ID: ").strip()
 secret=getpass.getpass("Existing Canva Client Secret (hidden): ").strip()
 redirect=input("Exact registered Redirect URL: ").strip()
 scopes=input("Existing enabled scopes, separated by spaces: ").strip()
 if not(client and secret and redirect and scopes):raise SystemExit("All inputs are required")
 if urlparse(redirect).scheme not in ("http","https"):raise SystemExit("Invalid redirect URL")
 verifier=secrets.token_urlsafe(64)
 challenge=base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
 state=secrets.token_urlsafe(32)
 params={"client_id":client,"response_type":"code","redirect_uri":redirect,"scope":scopes,"code_challenge":challenge,"code_challenge_method":"S256","state":state}
 authorize="https://www.canva.com/api/oauth/authorize?"+urlencode(params)
 print("Opening the official Canva authorization page. If it does not open, use this URL:")
 print(authorize)
 webbrowser.open(authorize)
 callback=getpass.getpass("Paste the full redirected URL here only (hidden): ").strip()
 expected=urlparse(redirect);actual=urlparse(callback)
 if (expected.scheme,expected.netloc,expected.path)!=(actual.scheme,actual.netloc,actual.path):raise SystemExit("Redirect URL mismatch")
 q=parse_qs(actual.query)
 if q.get("state",[""])[0]!=state:raise SystemExit("State mismatch; stop and restart authorization")
 code=q.get("code",[""])[0]
 if not code:raise SystemExit("No authorization code. Check the Canva consent result")
 body=urlencode({"grant_type":"authorization_code","code_verifier":verifier,"code":code,"redirect_uri":redirect}).encode()
 credentials=base64.b64encode((client+":"+secret).encode()).decode()
 request=Request("https://api.canva.com/rest/v1/oauth/token",data=body,headers={"Authorization":"Basic "+credentials,"Content-Type":"application/x-www-form-urlencoded"},method="POST")
 try:
  with urlopen(request,timeout=35) as response:result=json.load(response)
 except HTTPError as exc:
  try:detail=json.loads(exc.read())
  except Exception:detail={}
  safe=detail.get("code",detail.get("error","unknown"))
  known={"invalid_grant","invalid_client","invalid_request","invalid_scope","unauthorized_client","invalid_field"}
  raise SystemExit("Token exchange failed: HTTP %s, code=%s" % (exc.code,safe if isinstance(safe,str) and safe in known else "unclassified"))
 token=result.get("refresh_token")
 if not token:raise SystemExit("No refresh_token returned")
 dest=Path.home()/"canva-new-refresh-token.txt"
 fd=os.open(dest,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
 with os.fdopen(fd,"w",encoding="utf-8") as target:target.write(token)
 print("Refresh token saved locally:",dest)
 print("Paste its contents into GitHub secret CANVA_REFRESH_TOKEN, then run canva-reauthorize.yml exactly once.")
 print("Do not exchange this refresh token manually, upload this local token file, or paste its contents in chat.")
if __name__=="__main__":main()
