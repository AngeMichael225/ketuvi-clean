from pathlib import Path
from urllib.parse import urlsplit
import html
import json
import os
import re
import sys

def public_origin(value):
    if not value:
        return ''
    origin=urlsplit(value)
    if (origin.scheme!='https' or not origin.hostname or origin.username is not None
        or origin.path not in ('','/') or '?' in value or '#' in value
        or any(c.isspace() or c=='\\' for c in value)):
        raise ValueError('KETUVI_PUBLIC_ORIGIN doit contenir uniquement l’origine HTTPS du site.')
    if origin.port == 0:
        raise ValueError('Le port du domaine public doit être compris entre 1 et 65535.')
    return 'https://'+origin.netloc

ROOT=Path(__file__).resolve().parent.parent
PORTABLE='--static' in sys.argv
STATIC_EMAIL=PORTABLE or os.environ.get('KETUVI_FORM_MODE')=='mailto' or os.environ.get('VERCEL')=='1'
origin_value=os.environ.get('KETUVI_PUBLIC_ORIGIN','').strip()
if PORTABLE and os.environ.get('VERCEL_ENV'):
    if os.environ['VERCEL_ENV']=='production':
        if not origin_value and os.environ.get('VERCEL_PROJECT_PRODUCTION_URL'):
            origin_value='https://'+os.environ['VERCEL_PROJECT_PRODUCTION_URL']
    else:
        origin_value=''
PUBLIC_ORIGIN=public_origin(origin_value)
PUBLIC=ROOT/('dist' if PORTABLE else 'site/public')
ASSETS=PUBLIC/'assets'
if PORTABLE:
    from static_media import prepare_static_media, publish_assets
    photo_provenance, photo_dimensions, photo_widths=prepare_static_media(ROOT, PUBLIC)
else:
    from local_media import prepare_local_media
    for path in (ASSETS/'photos', ASSETS/'fonts', ASSETS/'icons'):
        path.mkdir(parents=True,exist_ok=True)
    photo_provenance, photo_dimensions, photo_widths=prepare_local_media(ROOT, ASSETS)

EMAIL='info@ketuvi.com'
RESIDENTIAL_ROOMS=[
    ('cuisine', 'Cuisine', 'Comptoirs, évier et façades d’armoires.'),
    ('salle-de-bain', 'Salle de bain', 'Lavabo, robinetterie, miroir et douche.'),
    ('pieces-de-vie', 'Pièces de vie', 'Meubles, tablettes et sols des pièces communes.'),
]
RESIDENTIAL_FREQUENCIES=[
    ('une-fois','Un seul passage'),
    ('hebdomadaire','Chaque semaine'),
    ('aux-deux-semaines','Toutes les deux semaines'),
    ('a-discuter','À discuter ensemble'),
]
COMMERCIAL_AREAS=[
    ('bureaux','Bureaux et salles de réunion'),
    ('espaces-communs','Espaces communs'),
    ('sols-passages','Sols et passages'),
]
COMMERCIAL_TIMES=[
    ('avant-ouverture','Avant l’ouverture'),
    ('pendant-ouverture','Pendant les heures d’ouverture'),
    ('apres-fermeture','Après la fermeture'),
    ('a-discuter','À déterminer ensemble'),
]
OCCASIONAL_REASONS=[
    ('demenagement','Je déménage'),
    ('apres-construction','Nettoyage après construction'),
    ('decapage-plancher','Décapage d’un plancher'),
    ('remise-en-etat','Je remets un lieu en état'),
    ('surface-ciblee','J’ai une surface précise à nettoyer'),
]
SERVICES=[
    {
        'key':'commercial', 'path':'entretien-menager-commercial', 'title':'Entretien commercial',
        'situation':'Je gère des bureaux ou un commerce.',
        'guide':'Organiser l’entretien des postes de travail et des espaces partagés autour des heures d’ouverture.',
        'home_photo':'home-downtown-office', 'description':'Bureaux, commerces et espaces partagés.',
        'headline':'Un lieu de travail dont on prend soin.'
    },
    {
        'key':'residential', 'path':'entretien-menager-residentiel', 'title':'Entretien résidentiel',
        'situation':'Je veux faire entretenir mon logement.',
        'guide':'Faire nettoyer ma cuisine ou plusieurs pièces, une seule fois ou régulièrement.',
        'home_photo':'residential', 'description':'Cuisine, salle de bain et pièces de vie, selon vos priorités.',
        'headline':'Retrouver le plaisir d’être chez soi.',
        'scope_title':'Quelles pièces souhaitez-vous faire entretenir ?'
    },
    {
        'key':'occasional', 'path':'travaux-ponctuels', 'title':'Travaux ponctuels',
        'situation':'Je déménage ou je remets un lieu en état.',
        'guide':'Faire nettoyer le logement que je quitte avant la remise des clés ou remettre en état un plancher marqué.',
        'home_photo':'condo-postconstruction', 'description':'Après des travaux, avant une remise de clés ou pour un plancher à reprendre.',
        'headline':'Le bon soin, au bon moment.', 'hero_photo':'floor-stripping-technician'
    }
]
def esc(value):return html.escape(str(value),quote=True)
def icon(key):
    source=(ROOT/'site/public/assets/icons'/f'ketuvi-{key}.svg').read_text(encoding='utf-8')
    source=re.sub(r'<title[^>]*>.*?</title>','',source,flags=re.S)
    source=re.sub(r'\s(?:role|aria-labelledby)="[^"]*"','',source)
    return source.replace('<svg ','<svg class="icon" aria-hidden="true" focusable="false" ',1)
def logo():
    return '<a class="brand" href="/" aria-label="KetuviClean — Accueil"><img src="/assets/brandmark.png" width="40" height="40" alt=""><span>Ketuvi<span class="brand-light">Clean</span></span></a>'
def photo_srcset(key):
    return ', '.join(f'/assets/photos/{key}-{width}.webp {width}w' for width in photo_widths[key])

