let images = [];
let currentIndex = 0;

function rebuildImages() {
    images = Array.from(document.querySelectorAll(".thumb")).map(img => img.src);
}

function openModalFromThumb(img) {
    rebuildImages();
    currentIndex = images.indexOf(img.src);
    if (currentIndex == -1) return;
    document.getElementById("modalImage").src = images[currentIndex];
    document.getElementById("imageModal").classList.add("open");
    document.body.style.overflow = "hidden";
}

function closeModal() {
    document.getElementById("imageModal").classList.remove("open");
    document.body.style.overflow = "";
}

function nextImage() {
    currentIndex = (currentIndex + 1) % images.length;
    document.getElementById("modalImage").src = images[currentIndex];
}

function prevImage() {
    currentIndex = (currentIndex - 1 + images.length) % images.length;
    document.getElementById("modalImage").src = images[currentIndex];
}

document.addEventListener("keydown", function(e) {
    const modal = document.getElementById("imageModal");
    if (!modal.classList.contains("open")) return;
    if (e.key == "ArrowRight") nextImage();
    if (e.key == "ArrowLeft") prevImage();
    if (e.key == "Escape") closeModal();
});