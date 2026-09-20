document.addEventListener('DOMContentLoaded', function() {
    carregarDashboard();
    carregarGraficoTodasApostas();
});

function carregarDashboard() {
    fetch('/api/dados_dashboard')
        .then(response => response.json())
        .then(dados => {
            document.getElementById('saldo').innerText = 'R$ ' + dados.saldo.toFixed(2);
            document.getElementById('totalApostas').innerText = dados.total_apostas;
            document.getElementById('vitorias').innerText = dados.vitorias;
            document.getElementById('derrotas').innerText = dados.derrotas;

            // Tabela de últimas apostas
            const tbdy = document.getElementById('tabelaUltimas');
            tbdy.innerHTML = '';
            if (dados.ultimas.length == 0) {
                tbdy.innerHTML = '<tr><td colspan="4" class="text-center">Nenhuma aposta recente.</td></tr>';
            } else {
                dados.ultimas.forEach(a => {
                    const linha = `<tr>
                        <td>${a.data}</td>
                        <td>${a.local}</td>
                        <td>R$ ${a.valor.toFixed(2)}</td>
                        <td><span class="badge ${a.resultado == 'Vitória' ? 'bg-success' : 'bg-danger'}">${a.resultado}</span></td>
                    </tr>`;
                    tbdy.innerHTML += linha;
                });
            }
        })
        .catch(error => console.error('Erro ao carregar dashboard:', error));
}

function carregarGraficoTodasApostas() {
    fetch('/api/todas_apostas')
        .then(response => response.json())
        .then(dadosUsuarios => {
            const ctx = document.getElementById('graficoEvolucao').getContext('2d');
            
            if (window.graficoGlobal) {
                window.graficoGlobal.destroy();
            }
            
            if (!dadosUsuarios || dadosUsuarios.length === 0) {
                window.graficoGlobal = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: ['Sem dados'],
                        datasets: [{
                            label: 'Nenhuma aposta registrada',
                            data: [0],
                            borderColor: '#6c757d',
                            backgroundColor: 'rgba(108, 117, 125, 0.1)'
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                labels: { color: '#ffffff' }
                            }
                        }
                    }
                });
                return;
            }
            
            // Preparar datasets - TODOS com o MESMO número de pontos
            const datasets = dadosUsuarios.map(usuario => {
                return {
                    label: usuario.usuario,
                    data: usuario.valores,
                    borderColor: usuario.cor,
                    backgroundColor: usuario.cor + '33',
                    tension: 0.1,
                    fill: false,
                    spanGaps: false,
                    pointBackgroundColor: usuario.valores.map(v => {
                        if (v === null) return 'transparent';
                        return v >= 0 ? '#28a745' : '#dc3545';
                    }),
                    pointRadius: usuario.valores.map(v => v === null ? 0 : 5),
                    borderWidth: 2,
                    pointBorderColor: usuario.valores.map(v => {
                        if (v === null) return 'transparent';
                        return v >= 0 ? '#28a745' : '#dc3545';
                    })
                };
            });
            
            const labels = dadosUsuarios.length > 0 ? dadosUsuarios[0].labels : [];
            
            window.graficoGlobal = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: datasets
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            labels: {
                                color: '#ffffff',
                                font: { size: 11 }
                            }
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    let label = context.dataset.label || '';
                                    let valor = context.parsed.y;
                                    
                                    if (valor === null || valor === undefined) {
                                        return label + ': Sem aposta';
                                    }
                                    
                                    if (valor >= 0) {
                                        return label + ': +R$ ' + valor.toFixed(2) + ' 🏆';
                                    } else {
                                        return label + ': -R$ ' + Math.abs(valor).toFixed(2) + ' 📉';
                                    }
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            ticks: {
                                color: '#94a3b8',
                                maxRotation: 0,
                                stepSize: 1
                            },
                            grid: {
                                color: 'rgba(255,255,255,0.05)',
                                display: false
                            },
                            title: {
                                display: true,
                                text: 'Número da Aposta',
                                color: '#94a3b8',
                                font: { size: 12 }
                            }
                        },
                        y: {
                            beginAtZero: true,
                            ticks: {
                                color: '#94a3b8',
                                callback: function(value) {
                                    return 'R$ ' + value.toFixed(2);
                                }
                            },
                            grid: {
                                color: 'rgba(255,255,255,0.08)'
                            }
                        }
                    }
                }
            });
        })
        .catch(error => console.error('Erro ao carregar gráfico:', error));
}

const datasets = dadosUsuarios.map(usuario => {
    return {
        label: usuario.usuario,
        data: usuario.valores,
        borderColor: usuario.cor,
        backgroundColor: usuario.cor + '33',
        tension: 0.1,
        fill: false,
        spanGaps: true,   // <-- era false
        pointBackgroundColor: usuario.valores.map(v => {
            if (v === null || v === 0) return 'transparent';
            return v >= 0 ? '#28a745' : '#dc3545';
        }),
        pointRadius: usuario.valores.map(v => (v === null || v === 0) ? 0 : 5),
        borderWidth: 2,
        pointBorderColor: usuario.valores.map(v => {
            if (v === null || v === 0) return 'transparent';
            return v >= 0 ? '#28a745' : '#dc3545';
        })
    };
});