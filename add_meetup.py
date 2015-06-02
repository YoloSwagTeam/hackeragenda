import numpy
import requests

from io import BytesIO

from PIL import Image
from bs4 import BeautifulSoup
from redbaron import RedBaron
from colorific.palette import extract_colors

template = """
@event_source(background_color="%(background_color)s", text_color="%(text_color)s", url="%(url)s", predefined_tags=[%(tags)s])
def %(function_name)s():
    \"\"\"%(description)s\"\"\"
    return generic_meetup("%(meetup_name)s")
""".strip()


def color_distance(rgb1, rgb2):
    '''d = {} distance between two colors(3)'''
    rm = 0.5 * (rgb1[0] + rgb2[0])
    d = sum((2 + rm, 4, 3 - rm) * (rgb1 - rgb2) ** 2) ** 0.5
    return d


def rgb_to_hex(rgb):
    return "#" + "".join(map(lambda x: hex(x)[2:], rgb))


target_url = "http://www.meetup.com/Apprendre-a-programmer-un-site-WEB-debutant/"

soup = BeautifulSoup(requests.get(target_url).content)

description = soup.find("div", id="groupDesc")
description = (" " * 4).join(map(lambda x: str(x), description.contents)) + (" " * 4)
description = "\n".join(map(lambda x: x.rstrip(), description.split("\n")))

target_meetup_name = target_url.split("/")[-2]
target = target_url.split("/")[-2].lower().replace("-", "_")

logo_url = soup.find("img", "photo")["src"]
palette = extract_colors(Image.open(BytesIO(requests.get(logo_url).content)))
colors = palette.colors

background_color = colors[0].value

if len(colors) == 2:
    text_color = colors[1].value
else:
    numpy.array(background_color)
    text_color = max([(x.value, color_distance(numpy.array(background_color), numpy.array(x.value))) for x in colors[1:]], key=lambda x: x[1])[0]

red = RedBaron(open("agendas/be.py", "r").read())

before = red("def", recursive=False)[0]

for i in red("def", recursive=False):
    if target < i.name:
        break

    before = i

i.insert_before(template % {
    "background_color": rgb_to_hex(background_color),
    "text_color": rgb_to_hex(text_color),
    "url": target_url,
    "tags": "",
    "function_name": target,
    "description": description,
    "meetup_name": target_meetup_name,
})

red.dumps()

open("agendas/be.py", "w").write(red.dumps())
