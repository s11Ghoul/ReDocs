// JavaScript функции для Re:Docs

// Функция для подтверждения удаления документа
function confirmDelete(documentId, documentName) {
    return confirm(`Вы уверены, что хотите удалить документ "${documentName}"? Это действие нельзя отменить.`);
}

// Функция для обновления статуса документа на основе даты окончания
function updateDocumentStatus() {
    const today = new Date();
    const expiryDateElements = document.querySelectorAll('.expiry-date');

    expiryDateElements.forEach(function(element) {
        const expiryDate = new Date(element.dataset.date);
        const daysLeft = Math.ceil((expiryDate - today) / (1000 * 60 * 60 * 24));
        const statusElement = element.closest('tr').querySelector('.status');

        if (daysLeft < 0) {
            statusElement.innerHTML = '<span class="badge bg-danger">Просрочен</span>';
        } else if (daysLeft <= 30) {
            statusElement.innerHTML = '<span class="badge bg-warning text-dark">Скоро истекает</span>';
        } else {
            statusElement.innerHTML = '<span class="badge bg-success">Действителен</span>';
        }
    });
}

// Инициализация всплывающих подсказок Bootstrap
function initializeTooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Функция для предварительного просмотра загружаемого файла
function previewFile() {
    const fileInput = document.getElementById('id_document_file');
    const fileInfoContainer = document.getElementById('file-info');

    if (fileInput && fileInfoContainer && fileInput.files.length > 0) {
        const file = fileInput.files[0];
        const fileSize = (file.size / 1024 / 1024).toFixed(2); // в МБ

        let fileIcon = 'fas fa-file';
        if (file.type.includes('pdf')) {
            fileIcon = 'fas fa-file-pdf';
        } else if (file.type.includes('image')) {
            fileIcon = 'fas fa-file-image';
        }

        fileInfoContainer.innerHTML = `
            <div class="alert alert-info">
                <i class="${fileIcon}"></i> ${file.name} (${fileSize} МБ)
            </div>
        `;
    }
}

// Функция для проверки размера файла перед отправкой формы
function validateFileSize() {
    const fileInput = document.getElementById('id_document_file');
    const maxSize = 10 * 1024 * 1024; // 10 МБ

    if (fileInput && fileInput.files.length > 0) {
        if (fileInput.files[0].size > maxSize) {
            alert('Размер файла превышает допустимый лимит в 10 МБ');
            return false;
        }
    }

    return true;
}

// Функция для проверки формата файла
function validateFileExtension() {
    const fileInput = document.getElementById('id_document_file');
    const allowedExtensions = ['pdf', 'jpg', 'jpeg'];

    if (fileInput && fileInput.files.length > 0) {
        const fileName = fileInput.files[0].name;
        const fileExtension = fileName.split('.').pop().toLowerCase();

        if (!allowedExtensions.includes(fileExtension)) {
            alert('Допустимые форматы файлов: PDF, JPG');
            return false;
        }
    }

    return true;
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    // Инициализация всплывающих подсказок
    initializeTooltips();

    // Обработчик для предварительного просмотра файла
    const fileInput = document.getElementById('id_document_file');
    if (fileInput) {
        fileInput.addEventListener('change', previewFile);
    }

    // Обработчик для формы с валидацией файла
    const documentForm = document.querySelector('form.needs-validation');
    if (documentForm) {
        documentForm.addEventListener('submit', function(event) {
            if (!validateFileSize() || !validateFileExtension()) {
                event.preventDefault();
                event.stopPropagation();
            }
        });
    }

    // Автоматическое закрытие алертов через 5 секунд
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert.alert-success, .alert.alert-info');
        alerts.forEach(function(alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
});