def photo(key,alt=None,cls='',priority=False,sizes='(max-width: 760px) 100vw, 50vw',cover=False):
    if alt is None:
        alt = photo_provenance[key]['description']
    loading = 'fetchpriority="high"' if priority else 'loading="lazy"'
    slot = sizes if priority or cover else f'auto, {sizes}'
    width,height = photo_dimensions[key]
    fallback = min(1440,width)
    image = f'<img class="{cls}" src="/assets/photos/{key}-{fallback}.webp" srcset="{photo_srcset(key)}" sizes="{slot}" width="{width}" height="{height}" alt="{esc(alt)}" {loading} decoding="async">'
    if not cover:
        return image
    portrait_key = f'{key}-portrait'
    width,height = photo_dimensions[portrait_key]
    return f'<picture><source media="(max-width: 450px) and (max-aspect-ratio: 3/5)" srcset="{photo_srcset(portrait_key)}" sizes="max(100vw, clamp(386px, 57.5svh, 503px))" width="{width}" height="{height}">{image}</picture>'
def arrow(cls='button-arrow'):
    return f'<svg class="{cls}" width="24" height="24" viewBox="0 0 24 24" fill="none" aria-hidden="true" focusable="false"><path d="M5 12h14m-6-6 6 6-6 6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'
def button(text,href,secondary=False,extra_class='',current=False):
    return f'<a class="button {"button-secondary" if secondary else "button-primary"} {extra_class}" href="{esc(href)}"'+(' aria-current="page"' if current else '')+f'><span>{text}</span>{arrow()}</a>'

def quote_link(service=None):
    return '/contact/' + (f'?service={service}' if service else '') + '#demande'

def planner_shortcut(classes,compact=False):
    content='Soumission' if compact else f'<span>Demander une soumission</span>{arrow()}'
    return f'<button type="submit" form="quote-planner" class="{classes}">{content}</button>'

def nav(current):
    easter_egg='<span class="nav-easter-egg" aria-hidden="true">Jésus est le Roi des rois</span>' if current=='home' else ''
    active=lambda path:' aria-current="page"' if current==path else ''
    service_links=''.join(f'<a href="/{s["path"]}/"{active(s["path"])}>{icon(s["key"])}<span>{s["title"]}</span></a>' for s in SERVICES)
    selected=next((s['key'] for s in SERVICES if s['path']==current),None)
    if selected:
        quote_action=planner_shortcut('button button-primary nav-contact')
        mobile_quote=planner_shortcut('mobile-quote',compact=True)
    elif current=='carrieres':
        quote_action=button('Postuler','#candidature',extra_class='nav-contact')
        mobile_quote='<a class="mobile-quote" href="#candidature">Postuler</a>'
    else:
        quote_href='#demande' if current=='contact' else quote_link()
        quote_action=button('Demander une soumission',quote_href,extra_class='nav-contact',current=current=='contact')
        mobile_quote=f'<a class="mobile-quote" href="{esc(quote_href)}">Soumission</a>'
    return f'''<a class="skip-link" href="#contenu">Aller au contenu</a><header class="site-header" data-header><div class="nav-shell">{logo()}{easter_egg}{mobile_quote}<details class="basic-menu"><summary>Menu</summary><nav aria-label="Navigation mobile"><a href="/services/">Nos services</a><a href="/a-propos/">À propos</a><a href="/carrieres/">Carrières</a></nav></details><button class="menu-toggle" type="button" aria-expanded="false" aria-controls="main-nav" aria-label="Ouvrir le menu"><span></span><span></span></button><nav class="main-nav" id="main-nav" aria-label="Navigation principale"><details class="nav-services"><summary>Services<svg width="12" height="8" viewBox="0 0 12 8" aria-hidden="true"><path d="m1 1 5 5 5-5" fill="none" stroke="currentColor" stroke-width="1.6"/></svg></summary><div class="nav-dropdown"><a class="all-services" href="/services/">Tous nos services</a>{service_links}</div></details><a href="/a-propos/"{active('a-propos')}>À propos</a><a href="/carrieres/"{active('carrieres')}>Carrières</a>{quote_action}</nav></div></header>'''
def footer(current):
    links=''.join(f'<a href="/{s["path"]}/">{s["title"]}</a>' for s in SERVICES)
    selected=next((s['key'] for s in SERVICES if s['path']==current),None)
    contact=''
    if selected or current in ('home','services','a-propos'):
        action=planner_shortcut('button button-primary') if selected else button('Demander une soumission',quote_link())
        contact=f'''<div class="signature-invitation"><h2>Parlons de vos espaces.</h2>
            <div class="signature-action">{action}</div></div>'''
    return f'''<footer class="signature-footer"><div class="container">
        {contact}
        <div class="signature-directory"><div class="signature-contact">
            <a class="signature-brand" href="/" aria-label="KetuviClean — Accueil"><img src="/assets/brandmark-white.png" width="173" height="160" alt="">
                <span>Ketuvi<span class="brand-light">Clean</span></span></a>
            <a class="signature-email" href="mailto:{EMAIL}">{EMAIL}</a>
        </div><nav class="signature-links" aria-labelledby="footer-services"><h2 id="footer-services"><a href="/services/">Nos services</a></h2>{links}</nav>
        <nav class="signature-links" aria-labelledby="footer-company"><h2 id="footer-company">Ketuvi</h2>
            <a href="/a-propos/">À propos</a><a href="/carrieres/">Carrières</a><a href="/contact/">Nous contacter</a></nav></div>
        <div class="signature-legal"><span>© 2026 Nettoyage Ketuvi Inc. · NEQ 1179475471</span><a href="/confidentialite/">Confidentialité</a>
            <a class="back-to-top" href="#haut" aria-label="Retour en haut de la page" title="Retour en haut de la page">
                <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 20V5m-7 7 7-7 7 7"/></svg>
            </a>
        </div>
    </div></footer>'''
def published_metadata(current,body):
    if not PUBLIC_ORIGIN or current=='404':
        return '<meta name="robots" content="noindex">'
    route='/' if current=='home' else f'/{current}/'
    canonical=esc(PUBLIC_ORIGIN+route)
    tags=[f'<link rel="canonical" href="{canonical}">', f'<meta property="og:url" content="{canonical}">',
          '<meta property="og:type" content="website">','<meta property="og:site_name" content="KetuviClean">',
          '<meta property="og:locale" content="fr_CA">']
    # Reuse the first editorial image of the page so a sharing card follows future photo changes.
    first=re.search(r'<img\b[^>]*?\ssrc="(/assets/photos/([^"]+)-(\d+)\.webp)"[^>]*?\salt="([^"]*)"',body)
    if first:
        image_path,key,width,alt=first.groups()
        image_alt=html.unescape(alt) or photo_provenance[key]['description']
        native_width,native_height=photo_dimensions[key]
        height=round(int(width)*native_height/native_width)
    else:
        image_path,image_alt='/assets/brandmark.png','Symbole de KetuviClean'
    tags.extend([f'<meta property="og:image" content="{esc(PUBLIC_ORIGIN+image_path)}">',
                 f'<meta property="og:image:alt" content="{esc(image_alt)}">'])
    if first:
        tags.extend([f'<meta property="og:image:width" content="{width}">',f'<meta property="og:image:height" content="{height}">'])
    return ''.join(tags)

