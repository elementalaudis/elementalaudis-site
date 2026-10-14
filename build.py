#!/usr/bin/env python3
"""
Elementa Laudis site builder.

Reads site.json (English) and site.pl.json (Polish) and writes the whole
site. English pages go in the root, Polish pages go in the pl/ folder.

To add a work, put the photos in images/, add a block to BOTH json files,
then run:  python3 build.py

Requires only the Python standard library.
"""

import json, os, html, datetime, struct

HERE = os.path.dirname(os.path.abspath(__file__))
_DIMS = {}


def jpeg_size(path):
    """Width and height of a JPEG, read from its header. Standard library only."""
    if path in _DIMS:
        return _DIMS[path]
    try:
        with open(path, "rb") as f:
            if f.read(2) != b"\xff\xd8":
                return None
            while True:
                b = f.read(1)
                while b and b != b"\xff":
                    b = f.read(1)
                marker = f.read(1)
                while marker == b"\xff":
                    marker = f.read(1)
                if not marker:
                    return None
                m = marker[0]
                if m in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
                         0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                    f.read(3)
                    h, w = struct.unpack(">HH", f.read(4))
                    _DIMS[path] = (w, h)
                    return (w, h)
                (ln,) = struct.unpack(">H", f.read(2))
                f.read(ln - 2)
    except Exception:
        return None

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?'
         'family=Montserrat:wght@300;400;500&display=swap" rel="stylesheet">')

# ---------------------------------------------------------------- languages
UI = {
    "en": {
        "html_lang": "en",
        "nav": ["Work", "Available", "Marquetry", "About", "Exhibitions", "Contact"],
        "site_title": "{name}, {studio} | Contemporary marquetry in {city}",
        "work_eyebrow": "Selected work",
        "work_head": "Every piece is one of a kind",
        "work_intro": "I choose, cut, dye and lay every veneer by hand, so no panel can ever be repeated. Two pieces of wood never carry the same grain, and that is the whole appeal of working this way.",
        "avail_eyebrow": "Available works",
        "avail_head": "Acquire a piece",
        "avail_intro": "My prices are the same wherever you find the work, whether that is the studio, a fair or this page. Everything arrives with a signed certificate of authenticity. I arrange delivery within the UK myself, and I will quote for international shipping if you ask.",
        "avail_note": 'If you would rather talk first, or come and see a piece in the studio before you decide, please <a href="{contact}">write to me</a>. Visitors are welcome by appointment, and I am happy to split payment over two or three instalments at no extra cost.',
        "status_available": "Available, view details",
        "status_sold": "Sold",
        "btn_buy": "Acquire",
        "btn_enquire": "Enquire",
        "btn_details": "Details",
        "about_eyebrow": "About",
        "about_btn": "Studio visits and commissions",
        "ex_eyebrow": "Exhibitions and fairs",
        "ex_head": "Where to see the work",
        "contact_eyebrow": "Enquiries",
        "contact_head": "Get in touch",
        "contact_intro": "Whether it is about buying a piece, commissioning something, gallery representation, press or a visit to the studio, please write to me directly. I answer every message myself.",
        "f_name": "Your name", "f_email": "Email", "f_message": "Message",
        "f_send": "Send enquiry", "f_subscribe": "Subscribe",
        "nl_eyebrow": "Studio letter",
        "nl_head": "New work, first",
        "nl_intro": "A few times a year I send out new pieces before they go public, along with exhibition dates and the occasional note from the workbench. Nothing more often than that.",
        "nl_label": "Email address",
        "addr_line": "Visits by appointment.",
        "crumb": "Back to all work",
        "series_label": "{series} series",
        "series_works": "{n} works",
        "member_of": "Member of",
        "t_medium": "Medium", "t_dims": "Dimensions", "t_year": "Year",
        "t_edition": "Edition", "t_unique": "Unique work",
        "dims_note": "(h × w)",
        "piece_fine": "I deliver within the UK personally, and I will crate and ship internationally on quotation. The work arrives with a signed certificate of authenticity. If it helps, payment can be split over two or three instalments at no extra cost, so just ask.",
        "stmt_eyebrow": "About this work",
        "det_eyebrow": "Details", "det_head": "Closer",
        "det_note": "Click any image to see it larger.",
        "prev": "Previous", "next": "Next",
        "thanks_title": "Thank you",
        "thanks_body": "Thank you for writing. Your message has come through and I read everything myself, so I will get back to you within a day or two.",
        "thanks_back": "Back to the work",
        "other_lang": "Polish",
        "band_head": "New work, before it goes public",
        "band_intro": "A few times a year I send out new pieces before anyone else sees them, along with exhibition dates and the occasional note from the workbench. Nothing more often than that, and you can leave whenever you like.",
        "piece_terms": 'Full terms, including your right to change your mind within fourteen days, are on the <a href="terms.html">buying, delivery and returns</a> page.',
    },
    "pl": {
        "html_lang": "pl",
        "nav": ["Prace", "Dostępne", "Intarsja", "O mnie", "Wystawy", "Kontakt"],
        "site_title": "{name}, {studio} | Współczesna intarsja, {city}",
        "work_eyebrow": "Wybrane prace",
        "work_head": "Każde dzieło jest jedyne w swoim rodzaju",
        "work_intro": "Każdy fornir dobieram, wycinam i układam ręcznie. Żadnego z tych dzieł nie da się powtórzyć. Dwa kawałki drewna nigdy nie mają tego samego wzoru i w tym właśnie tkwi całe piękno.",
        "avail_eyebrow": "Prace na sprzedaż",
        "avail_head": "Jak kupić pracę",
        "avail_intro": "Ceny moich prac są wszędzie takie same, jeśli odwiedzisz mnie w pracowni, na targach, na tej stronie lub w galerii sztuki. Do każdej dołączam podpisany certyfikat autentyczności. Dostawę na terenie Wielkiej Brytanii załatwiam osobiście, a wysyłkę za granicę wyceniam na życzenie.",
        "avail_note": 'Jeśli chciałbyś/chciałabyś najpierw mnie poznać i porozmawiać albo po prostu zobaczyć pracę na żywo w pracowni, zanim się zdecydujesz, to <a href="{contact}">napisz do mnie</a>. Odwiedziny są możliwe po wcześniejszym umówieniu, a płatność chętnie rozłożę na dwie albo trzy części bez żadnej dopłaty.',
        "status_available": "Dostępna, zobacz szczegóły",
        "status_sold": "Sprzedana",
        "btn_buy": "Kup dzieło",
        "btn_enquire": "Zapytaj",
        "btn_details": "Szczegóły",
        "about_eyebrow": "O mnie",
        "about_btn": "Wizyty w pracowni i zamówienia autorskie",
        "ex_eyebrow": "Wystawy i targi",
        "ex_head": "Gdzie można zobaczyć prace",
        "contact_eyebrow": "Kontakt",
        "contact_head": "Napisz do mnie",
        "contact_intro": "Niezależnie od tego, czy chodzi o zakup pracy, o zamówienie autorskie, o współpracę z galerią, o prasę czy o wizytę w pracowni, napisz do mnie bezpośrednio. Każdą wiadomość czytam osobiście.",
        "f_name": "Imię i nazwisko", "f_email": "E-mail", "f_message": "Wiadomość",
        "f_send": "Wyślij wiadomość", "f_subscribe": "Zapisz się",
        "nl_eyebrow": "List z pracowni",
        "nl_head": "Nowe prace w pierwszej kolejności",
        "nl_intro": "Kilka razy w roku wysyłam nowe prace, zanim pokażę je publicznie, a przy okazji terminy wystaw i od czasu do czasu notatkę znad stołu warsztatowego. Częściej się nie odzywam.",
        "nl_label": "Adres e-mail",
        "addr_line": "Wizyty po wcześniejszym umówieniu.",
        "crumb": "Wróć do wszystkich prac",
        "series_label": "Cykl {series}",
        "series_works": "Liczba prac: {n}",
        "member_of": "Członek",
        "t_medium": "Technika", "t_dims": "Wymiary", "t_year": "Rok",
        "t_edition": "Egzemplarz", "t_unique": "Unikat",
        "dims_note": "(wys. × szer.)",
        "piece_fine": "Na terenie Wielkiej Brytanii dostarczam osobiście, a za granicę pakuję dzieło w skrzynię i wysyłam po wcześniejszej wycenie. Do każdej pracy dołączam podpisany certyfikat autentyczności. Płatność można rozłożyć na dwie albo trzy części bez żadnej dopłaty, wystarczy o to poprosić.",
        "stmt_eyebrow": "O tym dziele",
        "det_eyebrow": "Szczegóły", "det_head": "Z bliska",
        "det_note": "Kliknij dowolne zdjęcie, żeby zobaczyć je w powiększeniu.",
        "prev": "Poprzednia", "next": "Następna",
        "thanks_title": "Dziękuję",
        "thanks_body": "Dziękuję za wiadomość. Doszła do mnie, a czytam wszystko osobiście, więc odezwę się w ciągu dnia albo dwóch.",
        "thanks_back": "Wróć do prac",
        "other_lang": "English",
        "band_head": "Nowe prace, zanim trafią do publicznej wiadomości",
        "band_intro": "Kilka razy w roku wysyłam nowe prace, zanim zobaczy je ktokolwiek inny, a przy okazji terminy wystaw i od czasu do czasu notatkę znad stołu warsztatowego. Częściej się nie odzywam, a wypisać się możesz w każdej chwili.",
        "piece_terms": 'Pełne zasady, w tym prawo do zmiany zdania w ciągu czternastu dni, znajdziesz na stronie <a href="terms.html">zakup, dostawa i zwroty</a>.',
    },
}

