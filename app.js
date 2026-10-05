const API_URL = "https://watch-api-eight.vercel.app";

// Include API Key header if using the protected /api/v1/ routes
const API_KEY = "watch-api-001";
const requestHeaders = {
    "x-api-key": API_KEY
};

let allWatches = [];
let featuredWatches = [];
let currentHeroIndex = 0;
let selectedBrand = "";
let isHeroAnimating = false;

// FETCH WATCHES
async function loadWatches() {
    try {
        // Tries standard endpoint first, falls back to /api/v1/watches
        let response = await fetch(`${API_URL}/watches`);
        if (!response.ok) {
            response = await fetch(`${API_URL}/api/v1/watches`, { headers: requestHeaders });
        }

        const data = await response.json();
        allWatches = data.watches;
        
        // Hero takes the first 5 watches
        featuredWatches = allWatches.slice(0, 5);
        
        // Displays all 30 watches into the catalog grid
        displayWatches(allWatches);
        if (featuredWatches.length > 0) {
            updateHero(0);
        }
    } catch (error) {
        console.error(error);
        document.getElementById("watchGrid").innerHTML = "<p style='grid-column: 1/-1; text-align:center; color:#3D3D3D;'>Unable to connect to the Horology API.</p>";
    }
}

// RENDER GRID (ALL 30 WATCHES)
function displayWatches(watches) {
    const grid = document.getElementById("watchGrid");
    grid.innerHTML = "";

    if (!watches || watches.length === 0) {
        grid.innerHTML = "<p style='grid-column: 1/-1; text-align:center; color:#3D3D3D; padding: 40px 0;'>No timepieces found matching your selection.</p>";
        return;
    }

    watches.forEach(watch => {
        const card = document.createElement("div");
        card.className = "watch-card";
        card.onclick = () => openModal(watch);

        card.innerHTML = `
            <div class="card-top">
                <img src="${watch.image}" alt="${watch.model}" onerror="this.src='https://placehold.co/300x300/336659/FDFDFD?text=${encodeURIComponent(watch.brand)}'">
            </div>
            <div class="card-bottom">
                <p class="card-brand">${watch.brand}</p>
                <h4 class="card-title">${watch.model} "${watch.nickname}"</h4>
            </div>
        `;

        grid.appendChild(card);
    });
}

// HERO UPDATE
function updateHero(index) {
    if (!featuredWatches || featuredWatches.length === 0) return;
    currentHeroIndex = index;
    const watch = featuredWatches[currentHeroIndex];

    document.getElementById("heroBrand").innerText = watch.brand.toUpperCase();
    document.getElementById("heroTitle").innerText = `${watch.model} "${watch.nickname}"`;
    document.getElementById("heroDesc").innerText = watch.description;
    document.getElementById("heroRef").innerText = `Ref. ${watch.reference_number}`;
    document.getElementById("heroMaterial").innerText = watch.case_material;

    const heroImg = document.getElementById("heroImage");
    heroImg.src = watch.image;
    heroImg.onerror = () => {
        heroImg.src = `https://placehold.co/500x500/1F493D/F3EFE8?text=${encodeURIComponent(watch.model)}`;
    };

    // Numbering Folio
    const heroPagination = document.getElementById("heroPagination");
    if (heroPagination) {
        const currentNum = String(currentHeroIndex + 1).padStart(2, '0');
        const totalNum = String(featuredWatches.length).padStart(2, '0');
        heroPagination.innerText = `N° ${currentNum} / ${totalNum}`;
    }
}

// DEPTH ZOOM TRANSITION
function transitionHero(nextIndex, direction = "next") {
    if (isHeroAnimating || !featuredWatches || featuredWatches.length === 0) return;
    isHeroAnimating = true;

    const heroImg = document.getElementById("heroImage");
    const heroContent = document.querySelector(".hero-content");

    const exitClass = direction === "next" ? "zoom-exit-left" : "zoom-exit-right";
    heroImg.classList.add(exitClass);
    heroContent.classList.add("text-exit");

    setTimeout(() => {
        updateHero(nextIndex);

        heroImg.classList.remove(exitClass);
        heroContent.classList.remove("text-exit");

        const enterClass = direction === "next" ? "zoom-enter-right" : "zoom-enter-left";
        heroImg.classList.add(enterClass);
        heroContent.classList.add("text-enter");

        void heroImg.offsetWidth;
        void heroContent.offsetWidth;

        heroImg.classList.remove(enterClass);
        heroContent.classList.remove("text-enter");

        setTimeout(() => {
            isHeroAnimating = false;
        }, 500);
    }, 280);
}

// HERO NAVIGATION
function prevHeroWatch() {
    if (featuredWatches.length === 0) return;
    const prevIndex = (currentHeroIndex - 1 + featuredWatches.length) % featuredWatches.length;
    transitionHero(prevIndex, "prev");
}

function nextHeroWatch() {
    if (featuredWatches.length === 0) return;
    const nextIndex = (currentHeroIndex + 1) % featuredWatches.length;
    transitionHero(nextIndex, "next");
}

