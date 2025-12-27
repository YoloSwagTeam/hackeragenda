# Introduction

[Hackeragenda](http://hackeragenda.be) is a website that aggregate events in Belgium that are
interesting for hackers of the hackerspace community. It does that by fetching
data from other website (by scraping most of the time ...) *instead* of asking
users to submit events on it. This is my modest attemp to answer the problem
"everyone is doing shitload of things and no one is aware of that and that
sucks".

# Installation

``` shell
git clone https://github.com/Psycojoker/hackeragenda.git
cd hackeragenda
pdm install
pdm run python manage.py migrate
```

# Usage

To update the events:

``` shell
pdm run fetch_events
```

In production, this command is in a crontab that run every one hour.

You can launch only one or more specific parser by passing them as args of the command:

``` shell
pdm run fetch_events urlab agenda_du_libre_be hsbxl
```

If you don't want any output you can use the <code>--quiet</code> command line
option (this is very usefull if you want to use it in a crontab):

``` shell
pdm run fetch_events --quiet
```

# How to add an organisation

Events are periodically fetched from organisations websites. Therefore, you 
have to write an `@event_source` decorated function *(aka fetcher)* in 
[`agendas/<your category>`](https://github.com/Psycojoker/hackeragenda/tree/master/agendas/). The decorator allows you to
specify options for your organisation. This function should 
[yield](https://wiki.python.org/moin/Generators) all the events you want to add.


## Write a custom event_source

You could provide a description for your organization with a python docstring.
Here's a small fetcher example:

```python
@event_source(background_color="#424242", text_color="#777", url="https://my.organisat.io/n")
def my_organisation():
    """My organization is a hackerspace in a train"""
    events = json.loads(urlopen("https://my.organisat.io/n/events").read())
    for ev in events:
        tags = ["hackerspace"]
        if "weekly meeting" in ev.name.lower():
            tags.append("meeting")
        yield {
            'title': ev.name,
            'start': ev.start_time,
            'end': ev.end_time,
            'url': ev.href,
            'tags': tags
        }
```

## Meetup

If your organisation use Meetup to schedule its events, you just have to add
this unique line at toplevel (this automagically creates an event_source):

```python
generic_meetup("my_org_name_on_hackeragenda", "my_org_name_on_Meetup", **same options as @event_source)
```

## Eventbrite

```python
generic_eventbrite("my_org_name_on_hackeragenda", "my_org-1865700117", **same options as @event_source)
```

## Facebook

Adding events from a Facebook group or page is pretty easy as well:

```python
generic_facebook("my_org_name_on_hackeragenda", "facebook_id", **same options as @event_source)
```

This requires to have FACEBOOK_APP_ID and FACEBOOK_APP_SECRET defined in the
settings file of your agenda with the credentials of your Facebook
application.

## Google Agenda

```python
generic_google_agenda(
    "my_org_name",
    "https://www.google.com/calendar/ical/<calendar_id>/public/basic.ics",
    **same options as @event_source)
```

## Implement the Hackeragenda API

Moreover, you can also implement the hackeragenda JSON api on your side, and add
the following line at toplevel in `events/management/commands/fetch_events.py`:

```python
json_api("my_org", "https://my.organisat.io/n/hackeragenda.json", **same options as @event_source)
```

A `GET` on the provided url should return something like this:

```json
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
```

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

# Other countries

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

Current public instance (known to me):

* [Belgium](http://hackeragenda.be)
* [France](http://hackeragenda.fr)
