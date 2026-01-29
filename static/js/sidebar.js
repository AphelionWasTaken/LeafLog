const sidebar = document.getElementById("sidebar");
const backdrop = document.getElementById("backdrop");
const menuButton = document.getElementById("menuButton");

menuButton.addEventListener("click", () => {
    sidebar.classList.add("open");
    backdrop.classList.add("show");
});

function closeSidebar() {
    sidebar.classList.remove("open");
    backdrop.classList.remove("show");
}