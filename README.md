Introduction
============

http://hackeragenda.be is a website that aggregate events in Belgium that are
interesting for hackers of the hackerspace community. It does that by fetching
data from other website (by scraping most of the time ...) *instead* of asking
users to submit events on it. This is my modest attemp to answer the problem
"everyone is doing shitload of things and no one is aware of that and that
sucks".

Installation
============

You need [bower](http://bower.io/)! You'll probably need to have a rescent version of nodejs to install it.

    git clone https://github.com/Psycojoker/hackeragenda.git
    cd hackeragenda
    virtualenv ve
    source ve/bin/activate
    pip install -r requirements.txt
    python manage.py syncdb --noinput
    python manage.py migrate
    python manage.py bower_install

Usage
=====

To update the events:

    python manage.py fetch_events

In production, this command is in a crontab that run every one hour.

How to add an organisation
==========================

1. Add a new function in `events/management/commands/fetch_events.py`
2. Add the function in the sources (`fetch_events.py` line ~36)
3. Add a color to the organization in `events/colors.py`
4. You might want to modify default filters in hackeragenda/settings.py
5. Test
6. Pull request

Example of a commit that add an organisation for the "Code" section: https://github.com/Psycojoker/hackeragenda/commit/0e91e210a8a093e5704af8665ee16c6001834d20

Other countries
===============

I'm looking for volunteers to open other instance of hackeragenda in other
countries. France will probably be the next one. Don't hesitate to contact me
if you want to do so!(see my mail on my profile) I can provide hosting (but
without giving you access to it :/) and I'd like you to be at least able to
write a web parser in python using
[BeaufitulSoup](http://www.crummy.com/software/BeautifulSoup/) (or learn how
to) and be ready to learn a bit of Django (not that much) if you don't already
know it.

My objective is to end up with Hackeragenda all over the world and
meta-hackeragenda like hackeragenda.eu.
