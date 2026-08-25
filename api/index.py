from fastapi import FastAPI, HTTPException, Header, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Simple Watch API",
    description="A beginner-friendly REST API containing information about watches.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

watches = [
    {
        "id": 1,
        "brand": "Rolex",
        "model": "GMT-Master II",
        "nickname": "Pepsi",
        "reference_number": "126710BLRO",
        "case_material": "Oystersteel",
        "case_size": "40mm",
        "dial_color": "Black",
        "bezel_material": "Bidirectional Red & Blue Cerachrom Ceramic",
        "movement": "Automatic (Calibre 3285)",
        "power_reserve": "70 Hours",
        "water_resistance": "100m",
        "image": "images/pepsi.jpg",
        "description": "An iconic dual-time pilot watch featuring a bidirectional red and blue Cerachrom ceramic bezel. Powered by the automatic Calibre 3285 movement with a 70-hour power reserve, 40mm case diameter, and 100m water resistance."
    },
    {
        "id": 2,
        "brand": "Omega",
        "model": "Speedmaster Professional",
        "nickname": "Moonwatch",
        "reference_number": "310.30.42.50.01.001",
        "case_material": "Stainless Steel",
        "case_size": "42mm",
        "dial_color": "Black Step Dial",
        "bezel_material": "Anodized Aluminum with Tachymeter Scale",
        "movement": "Manual-Wind (Co-Axial Master Chronometer Calibre 3861)",
        "power_reserve": "50 Hours",
        "water_resistance": "50m",
        "image": "images/moonwatch.jpg",
        "description": "The legendary chronograph flight-qualified by NASA for all manned space missions. Powered by the manual-wind Co-Axial Master Chronometer Calibre 3861 with a 50-hour power reserve, 42mm case diameter, and 50m water resistance."
    },
    {
        "id": 3,
        "brand": "Audemars Piguet",
        "model": "Royal Oak Jumbo Extra-Thin",
        "nickname": "Jumbo",
        "reference_number": "16202ST.OO.1240ST.01",
        "case_material": "Stainless Steel",
        "case_size": "39mm",
        "dial_color": "Bleu Nuit Nuage 50 Petite Tapisserie",
        "bezel_material": "Stainless Steel with 8 Hexagonal Screws",
        "movement": "Automatic (Calibre 7121)",
        "power_reserve": "55 Hours",
        "water_resistance": "50m",
        "image": "images/jumbo.jpg",
        "description": "An iconic luxury sports watch featuring an integrated bracelet and signature Petite Tapisserie blue dial. Powered by the self-winding Calibre 7121 with a 55-hour power reserve, 39mm case diameter, 8.1mm thickness, and 50m water resistance."
    },
    {
        "id": 4,
        "brand": "Patek Philippe",
        "model": "Nautilus",
        "nickname": "Nautilus Blue",
        "reference_number": "5711/1A-010",
        "case_material": "Stainless Steel",
        "case_size": "40mm",
        "dial_color": "Horizontally Embossed Blue Sunburst",
        "bezel_material": "Stainless Steel Rounded Octagonal",
        "movement": "Automatic (Calibre 26-330 S C)",
        "power_reserve": "45 Hours",
        "water_resistance": "120m",
        "image": "images/nautilus.jpg",
        "description": "A prestigious luxury sports watch defined by its rounded octagonal bezel and horizontally embossed blue dial. Powered by the self-winding Calibre 26-330 S C with a 45-hour power reserve, 40mm case diameter, and 120m water resistance."
    },
    {
        "id": 5,
        "brand": "Richard Mille",
        "model": "RM 011",
        "nickname": "Felipe Massa",
        "reference_number": "RM 011 FM",
        "case_material": "Grade 5 Titanium",
        "case_size": "50.0mm x 40.0mm",
        "dial_color": "Skeletonized Transparent",
        "bezel_material": "Grade 5 Titanium",
        "movement": "Automatic Flyback Chronograph (Calibre RMAC1)",
        "power_reserve": "50 Hours",
        "water_resistance": "50m",
        "image": "images/rm011.jpg",
        "description": "An avant-garde motorsport timepiece featuring a flyback chronograph and annual calendar in a signature tonneau case. Powered by the automatic skeletonized Calibre RMAC1 with a 50-hour power reserve, 50mm x 40mm dimensions, and 50m water resistance."
    },
    {
        "id": 6,
        "brand": "Rolex",
        "model": "Submariner Date",
        "nickname": "Kermit",
        "reference_number": "126610LV",
        "case_material": "Oystersteel",
        "case_size": "41mm",
        "dial_color": "Black",
        "bezel_material": "Unidirectional Green Cerachrom Ceramic",
        "movement": "Automatic (Calibre 3235)",
        "power_reserve": "70 Hours",
        "water_resistance": "300m",
        "image": "images/kermit.jpg",
        "description": "A benchmark divers watch featuring a green unidirectional Cerachrom bezel and black dial. Powered by the automatic Calibre 3235 movement with a 70-hour power reserve, 41mm case diameter, and 300m water resistance."
    },
    {
        "id": 7,
        "brand": "Rolex",
        "model": "Cosmograph Daytona",
        "nickname": "Panda",
        "reference_number": "126500LN",
        "case_material": "Oystersteel",
        "case_size": "40mm",
        "dial_color": "White Lacquer with Black Sub-Dials",
        "bezel_material": "Black Cerachrom Ceramic with Tachymetric Scale",
        "movement": "Automatic Chronograph (Calibre 4131)",
        "power_reserve": "72 Hours",
        "water_resistance": "100m",
        "image": "images/panda.jpg",
        "description": "A celebrated racing chronograph with a white lacquer dial and black Cerachrom tachymetric bezel. Powered by the automatic Calibre 4131 movement with a 72-hour power reserve, 40mm case diameter, and 100m water resistance."
    },
    {
        "id": 8,
        "brand": "Omega",
        "model": "Seamaster Diver 300M",
        "nickname": "No Time to Die",
        "reference_number": "210.90.42.20.01.001",
        "case_material": "Grade 2 Titanium",
        "case_size": "42mm",
        "dial_color": "Tropical Matte Brown Aluminum",
        "bezel_material": "Tropical Brown Aluminum with Vintage Super-LumiNova",
        "movement": "Automatic (Co-Axial Master Chronometer Calibre 8806)",
        "power_reserve": "55 Hours",
        "water_resistance": "300m",
        "image": "images/nttd.jpg",
        "description": "The military-inspired 007 edition timepiece featuring a tropical brown aluminum dial and titanium mesh bracelet. Powered by the automatic Co-Axial Master Chronometer Calibre 8806 with a 55-hour power reserve, 42mm case diameter, and 300m water resistance."
    },
    {
        "id": 9,
        "brand": "Omega",
        "model": "Seamaster Aqua Terra 150M",
        "nickname": "Terracotta",
        "reference_number": "220.10.38.20.13.003",
        "case_material": "Stainless Steel",
        "case_size": "38mm",
        "dial_color": "Sun-Brushed Terracotta Brass",
        "bezel_material": "Smooth Stainless Steel",
        "movement": "Automatic (Co-Axial Master Chronometer Calibre 8800)",
        "power_reserve": "55 Hours",
        "water_resistance": "150m",
        "image": "images/terracotta.jpg",
        "description": "A versatile luxury sports watch featuring a sun-brushed terracotta-colored brass dial. Powered by the automatic Co-Axial Master Chronometer Calibre 8800 with a 55-hour power reserve, 38mm case diameter, and 150m water resistance."
    },
    {
        "id": 10,
        "brand": "Audemars Piguet",
        "model": "Royal Oak Offshore Chronograph",
        "nickname": "Offshore Ghost",
        "reference_number": "26470IO.OO.A006CA.01",
        "case_material": "Titanium",
        "case_size": "42mm",
        "dial_color": "Slate Grey Méga Tapisserie",
        "bezel_material": "Grey Ceramic",
        "movement": "Automatic Chronograph (Calibre 3126 / 3840)",
        "power_reserve": "50 Hours",
        "water_resistance": "100m",
        "image": "images/ghost.jpg",
        "description": "A robust, sporty chronograph featuring a ceramic bezel and slate grey Méga Tapisserie dial. Powered by the automatic Calibre 3126 / 3840 with a 50-hour power reserve, 42mm case diameter, and 100m water resistance."
    },
    {
        "id": 11,
        "brand": "Audemars Piguet",
        "model": "Royal Oak Double Balance Wheel",
        "nickname": "Skeleton Royal Oak",
        "reference_number": "15407ST.OO.1220ST.01",
        "case_material": "Stainless Steel",
        "case_size": "41mm",
        "dial_color": "Slate Grey Openworked Skeleton",
        "bezel_material": "Stainless Steel with 8 Hexagonal Screws",
        "movement": "Automatic (Calibre 3132)",
        "power_reserve": "45 Hours",
        "water_resistance": "50m",
        "image": "images/skeletonro.jpg",
        "description": "A high-complication horological piece featuring a patented dual balance wheel assembly visible through a skeletonized dial. Powered by the self-winding Calibre 3132 with a 45-hour power reserve, 41mm case diameter, and 50m water resistance."
    },
    {
        "id": 12,
        "brand": "Patek Philippe",
        "model": "Aquanaut",
        "nickname": "Jumbo Aquanaut",
        "reference_number": "5167A-001",
        "case_material": "Stainless Steel",
        "case_size": "40.8mm",
        "dial_color": "Black Embossed",
        "bezel_material": "Satin-Brushed Stainless Steel",
        "movement": "Automatic (Calibre 26-330 S C)",
        "power_reserve": "45 Hours",
        "water_resistance": "120m",
        "image": "images/aquanaut.jpg",
        "description": "A contemporary, dynamic sports timepiece featuring a black embossed dial and composite Tropical strap. Powered by the self-winding Calibre 26-330 S C with a 45-hour power reserve, 40.8mm case diameter, and 120m water resistance."
    },
    {
        "id": 13,
        "brand": "Patek Philippe",
        "model": "Grand Complications",
        "nickname": "Perpetual Calendar Chronograph",
        "reference_number": "5270P-001",
        "case_material": "Platinum",
        "case_size": "41mm",
        "dial_color": "Golden Opaline Salmon",
        "bezel_material": "Polished Platinum",
        "movement": "Manual-Wind Grand Complication (Calibre CH 29-535 PS Q)",
        "power_reserve": "65 Hours",
        "water_resistance": "30m",
        "image": "images/perpetual.jpg",
        "description": "An exquisite haute horlogerie grand complication featuring a perpetual calendar, moon phase, and salmon dial. Powered by the manual-wind Calibre CH 29-535 PS Q with a 65-hour power reserve, 41mm case diameter, and 30m water resistance."
    },
    {
        "id": 14,
        "brand": "Richard Mille",
        "model": "RM 035",
        "nickname": "Baby Nadal",
        "reference_number": "RM 035-02",
        "case_material": "Carbon TPT",
        "case_size": "49.9mm x 44.5mm",
        "dial_color": "Skeletonized Transparent",
        "bezel_material": "Carbon TPT",
        "movement": "Automatic (Calibre RMAL1)",
        "power_reserve": "55 Hours",
        "water_resistance": "50m",
        "image": "images/babynadal.jpg",
        "description": "An ultralight, high-shock sports watch developed alongside Rafael Nadal. Features a skeletonized movement and variable-geometry rotor, powered by the automatic Calibre RMAL1 with a 55-hour power reserve, 49.9mm x 44.5mm dimensions, and 50m water resistance."
    },
    {
        "id": 15,
        "brand": "Richard Mille",
        "model": "RM 055",
        "nickname": "Bubba Watson",
        "reference_number": "RM 055",
        "case_material": "Grade 5 Titanium with White Rubber Casing",
        "case_size": "49.9mm x 42.7mm",
        "dial_color": "Skeletonized Transparent",
        "bezel_material": "ATZ White Ceramic",
        "movement": "Manual-Wind (Calibre RMUL2)",
        "power_reserve": "55 Hours",
        "water_resistance": "30m",
        "image": "images/bubbawatson.jpg",
        "description": "A manual-wind skeletonized sports watch engineered to withstand extreme accelerations. Powered by the manual-wind Calibre RMUL2 with a 55-hour power reserve, 49.9mm x 42.7mm dimensions, and 30m water resistance."
    },
    {
        "id": 16,
        "brand": "Rolex",
        "model": "Day-Date 40",
        "nickname": "President",
        "reference_number": "228238",
        "case_material": "18k Yellow Gold",
        "case_size": "40mm",
        "dial_color": "Champagne",
        "bezel_material": "Fluted 18k Yellow Gold",
        "movement": "Automatic (Calibre 3255)",
        "power_reserve": "70 Hours",
        "water_resistance": "100m",
        "image": "images/president.jpg",
        "description": "The quintessential prestige watch featuring the iconic President bracelet and champagne dial with fluted bezel. Powered by the automatic Calibre 3255 with a 70-hour power reserve, 40mm case diameter, and 100m water resistance."
    },
    {
        "id": 17,
        "brand": "Omega",
        "model": "Planet Ocean 600M",
        "nickname": "Deep Black",
        "reference_number": "215.92.46.22.01.001",
        "case_material": "Black Ceramic",
        "case_size": "45.5mm",
        "dial_color": "Black Zirconium Dioxide Ceramic",
        "bezel_material": "Unidirectional Black Ceramic with Liquidmetal Scale",
        "movement": "Automatic GMT (Co-Axial Master Chronometer Calibre 8906)",
        "power_reserve": "60 Hours",
        "water_resistance": "600m",
        "image": "images/planetocean.jpg",
        "description": "A state-of-the-art diving watch combining GMT functionality with extreme depth rating in a solid black ceramic case. Powered by the automatic Co-Axial Master Chronometer Calibre 8906 with a 60-hour power reserve, 45.5mm case diameter, and 600m water resistance."
    },
    {
        "id": 18,
        "brand": "Audemars Piguet",
        "model": "Royal Oak Chronograph",
        "nickname": "ROC Panda",
        "reference_number": "26331ST.OO.1220ST.03",
        "case_material": "Stainless Steel",
        "case_size": "41mm",
        "dial_color": "Silver-Toned Grande Tapisserie with Black Counters",
        "bezel_material": "Stainless Steel with 8 Hexagonal Screws",
        "movement": "Automatic Integrated Chronograph (Calibre 2385)",
        "power_reserve": "40 Hours",
        "water_resistance": "50m",
        "image": "images/rocpanda.jpg",
        "description": "A sporty high-horology chronograph featuring a silver-toned Grande Tapisserie dial and contrasting black sub-dials. Powered by the self-winding Calibre 2385 with a 40-hour power reserve, 41mm case diameter, and 50m water resistance."
    },
    {
        "id": 19,
        "brand": "Patek Philippe",
        "model": "Calatrava",
        "nickname": "Clous de Paris",
        "reference_number": "6119R-001",
        "case_material": "18k Rose Gold",
        "case_size": "39mm",
        "dial_color": "Silvery Grained",
        "bezel_material": "Guilloched Clous de Paris 18k Rose Gold",
        "movement": "Manual-Wind (Calibre 30-255 PS)",
        "power_reserve": "65 Hours",
        "water_resistance": "30m",
        "image": "images/calatrava.jpg",
        "description": "The benchmark round dress watch featuring a refined guilloche hobnail bezel and silvery grained dial. Powered by the manual-wind Calibre 30-255 PS with a 65-hour power reserve, 39mm case diameter, and 30m water resistance."
    },
    {
        "id": 20,
        "brand": "Richard Mille",
        "model": "RM 67-02",
        "nickname": "Sprint",
        "reference_number": "RM 67-02",
        "case_material": "Carbon TPT and Quartz TPT",
        "case_size": "38.7mm x 47.5mm",
        "dial_color": "Skeletonized Transparent",
        "bezel_material": "Quartz TPT",
        "movement": "Automatic Extra-Flat (Calibre CRMA7)",
        "power_reserve": "50 Hours",
        "water_resistance": "30m",
        "image": "images/rm6702.jpg",
        "description": "An ultra-thin, featherweight athletic watch weighing just 32 grams including its seamless comfort strap. Powered by the automatic skeletonized Calibre CRMA7 with a 50-hour power reserve, 38.7mm x 47.5mm dimensions, and 50m water resistance."
    }
]