def layout(title,description,body,current='home'):
    guide_styles='<link rel="stylesheet" href="/assets/service-guide.css">' if current=='services' else ''
    room_styles='<link rel="stylesheet" href="/assets/room-picker.css">' if current in ('entretien-menager-residentiel','contact') else ''
    planner_styles='<link rel="stylesheet" href="/assets/service-planner.css">' if current in ('entretien-menager-commercial','travaux-ponctuels') else ''
    planner_script='<script type="module" src="/assets/service-planner.js"></script>' if any(s['path']==current for s in SERVICES) else ''
    hero_scripts='<script type="module" src="/assets/hero.js"></script>' if current=='home' else ''
    font_preload='' if PORTABLE else '<link rel="preload" href="/assets/fonts/helvetica-roman.otf" as="font" type="font/otf" crossorigin>'
    return f'''<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="theme-color" content="#B35CFF"><meta name="description" content="{esc(description)}"><meta property="og:title" content="{esc(title)} | KetuviClean"><meta property="og:description" content="{esc(description)}">{published_metadata(current,body)}<title>{esc(title)} | KetuviClean</title><link rel="icon" href="/assets/brandmark.png">{font_preload}<link rel="stylesheet" href="/assets/styles.css"><link rel="stylesheet" href="/assets/hero.css"><link rel="stylesheet" href="/assets/footer.css">{room_styles}{planner_styles}{guide_styles}<script type="module" src="/assets/app.js"></script>{hero_scripts}{planner_script}</head><body id="haut" tabindex="-1" data-page="{current}">{nav(current)}<main id="contenu" tabindex="-1">{body}</main>{footer(current)}</body></html>'''

def home_service_cards():
    items=[]
    for service in SERVICES:
        key = service['home_photo']
        items.append(f'''<article class="service-cover"><a href="/{service['path']}/" aria-labelledby="card-{service['key']}"><div class="service-cover-media">{photo(key,sizes='(max-width: 700px) 100vw, 34vw')}</div><div class="service-cover-label"><div>{icon(service['key'])}<h3 id="card-{service['key']}">{service['title']}</h3></div><span class="service-cover-arrow">{arrow('cover-arrow')}</span></div></a><p>{service['description']}</p></article>''')
    return '<div class="service-covers">'+''.join(items)+'</div>'

def service_guide():
    examples={
        'commercial': [('Bureaux après la fermeture','espace=bureaux&creneau=apres-fermeture'),
                       ('Espaces communs avant l’ouverture','espace=espaces-communs&creneau=avant-ouverture')],
        'residential': [('Cuisine et salle de bain','piece=cuisine&piece=salle-de-bain'),
                        ('Pièces de vie seulement','piece=pieces-de-vie')],
        'occasional': [('Nettoyage avant la remise des clés','motif=demenagement'),
                       ('Nettoyage d’un condo après construction','motif=apres-construction')]
    }
    rows=[]
    for service in SERVICES:
        key=service['key']
        image=photo('catalogue-'+key,alt='',sizes='(max-width: 700px) 23vw, 200px')
        shortcuts=''.join(
            f'<a href="/contact/?service={key}&amp;{esc(params)}#demande">{esc(label)}{arrow("inline-arrow")}</a>'
            for label,params in examples[key])
        rows.append(f'''<li><a class="guide-choice" href="/{service['path']}/"
            aria-labelledby="situation-{key} destination-{key}" aria-describedby="example-{key}">
            {image}
            <div class="guide-copy"><h2 id="situation-{key}">{esc(service['situation'])}</h2>
                <p id="example-{key}">{esc(service['guide'])}</p></div>
            <span class="guide-destination" id="destination-{key}">{esc(service['title'])}{arrow('guide-arrow')}</span>
        </a><details class="guide-examples" name="guide-examples">
            <summary aria-label="Partir d’un exemple — {esc(service['title'])}">Partir d’un exemple<span class="plus" aria-hidden="true"></span></summary>
            <div class="guide-shortcuts"><p>Choisissez un exemple pour ouvrir votre soumission préremplie.</p>{shortcuts}</div>
        </details></li>''')
    return f'''<section class="container service-guide" aria-labelledby="guide-title">
        <div class="guide-header"><h1 id="guide-title">Quel entretien<br>vous faut-il&nbsp;?</h1>
            <div><p>Pour l’entretien courant, choisissez selon le lieu. Pour un déménagement ou une remise en état, explorez les travaux ponctuels.</p>
                <a class="editorial-link" href="{quote_link('general')}">J’aimerais en discuter{arrow('inline-arrow')}</a></div>
        </div><ul class="guide-list">{''.join(rows)}</ul></section>'''

quote_instructions=('Choisissez le service et les espaces dans le formulaire, puis ouvrez le courriel préparé. Envoyez-le depuis votre messagerie à info@ketuvi.com.' if STATIC_EMAIL else 'Remplissez le formulaire en indiquant le type de service recherché, les espaces concernés et vos besoins. Vous pouvez aussi nous écrire à info@ketuvi.com.')
FAQ=[('Comment demander une soumission ?',quote_instructions),('Quel service choisir pour mon espace ?','Pour l’entretien courant de votre logement, choisissez le résidentiel, même pour un seul passage. Pour vos bureaux ou votre commerce, choisissez le commercial. Pour un nettoyage avant la remise des clés ou une remise en état, consultez les travaux ponctuels.'),('Puis-je décrire un besoin particulier ?','Oui. Précisez les zones concernées, votre échéancier et les points d’attention dans votre message. Le périmètre de l’intervention se définit avec vous.')]
def faq(items=FAQ):return '<div class="faq-list">'+''.join(f'<details><summary>{q}<span class="plus" aria-hidden="true"></span></summary><p>{a}</p></details>' for q,a in items)+'</div>'

