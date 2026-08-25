const tema = localStorage.getItem("tema") || "dark";

document.documentElement.setAttribute("data-bs-theme", tema);
document.body.classList.toggle("bg-dark", tema === "dark");
document.body.classList.toggle("tema-escuro", tema === "dark");