# cne-listas

## Passos completos no Windows PowerShell

> Os comandos abaixo assumem que **Git 2.50+** e **Python 3.11+** já estão
> instalados. Execute todos os passos numa janela do PowerShell.

1. **Confirmar pré-requisitos**

   ```powershell
   git --version
   python --version
   ```

2. **Clonar o repositório para `C:\Users\<utilizador>`**

   ```powershell
   cd C:\Users\<utilizador>
   git clone https://github.com/disruptio-org/cne-listas.git
   cd .\cne-listas
   ```

3. **Criar e ativar o ambiente virtual**

   ```powershell
   py -3 -m venv .venv
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\.venv\Scripts\Activate.ps1
   ```

4. **Instalar dependências obrigatórias e opcionais**

   O endpoint `/api/ocr-csv` usa uploads multipart, pelo que o pacote
   `python-multipart` é obrigatório além de FastAPI e Uvicorn.

   ```powershell
   pip install fastapi uvicorn python-multipart pdfplumber pillow pytesseract paddleocr spacy camelot-py[cv]
   ```

   *Se não quiser instalar todas as bibliotecas pesadas, garanta pelo menos:*

   ```powershell
   pip install fastapi uvicorn python-multipart pdfplumber pillow pytesseract
   ```

5. **Iniciar a API (deixar esta janela aberta)**

   ```powershell
   cd .\api
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

6. **Testar os endpoints numa segunda janela**

   Abra um novo PowerShell, volte à pasta do projeto e ative o ambiente:

   ```powershell
   cd C:\Users\<utilizador>\cne-listas
   .\.venv\Scripts\Activate.ps1
   ```

   *Health-check*

   ```powershell
   curl http://localhost:8000/api/health
   ```

   *Processar um PDF ou imagem (substitua o caminho pelo ficheiro real)*

   ```powershell
   curl -X POST `
        -H "Accept: text/csv" `
        -F "files=@C:\caminho\para\documento.pdf" `
        http://localhost:8000/api/ocr-csv `
        -o resultado.csv
   ```

7. **Validar o CSV gerado**

   ```powershell
   python .\scripts\test_csv_contract.py .\resultado.csv
   ```

8. **(Opcional) Executar os testes automatizados**

   ```powershell
   python -m pytest tests/test_render.py tests/test_api.py
   ```

   Os testes confirmam que PDFs sem texto extraível são rasterizados e que
   violações do contrato devolvem HTTP 422.
