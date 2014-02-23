YOU NEED [BOWER](http://bower.io/)! You'll probably need to have a rescent version of nodejs to install it.

Foobar:

    git clone https://github.com/Psycojoker/hackeragenda.git
    cd hackeragenda
    virtualenv ve
    source ve/bin/activate
    pip install -r requirements.txt
    python manage.py syncdb --noinput
    python manage.py bower_install

To update the events:

    python manage.py fetch_events

To add a new organization :

1. Add a new function in `events/management/commands/fetch_events.py`
2. Add the function in the sources (`fetch_events.py` line ~36)
3. Add a color to the organization in `events/colors.py`
4. Test
5. Pull request