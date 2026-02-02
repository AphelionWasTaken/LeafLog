function confirmAction(url, message, buttonText = "Delete", buttonColor = "#c52222", buttonGlow = "rgba(197, 34, 34, 0.2)") {
    const modal = document.getElementById("deleteModal");
    const form = document.getElementById("deleteForm");
    const msg = document.getElementById("deleteMessage");
    const btn = document.getElementById("confirmBtn");

    form.action = url;
    msg.textContent = message;
    btn.textContent = buttonText;
    btn.style.background = buttonColor;
    btn.style.boxShadow = `0 10px 20px ${buttonGlow}`;

    modal.classList.add("open");
    document.getElementById("backdrop").classList.add("show");
}

function closeDeleteModal() {
    document.getElementById("deleteModal").classList.remove("open");
    document.getElementById("backdrop").classList.remove("show");
}