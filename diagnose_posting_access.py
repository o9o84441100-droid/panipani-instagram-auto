"""Read-only Instagram checks and one Canva credential refresh; never publish."""
import json,os,re
from pathlib import Path
import requests
def instagram():
 token=os.getenv("INSTAGRAM_ACCESS_TOKEN","")
 if not token:return {"status":"missing_secret"}
 r=requests.get("https://graph.instagram.com/me",headers={"Authorization":"Bearer "+token},params={"fields":"id,username"},timeout=45)
 try:data=r.json()
 except ValueError:return {"http":r.status_code,"status":"non_json"}
 err=data.get("error") or {}
 if not r.ok or err:
  msg=str(err.get("message","")).replace(token,"[REDACTED]")
  return {"status":"blocked","http":r.status_code,"endpoint":"/me","code":err.get("code"),"subcode":err.get("error_subcode"),"type":err.get("type"),"transient":err.get("is_transient",False),"message":msg}
 if str(data.get("id"))!="28854255504200287":return {"status":"wrong_account"}
 return {"status":"connected","http":r.status_code}
def canva():
 from canva_oauth import get_access_token
 try:
  token=get_access_token()
  r=requests.get("https://api.canva.com/rest/v1/users/me",headers={"Authorization":"Bearer "+token},timeout=35)
  return {"status":"connected" if r.ok else "access_failed","http":r.status_code}
 except Exception as e:
  # OAuth errors are deliberately sanitized by the credential module.
  return {"status":"failed","message":str(e)}
def main():
 results={"instagram":instagram(),"canva":canva()}
 Path("output").mkdir(exist_ok=True)
 Path("output/auth_diagnosis.json").write_text(json.dumps(results,ensure_ascii=False,indent=2))
 summary=os.getenv("GITHUB_STEP_SUMMARY")
 if summary:
  with open(summary,"a") as target:target.write("Credential diagnosis (no publication):\n"+json.dumps(results,ensure_ascii=False,indent=2))
 print(json.dumps(results,ensure_ascii=False))
if __name__=="__main__":main()
