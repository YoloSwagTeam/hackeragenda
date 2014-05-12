Introduction
============

Hackeragenda is a website that aggregate events in Belgium that are interesting
for hackers of the hackerspace community. It does that by fetching data from
other website (by scraping most of the time ...) *instead* of asking users to
submit events on it. This is my modest attemp to answer the problem "eve ryone
is doing shitload of things and no one is aware of that and that sucks".

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
