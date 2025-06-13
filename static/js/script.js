
    function toggleFavorite(icon) {
      icon.classList.toggle("active");
      if (icon.classList.contains("active")) {
        icon.textContent = "♥";
        icon.setAttribute("data-tooltip", "إزالة من المفضلة");
      } else {
        icon.textContent = "♡";
        icon.setAttribute("data-tooltip", "أضف إلى المفضلة");
      }
    }


    function toggleFavorite(icon) {
      icon.classList.toggle("active");
      icon.textContent = icon.classList.contains("active") ? "♥" : "♡";
      icon.setAttribute("data-tooltip", icon.classList.contains("active") ? "إزالة من المفضلة" : "أضف إلى المفضلة");
    }

    function toggleFullDescription(button) {
      const description = button.previousElementSibling;
      description.classList.toggle("expanded");
      button.textContent = description.classList.contains("expanded") ? "إخفاء" : "عرض المزيد";
    }
