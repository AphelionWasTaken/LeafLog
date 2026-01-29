function toggleNotes(btn) {
    const notesText = btn.previousElementSibling;
    if (notesText.classList.contains("collapsed")) {
        notesText.classList.remove("collapsed");
        btn.innerText = "Show less";
    } else {
        notesText.classList.add("collapsed");
        btn.innerText = "Show more";
    }
}

function NoteTruncation() {
    document.querySelectorAll(".notes-text").forEach(note => {
        const lineHeight = parseFloat(getComputedStyle(note).lineHeight);
        const maxLines = 6;
        const maxHeight = lineHeight * maxLines;

        if (note.scrollHeight > maxHeight + 5) {
            note.classList.add("collapsed");
            note.nextElementSibling.style.display = "inline";
        }
    });
}

window.addEventListener("load", NoteTruncation);