// SEARCH
async function searchWatches() {
    const query = document.getElementById("searchInput").value.trim();
    
    document.querySelectorAll(".brand-circle").forEach(btn => btn.classList.remove("active"));
    selectedBrand = "";

    if (!query) {
        displayWatches(allWatches);
        return;
    }

    try {
        let response = await fetch(`${API_URL}/watches/search?q=${encodeURIComponent(query)}`);
        if (!response.ok) {
            response = await fetch(`${API_URL}/api/v1/watches/search?q=${encodeURIComponent(query)}`, { headers: requestHeaders });
        }
        const data = await response.json();
        displayWatches(data.results);
    } catch (error) {
        // Fallback local client search across all 30 watches
        const filtered = allWatches.filter(w => 
            w.brand.toLowerCase().includes(query.toLowerCase()) ||
            w.model.toLowerCase().includes(query.toLowerCase()) ||
            w.nickname.toLowerCase().includes(query.toLowerCase()) ||
            w.reference_number.toLowerCase().includes(query.toLowerCase()) ||
            (w.category && w.category.toLowerCase().includes(query.toLowerCase()))
        );
        displayWatches(filtered);
    }
}

// BRAND FILTER (Filters across all 30 watches)
function toggleBrandFilter(brandName, element) {
    const isAlreadySelected = element.classList.contains("active");

    document.querySelectorAll(".brand-circle").forEach(btn => btn.classList.remove("active"));
    document.getElementById("searchInput").value = "";

    if (isAlreadySelected) {
        selectedBrand = "";
        displayWatches(allWatches);
    } else {
        selectedBrand = brandName;
        element.classList.add("active");
        const filtered = allWatches.filter(w => w.brand.toLowerCase() === brandName.toLowerCase());
        displayWatches(filtered);
    }
}

// MODAL (Populates full technical details for 30 watches)
function openModal(watch) {
    document.getElementById("modalBrand").innerText = watch.brand;
    document.getElementById("modalTitle").innerText = watch.model;
    document.getElementById("modalNickname").innerText = `"${watch.nickname}"`;
    document.getElementById("modalRef").innerText = watch.reference_number;
    document.getElementById("modalMaterial").innerText = watch.case_material;
    document.getElementById("modalDescription").innerText = watch.description;

    // Additional fields from expanded 30-watch dataset
    const sizeVal = watch.case_size_mm ? `${watch.case_size_mm} mm` : (watch.case_size || "N/A");
    document.getElementById("modalSize").innerText = sizeVal;
    document.getElementById("modalDial").innerText = watch.dial_color || "N/A";
    document.getElementById("modalMovement").innerText = watch.movement || "N/A";

    const powerVal = watch.power_reserve_hours ? `${watch.power_reserve_hours} Hours` : (watch.power_reserve || "N/A");
    document.getElementById("modalPower").innerText = powerVal;

    const wrVal = watch.water_resistance_m ? `${watch.water_resistance_m} m` : (watch.water_resistance || "N/A");
    document.getElementById("modalWR").innerText = wrVal;

    const catYear = `${watch.category || "Luxury"} (${watch.year || "Classic"})`;
    document.getElementById("modalCatYear").innerText = catYear;

    const priceFormatted = watch.price_php ? `₱${watch.price_php.toLocaleString()}` : "Price upon request";
    document.getElementById("modalPrice").innerText = priceFormatted;

    const modalImg = document.getElementById("modalImage");
    modalImg.src = watch.image;
    modalImg.onerror = () => {
        modalImg.src = `https://placehold.co/400x400/336659/FDFDFD?text=${encodeURIComponent(watch.model)}`;
    };

    document.getElementById("detailModal").classList.add("open");
}

function closeModal() {
    document.getElementById("detailModal").classList.remove("open");
}

function handleBackdropClick(event) {
    if (event.target.id === "detailModal") {
        closeModal();
    }
}

// PARALLAX & SPOTLIGHT
const heroSection = document.getElementById("hero");
if (heroSection) {
    heroSection.addEventListener("mousemove", (e) => {
        if (isHeroAnimating) return;

        const rect = heroSection.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;

        heroSection.style.setProperty("--mouse-x", `${mouseX}px`);
        heroSection.style.setProperty("--mouse-y", `${mouseY}px`);

        const percentX = (mouseX / rect.width) - 0.5;
        const percentY = (mouseY / rect.height) - 0.5;

        const heroImg = document.getElementById("heroImage");
        if (heroImg) {
            const shiftX = percentX * -24;
            const shiftY = percentY * -24;
            heroImg.style.transform = `translate(${shiftX}px, ${shiftY}px)`;
        }
    });

    heroSection.addEventListener("mouseleave", () => {
        const heroImg = document.getElementById("heroImage");
        if (heroImg && !isHeroAnimating) {
            heroImg.style.transform = "translate(0px, 0px)";
        }
    });
}

// EVENTS
document.getElementById("searchInput").addEventListener("keypress", (e) => {
    if (e.key === "Enter") searchWatches();
});

loadWatches();