// Configuração da API - altere aqui se necessário
const API_URL = 'http://localhost:5000';

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
        
        // Fazer chamada à API
        const response = await fetch(`${API_URL}/verificar_grupos`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(dados)
        });
        
        const result = await response.json();
        
        if (result.sucesso) {
            mostrarResultados(result);
        } else {
            mostrarErro(result.erro);
        }
        
    } catch (error) {
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            mostrarErro('Erro de conexão: Certifique-se de que o servidor Python está rodando em http://localhost:5000');
        } else {
            mostrarErro('Erro ao processar os dados: ' + error.message);
        }
    } finally {
        // Esconder loading e reabilitar botão
        document.getElementById('loading').style.display = 'none';
        btn.disabled = false;
        btn.textContent = '🔍 Verificar Grupos';
    }
});

function mostrarResultados(response) {
    let output = '';
    
    // Adicionar separador inicial
    output += '=' .repeat(60) + '\n';
    output += '           VERIFICAÇÃO DE GRUPOS E SUBGRUPOS\n';
    output += '=' .repeat(60) + '\n\n';
    
    // Resultado do Grupo G
    output += formatarResultadoGrupo(response.grupoG);
    output += '\n' + '-'.repeat(60) + '\n\n';
    
    // Resultado do Grupo H
    output += formatarResultadoGrupo(response.grupoH);
    output += '\n' + '-'.repeat(60) + '\n\n';
    
    // Resultado do teste de subgrupo
    output += formatarResultadoSubgrupo(response.subgrupo);
    
    // Adicionar separador final
    output += '\n' + '='.repeat(60) + '\n';
    output += '                    FIM DA VERIFICAÇÃO\n';
    output += '='.repeat(60);
    
    // Mostrar na interface
    document.getElementById('outputText').textContent = output;
    document.getElementById('outputContainer').style.display = 'block';
    
    // Scroll suave até os resultados
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
    
    // Adicionar todas as mensagens
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
    
    // Adicionar todas as mensagens do teste de subgrupo
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
    
    // Scroll até o erro
    errorDiv.scrollIntoView({
        behavior: 'smooth',
        block: 'center'
    });
}

// Sincronizar operações (opcional - para facilitar o uso)
document.getElementById('operacaoG').addEventListener('change', function() {
    const operacaoH = document.getElementById('operacaoH');
    if (operacaoH.value === '') {
        operacaoH.value = this.value;
    }
});

// Sincronizar módulos (opcional - para facilitar o uso)
document.getElementById('moduloG').addEventListener('input', function() {
    const moduloH = document.getElementById('moduloH');
    if (moduloH.value === '') {
        moduloH.value = this.value;
    }
});