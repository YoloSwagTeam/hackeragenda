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

You need [bower](http://bower.io/)! You'll probably need to have a recent 
version of nodejs to install it.

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

Events are periodically fetched from organisations websites. Therefore, you 
have to write an `@event_source` decorated function *(aka fetcher)* in 
`events/management/commands/fetch_events.py`. The decorator allows you to 
specify the colorset for your organisation and its intended agenda. Your 
function should take 1 argument: a function to add events to the database.


Here's a small fetcher example:

    @event_source(background_color="#424242", text_color="#777", agenda="be")
    def my_organisation(create_event):
        events = json.loads(urlopen("https://my.organisat.io/n").read())
        for ev in events:
            create_event(
                title=ev.name,
                start=ev.start_time,
                end=ev.end_time,
                url=ev.href
            )

If your organisation use Meetup to schedule its events, you just have to add
this unique line at toplevel:

    generic_meetup("my_org_name_on_hackeragenda", "my_org_name_on_Meetup", background_color="#424242", text_color="#777", agenda="be")

Moreover, you can also implement the hackeragenda JSON api on your side, and add
the following line at toplevel in `events/management/commands/fetch_events.py`:

    json_api("my_org", "https://my.organisat.io/n/hackeragenda.json", background_color="#424242", text_color="#777", agenda="be")

A `GET` on provided url should return something like this:
    
    {
        "org": "my_organisation",
        "api" : 0.1,
        "events" : [
            {
               "title": "Small conf",
               "start": "2012-05-23 12:00",
               "end": "2012-05-23 18:23",
               "all_day": false,
               "url": "https://my.organisat.io/n/LearnRubyWithSinatra"
            },
            {
               "title": "Marvelous conference",
               "start": "2012-05-23 12:00",
               "all_day": true,
               "location": "123 avenue du soleil",
               "url": "https://my.organisat.io/n/PwnGoogleWithx86_64Assembly"
            }
        ]
    }

The following attributes are **required**:

* "org" : Organisation name (string)
* "api" : API version number (currently 0.1) (float)
* "events" : A list of events objects (list of objects)
    * "title" : Name of the event (string)
    * "url" : URL for this event (string)
    * "start" : start date of the event, in ISO8601 (string)

Each event could optionally provide the following attributes:

* "end" : end of the event, in ISO8601 (string)
* "all_day" : Is the event the whole day? (boolean)
* "location" : Human readable adress for your event (string)

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
