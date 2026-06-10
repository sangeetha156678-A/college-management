(function () {
  "use strict";

  var passwordInput = document.getElementById("userpassword");
  var toggleBtn = document.getElementById("password-toggle");
  var toggleIcon = document.getElementById("password-toggle-icon");

  if (toggleBtn && passwordInput) {
    toggleBtn.addEventListener("click", function () {
      var isHidden = passwordInput.type === "password";
      passwordInput.type = isHidden ? "text" : "password";

      if (toggleIcon) {
        toggleIcon.classList.toggle("bi-eye", !isHidden);
        toggleIcon.classList.toggle("bi-eye-slash", isHidden);
      }

      toggleBtn.setAttribute("aria-label", isHidden ? "Hide password" : "Show password");
      toggleBtn.setAttribute("aria-pressed", isHidden ? "true" : "false");
    });
  }

  var form = document.getElementById("portal-login-form");
  var roleInput = document.getElementById("login_role");

  if (form && roleInput) {
    form.addEventListener("submit", function () {
      var activeTab = document.querySelector(".erp-tab.active");
      if (activeTab) {
        var href = activeTab.getAttribute("href") || "";
        var match = href.match(/[?&]role=([^&]+)/);
        if (match && match[1]) {
          roleInput.value = match[1];
        }
      }
    });
  }
})();
