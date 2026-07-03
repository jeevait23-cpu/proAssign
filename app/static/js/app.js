const toasts = document.querySelectorAll(".toast");

toasts.forEach((toast) => {
  window.setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateY(-6px)";
    toast.style.transition = "opacity 180ms ease, transform 180ms ease";
  }, 4200);
});
