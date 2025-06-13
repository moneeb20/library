
// فتح وإغلاق النوافذ المنبثقة
function openPopup(popupId) {
    document.getElementById(popupId).style.display = "block";
}

function closePopup(popupId) {
    document.getElementById(popupId).style.display = "none";
}

// إغلاق النافذة عند النقر خارجها
window.onclick = function(event) {
    if (event.target.className === "popup-form") {
        event.target.style.display = "none";
    }
}

// عرض قائمة الكتب
function showBooks() {
    fetch('/get-books')
        .then(response => response.json())
        .then(data => {
            const table = document.getElementById("booksTable");
            table.innerHTML = `
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>العنوان</th>
                        <th>المؤلف</th>
                        <th>السعر</th>
                        <th>النوع</th>
                    </tr>
                </thead>
                <tbody>
                    ${data.map(book => `
                        <tr>
                            <td>${book.book_id}</td>
                            <td>${book.title}</td>
                            <td>${book.author}</td>
                            <td>${book.price}</td>
                            <td>${book.book_type}</td>
                        </tr>
                    `).join('')}
                </tbody>
            `;
            openPopup('booksPopup');
        });
}


function showAddBookForm() {
    fetch('/get-categories')
        .then(response => response.json())
        .then(categories => {
            const formContent = document.getElementById("addBookFormContent");
            formContent.innerHTML = `
                <div class="form-group">
                    <label for="title">عنوان الكتاب:</label>
                    <input type="text" name="title" required>
                </div>
                <div class="form-group">
                    <label for="author">المؤلف:</label>
                    <input type="text" name="author" required>
                </div>
                <div class="form-group">
                    <label for="category_id">التصنيف:</label>
                    <select name="category_id" required>
                        ${categories.map(cat => 
                            <option value="${cat.category_id}">${cat.name}</option>
                        ).join('')}
                    </select>
                </div>
                <!-- باقي حقول النموذج -->
            `;
            openPopup('addBookPopup');
        });
}

