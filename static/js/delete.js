function confirmDelete(actionUrl, message) {
    const modal = document.getElementById("deleteModal");
    const form = document.getElementById("deleteForm");
    const msg = document.getElementById("deleteMessage");

    form.action = actionUrl;
    msg.innerText = message;

    modal.classList.add("open");
    document.getElementById("backdrop").classList.add("show");
}

function closeDeleteModal() {
    document.getElementById("deleteModal").classList.remove("open");
    document.getElementById("backdrop").classList.remove("show");
}