LANGS = [
    {"code": "en", "file": "site.json",    "dir": "",   "asset": "",     "form_suffix": ""},
    {"code": "pl", "file": "site.pl.json", "dir": "pl", "asset": "../",  "form_suffix": "-pl"},
]


def money(n, code):
    s = "{:,}".format(int(n))
    return f"£{s}" if code == "en" else f"{s} £".replace(",", " ")


def dims(w, code):
    def fmt(v):
        s = "%g" % v
        return s.replace(".", ",") if code == "pl" else s
    return f"{fmt(w['height_cm'])} × {fmt(w['width_cm'])} cm"


LIGHTBOX = """
<div id="lb" role="dialog" aria-modal="true" aria-label="">
  <button class="close" aria-label="Close">×</button><img alt="">
</div>
<script>
(function(){
  var lb=document.getElementById('lb'), im=lb.querySelector('img');
  function open(s,a){im.src=s;im.alt=a||'';lb.classList.add('on');document.body.style.overflow='hidden';}
  function close(){lb.classList.remove('on');im.src='';document.body.style.overflow='';}
  document.querySelectorAll('img[data-full]').forEach(function(i){
    i.addEventListener('click',function(){open(i.dataset.full,i.alt);});});
  lb.addEventListener('click',close);
  document.addEventListener('keydown',function(e){if(e.key==='Escape')close();});
  function ph(i){if(!i.parentNode)return;var d=document.createElement('div');
    d.className='ph';d.textContent='Add '+i.getAttribute('src');i.replaceWith(d);}
  document.querySelectorAll('img[src*="images/"]').forEach(function(i){
    i.addEventListener('error',function(){ph(i);});
    if(i.complete&&i.naturalWidth===0)ph(i);});
})();
</script>
</body>
</html>"""


