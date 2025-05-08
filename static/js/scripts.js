// JavaScript функции для Re:Docs

// Функция для подтверждения удаления документа
function confirmDelete(documentId, documentName) {
    return confirm(`Вы уверены, что хотите удалить документ "${documentName}"? Это действие нельзя отменить.`);
}

// Функция для обновления статуса документа на основе даты истечения срока
function updateDocumentStatuses() {
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    // Обновляем строки в таблице документов
    const documentRows = document.querySelectorAll('tr.document-row');

    let activeCount = 0;
    let expiringSoonCount = 0;
    let expiredCount = 0;

    documentRows.forEach(function(row) {
        const expiryDateCell = row.querySelector('td:nth-child(4)');
        const statusCell = row.querySelector('td:nth-child(5) .badge');

        if (expiryDateCell && statusCell) {
            // Получаем дату в формате DD.MM.YYYY
            const dateParts = expiryDateCell.textContent.trim().split('.');
            if (dateParts.length === 3) {
                const expiryDate = new Date(parseInt(dateParts[2]), parseInt(dateParts[1]) - 1, parseInt(dateParts[0]));
                const timeDiff = expiryDate - today;
                const daysLeft = Math.ceil(timeDiff / (1000 * 60 * 60 * 24));

                // Обновляем статус на основе разницы дат
                if (daysLeft < 0) {
                    // Документ просрочен
                    statusCell.className = 'badge bg-danger';
                    statusCell.textContent = 'Просрочен';
                    row.setAttribute('data-status', 'expired');
                    expiredCount++;
                } else if (daysLeft <= 30) {
                    // Документ скоро истекает
                    statusCell.className = 'badge bg-warning text-dark';
                    statusCell.textContent = 'Скоро истекает';
                    row.setAttribute('data-status', 'expiring_soon');
                    expiringSoonCount++;
                } else {
                    // Документ действителен
                    statusCell.className = 'badge bg-success';
                    statusCell.textContent = 'Действителен';
                    row.setAttribute('data-status', 'active');
                    activeCount++;
                }
            }
        }
    });

    // Обновляем счетчики на странице, если они есть
    updateCounters(activeCount, expiringSoonCount, expiredCount);
}

// Функция для обновления счетчиков на странице
function updateCounters(activeCount, expiringSoonCount, expiredCount) {
    // Обновляем счетчики на странице документов и дашборде
    const activeCounterElements = document.querySelectorAll('.card.bg-success h2, .card.bg-success h3');
    const expiringSoonCounterElements = document.querySelectorAll('.card.bg-warning h2, .card.bg-warning h3');
    const expiredCounterElements = document.querySelectorAll('.card.bg-danger h2, .card.bg-danger h3');
    const totalCounterElements = document.querySelectorAll('.card.bg-primary h2, .card.bg-primary h3, .card:not([class*="bg-"]) h2');

    // Обновляем счетчик активных документов (включает и действительные, и скоро истекающие)
    activeCounterElements.forEach(element => {
        element.textContent = activeCount;
    });

    // Обновляем счетчик документов, срок которых скоро истекает
    expiringSoonCounterElements.forEach(element => {
        element.textContent = expiringSoonCount;
    });

    // Обновляем счетчик просроченных документов
    expiredCounterElements.forEach(element => {
        element.textContent = expiredCount;
    });

    // Обновляем общий счетчик документов
    const totalCount = activeCount + expiringSoonCount + expiredCount;
    totalCounterElements.forEach(element => {
        if (element.closest('.card:not([class*="bg-"])')) {
            element.textContent = totalCount;
        }
    });
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

    // Запускаем обновление статусов, если на странице есть таблица документов
    if (document.querySelectorAll('tr.document-row').length > 0) {
        updateDocumentStatuses();
    }

    // Автоматическое закрытие алертов через 5 секунд
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert.alert-success, .alert.alert-info');
        alerts.forEach(function(alert) {
            if (bootstrap && bootstrap.Alert) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        });
    }, 5000);
});

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