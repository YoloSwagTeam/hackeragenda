import requests

from bs4 import BeautifulSoup
from redbaron import RedBaron

template = """
@event_source(background_color="%(background_color)s", text_color="%(text_color)s", url="%(url)s", predefined_tags=[%(tags)s])
def %(function_name)s():
        \"\"\"%(description)s\"\"\"
            return generic_meetup("%(meetup_name)s")
""".strip()

target_url = "http://www.meetup.com/Apprendre-a-programmer-un-site-WEB-debutant/"

soup = BeautifulSoup(requests.get(target_url).content)

description = soup.find("div", id="groupDesc")
description = (" " * 4).join(map(lambda x: str(x), description.contents)) + (" " * 4)

target_meetup_name = target_url.split("/")[-2]
target = target_url.split("/")[-2].lower().replace("-", "_")

red = RedBaron(open("agendas/be.py", "r").read())

before = red("def", recursive=False)[0]

for i in red("def", recursive=False):
    if target < i.name:
        break

    before = i

print i.name
print
print template % {
    "background_color": "",
    "text_color": "",
    "url": target_url,
    "tags": "",
    "function_name": target,
    "description": description,
    "meetup_name": target_meetup_name,
}
