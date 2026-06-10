(function () {
  "use strict";

  var nav = document.getElementById("site-nav");
  var toggle = document.getElementById("nav-toggle");
  var menu = document.getElementById("nav-menu");

  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var isOpen = nav.classList.toggle("nav-open");
      toggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
    });
  }

  if (menu && nav) {
    menu.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () {
        nav.classList.remove("nav-open");
        if (toggle) {
          toggle.setAttribute("aria-expanded", "false");
        }
      });
    });
  }

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && nav) {
      nav.classList.remove("nav-open");
      if (toggle) {
        toggle.setAttribute("aria-expanded", "false");
      }
    }
  });

  document.querySelectorAll('a[href*="#"]').forEach(function (anchor) {
    anchor.addEventListener("click", function (e) {
      var href = anchor.getAttribute("href");
      if (!href || href.indexOf("#") === -1) {
        return;
      }

      var hashIndex = href.indexOf("#");
      var hash = href.substring(hashIndex);
      if (hash === "#" || hash.length < 2) {
        return;
      }

      var path = href.substring(0, hashIndex);
      var onSamePage =
        !path ||
        path === window.location.pathname ||
        path === window.location.pathname.replace(/\/$/, "") + "/" ||
        path.endsWith(window.location.pathname);

      if (!onSamePage && path) {
        return;
      }

      var target = document.querySelector(hash);
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: "smooth", block: "start" });
        if (history.pushState) {
          history.pushState(null, null, hash);
        }
      }
    });
  });
})();