SERVICE_QUESTIONS={
    'commercial':[
        ('Puis-je choisir plusieurs espaces ?', 'Oui. Cochez les espaces à entretenir. Dans votre demande, vous pouvez aussi préciser les zones très fréquentées ou les contraintes d’accès.'),
        ('Et si je ne connais pas encore le meilleur moment ?', 'Choisissez « À déterminer ensemble ». Vous pourrez préciser vos heures d’ouverture dans la demande si vous les connaissez.')
    ],
    'residential':[
        ('Puis-je choisir seulement la cuisine ou la salle de bain ?', 'Oui. Cochez la ou les pièces souhaitées. Vous pourrez modifier votre sélection dans la demande de soumission.'),
        ('Où indiquer la fréquence souhaitée ?', 'Sous la liste des pièces, choisissez un seul passage, chaque semaine ou toutes les deux semaines. Vous pourrez modifier ce choix dans votre demande ou nous proposer un autre rythme dans votre message.')
    ],
    'occasional':[
        ('Que préciser pour une remise en état ?', 'Décrivez la situation de départ, les surfaces concernées et le résultat recherché. Mentionnez les matériaux délicats dans votre message.'),
        ('Que préciser après des travaux ?', 'Indiquez les pièces touchées, les surfaces neuves à protéger et le moment où les ouvriers auront terminé. Ces détails nous aident à évaluer le nettoyage à prévoir.'),
        ('Où indiquer la date de remise des clés ?', 'Choisissez « Je déménage » pour ajouter la date de remise des clés. Si elle est encore inconnue, vous pouvez préparer votre demande et préciser la date plus tard.')
    ]
}

def residential_work_photo():
    return f'''<figure class="room-planner-photo">
        {photo('residential-cabinet-care',sizes='(max-width: 760px) 100vw, 48vw')}
        <figcaption>L’essuyage des façades d’armoires.</figcaption>
    </figure>'''

def home_hero():
    scenes=[
        ('hero-editorial','Une professionnelle Ketuvi à l’œuvre dans un intérieur lumineux.','À la maison','/entretien-menager-residentiel/','Entretien résidentiel'),
        ('modern-office-meeting',None,'Au bureau','/entretien-menager-commercial/','Entretien commercial'),
        ('detail-editorial','Un geste d’entretien en gros plan.','Le geste de près','#le-travail-de-pres','Découvrir les gestes d’entretien'),
    ]
    frames=[]
    for i,(key,alt,caption,url,destination) in enumerate(scenes):
        visual=photo(key,alt,priority=i==0,sizes='min(100vw, 1800px)',cover=True)
        # The first shot renders in plain HTML. Other images load on selection.
        content=visual if i==0 else '<template>'+visual.replace('loading="lazy"','loading="eager"')+'</template>'
        frames.append(f'<div class="cover-shot" data-caption="{esc(caption)}" data-url="{esc(url)}" data-destination="{esc(destination)}" data-current="{str(i==0).lower()}" aria-hidden="{str(i!=0).lower()}">{content}</div>')
    _,_,caption,url,destination=scenes[0]
    return f'''<section class="cover-story" aria-labelledby="cover-heading"><div class="cover-window">
        <div class="cover-gallery" aria-label="Photographies des services Ketuvi">{''.join(frames)}</div>
        <div class="cover-scrim" aria-hidden="true"></div>
        <div class="cover-copy"><p class="cover-context">Entretien ménager résidentiel et commercial</p><h1 id="cover-heading"><span>Le propre,</span><span>ça se voit.</span></h1>
        <div class="cover-actions">{button("Demander une soumission",quote_link())}<a class="cover-guide-link" href="/services/">Quel service choisir ?{arrow('inline-arrow')}</a></div></div>
        <div class="cover-controls" role="group" aria-label="Parcourir les photographies">
            <a class="cover-readout" href="{esc(url)}" aria-label="{esc(caption)} — {esc(destination)}"><span data-count hidden aria-hidden="true"></span><span class="scene-title"><span data-caption-label>{esc(caption)}</span>{arrow('scene-arrow')}</span></a>
            <button hidden type="button" data-direction="-1" aria-label="Photo précédente">{arrow('gallery-arrow')}</button><button hidden type="button" data-direction="1" aria-label="Photo suivante">{arrow('gallery-arrow')}</button>
            <span class="gallery-announcement" role="status" aria-atomic="true"></span>
        </div>
        </div></section>'''

def photo_story():
    return f'''<section class="container craft-story" id="le-travail-de-pres" aria-labelledby="craft-title">
        <div class="showcase-heading"><h2 id="craft-title">Le travail de près.</h2><a class="editorial-link" href="/a-propos/">Découvrir notre approche{arrow('inline-arrow')}</a></div>
        <div class="craft-spread">
            <figure>{photo('team','Une professionnelle en polo Ketuvi essuie une cloison vitrée.',sizes='(max-width: 700px) 100vw, 55vw')}
                <figcaption><h3>Cloisons vitrées</h3><p>À contre-jour, les empreintes à hauteur de main se voient mieux. La lumière aide à repérer les endroits à reprendre.</p></figcaption>
            </figure>
            <figure>{photo('home-report-detail',sizes='(max-width: 700px) 100vw, 35vw')}
                <figcaption><h3>Préparation des microfibres</h3><p>Le pliage laisse plusieurs faces de tissu disponibles. On peut ainsi retourner la microfibre et poursuivre l’essuyage avec une face propre.</p></figcaption>
            </figure>
        </div></section>'''

home = (
    home_hero()
    + f'''<section class="container service-showcase" id="services"><div class="showcase-heading"><h2>Nos services.</h2><a class="editorial-link" href="/services/">Quel service choisir ?{arrow('inline-arrow')}</a></div>{home_service_cards()}</section>'''
    + photo_story()
    + f'''<section class="section container faq-section"><h2>Vos questions.</h2>{faq()}</section>'''
)

def page_hero(title,intro,key,action=None,context=''):
    action_html=f'<div class="page-hero-action">{button(*action)}</div>' if action else ''
    context_html=f'<p class="section-context">{context}</p>' if context else ''
    return f'<section class="page-hero"><div class="container page-hero-grid"><div>{context_html}<h1>{title}</h1><p>{intro}</p>{action_html}</div><div class="page-hero-image">{photo(key,priority=True)}</div></div></section>'

