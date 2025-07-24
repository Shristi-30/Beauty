document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide flash messages after 5 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Category filter on the homepage
    const categoryFilter = document.getElementById('categoryFilter');
    if (categoryFilter) {
        categoryFilter.addEventListener('change', function() {
            const selectedCategory = this.value;
            const productCards = document.querySelectorAll('.product-card');
            
            // If "All Categories" is selected, show all products
            if (selectedCategory === 'All Categories') {
                productCards.forEach(card => {
                    card.parentElement.style.display = 'block';
                });
                return;
            }
            
            // Otherwise, filter by the selected category
            productCards.forEach(card => {
                const cardCategory = card.querySelector('.card-text.text-muted').textContent;
                if (cardCategory === selectedCategory) {
                    card.parentElement.style.display = 'block';
                } else {
                    card.parentElement.style.display = 'none';
                }
            });
        });
    }
    
    // Form validation for create product
    const createProductForm = document.querySelector('form[action="/create_makeup"]');
    if (createProductForm) {
        createProductForm.addEventListener('submit', function(event) {
            const priceInput = document.getElementById('price');
            const stockInput = document.getElementById('stock');
            
            if (parseFloat(priceInput.value) <= 0) {
                alert('Price must be greater than 0');
                event.preventDefault();
                return false;
            }
            
            if (parseInt(stockInput.value) <= 0) {
                alert('Stock must be at least 1');
                event.preventDefault();
                return false;
            }
            
            return true;
        });
    }
    
    // Image preview for create product form
    const imageUrlInput = document.getElementById('image_url');
    if (imageUrlInput) {
        const previewImage = document.createElement('img');
        previewImage.className = 'img-thumbnail mt-2';
        previewImage.style.maxHeight = '200px';
        previewImage.src = imageUrlInput.value;
        imageUrlInput.parentNode.appendChild(previewImage);
        
        imageUrlInput.addEventListener('input', function() {
            previewImage.src = this.value;
        });
    }
});