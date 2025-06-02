// Main JavaScript file for the social media app

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Handle comment form submission with AJAX
    const commentForm = document.getElementById('comment-form');
    if (commentForm) {
        commentForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            const url = this.getAttribute('action');
            
            fetch(url, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Add the new comment to the list
                    const commentsList = document.getElementById('comments-list');
                    commentsList.innerHTML = data.html + commentsList.innerHTML;
                    
                    // Clear the form
                    document.getElementById('id_content').value = '';
                    
                    // Show success message
                    const alertDiv = document.createElement('div');
                    alertDiv.className = 'alert alert-success';
                    alertDiv.textContent = 'Comment added successfully!';
                    commentForm.parentNode.insertBefore(alertDiv, commentForm);
                    
                    // Auto-hide the alert
                    setTimeout(() => {
                        alertDiv.remove();
                    }, 3000);
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    }
});
