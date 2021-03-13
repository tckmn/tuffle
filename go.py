#!/usr/bin/env python3

import xml.etree.ElementTree as ET
import glob

ABBREV = {
    'sectorname_FINAL':                 'LS',
    'sectorname_CIVILIAN_SECTOR':       'CS',
    'sectorname_ENGI_SECTOR':           'EC',
    'sectorname_ENGI_HOME':             'EH',
    'sectorname_PIRATE_SECTOR':         'PC',
    'sectorname_REBEL_SECTOR_MINIBOSS': 'RS',
    'sectorname_REBEL_SECTOR':          'RC',
    'sectorname_MANTIS_SECTOR':         'MC',
    'sectorname_MANTIS_HOME':           'MH',
    'sectorname_NEBULA_SECTOR':         'UN',
    'sectorname_SLUG_HOME':             'SH',
    'sectorname_SLUG_SECTOR':           'SC',
    'sectorname_ZOLTAN_SECTOR':         'ZC',
    'sectorname_ZOLTAN_HOME':           'ZH',
    'sectorname_ROCK_SECTOR':           'RC',
    'sectorname_ROCK_HOME':             'RH',
    'sectorname_CRYSTAL_HOME':          'CW',
    'sectorname_LANIUS_SECTOR':         'AS'
}

DATA = lambda x: f'ftldata/data/{x}'

NOTHING = '<p class="nothing">[Nothing happens.]</p>'

def mkdict(tags, tag, fn, idstr):
    d = {t.get('name'): [fn(t)] for t in tags if t.tag == tag}
    add = [t for t in tags if t.tag == f'{tag}List']
    while add:
        t = add.pop(0)
        if all((lambda lookup: lookup is None or lookup in d)(tt.get(idstr)) for tt in t):
            d[t.get('name')] = [el for tt in t for el in (lambda lookup: [fn(tt)] if lookup is None else d[lookup])(tt.get(idstr))]
        else:
            add.append(t)
    return d
    # return {
    #     **{k: [v] for k,v in tmp.items()},
    #     **{t.get('name'): [tmp[tt.get(idstr)] if tt.get(idstr) else fn(tt) for tt in t] for t in ttags+etags if t.tag == f'{tag}List'}
    # }

etags = [t for path in glob.glob(DATA('events*.xml')) + [DATA('newEvents.xml'), DATA('dlcEvents_anaerobic.xml')] for t in ET.parse(path).getroot()]
ttags = [t for path in glob.glob(DATA('text_*.xml')) for t in ET.parse(path).getroot()]

class Event:
    def __init__(self, tags):
        self.tags = tags
        self.where = set()

texts = mkdict(ttags+etags, 'text', lambda x: x.text, 'id')
events = {k: Event(v) for k,v in mkdict(etags, 'event', lambda x: x, 'load').items()}

for sec in ET.parse(DATA('sector_data.xml')).getroot().iter('sectorDescription'):
    secname = sec.find('nameList').find('name')
    if secname is None: continue
    secname = secname.get('id')
    if secname == 'sectorname_STANDARD_SPACE': continue
    for ch in sec:
        if ch.tag == 'event':
            events[ch.get('name')].where.add(secname)

def gettext(ev, klass='text'):
    if (t := ev.find('text')) is None: return ''
    i1, i2 = t.get('id'), t.get('load')
    return ''.join(f'<p class="{klass}">{t}</p>' for t in (texts[i1 or i2] if i1 or i2 else [t.text]))

def renderwhere(where):
    return f'''
    <div class="where">
        {''.join(f'<span data-tooltip="{texts[w][0]}">{ABBREV[w]}</span>' for w in sorted(where, key=lambda w: ABBREV[w]))}
    </div>
    '''

def renderev(ev):
    return f'''
    <ul class="event">
        <li>
            {gettext(ev, 'evtext')}
            {renderchoices(ev.findall('choice'))}
        </li>
    </ul>
    '''

def renderchoices(choices):
    return '<ol class="choices">' + ''.join(f'''
        <li>
            {gettext(c)}
            {rendersubev(c.find('event'))}
        </li>
    ''' for c in choices) + '</ol>'

def rendersubev(ev):
    if ev.get('load'):
        v = events[ev.get('load')]
        return ''.join(renderev(ev) for ev in v.tags)
    if len(ev):
        return renderev(ev)
    return NOTHING

with open('out/tuffle.html', 'w') as f:
    f.write('''
    <!DOCTYPE html>
    <html lang='en'>
        <head>
            <meta charset='utf-8'>
            <meta name='viewport' content='width=device-width'>
            <title>tuffle</title>
            <link rel='stylesheet' type='text/css' href='tuffle.css'></link>
        </head>
        <body>
            <main>
    ''')

    for k,v in events.items():
        if not len(v.where): continue
        for ev in v.tags:
            f.write(f'<div class="econtainer"><div class="header"><div class="evname">{k} {ev.get("name")}</div>')
            f.write(renderwhere(v.where))
            f.write('</div>')
            f.write(renderev(ev))
            f.write('</div>')

    f.write('''
            </main>
        </body>
    </html>
    ''')

# tree = ET.parse('ftldata/data/events.xml').getroot()
# print(list(tree))
# events = []

# def mkevent(el):
#     print(el)

# for el in tree:
#     if el.tag == 'event':
#         events.append([mkevent(el)])
#     elif el.tag == 'eventList':
#         events.append([mkevent(ch) for ch in el])
