function updateFileCountAndPreview(input) {
const count = input.files.length;
document.getElementById('file-count').innerText = count + " photo(s) selected";
const previewContainer = document.getElementById('preview-container');
previewContainer.innerHTML = "";

if (input.files) {
    for (let i = 0; i < input.files.length; i++) {
        const file = input.files[i];
        const reader = new FileReader();
        reader.onload = function(e) {
            const img = document.createElement("img");
            img.src = e.target.result;
            img.style.width = "100px";
            img.style.height = "100px";
            img.style.objectFit = "cover";
            img.style.borderRadius = "8px";
            img.style.border = "1px solid #1f2937";
            previewContainer.appendChild(img);
        }
        reader.readAsDataURL(file);
    }
}
}