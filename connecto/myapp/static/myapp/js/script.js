// // TOGGLE MENU
// document.querySelectorAll('.menu-btn').forEach(btn => {
//     btn.addEventListener('click', (e) => {
//         e.stopPropagation();

//         // close all menus first
//         document.querySelectorAll('.menu-dropdown').forEach(m => m.classList.remove('show'));

//         let menu = btn.nextElementSibling;
//         menu.classList.toggle('show');
//     });
// });

// // CLOSE WHEN CLICK OUTSIDE
// document.addEventListener('click', () => {
//     document.querySelectorAll('.menu-dropdown').forEach(m => m.classList.remove('show'));
// });

// // DELETE POST
// document.querySelectorAll('.delete-btn').forEach(btn => {
//     btn.addEventListener('click', () => {
//         let post = btn.closest('.post-card');
//         post.remove();
//     });
// });

// // EDIT POST (basic)
// document.querySelectorAll('.edit-btn').forEach(btn => {
//     btn.addEventListener('click', () => {
//         alert("Edit feature coming soon 😄");
//     });
// });
const input = document.getElementById("imageInput");
const preview = document.getElementById("profilePreview");

input.addEventListener("change", function () {
    const file = this.files[0];
    if (file) {
        preview.src = URL.createObjectURL(file);
    }
});


const fileInput = document.getElementById("fileInput");
        const previewImage = document.getElementById("previewImage");
        const uploadBox = document.getElementById("uploadBox");

        fileInput.addEventListener("change", function () {
            const file = this.files[0];

            if (file) {
                const reader = new FileReader();

                reader.onload = function (e) {
                    previewImage.src = e.target.result;
                    previewImage.classList.remove("hidden");
                    uploadBox.style.display = "none";
                };

                reader.readAsDataURL(file);
            }
        });

        
