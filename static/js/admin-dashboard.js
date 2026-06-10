(function () {
  var modalOverlay = document.getElementById('adm-modal-overlay');
  var modalTitle = document.getElementById('adm-modal-title');
  var modalBody = document.getElementById('adm-modal-body');
  var modalCancel = document.getElementById('adm-modal-cancel');
  var modalConfirm = document.getElementById('adm-modal-confirm');
  var pendingForm = null;

  function openModal(title, body, form) {
    if (!modalOverlay) {
      form.submit();
      return;
    }
    modalTitle.textContent = title || 'Confirm action';
    modalBody.textContent = body || 'Are you sure?';
    pendingForm = form;
    modalOverlay.hidden = false;
  }

  function closeModal() {
    if (modalOverlay) modalOverlay.hidden = true;
    pendingForm = null;
  }

  if (modalCancel) modalCancel.addEventListener('click', closeModal);
  if (modalOverlay) {
    modalOverlay.addEventListener('click', function (e) {
      if (e.target === modalOverlay) closeModal();
    });
  }
  if (modalConfirm) {
    modalConfirm.addEventListener('click', function () {
      if (pendingForm) pendingForm.submit();
      closeModal();
    });
  }

  document.querySelectorAll('.adm-confirm-btn').forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      var form = btn.closest('form');
      if (!form) return;
      openModal(
        btn.getAttribute('data-confirm-title'),
        btn.getAttribute('data-confirm-body'),
        form
      );
    });
  });

  var selectAll = document.getElementById('adm-select-all');
  if (selectAll) {
    selectAll.addEventListener('change', function () {
      document.querySelectorAll('.adm-row-check').forEach(function (cb) {
        cb.checked = selectAll.checked;
      });
    });
  }
})();