def room_choices(show_examples=False):
    choices=[]
    for key,label,description in RESIDENTIAL_ROOMS:
        detail=f'<small id="detail-{key}">{esc(description)}</small>' if show_examples else ''
        described_by=f' aria-describedby="detail-{key}"' if show_examples else ''
        choices.append(f'''<label class="room-choice">
            <input type="checkbox" name="piece" value="{key}" aria-labelledby="label-{key}"{described_by}>
            <span class="room-choice-copy"><span id="label-{key}">{esc(label)}</span>{detail}</span></label>''')
    return ''.join(choices)

def select_options(items):
    return ''.join(f'<option value="{esc(key)}">{esc(label)}</option>' for key,label in items)

def planner_choices(name,kind,options,examples):
    return ''.join(f'''<label class="planner-choice">
        <input type="{kind}" name="{name}" value="{key}" aria-labelledby="choice-{key}" aria-describedby="example-{key}">
        <span><strong id="choice-{key}">{esc(label)}</strong><small id="example-{key}">{esc(examples[key])}</small></span>
    </label>''' for key,label in options)

def commercial_planner():
    examples={
        'bureaux':'Postes de travail et tables de réunion.',
        'espaces-communs':'Salle de pause, cuisine ou sanitaires.',
        'sols-passages':'Entrées et corridors fréquentés.'
    }
    times=select_options(COMMERCIAL_TIMES)
    return f'''<section id="preparer-mes-locaux" class="container section service-planner service-planner-commercial" aria-labelledby="commercial-planner-title">
        <div class="planner-content"><h2 id="commercial-planner-title">À quel moment vos locaux sont-ils libres ?</h2>
          <form id="quote-planner" method="get" action="/contact/#demande" class="planner-form">
            <input type="hidden" name="service" value="commercial">
            <fieldset><legend>Espaces à entretenir <span>(facultatif)</span></legend>
              <div class="planner-choices">{planner_choices('espace','checkbox',COMMERCIAL_AREAS,examples)}</div>
            </fieldset>
            <div class="planner-field"><label for="planner-time">Créneau souhaité <span>(facultatif)</span></label>
              <select name="creneau" id="planner-time"><option value="">Choisir un créneau</option>{times}</select>
            </div>
            <button class="button button-primary" type="submit">Préparer ma demande pour mes locaux{arrow()}</button>
          </form>
        </div>
        <figure class="planner-photo">{photo('commercial-feature',sizes='(max-width: 760px) 100vw, 48vw')}
          <figcaption>L’entretien d’une table partagée dans une salle de pause.</figcaption>
        </figure>
    </section>'''

def occasional_planner():
    examples={
        'demenagement':'Préparer les pièces avant la remise des clés.',
        'apres-construction':'Enlever la poussière de travaux sur les surfaces d’un condo ou d’un local.',
        'decapage-plancher':'Préciser le revêtement et l’état du fini à retirer.',
        'remise-en-etat':'Reprendre les sols ou les surfaces de plusieurs pièces.',
        'surface-ciblee':'S’occuper d’un matériau ou d’un endroit précis.'
    }
    return f'''<section id="preciser-mon-projet" class="container section service-planner" aria-labelledby="occasional-planner-title">
        <div class="planner-content"><h2 id="occasional-planner-title">Quel nettoyage avez-vous en tête ?</h2>
          <form id="quote-planner" method="get" action="/contact/#demande" class="planner-form">
            <input type="hidden" name="service" value="occasional">
            <fieldset><legend>Votre situation <span>(facultatif)</span></legend>
              <div class="planner-choices">{planner_choices('motif','radio',OCCASIONAL_REASONS,examples)}</div>
            </fieldset>
            <div class="planner-field planner-date"><label for="planner-key-date">Quelle est la date de remise des clés ? <span>(facultatif)</span></label>
              <input id="planner-key-date" type="date" name="date_cles">
            </div>
            <button class="button button-primary" type="submit">Préparer ma demande de nettoyage{arrow()}</button>
          </form>
        </div>
        <figure class="planner-photo">{photo('occasional-feature',sizes='(max-width: 760px) 100vw, 48vw')}
          <figcaption>Pour un escalier, précisez le matériau des marches dans votre demande.</figcaption>
        </figure>
    </section>'''

pages={ '':layout('Entretien ménager résidentiel et commercial','Découvrez les services résidentiels, commerciaux et ponctuels de KetuviClean et demandez une soumission.',home) }
pages['services']=layout('Choisir son service d’entretien','Identifiez le service Ketuvi qui correspond à votre situation : entretien de la maison ou des locaux, déménagement ou nettoyage ciblé.',service_guide(),'services')
for s in SERVICES:
    key=s['key']
    hero_photo=s.get('hero_photo',key+'-hero')
    service_intro={
        'commercial':'Bureaux, espaces communs et lieux d’accueil. Précisons les passages et les horaires qui conviennent à votre activité.',
        'residential':'De la cuisine aux pièces de vie, dites-nous quelles surfaces entretenir et à quel rythme.',
        'occasional':'Un condo à dépoussiérer après les travaux, un plancher à décaper ou un logement à préparer avant la remise des clés. Quel est votre projet ?'
    }
    actions={
        'residential':('Choisir mes pièces','#choisir-les-pieces'),
        'commercial':('Préciser mes besoins','#preparer-mes-locaux'),
        'occasional':('Choisir mon type de nettoyage','#preciser-mon-projet')
    }
    action=actions[key]
    body=page_hero(s['headline'],service_intro[key],hero_photo,action,s['title'])
    if key=='residential':
        body+=f'''<section class="container section service-priorities room-planner" id="choisir-les-pieces" aria-labelledby="room-planner-title">
            <div class="section-intro"><h2 id="room-planner-title">{s['scope_title']}</h2></div>
            <div class="room-planner-layout">{residential_work_photo()}
                <form id="quote-planner" class="room-picker" method="get" action="/contact/#demande">
                    <input type="hidden" name="service" value="residential">
                    <fieldset aria-labelledby="room-planner-title" aria-describedby="room-picker-hint">
                        <p id="room-picker-hint">Choisissez les pièces à inclure dans votre demande. Ce choix est facultatif.</p>
                        <div class="room-list">{room_choices(show_examples=True)}</div>
                    </fieldset>
                    <div class="field room-frequency"><label for="planner-frequency">Fréquence souhaitée <span>(facultatif)</span></label>
                        <select id="planner-frequency" name="frequence"><option value="">Choisir une fréquence</option>{select_options(RESIDENTIAL_FREQUENCIES)}</select></div>
                    <button class="button button-primary" type="submit">Préparer ma soumission{arrow()}</button>
                </form></div></section>'''
    elif key=='commercial':
        body+=commercial_planner()
    else:
        body+=occasional_planner()
    body+=f'''<section class="section container faq-section"><h2>Vos questions.</h2>{faq(SERVICE_QUESTIONS[key])}</section>'''
    pages[s['path']]=layout(s['title'],s['description'],body,s['path'])

