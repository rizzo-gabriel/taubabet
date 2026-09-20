// Quando a página carrega, aplicar o tema salvo
const temaSalvo = localStorage.getItem('tema') || 'dark';
aplicarTema(temaSalvo);

function aplicarTema(tema) {
    document.documentElement.setAttribute('data-bs-theme', tema);
    document.body.classList.remove('tema-escuro', 'tema-claro');
    if (tema === 'dark') {
        document.body.classList.add('tema-escuro');
    } else {
        document.body.classList.add('tema-claro');
    }
    localStorage.setItem('tema', tema);
}

// No evento de mudança do checkbox
document.getElementById('tema').addEventListener('change', function() {
    const novoTema = this.checked ? 'dark' : 'light';
    aplicarTema(novoTema);
});  //