class Builder:
    def __init__(self, lang):
        self.L = lang
        self.code = lang["code"]
        self.u = UI[self.code]
        self.a = lang["asset"]
        d = json.load(open(os.path.join(HERE, lang["file"]), encoding="utf-8"))
        self.ART, self.ABOUT, self.EX, self.WORKS = d["artist"], d["about"], d["exhibitions"], d["artworks"]
        self.PAGES = d["pages"]
        self.SERIES = [s["name"] for s in d.get("series", [])] or \
            list(dict.fromkeys(w["series"] for w in self.WORKS))
        # keep works in series order so next/previous walks a series through
        self.WORKS = [w for s in self.SERIES for w in self.WORKS if w["series"] == s] + \
            [w for w in self.WORKS if w["series"] not in self.SERIES]
        self.outdir = os.path.join(HERE, lang["dir"]) if lang["dir"] else HERE
        os.makedirs(self.outdir, exist_ok=True)

    # -------- helpers
    def url(self, page):
        """A page url in this language, relative to the page being written."""
        return page

    def other(self, page):
        """The same page in the other language."""
        return ("pl/" + page) if self.code == "en" else ("../" + page)

    def canonical(self, page, code=None):
        base = self.ART["domain"]
        d = {"en": "", "pl": "pl"}[code] if code else self.L["dir"]
        page = "" if page == "index.html" else page
        return f"{base}/{d}/{page}" if d else f"{base}/{page}"

    def dims_full(self, w):
        extra = w.get("dims_extra")
        return dims(w, self.code) + (f", {extra}" if extra else "")

    def series_id(self, name):
        import re
        return "series-" + re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")

    def buy_btn(self, w, cls="btn"):
        """Stripe checkout if the work has a payment link, otherwise an enquiry."""
        if w.get("stripe"):
            return f'<a class="{cls}" href="{w['stripe']}">{self.u['btn_buy']}</a>'
        return f'<a class="{cls}" href="#contact">{self.u['btn_enquire']}</a>'

    def dim_attr(self, filename):
        d = jpeg_size(os.path.join(HERE, "images", filename))
        return f' width="{d[0]}" height="{d[1]}"' if d else ""

    def head(self, title, desc, page, image, preload=""):
        alt_en = self.canonical(page, "en")
        alt_pl = self.canonical(page, "pl")
        return f"""<!DOCTYPE html>
<html lang="{self.u['html_lang']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">
<meta name="author" content="{self.ART['name']}">
<link rel="canonical" href="{self.canonical(page)}">
<link rel="alternate" hreflang="en" href="{alt_en}">
<link rel="alternate" hreflang="pl" href="{alt_pl}">
<link rel="alternate" hreflang="x-default" href="{alt_en}">
<link rel="icon" href="{self.a}mark.svg" type="image/svg+xml">
<meta property="og:type" content="website">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{self.canonical(page)}">
<meta property="og:image" content="{self.ART['domain']}/images/{image}">
<meta property="og:locale" content="{'en_GB' if self.code=='en' else 'pl_PL'}">
<meta name="twitter:card" content="summary_large_image">
{FONTS}
<link rel="stylesheet" href="{self.a}style.css">
{preload}
</head>
<body>"""

    def header(self, page, home=False):
        p = "" if home else "index.html"
        n = self.u["nav"]
        return f"""
<header class="site">
  <div class="wrap bar">
    <a class="brand" href="index.html">
      <img src="{self.a}mark.svg" alt="">
      <span>
        <span class="mark">{self.ART['studio']}</span>
        <span class="sub">{self.ART['name']}</span>
      </span>
    </a>
    <nav class="site" aria-label="{n[0]}">
      <ul>
        <li><a href="{p}#work">{n[0]}</a></li>
        <li><a href="{p}#available">{n[1]}</a></li>
        <li><a href="marquetry.html">{n[2]}</a></li>
        <li><a href="{p}#about">{n[3]}</a></li>
        <li><a href="{p}#exhibitions">{n[4]}</a></li>
        <li><a href="{p}#contact">{n[5]}</a></li>
        <li><a class="lang" href="{self.other(page)}">{self.u['other_lang']}</a></li>
      </ul>
    </nav>
  </div>
</header>"""


    def band(self):
        u, fs = self.u, self.L["form_suffix"]
        thanks = "/pl/thanks.html" if self.code == "pl" else "/thanks.html"
        return f"""
<section class="band">
  <div class="wrap band-inner">
    <div>
      <p class="eyebrow">{u['nl_eyebrow']}</p>
      <h2>{u['band_head']}</h2>
      <p>{u['band_intro']}</p>
    </div>
    <form name="newsletter{fs}" method="POST" data-netlify="true" netlify-honeypot="bot-field" action="{thanks}">
      <input type="hidden" name="form-name" value="newsletter{fs}">
      <p class="hp"><label>Leave this empty: <input name="bot-field"></label></p>
      <label for="band-email">{u['nl_label']}</label>
      <input id="band-email" type="email" name="email" required>
      <button class="btn" type="submit">{u['f_subscribe']}</button>
    </form>
  </div>
</section>"""

    def footer(self):
        links = "".join(f'<li><a href="{u}" rel="me noopener" target="_blank">{n}</a></li>'
                        for n, u in self.ART["social"].items())
        P = self.PAGES
        return f"""
<footer class="site">
  <div class="wrap foot-grid">
    <div>© {datetime.date.today().year} {self.ART['name']}, {self.ART['studio']}
      <span class="foot-links">
        <a href="marquetry.html">{P['marquetry']['nav']}</a>
        <a href="faq.html">{P['faq']['nav']}</a>
        <a href="press.html">{P['press']['nav']}</a>
        <a href="terms.html">{P['terms']['nav']}</a>
      </span>
      {self.memberships_line()}
    </div>
    <ul class="social">{links}
      <li><a href="mailto:{self.ART['email']}">E-mail</a></li>
    </ul>
  </div>
</footer>"""

    def memberships_line(self):
        ms = self.ART.get("memberships", [])
        if not ms:
            return ""
        links = ", ".join(f'<a href="{m['url']}" rel="noopener" target="_blank">{html.escape(m['name'])}</a>' for m in ms)
        return f'<span class="foot-member">{self.u["member_of"]} {links}</span>'

    def write(self, name, content):
        with open(os.path.join(self.outdir, name), "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  {os.path.join(self.L['dir'], name)}")


    # ---------------------------------------------------------------- schema
    def person_id(self):
        return self.ART["domain"] + "/#person"

    def studio_id(self):
        return self.ART["domain"] + "/#studio"

    def graph(self):
        dom = self.ART["domain"]
        a = self.ART
        person = {
            "@type": "Person", "@id": self.person_id(),
            "name": a["name"], "url": dom + "/",
            "jobTitle": "Marquetry Artist",
            "description": a["lede"],
            "email": a["email"],
            "image": f"{dom}/images/{self.ABOUT['portrait']}",
            "birthPlace": {"@type": "Place", "name": "Warsaw, Poland"},
            "nationality": {"@type": "Country", "name": "Poland"},
            "homeLocation": {"@type": "Place", "name": a["city"]},
            "knowsAbout": ["Marquetry", "Wood veneer", "Contemporary craft",
                           "Wood dyeing", "Book matching"],
            "knowsLanguage": ["en", "pl"],
            "sameAs": [u for u in a["social"].values() if "YOURHANDLE" not in u],
            "worksFor": {"@id": self.studio_id()},
            "memberOf": [{"@type": "Organization", "name": m["name"], "url": m["url"]}
                         for m in a.get("memberships", [])],
        }
        studio = {
            "@type": ["ArtGallery", "LocalBusiness"], "@id": self.studio_id(),
            "name": a["studio"], "url": dom + "/",
            "description": a["lede"],
            "founder": {"@id": self.person_id()},
            "email": a["email"],
            "image": f"{dom}/images/{self.ART['hero_image']}",
            "address": {"@type": "PostalAddress",
                        "streetAddress": "Unit 16, Gordon Works Complex, Valley Rd",
                        "addressLocality": "Sheffield", "postalCode": "S8 9FT",
                        "addressCountry": "GB"},
            "areaServed": ["GB", "EU", "Worldwide"],
            "priceRange": "££",
            "openingHoursSpecification": {"@type": "OpeningHoursSpecification",
                                          "description": "By appointment"},
            "makesOffer": [{"@type": "Offer", "itemOffered": {"@type": "VisualArtwork",
                            "name": f"{w['series']}: {w['title']}"},
                            "price": str(w["price"]), "priceCurrency": "GBP",
                            "url": f"{dom}/{self.L['dir'] + '/' if self.L['dir'] else ''}work-{w['slug']}.html"}
                           for w in self.WORKS if w["status"] != "sold"],
        }
        website = {"@type": "WebSite", "@id": dom + "/#website", "url": dom + "/",
                   "name": f"{a['name']}, {a['studio']}",
                   "inLanguage": ["en", "pl"], "publisher": {"@id": self.person_id()}}
        items = {"@type": "ItemList", "@id": dom + "/#works",
                 "name": "Artworks", "numberOfItems": len(self.WORKS),
                 "itemListElement": [
                     {"@type": "ListItem", "position": i + 1,
                      "url": f"{dom}/{self.L['dir'] + '/' if self.L['dir'] else ''}work-{w['slug']}.html",
                      "name": f"{w['series']}: {w['title']}"}
                     for i, w in enumerate(self.WORKS)]}
        events = []
        for e in self.EX:
            if not e.get("start"):
                continue
            ev = {"@type": "ExhibitionEvent", "name": e["what"],
                  "startDate": e["start"], "endDate": e["end"],
                  "description": e["where"],
                  "eventAttendanceMode": ("https://schema.org/OnlineEventAttendanceMode"
                                          if e.get("online") else
                                          "https://schema.org/OfflineEventAttendanceMode"),
                  "eventStatus": "https://schema.org/EventScheduled",
                  "performer": {"@id": self.person_id()},
                  "organizer": {"@id": self.person_id()}}
            if e.get("venue"):
                ev["location"] = {"@type": "Place", "name": e["venue"],
                                  "address": {"@type": "PostalAddress",
                                              "streetAddress": e.get("street", ""),
                                              "addressLocality": e.get("locality", ""),
                                              "postalCode": e.get("postcode", ""),
                                              "addressCountry": "GB"}}
            else:
                ev["location"] = {"@type": "VirtualLocation", "url": dom + "/"}
            if e.get("url"):
                ev["url"] = e["url"]
            events.append(ev)
        return [person, studio, website, items] + events

    def crumbs(self, trail):
        dom = self.ART["domain"]
        base = f"{dom}/{self.L['dir'] + '/' if self.L['dir'] else ''}"
        return {"@context": "https://schema.org", "@type": "BreadcrumbList",
                "itemListElement": [{"@type": "ListItem", "position": i + 1,
                                     "name": n, "item": base + u}
                                    for i, (n, u) in enumerate(trail)]}

    # -------- pages
    def build_index(self):
        u, a = self.u, self.a
        grid = []
        for s in self.SERIES:
          ws = [w for w in self.WORKS if w["series"] == s]
          if not ws:
              continue
          grid.append(f"""
      <div class="series-group" id="{self.series_id(s)}">
        <div class="series-head">
          <h3>{html.escape(s)}</h3>
          <p class="series-count">{u['series_works'].format(n=len(ws))}</p>
        </div>
        <div class="works">""")
          for w in ws:
            sold = w["status"] == "sold"
            grid.append(f"""
        <figure class="work">
          <a href="work-{w['slug']}.html">
            <div class="frame"><img src="{a}images/{w['card']}" alt="{html.escape(w['series'])} {html.escape(w['title'])}"{self.dim_attr(w["card"])} loading="lazy"></div>
            <figcaption>
              <p class="work-title">{html.escape(w['series'])}: {html.escape(w['title'])}</p>
              <p class="work-meta">{html.escape(w['medium'])}<br>{self.dims_full(w)} · {w['year']}</p>
              <span class="work-status{' sold' if sold else ''}">{u['status_sold'] if sold else u['status_available']}</span>
            </figcaption>
          </a>
        </figure>""")
          grid.append("""
        </div>
      </div>""")

        cards = []
        for s in self.SERIES:
          ws = [w for w in self.WORKS if w["series"] == s and w["status"] != "sold"]
          if not ws:
              continue
          cards.append(f"""
      <div class="series-group">
        <div class="series-head"><h3>{html.escape(s)}</h3></div>
        <div class="available">""")
          for w in ws:
            cards.append(f"""
        <article class="card">
          <a href="work-{w['slug']}.html"><div class="frame"><img src="{a}images/{w['card']}" alt="{html.escape(w['title'])}"{self.dim_attr(w["card"])} loading="lazy"></div></a>
          <div class="card-body">
            <p class="work-title"><a href="work-{w['slug']}.html">{html.escape(w['series'])}: {html.escape(w['title'])}</a></p>
            <p class="work-meta">{html.escape(w['medium'])} · {self.dims_full(w)} · {w['year']}</p>
            <p class="price">{money(w['price'], self.code)}</p>
            <div class="btn-row">
              {self.buy_btn(w)}
              <a class="btn quiet" href="work-{w['slug']}.html">{u['btn_details']}</a>
            </div>
          </div>
        </article>""")
          cards.append("""
        </div>
      </div>""")

        exl = []
        # newest at the top, oldest at the bottom; undated entries go last
        for e in sorted(self.EX, key=lambda e: e.get("start") or e.get("sort", "0000"), reverse=True):
            cls = "" if e.get("upcoming") else ' class="past"'
            exl.append(f"""        <li{cls}>
          <span class="when">{html.escape(e['when'])}</span>
          <p class="what"><strong>{html.escape(e['what'])}</strong><span class="where">{html.escape(e['where'])}</span></p>
        </li>""")

        about_ps = "\n          ".join(f"<p>{p}</p>" for p in self.ABOUT["paragraphs"])
        if self.ABOUT.get("membership_line"):
            about_ps += f'\n          <p class="member-line">{html.escape(self.ABOUT["membership_line"])}</p>'
        anns = self.ART.get("announce") or []
        if isinstance(anns, dict):
            anns = [anns]
        today = datetime.date.today().isoformat()
        anns = [x for x in anns if today <= x["until"]]
        # every current notice is written out; a small script shows only the first one
        # that has not ended yet, so a finished event drops off without a rebuild
        announce = "".join(
            f'<p class="announce" data-until="{x["until"]}"{"" if k == 0 else " hidden"}>{html.escape(x["text"])} '
            f'<a href="{x["link"]}">{html.escape(x["link_text"])}</a></p>' for k, x in enumerate(anns))
        if announce:
            announce += ("<script>(function(){var d=new Date(),t=d.getFullYear()+'-'+('0'+(d.getMonth()+1)).slice(-2)+'-'+('0'+d.getDate()).slice(-2),"
                         "s=false;document.querySelectorAll('.announce').forEach(function(p){if(!s&&t<=p.dataset.until){p.hidden=false;s=true;}else{p.hidden=true;}});})();</script>")
        fs = self.L["form_suffix"]
        thanks = ("/pl/thanks.html" if self.code == "pl" else "/thanks.html")

        ld = {"@context": "https://schema.org", "@graph": self.graph()}

        title = u["site_title"].format(name=self.ART["name"], studio=self.ART["studio"], city=self.ART["city"])
        preload = f'<link rel="preload" as="image" href="{a}images/{self.ART["hero_image"]}" fetchpriority="high">'
        out = self.head(title, self.ART["lede"], "index.html", self.ART["hero_image"], preload)
        out += self.header("index.html", home=True)
        out += f"""
<main id="top">

  <section class="hero first">
    <div class="wrap">
      {announce}
      <h1>{self.ART['tagline']}</h1>
      <p class="lede" style="margin-top:2rem;">{self.ART['lede']}</p>
      <figure class="hero-figure">
        <a href="{self.ART['hero_link']}">
          <div class="frame"><img src="{a}images/{self.ART['hero_image']}" alt="{html.escape(self.ART['name'])}"{self.dim_attr(self.ART["hero_image"])} fetchpriority="high" loading="eager"></div>
        </a>
        <figcaption>{self.ART['hero_caption']}</figcaption>
      </figure>
    </div>
  </section>

  <section id="work">
    <div class="wrap">
      <div class="section-head">
        <p class="eyebrow">{u['work_eyebrow']}</p>
        <h2>{u['work_head']}</h2>
        <p style="margin-top:1.2rem;">{u['work_intro']}</p>
      </div>
      {''.join(grid)}
    </div>
  </section>

  <section id="available">
    <div class="wrap">
      <div class="section-head">
        <p class="eyebrow">{u['avail_eyebrow']}</p>
        <h2>{u['avail_head']}</h2>
        <p style="margin-top:1.2rem;">{u['avail_intro']}</p>
      </div>
      {''.join(cards)}
      <p class="note" style="margin-top:3rem;">{u['avail_note'].format(contact='#contact')}</p>
      <p class="note" style="margin-top:1rem;">{u['piece_terms']}</p>
    </div>
  </section>

  <section id="about">
    <div class="wrap">
      <div class="about-grid">
        <div>
          <p class="eyebrow">{u['about_eyebrow']}</p>
          <h2>{html.escape(self.ABOUT['heading'])}</h2>
          <div style="margin-top:1.5rem;">
          {about_ps}
          </div>
          <p style="margin-top:2rem;"><a class="btn quiet" href="#contact">{u['about_btn']}</a></p>
        </div>
        <div>
          <figure style="margin:0;">
            <div class="frame"><img src="{a}images/{self.ABOUT['portrait']}" alt="{html.escape(self.ART['name'])}"{self.dim_attr(self.ABOUT["portrait"])} loading="lazy"></div>
            <figcaption class="fine" style="margin-top:.9rem;">{html.escape(self.ABOUT['portrait_caption'])}</figcaption>
          </figure>
        </div>
      </div>
    </div>
  </section>

  <section id="exhibitions">
    <div class="wrap">
      <div class="section-head">
        <p class="eyebrow">{u['ex_eyebrow']}</p>
        <h2>{u['ex_head']}</h2>
      </div>
      <ul class="exlist">
{chr(10).join(exl)}
      </ul>
    </div>
  </section>

  <section id="contact">
    <div class="wrap">
      <div class="contact-grid">
        <div>
          <p class="eyebrow">{u['contact_eyebrow']}</p>
          <h2>{u['contact_head']}</h2>
          <p style="margin-top:1.3rem;">{u['contact_intro']}</p>
          <form name="enquiry{fs}" method="POST" data-netlify="true" netlify-honeypot="bot-field" action="{thanks}">
            <input type="hidden" name="form-name" value="enquiry{fs}">
            <p class="hp"><label>Leave this empty: <input name="bot-field"></label></p>
            <label for="name">{u['f_name']}</label>
            <input id="name" type="text" name="name" required>
            <label for="email">{u['f_email']}</label>
            <input id="email" type="email" name="email" required>
            <label for="message">{u['f_message']}</label>
            <textarea id="message" name="message" required></textarea>
            <button class="btn" type="submit">{u['f_send']}</button>
          </form>
        </div>
        <div>
          <p class="eyebrow">{u['nl_eyebrow']}</p>
          <h3 style="margin-bottom:1.2rem;">{u['nl_head']}</h3>
          <p>{u['nl_intro']}</p>
          <form name="newsletter{fs}" method="POST" data-netlify="true" netlify-honeypot="bot-field" action="{thanks}">
            <input type="hidden" name="form-name" value="newsletter{fs}">
            <p class="hp"><label>Leave this empty: <input name="bot-field"></label></p>
            <label for="nl-email">{u['nl_label']}</label>
            <input id="nl-email" type="email" name="email" required>
            <button class="btn quiet" type="submit">{u['f_subscribe']}</button>
          </form>
          <p class="note" style="margin-top:3rem;">
            {self.ART['studio']}<br>
            {html.escape(self.ART['address'])}<br>
            {u['addr_line']} <a href="mailto:{self.ART['email']}">{self.ART['email']}</a>
          </p>
        </div>
      </div>
    </div>
  </section>

</main>
{self.footer()}
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
{LIGHTBOX}"""
        self.write("index.html", out)

    def build_work(self, w, prev, nxt):
        u, a = self.u, self.a
        figs = []
        for d in w["details"]:
            cls = ' class="wide"' if d.get("wide") else ""
            figs.append(f"""
        <figure{cls}>
          <div class="frame"><img src="{a}images/{d['file']}" alt="{html.escape(d['caption'])}, {html.escape(w['title'])}"{self.dim_attr(d["file"])} loading="lazy" data-full="{a}images/{d['file']}"></div>
          <figcaption>{html.escape(d['caption'])}</figcaption>
        </figure>""")

        sold = w["status"] == "sold"
        buy = (f'<span class="btn quiet" style="cursor:default;">{u["status_sold"]}</span>'
               if sold else
               f'<a class="btn" href="{w["stripe"]}">{u["btn_buy"]}</a>' if w.get("stripe") else "")
        enq_cls = "btn quiet" if (sold or w.get("stripe")) else "btn"

        title = f"{w['series']}: {w['title']}"
        desc = f"{title}, {w['medium']}, {dims(w, self.code)}, {w['year']}."
        page = f"work-{w['slug']}.html"

        ld = {"@context": "https://schema.org", "@type": "VisualArtwork", "name": title,
              "creator": {"@type": "Person", "name": self.ART["name"], "url": self.ART["domain"] + "/"},
              "artform": "Marquetry", "artMedium": w["medium"], "dateCreated": str(w["year"]),
              "height": {"@type": "Distance", "name": f"{w['height_cm']} cm"},
              "width": {"@type": "Distance", "name": f"{w['width_cm']} cm"},
              "image": f"{self.ART['domain']}/images/{w['full']}",
              "url": self.canonical(page),
              "offers": {"@type": "Offer", "price": str(w["price"]), "priceCurrency": "GBP",
                         "availability": "https://schema.org/SoldOut" if sold else "https://schema.org/InStock"}}

        statement = "\n      ".join(
            (f'<p class="lede">{p}</p>' if i == 0 else f"<p>{p}</p>")
            for i, p in enumerate(w["statement"]))

        out = self.head(f"{title}, {self.ART['name']} | {self.ART['studio']}", desc, page, w["full"])
        out += self.header(page)
        out += f"""
<main>
  <div class="wrap crumb"><a href="index.html#work">{u['crumb']}</a></div>

  <div class="wrap piece">
    <div class="piece-grid">
      <div>
        <img class="piece-img" src="{a}images/{w['full']}" alt="{html.escape(title)}, {dims(w, self.code)}"{self.dim_attr(w["full"])} fetchpriority="high" data-full="{a}images/{w['full']}">
      </div>
      <div class="tomb">
        <p class="eyebrow">{u['series_label'].format(series=html.escape(w['series']))}</p>
        <h1>{html.escape(w['title'])}</h1>
        <dl>
          <dt>{u['t_medium']}</dt><dd>{html.escape(w['medium'])}</dd>
          <dt>{u['t_dims']}</dt><dd>{dims(w, self.code)} {u['dims_note']}{(", " + html.escape(w["dims_extra"])) if w.get("dims_extra") else ""}</dd>
          <dt>{u['t_year']}</dt><dd>{w['year']}</dd>
          <dt>{u['t_edition']}</dt><dd>{u['t_unique']}</dd>
        </dl>
        <p class="price">{money(w['price'], self.code)}</p>
        <div class="btn-row">
          {buy}
          <a class="{enq_cls}" href="index.html#contact">{u['btn_enquire']}</a>
        </div>
        <p class="fine" style="margin-top:1.6rem;">{u['piece_fine']}</p>
        <p class="fine" style="margin-top:.8rem;">{u['piece_terms']}</p>
      </div>
    </div>
  </div>

  <section>
    <div class="wrap narrow">
      <p class="eyebrow">{u['stmt_eyebrow']}</p>
      {statement}
    </div>
  </section>

  <section>
    <div class="wrap">
      <p class="eyebrow">{u['det_eyebrow']}</p>
      <h2 style="margin-bottom:2.5rem;">{u['det_head']}</h2>
      <div class="details">{''.join(figs)}
      </div>
      <p class="fine" style="margin-top:2.5rem;">{u['det_note']}</p>
    </div>
  </section>

  <div class="wrap nextprev">
    <a href="work-{prev['slug']}.html">{u['prev']}: {html.escape(prev['series'])} {html.escape(prev['title'])}</a>
    <a href="work-{nxt['slug']}.html">{u['next']}: {html.escape(nxt['series'])} {html.escape(nxt['title'])}</a>
  </div>
{self.band()}
</main>
{self.footer()}
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<script type="application/ld+json">{json.dumps(self.crumbs([(u['nav'][0], ''), (title, page)]), ensure_ascii=False)}</script>
{LIGHTBOX}"""
        self.write(page, out)


    def build_marquetry(self):
        u, P = self.u, self.PAGES["marquetry"]
        secs = "".join(f"""
      <section class="prose">
        <h2>{html.escape(x['h'])}</h2>
        {''.join(f'<p>{html.escape(t)}</p>' for t in x['p'])}
      </section>""" for x in P["sections"])

        ld = [self.crumbs([(self.u['nav'][0], ''), (P['nav'], 'marquetry.html')]),
              {"@context": "https://schema.org", "@type": "Article",
               "headline": P["title"], "description": P["description"],
               "inLanguage": self.u["html_lang"],
               "author": {"@id": self.person_id()},
               "publisher": {"@id": self.studio_id()},
               "mainEntityOfPage": self.canonical("marquetry.html"),
               "about": {"@type": "DefinedTerm", "name": "Marquetry",
                         "description": P["sections"][0]["p"][0],
                         "inDefinedTermSet": "https://en.wikipedia.org/wiki/Marquetry"},
               "image": f"{self.ART['domain']}/images/{self.ART['hero_image']}"}]

        out = self.head(P["title"], P["description"], "marquetry.html", self.ART["hero_image"])
        out += self.header("marquetry.html")
        out += f"""
<main>
  <div class="wrap crumb"><a href="index.html">{html.escape(self.ART['studio'])}</a></div>
  <article class="wrap narrow article">
    <h1>{html.escape(P['title'])}</h1>
    <p class="lede" style="margin-top:1.6rem;">{html.escape(P['intro'])}</p>
    {secs}
    <p style="margin-top:3rem;"><a class="btn quiet" href="index.html#work">{u['crumb']}</a></p>
  </article>
{self.band()}\n</main>
{self.footer()}
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
{LIGHTBOX}"""
        self.write("marquetry.html", out)

    def build_faq(self):
        u, P = self.u, self.PAGES["faq"]
        items = "".join(f"""
      <div class="qa">
        <h2>{html.escape(x['q'])}</h2>
        <p>{html.escape(x['a'])}</p>
      </div>""" for x in P["items"])

        ld = [self.crumbs([(self.u['nav'][0], ''), (P['nav'], 'faq.html')]),
              {"@context": "https://schema.org", "@type": "FAQPage",
               "inLanguage": self.u["html_lang"],
               "mainEntity": [{"@type": "Question", "name": x["q"],
                               "acceptedAnswer": {"@type": "Answer", "text": x["a"]}}
                              for x in P["items"]]}]

        out = self.head(P["title"], P["description"], "faq.html", self.ART["hero_image"])
        out += self.header("faq.html")
        out += f"""
<main>
  <div class="wrap crumb"><a href="index.html">{html.escape(self.ART['studio'])}</a></div>
  <article class="wrap narrow article">
    <h1>{html.escape(P['title'])}</h1>
    <p class="lede" style="margin-top:1.6rem;">{html.escape(P['intro'])}</p>
    <div class="faq">{items}
    </div>
    <p style="margin-top:3rem;"><a class="btn quiet" href="index.html#contact">{u['contact_head']}</a></p>
  </article>
{self.band()}\n</main>
{self.footer()}
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
{LIGHTBOX}"""
        self.write("faq.html", out)

    def build_press(self):
        u, P = self.u, self.PAGES["press"]
        facts = "".join(f"<li>{html.escape(f)}</li>" for f in P["facts"])
        ld = [self.crumbs([(self.u['nav'][0], ''), (P['nav'], 'press.html')]),
              {"@context": "https://schema.org", "@type": "AboutPage",
               "name": P["title"], "description": P["description"],
               "inLanguage": self.u["html_lang"], "mainEntity": {"@id": self.person_id()}}]

        out = self.head(P["title"], P["description"], "press.html", self.ART["hero_image"])
        out += self.header("press.html")
        out += f"""
<main>
  <div class="wrap crumb"><a href="index.html">{html.escape(self.ART['studio'])}</a></div>
  <article class="wrap narrow article">
    <h1>{html.escape(P['title'])}</h1>
    <p class="lede" style="margin-top:1.6rem;">{html.escape(P['intro'])}</p>

    <section class="prose">
      <h2>{html.escape(P['short_label'])}</h2>
      <blockquote>{html.escape(P['short'])}</blockquote>
    </section>

    <section class="prose">
      <h2>{html.escape(P['long_label'])}</h2>
      <blockquote>{html.escape(P['long'])}</blockquote>
    </section>

    <section class="prose">
      <h2>{html.escape(P['facts_label'])}</h2>
      <ul class="facts">{facts}</ul>
    </section>

    <section class="prose">
      <h2>{html.escape(P['images_label'])}</h2>
      <p>{html.escape(P['images'])}</p>
    </section>

    <section class="prose">
      <h2>{html.escape(P['contact_label'])}</h2>
      <p>{html.escape(self.ART['name'])}<br>
      {html.escape(self.ART['studio'])}<br>
      {html.escape(self.ART['address'])}<br>
      <a href="mailto:{self.ART['email']}">{self.ART['email']}</a></p>
    </section>
  </article>
{self.band()}
</main>
{self.footer()}
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
{LIGHTBOX}"""
        self.write("press.html", out)


    def build_terms(self):
        u, P = self.u, self.PAGES["terms"]
        secs = "".join(f"""
      <section class="prose">
        <h2>{html.escape(x['h'])}</h2>
        {''.join(f'<p>{html.escape(t)}</p>' for t in x['p'])}
      </section>""" for x in P["sections"])

        ld = [self.crumbs([(self.u['nav'][0], ''), (P['nav'], 'terms.html')]),
              {"@context": "https://schema.org", "@type": "WebPage",
               "name": P["title"], "description": P["description"],
               "inLanguage": self.u["html_lang"],
               "publisher": {"@id": self.studio_id()},
               "about": {"@id": self.person_id()}}]

        out = self.head(P["title"], P["description"], "terms.html", self.ART["hero_image"])
        out += self.header("terms.html")
        out += f"""
<main>
  <div class="wrap crumb"><a href="index.html">{html.escape(self.ART['studio'])}</a></div>
  <article class="wrap narrow article">
    <h1>{html.escape(P['title'])}</h1>
    <p class="lede" style="margin-top:1.6rem;">{html.escape(P['intro'])}</p>
    {secs}
  </article>
{self.band()}
</main>
{self.footer()}
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
{LIGHTBOX}"""
        self.write("terms.html", out)

    def build_thanks(self):
        u = self.u
        self.write("thanks.html", f"""<!DOCTYPE html>
<html lang="{u['html_lang']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{u['thanks_title']}, {self.ART['studio']}</title>
<meta name="robots" content="noindex">
{FONTS}
<link rel="stylesheet" href="{self.a}style.css">
<style>
  body{{min-height:100vh;display:flex;align-items:center;justify-content:center;text-align:center;padding:2rem;}}
  h1{{font-size:clamp(2rem,5vw,3rem);margin:0 0 1rem;}}
  p{{max-width:28rem;margin:0 auto 2rem;color:var(--ink-soft);}}
</style>
</head>
<body>
  <div>
    <h1>{u['thanks_title']}</h1>
    <p>{u['thanks_body']}</p>
    <a class="btn" href="index.html">{u['thanks_back']}</a>
  </div>
</body>
</html>""")

    def run(self):
        print(f"{self.code.upper()}:")
        self.build_index()
        n = len(self.WORKS)
        for i, w in enumerate(self.WORKS):
            self.build_work(w, self.WORKS[(i - 1) % n], self.WORKS[(i + 1) % n])
        self.build_marquetry()
        self.build_faq()
        self.build_press()
        self.build_terms()
        self.build_thanks()
        d = self.L["dir"] + "/" if self.L["dir"] else ""
        return [d + "index.html"] + [d + f"work-{w['slug']}.html" for w in self.WORKS] + \
               [d + "marquetry.html", d + "faq.html", d + "press.html", d + "terms.html"]


