# encoding: utf-8

from agendas.env import *

generic_facebook("bite_back", "BiteBackOrg", background_color="#db0c38", text_color="#FFFFFF", agenda="vg_be", tags=["animal-rights"])


@event_source(background_color="#539316", text_color="#FFFFFF", agenda="vg_be", url="http://www.evavzw.be")
def eva(create_event):
    """EVA werd opgericht in 2000 door een handjevol gemotiveerde mensen uit het Gentse en is sindsdien uitgegroeid tot een organisatie met een tiental vaste medewerkers, verschillende lokale groepen en honderden vrijwilligers. Sinds haar ontstaan heeft de organisatie al heel wat activiteiten en projecten op poten gezet."""
    nl_months = {
             'januari': 1,
             'februari': 2,
             'maart': 3,
             'april': 4,
             'mei': 5,
             'juni': 6,
             'juli': 7,
             'augustus': 8,
             'september': 9,
             'oktober': 10,
             'november': 11,
             'december': 12
             }

    tags_mapping = {
            'EVA kookcursus': 'cooking class',
            'kookcursus': 'cooking class',
            'eten': 'eating',
            'EVA eten': 'eating',
            }

    now = datetime.now()

    src_url = "http://www.evavzw.be/index.php?option=com_agenda"
    soup = BeautifulSoup(requests.get(src_url).content)
    for month in soup(attrs={"class":'agenda'}):
        month_nb = int(nl_months[month['id'].split('_')[1]])

        # If the month has passed assume it's next year
        if month_nb < now.month:
            year = now.year + 1
        else:
            year = now.year

        for day in month('li'):
            if day.get('id') is None:
                continue

            day_nb = int(day['id'].split('_')[1])
            for event in day('li'):
                title = event.a.text
                url = 'http://www.evavzw.be/' + event.a['href']
                hour, minute = 0, 0
                tags = []

                for span in event('span'):
                    if 'time' in span['class']:
                        hour, minute = map(int, span.text.split('vanaf ')[1].split('u'))
                    else:
                        # Tag
                        tag = tags_mapping.get(span.text)
                        if tag is not None:
                            tags.append(tag)

                start = datetime(year, month_nb, day_nb, hour, minute)

                event = create_event(
                    title=title,
                    url=url,
                    start=start,
                )

                for tag in tags:
                    event.tags.add(tag)




generic_facebook("gaia", "gaia.be", background_color="#fdfafa", text_color="#5d3b80", agenda="vg_be", tags=["animal-rights"])


@event_source(background_color="#66b822", text_color="#FFFFFF", agenda="vg_be", url="http://www.jeudiveggie.be")
def jeudi_veggie(create_event):
    """Le Jeudi Veggie est une campagne qui nous invite à découvrir un jour par semaine, une assiette plus équilibrée, qui fait la part belle aux céréales, aux fruits et aux légumes. Une assiette sans viande ni poisson, mais avec plein de fruits et légumes."""
    tags_mapping = {
            'atelier': 'cooking class',
            'cours de cuisine': 'cooking class',
            'diner': 'eating',
            }

    # request events from today to next year
    today = datetime.now().strftime("%d-%m-%Y")
    next_year = (datetime.now() + timedelta(weeks=52)).strftime("%d-%m-%Y")

    src_url = "http://www.jeudiveggie.be/kalender/zoeken/%s_%s/" % (today, next_year)
    soup = BeautifulSoup(requests.get(src_url).content)

    main = soup.find(id='itemtag')
    for d in main(attrs={'class': 'date'}):
        full_date = d['href'].split('/')[2]
        day, month, year = full_date.split('-')

        url = 'http://www.jeudiveggie.be' + d['href']
        if d.text[2] == ':':
            time, title = d.text.split(' ', 1)
            hour, minute = time.split(':')

            start = datetime(int(year), int(month), int(day), int(hour), int(minute))
        else:
            title = d.text
            start = datetime(int(year), int(month), int(day))

        event = create_event(
            title=title,
            url=url,
            start=start,
        )

        # tags
        span = d.findNextSibling()
        if span.name == 'span':
            splitted = map(unicode.strip, span.text[1:-1].split(','))

            # first element is a tag
            t = tags_mapping.get(splitted[0])
            if t is not None:
                event.tags.add(t)

            # second one is a location
            if len(splitted) > 1:
                event.location = splitted[1]
                event.save()
