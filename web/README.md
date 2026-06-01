
# Web

Apenas um monorepo com Shadcn/UI que se conecta à API para facilitar os testes do modelo, nada demais.

## Pré-requisitos

* Node.js (versão 20 ou superior)
* pnpm (habilitado via Corepack ou instalado globalmente)

## Executando Localmente

1. Navegue até o diretório `web`.
2. Instale as dependências:

   ```bash
   pnpm install
   ```
3. Inicie o servidor de desenvolvimento:

   ```bash
   pnpm run dev
   ```
4. Abra [http://localhost:3000](http://localhost:3000) no navegador para visualizar o resultado.

## Executando com Docker

Você pode compilar e executar este serviço individualmente usando Docker:

```bash
docker build -t waldo-web .
docker run -p 3000:3000 waldo-web
```