@app.get("/")
def home():
    return {
        "message": "Welcome to the Watch Gallery API!",
        "endpoints": [
            "/watches",
            "/watches/{id}",
            "/watches/search"
        ]
    }

@app.get("/watches")
def get_watches():
    return {
        "count": len(watches),
        "watches": watches
    }

@app.get("/watches/search")
def search_watches(q: str = Query("", min_length=0)):
    if not q.strip():
        return {
            "query": "",
            "count": len(watches),
            "results": watches
        }

    query = q.lower().strip()
    results = []
    for watch in watches:
        searchable_text = (
            f"{watch['brand']} "
            f"{watch['model']} "
            f"{watch['nickname']} "
            f"{watch['reference_number']} "
            f"{watch['case_material']} "
            f"{watch['case_size']} "
            f"{watch['dial_color']} "
            f"{watch['bezel_material']} "
            f"{watch['movement']} "
            f"{watch['power_reserve']} "
            f"{watch['water_resistance']}"
        ).lower()

        if query in searchable_text:
            results.append(watch)

    return {
        "query": q,
        "count": len(results),
        "results": results
    }

@app.get("/watches/{watch_id}")
def get_watch(watch_id: int):
    for watch in watches:
        if watch["id"] == watch_id:
            return watch

    raise HTTPException(
        status_code=404,
        detail="Watch not found."
    )