about=(
    page_hero('Le soin des lieux et des gens.','Le point de départ de notre travail, c’est de comprendre comment vous vivez dans votre maison ou comment votre équipe occupe ses bureaux.','about-hero',('Parlons de vos besoins','/contact/'),'À propos de Ketuvi')
    + f'''<section class="container photo-report"><div class="report-pictures">
        <figure>{photo('about-field',sizes='(max-width: 700px) 65vw, 40vw')}</figure>
        <figure>{photo('about-detail',sizes='(max-width: 700px) 35vw, 22vw')}</figure>
        </div><div class="report-copy"><h2>Quelles sont vos priorités ?</h2><p>Une pièce où l’on mange, une vitre que tout le monde pousse, une entrée très fréquentée. Chaque lieu a ses habitudes. Nous en discutons avec vous pour définir les priorités de l’entretien.</p></div></section>'''
)
pages['a-propos']=layout('À propos de Ketuvi','Découvrez une approche de l’entretien qui relie le soin des espaces, l’écoute et le respect des personnes.',about,'a-propos')

def field(name,label,type='text',required=False,autocomplete='',wide=False):
    limit={'name':100,'email':254,'phone':40,'location':160,'availability':160}.get(name,160)
    return f'<div class="field {"field-wide" if wide else ""}"><label for="{name}">{label}{" <span>(facultatif)</span>" if not required else ""}</label><input id="{name}" name="{name}" type="{type}" maxlength="{limit}" '+('minlength="2" ' if name=='name' else '')+('required ' if required else '')+(f'autocomplete="{autocomplete}" ' if autocomplete else '')+'></div>'

def quote_service_fields():
    areas=''.join(f'''<label class="room-choice"><input type="checkbox" name="espace" value="{esc(key)}" aria-labelledby="area-{esc(key)}">
        <span class="room-choice-copy" id="area-{esc(key)}">{esc(label)}</span></label>''' for key,label in COMMERCIAL_AREAS)
    return f'''<fieldset class="quote-rooms field-wide" data-quote-service="residential" data-quote-rooms data-summary="Pièces à entretenir" hidden disabled>
            <legend>Pièces à entretenir <span>(facultatif)</span></legend><div class="room-list">{room_choices()}</div></fieldset>
        <div class="field field-wide" data-quote-service="residential" data-summary="Fréquence souhaitée" hidden>
            <label for="frequence">Fréquence souhaitée <span>(facultatif)</span></label>
            <select id="frequence" name="frequence" disabled><option value="">Choisir une fréquence</option>{select_options(RESIDENTIAL_FREQUENCIES)}</select></div>
        <fieldset class="quote-rooms field-wide" data-quote-service="commercial" data-summary="Espaces à entretenir" hidden disabled>
            <legend>Espaces à entretenir <span>(facultatif)</span></legend><div class="room-list">{areas}</div></fieldset>
        <div class="field field-wide" data-quote-service="commercial" data-summary="Créneau souhaité" hidden>
            <label for="creneau">Créneau souhaité <span>(facultatif)</span></label>
            <select id="creneau" name="creneau" disabled><option value="">Choisir un créneau</option>{select_options(COMMERCIAL_TIMES)}</select></div>
        <div class="field field-wide" data-quote-service="occasional" data-summary="Motif du nettoyage" hidden>
            <label for="motif">Motif du nettoyage <span>(facultatif)</span></label>
            <select id="motif" name="motif" disabled><option value="">Choisir un motif</option>{select_options(OCCASIONAL_REASONS)}</select></div>
        <div class="field field-wide" data-quote-service="occasional" data-moving-date data-summary="Date de remise des clés" hidden>
            <label for="date_cles">Date de remise des clés <span>(facultatif)</span></label>
            <input type="date" name="date_cles" id="date_cles" disabled></div>'''

