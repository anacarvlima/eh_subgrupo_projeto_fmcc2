// Configuração da API
const API_URL = '/api/subgrupo';

document.getElementById('gruposForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    // Limpar resultados anteriores
    document.getElementById('outputContainer').style.display = 'none';
    document.getElementById('errorMessage').style.display = 'none';
    
    // Mostrar loading
    document.getElementById('loading').style.display = 'block';
    
    // Desabilitar botão
    const btn = document.querySelector('.btn-verificar');
    btn.disabled = true;
    btn.textContent = 'Verificando...';
    
    try {
        // Coletar dados do formulário
        const elementosG = document.getElementById('elementosG').value
            .trim()
            .split(/\s+/)
            .map(x => parseInt(x))
            .filter(x => !isNaN(x));
        
        const elementosH = document.getElementById('elementosH').value
            .trim()
            .split(/\s+/)
            .map(x => parseInt(x))
            .filter(x => !isNaN(x));
        
        if (elementosG.length === 0 || elementosH.length === 0) {
            throw new Error('Por favor, digite pelo menos um elemento para cada grupo');
        }
        
        const dados = {
            grupoG: {
                elementos: elementosG,
                operacao: document.getElementById('operacaoG').value,
                modulo: document.getElementById('moduloG').value || null
            },
            grupoH: {
                elementos: elementosH,
                operacao: document.getElementById('operacaoH').value,
                modulo: document.getElementById('moduloH').value || null
            }
        };
        
        // Chamada à API
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(dados)
        });

        // Tenta converter para JSON
        let result;
        try {
            result = await response.json();
        } catch (err) {
            throw new Error('Resposta inválida do servidor');
        }
        
        // Verifica sucesso
        if (result.sucesso) {
            mostrarResultados(result);
        } else {
            mostrarErro(result.erro || 'Erro desconhecido no servidor');
        }
        
    } catch (error) {
        mostrarErro('Erro ao processar os dados: ' + error.message);
    } finally {
        // Esconder loading e reabilitar botão
        document.getElementById('loading').style.display = 'none';
        btn.disabled = false;
        btn.textContent = '🔍 Verificar Grupos';
    }
});

function mostrarResultados(response) {
    let output = '';
    
    output += '='.repeat(60) + '\n';
    output += '           VERIFICAÇÃO DE GRUPOS E SUBGRUPOS\n';
    output += '='.repeat(60) + '\n\n';
    
    output += formatarResultadoGrupo(response.grupoG);
    output += '\n' + '-'.repeat(60) + '\n\n';
    
    output += formatarResultadoGrupo(response.grupoH);
    output += '\n' + '-'.repeat(60) + '\n\n';
    
    output += formatarResultadoSubgrupo(response.subgrupo);
    
    output += '\n' + '='.repeat(60) + '\n';
    output += '                    FIM DA VERIFICAÇÃO\n';
    output += '='.repeat(60);
    
    document.getElementById('outputText').textContent = output;
    document.getElementById('outputContainer').style.display = 'block';
    
    document.getElementById('outputContainer').scrollIntoView({
        behavior: 'smooth',
        block: 'start'
    });
}

function formatarResultadoGrupo(grupo) {
    let output = '';
    
    output += `TESTANDO GRUPO ${grupo.nome}:\n`;
    output += `Elementos: {${grupo.elementos.join(', ')}}\n`;
    output += `Operação: ${grupo.operacao}${grupo.modulo ? ` (mod ${grupo.modulo})` : ''}\n\n`;
    
    output += 'VERIFICANDO PROPRIEDADES:\n';
    grupo.mensagens.forEach(mensagem => {
        output += `  ${mensagem}\n`;
    });
    
    output += '\n';
    output += `STATUS FINAL: ${grupo.eh_grupo ? 'GRUPO VÁLIDO ✅' : 'NÃO É UM GRUPO ❌'}\n`;
    
    if (grupo.identidade !== null) {
        output += `Elemento identidade: ${grupo.identidade}\n`;
    }
    
    return output;
}

function formatarResultadoSubgrupo(subgrupo) {
    let output = '';
    
    output += 'TESTANDO SE H É SUBGRUPO DE G:\n\n';
    subgrupo.mensagens.forEach(mensagem => {
        output += `  ${mensagem}\n`;
    });
    
    output += '\n';
    output += `RESULTADO FINAL: ${subgrupo.eh_subgrupo ? 'H É SUBGRUPO DE G ✅' : 'H NÃO É SUBGRUPO DE G ❌'}\n`;
    
    return output;
}

function mostrarErro(mensagem) {
    const errorDiv = document.getElementById('errorMessage');
    errorDiv.textContent = mensagem;
    errorDiv.style.display = 'block';
    
    errorDiv.scrollIntoView({
        behavior: 'smooth',
        block: 'center'
    });
}

// Sincronizar operações e módulos
document.getElementById('operacaoG').addEventListener('change', function() {
    const operacaoH = document.getElementById('operacaoH');
    if (!operacaoH.value) operacaoH.value = this.value;
});
document.getElementById('moduloG').addEventListener('input', function() {
    const moduloH = document.getElementById('moduloH');
    if (!moduloH.value) moduloH.value = this.value;
});
