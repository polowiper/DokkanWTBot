import json 
from datetime import datetime, timezone, timedelta



path = "fetches"


for i in range(0, 293):
    with open(f"{path}/fetch{i}.json", "r") as e:
        data = json.load(e)
        update = datetime.utcfromtimestamp(data["userlist"]["updated_at"]).replace(tzinfo=timezone.utc)
        print(f"fetch{i} | update:{update}")

end = datetime.fromisoformat(data["end_at"]).astimezone(timezone.utc)

print(f"End : {end}")