if __name__ == "__main__":
    print("Building elementalaudis.com")
    pages, domain, builders = [], None, {}
    for lang in LANGS:
        b = Builder(lang)
        builders[lang["code"]] = b
        domain = b.ART["domain"]
        pages += b.run()

    today = datetime.date.today().isoformat()

    def loc(p):
        p = p.replace("index.html", "")
        return f"{domain}/{p}"

    def alts(p):
        bare = p[3:] if p.startswith("pl/") else p
        return (f'<xhtml:link rel="alternate" hreflang="en" href="{loc(bare)}"/>'
                f'<xhtml:link rel="alternate" hreflang="pl" href="{loc("pl/" + bare)}"/>'
                f'<xhtml:link rel="alternate" hreflang="x-default" href="{loc(bare)}"/>')

    urls = "".join(
        f"<url><loc>{loc(p)}</loc><lastmod>{today}</lastmod>"
        f"<changefreq>monthly</changefreq>"
        f"<priority>{'1.0' if p in ('index.html',) else '0.8'}</priority>{alts(p)}</url>"
        for p in pages)
    open(os.path.join(HERE, "sitemap.xml"), "w", encoding="utf-8").write(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        'xmlns:xhtml="http://www.w3.org/1999/xhtml">' + urls + "</urlset>")
    print("  sitemap.xml")

    # robots.txt: everything welcome, including the AI search crawlers,
    # because being quoted in an AI answer is now a way of being found.
    bots = ["Googlebot", "Googlebot-Image", "Bingbot", "Google-Extended",
            "OAI-SearchBot", "ChatGPT-User", "GPTBot",
            "Claude-SearchBot", "Claude-User", "ClaudeBot",
            "PerplexityBot", "Perplexity-User",
            "Applebot", "Applebot-Extended", "Amazonbot",
            "meta-externalagent", "Bytespider", "CCBot", "cohere-ai", "Diffbot"]
    lines = ["User-agent: *", "Allow: /", ""]
    for bot in bots:
        lines += [f"User-agent: {bot}", "Allow: /", ""]
    lines += [f"Sitemap: {domain}/sitemap.xml", ""]
    open(os.path.join(HERE, "robots.txt"), "w", encoding="utf-8").write("\n".join(lines))
    print("  robots.txt")

    # llms.txt: a plain map of the site for AI assistants that read it
    b = builders["en"]
    A, PG = b.ART, b.PAGES
    works = "\n".join(
        f"- [{w['series']}: {w['title']}]({domain}/work-{w['slug']}.html): "
        f"{w['medium']}, {dims(w, 'en')}, {w['year']}, "
        f"{'sold' if w['status'] == 'sold' else money(w['price'], 'en')}"
        for w in b.WORKS)
    llms = f"""# {A['name']}, {A['studio']}

> {A['lede']}

Contemporary marquetry artist based in {A['city']}, United Kingdom. Works are unique
panels of hand cut wood veneer, dyed by the artist, at wall scale rather than the
furniture scale marquetry is normally made at. Work is sold directly from this site and through
exhibitions and fairs, and is held in private collections in five countries.
Works are grouped in three series: Innerysm, Now, and Now feat. Addiction.
Member of Joined Up Heritage Sheffield (JUHS). The site is published in English at {domain}/ and in Polish at {domain}/pl/.

## Artworks

{works}

## Background and explanation

- [What marquetry is and how these panels are made]({domain}/marquetry.html): definition of marquetry, the making process, the difference between marquetry, inlay and intarsia, and why so few people still make it by hand
- [Questions I get asked]({domain}/faq.html): prices, commissions, delivery, studio visits, caring for a veneer panel
- [Press and information]({domain}/press.html): short and long biography, key facts, image use, contact

## Contact

- Email: {A['email']}
- Studio: {A['address']}, visits by appointment
- Enquiries and commissions: {domain}/#contact
"""
    open(os.path.join(HERE, "llms.txt"), "w", encoding="utf-8").write(llms)
    print("  llms.txt")
    print(f"Done, {len(pages)} pages in two languages.")
