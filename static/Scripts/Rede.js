// Adicione esta tag no seu index.html: <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>

// Variáveis de referência
const inputNome = document.getElementById('inputNome');
const resultadosDiv = document.getElementById('resultados');
const iaBoxDiv = document.getElementById('ia-box');
const chatBox = document.getElementById('chat-box');
const chatInput = document.getElementById('chat-input');
const analiseResultadoDiv = document.getElementById('analise-resultado');


/**
 * 1. FUNÇÃO PRINCIPAL DE BUSCA E SUGESTÃO (MYSQL + GEMINI)
 */
async function buscarItem() {
    const nome = inputNome.value.trim();
    if (!nome) return;

    // Limpa resultados e define o estado de carregamento
    resultadosDiv.innerHTML = '<p class="placeholder"><i class="fas fa-spinner fa-spin"></i> Buscando no banco...</p>';
    iaBoxDiv.innerHTML = '<p class="placeholder"><i class="fas fa-magic fa-spin"></i> Consultando o Gemini...</p>';

    // Remove qualquer formulário de salvamento anterior
    const oldForm = document.getElementById('salvar-form');
    if (oldForm) oldForm.remove();

    try {
        const response = await fetch('/buscar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ nome: nome })
        });

        const data = await response.json();

        // --- 1. Renderizar Resultados do Banco (MySQL) ---
        let htmlContent = '';
        if (data.itens && data.itens.length > 0) {
            data.itens.forEach(item => {
                htmlContent += `<p><strong>${item.nome}</strong> | Categoria: ${item.categoria} | Valor: R$ ${parseFloat(item.valor).toFixed(2)}</p>`;
            });
        } else {
            htmlContent = `<p class="placeholder">Nenhum item encontrado no banco de dados para "${nome}".</p>`;
        }
        resultadosDiv.innerHTML = htmlContent;

        // --- 2. Renderizar Sugestão da IA (Gemini) - USANDO MARKED.JS ---
        // Converte a saída Markdown do Gemini em HTML formatado
        const iaHtml = marked.parse(data.sugestao_ia); 
        iaBoxDiv.innerHTML = iaHtml;

        // --- 3. Botão de Salvar Item (se não encontrado) ---
        if (data.itens.length === 0) {
            iaBoxDiv.innerHTML += `
                <div class="save-prompt">
                    <p style="margin-top: 15px;">Item não encontrado. Deseja adicionar "${data.item_para_salvar}" ao inventário?</p>
                    <button onclick="mostrarFormularioSalvar('${data.item_para_salvar}')"><i class="fas fa-plus-circle"></i> Adicionar Item Agora</button>
                </div>
            `;
        }

    } catch (error) {
        console.error('Erro na requisição:', error);
        resultadosDiv.innerHTML = '<p style="color: red;">Erro ao comunicar com o servidor.</p>';
        iaBoxDiv.innerHTML = '<p style="color: red;">Erro ao comunicar com o servidor.</p>';
    }
}


/**
 * 2. FUNÇÕES DE SALVAMENTO DE ITEM
 */
function mostrarFormularioSalvar(nome) {
    const oldForm = document.getElementById('salvar-form');
    if (oldForm) oldForm.remove();

    // Tenta obter o texto formatado (sem tags HTML) para a descrição
    const iaText = iaBoxDiv.innerText; 
    
    // Tenta extrair um valor aproximado da sugestão da IA para pré-preenchimento
    let defaultValor = '0.00';
    const valorMatch = iaText.match(/R\$\s*([\d,\.]+)/);
    if (valorMatch) {
        defaultValor = valorMatch[1].replace(',', '.');
    }

    const formHtml = `
        <div id="salvar-form" class="save-form-box">
            <h4>Adicionar Item: ${nome}</h4>
            <input type="text" id="salvar-categoria" placeholder="Categoria (Ex: Switch, Placa de Vídeo)" value="Hardware/Rede">
            <input type="number" id="salvar-valor" placeholder="Valor (Ex: 1500.00)" value="${defaultValor}" step="0.01">
            <textarea id="salvar-descricao" placeholder="Descrição/Detalhes (Preenchido com a sugestão da IA)">${iaText.substring(0, 300)}...</textarea>
            <button onclick="salvarItem('${nome}')"><i class="fas fa-save"></i> Confirmar e Salvar</button>
        </div>
    `;
    iaBoxDiv.insertAdjacentHTML('afterend', formHtml);
}

async function salvarItem(nome) {
    const categoria = document.getElementById('salvar-categoria').value;
    const valor = document.getElementById('salvar-valor').value;
    const descricao = document.getElementById('salvar-descricao').value;

    const response = await fetch('/salvar_item', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nome, categoria, valor, descricao })
    });

    const data = await response.json();
    alert(data.message);
    
    const form = document.getElementById('salvar-form');
    if (form) form.remove(); 
    
    buscarItem();
}


/**
 * 3. FUNÇÃO DE EXPORTAÇÃO PARA EXCEL
 */
function exportarExcel() {
    window.location.href = '/exportar_excel';
}


/**
 * 4. FUNÇÕES DO CHATBOT TÉCNICO
 */
async function enviarChat() {
    const pergunta = chatInput.value.trim();
    if (!pergunta) return;

    chatBox.innerHTML += `<p class="user-message">Você: ${pergunta}</p>`;
    chatBox.scrollTop = chatBox.scrollHeight;
    chatInput.value = '';

    const loadingId = 'loading-chat-' + Date.now();
    chatBox.innerHTML += `<p id="${loadingId}" class="bot-message"><i class="fas fa-circle-notch fa-spin"></i> Gemini está pensando...</p>`;
    chatBox.scrollTop = chatBox.scrollHeight;

    try {
        const response = await fetch('/chat_tecnico', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ pergunta: pergunta })
        });

        const data = await response.json();
        
        const loading = document.getElementById(loadingId);
        if (loading) loading.remove();

        // Converte a saída Markdown do chat para HTML
        const chatHtml = marked.parse(data.resposta);
        chatBox.innerHTML += `<p class="bot-message"><i class="fas fa-robot"></i> Gemini: ${chatHtml}</p>`;
        chatBox.scrollTop = chatBox.scrollHeight;

    } catch (error) {
        const loading = document.getElementById(loadingId);
        if (loading) loading.remove();
        chatBox.innerHTML += `<p class="bot-message" style="color: red;"><i class="fas fa-times-circle"></i> Erro de comunicação com o servidor.</p>`;
    }
}


/**
 * 5. FUNÇÃO DE ANÁLISE MULTIMODAL (IMAGEM + TEXTO)
 */
async function analisarImagem() {
    const fileInput = document.getElementById('image-upload');
    const descricaoProblema = document.getElementById('problema-desc').value;

    if (fileInput.files.length === 0) {
        alert("Por favor, selecione uma imagem para análise.");
        return;
    }
    
    analiseResultadoDiv.innerHTML = '<p class="placeholder"><i class="fas fa-search-plus fa-spin"></i> Analisando imagem e contexto...</p>';

    const formData = new FormData();
    formData.append('foto', fileInput.files[0]);
    formData.append('descricao_problema', descricaoProblema);

    try {
        const response = await fetch('/analisar_imagem', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        
        // Converte a saída Markdown da análise para HTML
        const analiseHtml = marked.parse(data.analise);
        analiseResultadoDiv.innerHTML = analiseHtml;
        
    } catch (error) {
        console.error('Erro na análise de imagem:', error);
        analiseResultadoDiv.innerHTML = `<p style="color: red;">Erro ao processar a análise. Verifique o servidor.</p>`;
    }
}