def form(kind='quote'):
    application=kind=='application'
    noun='candidature' if application else 'demande'
    if STATIC_EMAIL:
        action=f'mailto:{EMAIL}'
        intro='Vos réponses préparent un courriel. Vous pourrez le relire et l’envoyer depuis votre messagerie.'
        submit_label='Préparer mon courriel'
        heading='Votre courriel est prêt.'
        note=f'Ouvrez votre messagerie et envoyez le courriel à {EMAIL}. Vous pouvez aussi copier son contenu.'
    else:
        action='/api/requests'
        intro=f'Votre {noun} sera enregistrée sur le serveur de cet aperçu. Vous pourrez ensuite l’envoyer à Ketuvi par courriel.'
        submit_label=f'Enregistrer ma {noun}'
        heading=f'{noun.capitalize()} enregistrée.'
        note=f'Pour transmettre votre message à Ketuvi, ouvrez le courriel préparé et envoyez-le à {EMAIL}.'
    contact_fields=field('name','Nom complet',required=True,autocomplete='name')+field('email','Adresse courriel','email',True,'email')+field('phone','Téléphone','tel',False,'tel')+field('location','Ville',autocomplete='address-level2')
    if application:fields=contact_fields+field('availability','Disponibilités',wide=True)
    else:
        services=''.join(f'<option value="{s["key"]}">{s["title"]}</option>' for s in SERVICES)
        fields=f'''<div class="quote-selection field-wide">
            <div class="quote-selection-preview" data-selection-preview hidden>
                <p id="quote-selection-summary"><strong data-selection-service></strong><span data-selection-details></span></p>
                <button type="button" class="selection-action" data-edit-selection aria-expanded="false" aria-controls="quote-selection-fields" aria-describedby="quote-selection-summary">Modifier</button>
            </div>
            <div id="quote-selection-fields" class="quote-selection-fields">
                <div class="field"><label for="service">Quel service recherchez-vous ?</label>
                    <select id="service" name="service" required><option value="">Choisir un service</option>{services}<option value="general">Je souhaite en discuter</option></select></div>
                {quote_service_fields()}
                <button type="button" class="selection-action" data-apply-selection hidden>Appliquer mes choix</button>
            </div></div>'''
        fields+=contact_fields
    optional_note='' if application else ' <span data-note-optional hidden>(facultatif)</span>'
    fields+=f'<div class="field field-wide"><label for="message">{"Votre expérience et ce que vous recherchez" if application else "Votre espace et vos besoins"}{optional_note}</label><textarea id="message" name="message" rows="5" minlength="10" maxlength="4000" required aria-describedby="message-help"></textarea><span class="field-help" id="message-help">{"Présentez votre parcours et votre intérêt pour l’entretien professionnel." if application else "Précisez les surfaces, la fréquence ou le moment souhaité."}</span></div>'
    subject='Candidature%20spontan%C3%A9e' if application else 'Demande%20de%20soumission'
    consent_text=(
        'J’accepte que Ketuvi utilise mes renseignements pour examiner ma candidature et communiquer avec moi à son sujet.'
        if application else
        'J’accepte que Ketuvi utilise mes renseignements pour étudier ma demande de soumission et me répondre.'
    )
    show_recap=STATIC_EMAIL or not application
    recap='' if not show_recap else f'''<details class="confirmation-details" data-quote-recap>
        <summary><strong>{"Aperçu du courriel" if STATIC_EMAIL else "Ma demande"}</strong><span data-quote-brief></span></summary>
        <label for="quote-document">Récapitulatif complet</label>
        <textarea id="quote-document" data-quote-document readonly rows="8" spellcheck="false"></textarea>
        </details>'''
    copy_action='' if not show_recap else f'''<button class="text-button" type="button" data-copy-quote>{"Copier le courriel" if STATIC_EMAIL else "Copier ma demande et sa référence"}</button>
        <p class="confirmation-feedback" data-copy-status role="status"></p>'''
    provider_notice='' if STATIC_EMAIL else ' En mode d’envoi direct, Resend conserve le courriel aux États-Unis.'
    receipt='' if STATIC_EMAIL else '<p>Votre référence <strong data-receipt></strong></p>'
    return f'''<div class="form-shell">
        <p class="form-fallback">Pour transmettre votre {"candidature" if application else "demande de soumission"}, <a href="mailto:{EMAIL}?subject={subject}">écrivez à {EMAIL}</a>. Consultez notre <a href="/confidentialite/">politique de confidentialité</a> pour savoir comment Ketuvi traite votre message.</p>
        <form class="request-form" data-request-form data-kind="{kind}" data-delivery="{'mailto' if STATIC_EMAIL else 'server'}" method="post" action="{action}" hidden>
            <p class="form-intro">{intro}</p>
            <input type="hidden" name="kind" value="{kind}"><div class="form-grid">{fields}</div>
            <div class="form-trap" aria-hidden="true"><label for="website">Site web</label><input id="website" name="website" tabindex="-1" autocomplete="off"></div>
            <label class="consent"><input type="checkbox" name="consent" required><span>{consent_text}</span></label>
            <p class="field-help">Vous pouvez demander l’accès à vos renseignements, leur rectification ou le retrait de votre consentement.{provider_notice} <a href="/confidentialite/" target="_blank" rel="noopener">Politique de confidentialité <span class="new-window-note">(nouvel onglet)</span></a></p>
            <button class="button button-primary submit-button" type="submit" disabled>{submit_label}</button>
            <p class="form-status" role="status" aria-live="polite"></p>
        </form>
        <div class="form-success" hidden tabindex="-1"><span class="success-symbol">{icon('contact')}</span><h2>{heading}</h2>
            {receipt}<p class="delivery-note">{note}</p>
            {recap}<a class="button button-primary" data-email-copy href="mailto:{EMAIL}">Ouvrir le courriel à envoyer</a>
            {copy_action}<button class="text-button" type="button" data-new-request>Préparer un autre message</button>
        </div></div>'''

