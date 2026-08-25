function tocar1() {
    const audio = document.getElementById("money_meme");
    audio.play();
}
function tocar2() {
    const audio = document.getElementById("laugh_meme");
    audio.play();
}

function salvar() {
    const cookies = document.getElementById("cookies");

    // Se o checkbox NÃO estiver marcado (cookies desativados)
    if (!cookies.checked) {
        const modal = new bootstrap.Modal(
            document.getElementById("modalCookies")
        );
        modal.show();
    } else {
        document.getElementById("meuFormulario").submit();
    }
}

const checkboxTema = document.getElementById("tema");

if (checkboxTema) {
    checkboxTema.checked = localStorage.getItem("tema") !== "light";

    checkboxTema.addEventListener("change", function () {
        const tema = this.checked ? "dark" : "light";

        document.documentElement.setAttribute("data-bs-theme", tema);
        document.body.classList.toggle("bg-dark", this.checked);
        document.body.classList.toggle("tema-escuro", this.checked);

        localStorage.setItem("tema", tema);
    });
}

async function gerarQR() {
    const valor = document.getElementById("valor").value;

    if (!valor) {
        alert("Digite um valor antes de gerar o QR Code!");
        return;
    }

    const res = await fetch("/gerar_qr", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ valor })
    });

    const data = await res.json();

    const img = document.getElementById("qrcode");

    // força atualizar imagem
    img.src = data.img + "?t=" + new Date().getTime();

    img.style.display = "block";
}

const btn = document.getElementById("btnMostrarVideo");
const container = document.getElementById("videoContainer");
const video = document.getElementById("video");

btn.addEventListener("click", function () {
    container.style.display = "flex";
    video.currentTime = 0;
    video.play();
});

video.addEventListener("ended", function () {
    container.style.display = "none";
});