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
