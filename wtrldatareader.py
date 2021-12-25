import requests

r = requests.post(url="https://www.wtrl.racing/api/wtrlruby.php",
                  data={
                      "wtrlid": "wtrlttt",
                      "season": "140", # session
                      "action": "results"
                  },
                  headers= {
                      "Authorization": WTRL['bearer'], # static for ur account
                      "Content-Type": "application/x-www-form-urlencoded"
                  })
print(r.status_code)
print(r.json())
