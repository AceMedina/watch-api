# Watch Gallery

A full-stack luxury timepiece showcase and watch catalog featuring a dynamic interactive search, brand filters, and technical specifications for iconic watches.

---

## Gallery Features & Highlights

Watch Gallery blends classic magazine editorial typography with modern web interactivity:

* **Dynamic Hero Carousel:** Cycles through featured flagship timepieces with smooth modulo navigation, depth-zoom scaling, and slide pagination folio counters (`01 / 05`).
* **Interactive Background & Parallax:** Mouse-tracking spotlight gradient that follows cursor coordinates with subtle parallax shift on desktop screens.
* **Curated Watch Catalog:** Responsive 4-column card grid rendering 30 luxury watches with high-resolution imagery and brand tags.
* **Specification Modal:** Click-to-inspect modal window breaking down reference numbers, case dimensions, calibres, power reserves, water resistance depth, origin, and real Philippine market pricing.
* **Editorial Aesthetic:** Designed with a deep pine green palette (`#1F493D`), warm accents, and classic serif styling inspired by luxury horology publications.

---

## How the Website Uses the API

Watch details, technical specifications, and market values are powered by a custom FastAPI backend (`https://watch-api-eight.vercel.app`):

1. **Catalog Ingestion:** On page load, the frontend fetches all 30 timepieces via `/api/v1/watches` (or `/watches`) to populate both the featured hero carousel and the main catalog grid.
2. **Instant Search:** Typing into the search bar dispatches queries to `/api/v1/watches/search?q={query}` to query against brand, model, nickname, and reference numbers.
3. **Brand Quick-Select:** Circular brand avatars (Rolex, Omega, Audemars Piguet, Patek Philippe, Richard Mille) trigger client-side filtering with active state toggling.
4. **Local Image Optimization:** References clean relative paths (`images/{name}.jpg`) paired with automated fallback placeholders to maintain visual stability.

---

## Supported Brands & Timepieces

The gallery curates 30 luxury references across 5 Swiss horology manufactures:

* **Rolex:** GMT-Master II ("Pepsi" & "Sprite"), Cosmograph Daytona ("Panda"), Submariner Date ("Kermit" & "Black"), Day-Date 40 ("President").
* **Omega:** Speedmaster Professional ("Moonwatch"), Seamaster Diver 300M ("No Time to Die" & "Blue Wave"), Aqua Terra 150M ("Terracotta"), Planet Ocean 600M ("Deep Black"), Constellation Globemaster.
* **Audemars Piguet:** Royal Oak Jumbo Extra-Thin ("Jumbo"), Double Balance Wheel Skeleton, Royal Oak Chronograph ("ROC Panda" & "ROC Blue Dial"), Royal Oak Offshore Chronograph ("Offshore Ghost"), Royal Oak Offshore Diver ("Offshore Diver Khaki").
* **Patek Philippe:** Nautilus ("Nautilus Blue" & "Nautilus Moonphase"), Aquanaut ("Jumbo Aquanaut" & "Aquanaut Orange Chrono"), Grand Complications Perpetual Calendar Chronograph, Calatrava ("Clous de Paris").
* **Richard Mille:** RM 011 ("Felipe Massa"), RM 035 ("Baby Nadal"), RM 055 ("Bubba Watson"), RM 67-02 ("Sprint"), RM 029 ("Big Date"), RM 30-01 ("Decoupleable Rotor").

---

## Files in This Project

watch-gallery/
├── images/        # High-resolution watch renders and brand emblems
├── index.html     # Semantic structure, navigation bar, hero, and modal markup
├── style.css      # Editorial pine green theme, typography, transitions, and responsive grid
├── app.js         # Fetch API client, depth-zoom carousel controller, and search/filter logic
├── api.py         # FastAPI backend with Pydantic validation, search endpoint, and API key protection
└── README.md      # Project overview and technical documentation