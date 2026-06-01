# Backend

Isso é so uma Api em python com fastAPi para instanciar um pytorch do nosso modelo, receber uma img, enviar pro modelo, e retornar um stream de dados com o retorno do modelo. não tem nada de mais aqui. sendo bem sincero

## Rodando local (MAS PRA QUE? TEMOS DOCKER!!)

- obs, me basei que isso sejá executado no mac ou linux. não sei como funciona ambientes virtuais python no windows 😭

1. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requeriments.txt
   ```
3. Run the server:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

## Rodando com Docker


```bash
docker build -t waldo-api .
docker run -p 8001:8000 waldo-api
```
``