contact=f'''<section class="container contact-layout">
    <div class="contact-copy"><h1>Parlons de<br>vos espaces.</h1><p>Quelles pièces souhaitez-vous faire nettoyer, et à quel moment ?</p><a class="contact-email" href="mailto:{EMAIL}">{EMAIL}</a>
        <details class="quote-followup"><summary>Que se passe-t-il après ma demande ?</summary><p>Vos précisions servent à préparer la soumission. Vous pourrez discuter des travaux et du prix avant de convenir d’une date d’intervention.</p></details></div>
    <section class="contact-form-area" id="demande" tabindex="-1" aria-labelledby="quote-title"><h2 id="quote-title">Votre demande de soumission.</h2>{form()}</section>
    <figure class="contact-photo">{photo('contact-notebook-daylight')}</figure>
</section>'''
pages['contact']=layout('Contact et soumission','Présentez votre besoin d’entretien à KetuviClean ou écrivez à info@ketuvi.com.',contact,'contact')
careers=(
    page_hero('Travailler chez Ketuvi.','Vous aimez le travail soigné et le contact avec les gens ? Présentez-nous votre expérience en entretien et vos disponibilités.','careers-daylight-portrait',('Présenter ma candidature','#candidature'),'Carrières')
    + f'''<section class="container section application-layout">
        <div><h2>Faisons connaissance.</h2><p>Parlez-nous des lieux où vous avez travaillé et des tâches que vous aimez réaliser.</p><a class="text-link" href="mailto:{EMAIL}?subject=Candidature%20spontan%C3%A9e">{EMAIL}</a></div>
        <div id="candidature" tabindex="-1" aria-labelledby="application-title"><h2 id="application-title">Votre candidature spontanée.</h2>{form('application')}</div>
        <figure class="application-photo">{photo('careers-field')}</figure>
    </section>'''
)
pages['carrieres']=layout('Carrières','Présentez votre candidature spontanée à KetuviClean.',careers,'carrieres')
privacy=f'''<section class="container simple-hero">
    <h1>Politique de<br>confidentialité.</h1>
    <p>Comment Ketuvi utilise vos renseignements quand vous demandez une soumission ou présentez votre candidature.</p>
    <p>Dernière révision le <time datetime="2026-11-24">24 novembre 2026</time>.</p>
</section><section class="container prose section">
    <h2>Ce que vous nous confiez.</h2>
    <p>Nettoyage Ketuvi Inc. exploite le site KetuviClean. Son numéro d’entreprise du Québec (NEQ) est le <strong>1179475471</strong>. Vous pouvez le vérifier au <a href="https://www.quebec.ca/entreprises-et-travailleurs-autonomes/obtenir-renseignements-entreprise/recherche-registre-entreprises/acceder-registre-entreprises">Registre des entreprises du Québec</a>.</p>
    <p>Les deux formulaires demandent votre nom, votre adresse courriel et votre accord pour traiter votre demande. Votre téléphone et votre ville sont facultatifs.</p>
    <p><strong>Pour une soumission,</strong> Ketuvi utilise le service choisi et votre description des lieux pour étudier vos besoins et vous répondre. Selon le service, vous pouvez préciser les pièces à entretenir, le moment souhaité ou la date de remise des clés.</p>
    <p><strong>Pour une candidature,</strong> Ketuvi utilise votre présentation et vos coordonnées pour examiner votre candidature et vous contacter à son sujet. Vous pouvez aussi indiquer vos disponibilités.</p>
    <h2>Comment votre message nous parvient.</h2>
    <p>Le formulaire indique son mode de transmission avant votre validation.</p>
    <p><strong>Sur le site public, lorsque vous envoyez le courriel vous-même,</strong> votre navigateur prépare un brouillon à partir de vos réponses. Le site ne reçoit ni n’enregistre ces réponses sur son serveur. Ouvrez le brouillon dans votre messagerie, vérifiez son contenu et envoyez-le à {EMAIL}. Si vous préférez écrire directement à cette adresse, votre message passe également par votre messagerie.</p>
    <p><strong>Dans l’aperçu local,</strong> la demande est enregistrée sur l’ordinateur qui héberge l’aperçu. Pour la faire parvenir à Ketuvi, ouvrez le courriel préparé et envoyez-le avec votre messagerie.</p>
    <p><strong>Lorsque l’envoi direct est activé,</strong> le serveur transmet votre message à {EMAIL} par l’intermédiaire de Resend. Ce fournisseur conserve le contenu du courriel et les journaux de livraison aux États-Unis. Le serveur du site garde aussi une fiche privée de la demande et une référence de transmission.</p>
    <h2>Combien de temps les renseignements sont-ils conservés ?</h2>
    <p>Une fois le traitement de votre demande terminé, la loi prévoit la destruction des renseignements ou leur anonymisation en vue d’une utilisation légitime, sous réserve des délais de conservation prévus par la loi. Pour connaître la durée applicable à votre demande et savoir qui peut consulter votre dossier chez Ketuvi, écrivez à l’adresse ci-dessous.</p>
    <h2>Vos droits et vos recours.</h2>
    <p>Vous pouvez demander à consulter vos renseignements, à en recevoir une copie ou à faire corriger une information inexacte, incomplète ou équivoque. Vous pouvez aussi retirer votre consentement à leur utilisation ou à leur communication dans les limites prévues par la loi. Ce retrait peut empêcher Ketuvi de poursuivre le traitement de votre demande.</p>
    <p>Au Québec, la personne ayant la plus haute autorité dans une entreprise est responsable de la protection des renseignements personnels, sauf délégation écrite de cette fonction.</p>
    <p>Pour transmettre une demande ou une plainte à la personne responsable chez Ketuvi, écrivez à notre adresse générale <a href="mailto:{EMAIL}?subject=Confidentialit%C3%A9">{EMAIL}</a> avec l’objet « Confidentialité ». Décrivez votre demande et indiquez sa référence si vous l’avez. Une vérification de votre identité peut être nécessaire avant de vous communiquer des renseignements.</p>
    <p>La Commission d’accès à l’information du Québec explique <a href="https://www.cai.gouv.qc.ca/protection-renseignements-personnels/citoyens-protection-renseignements-personnels/acces-et-protection-renseignements-personnels">comment exercer vos droits et quels recours s’offrent à vous</a>.</p>
    <h2>Navigation sur le site.</h2>
    <p>Le site héberge ses images et ses polices. Il n’installe aucun témoin publicitaire ou de mesure d’audience.</p>
</section>'''
pages['confidentialite']=layout('Confidentialité','Découvrez comment Ketuvi traite les soumissions et les candidatures et comment exercer vos droits sur vos renseignements personnels.',privacy,'confidentialite')
for route,source in pages.items():
    directory=PUBLIC/route;directory.mkdir(parents=True,exist_ok=True)
    (directory/'index.html').write_text(source,encoding='utf-8')
(PUBLIC/'404.html').write_text(layout('Page introuvable','Cette page n’existe pas.',f'<section class="container simple-hero not-found"><h1>Cette page<br>n’existe pas.</h1><p>Retrouvez nos services ou revenez à l’accueil.</p>{button("Revenir à l’accueil","/")}</section>','404'),encoding='utf-8')
robots='User-agent: *\nDisallow: /api/\n'
sitemap=PUBLIC/'sitemap.xml'
if PUBLIC_ORIGIN:
    urls=''.join(f'  <url><loc>{esc(PUBLIC_ORIGIN)}/{route+"/" if route else ""}</loc></url>\n' for route in pages)
    sitemap.write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+urls+'</urlset>\n',encoding='utf-8')
    robots+='Sitemap: '+PUBLIC_ORIGIN+'/sitemap.xml\n'
else:
    sitemap.unlink(missing_ok=True)
(PUBLIC/'robots.txt').write_text(robots,encoding='utf-8')
if PORTABLE:
    publish_assets(ROOT, PUBLIC, pages)
else:
    (ROOT/'site/routes.json').write_text(json.dumps(['/'+r+'/' if r else '/' for r in pages],ensure_ascii=False,indent=2),encoding='utf-8')
    ignore_file=ROOT/'.vercelignore'
    if ignore_file.exists():
        marker='# Photos référencées par les pages (actualisées par npm run build)'
        ignore_source=ignore_file.read_text(encoding='utf-8')
        if marker not in ignore_source:
            raise ValueError('Section des photos absente de .vercelignore.')
        stems=sorted(set(re.findall(r'/assets/photos/([\w-]+)-\d+\.webp', ''.join(pages.values()))))
        allowlist=''.join(f'!site/public/assets/photos/{stem}-[0-9]*.webp\n' for stem in stems)
        ignore_file.write_text(ignore_source.split(marker,1)[0]+marker+'\n'+allowlist, encoding='utf-8')
    print(f'KetuviClean: {len(pages)} pages, {sum(map(len, photo_widths.values()))} images WebP, Helvetica Neue et 6 icônes. Destinataire: {EMAIL}.')
