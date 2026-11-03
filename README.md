# Dragonwilds Join Code

Página web pública e somente leitura que mostra o `JoinCode` mais recente do
contêiner `dragonwilds-local`.

O site roda em um contêiner próprio. Ele não recebe o socket do Docker e não
executa comandos no host. O servidor Dragonwilds grava uma cópia de seu stdout
em `shared_logs/dragonwilds.log`, montada como somente leitura no contêiner web.

## Estrutura esperada no Ubuntu

```text
~/dragonwilds-server/
├── docker-compose.yml
├── server_files/
└── dragonwilds-join-code/
    ├── Dockerfile
    └── docker-compose.join-code.yml
```

O `docker-compose.yml` principal continua sendo o arquivo que você já possui.
O segundo Compose complementa o primeiro: mantém o volume de `server_files`,
adiciona o arquivo de log compartilhado e cria o serviço `join-code`.

## Instalação

Na pasta do servidor:

```bash
cd ~/dragonwilds-server
git clone https://github.com/JoaoBoll/dragonwilds-join-code.git
mkdir -p shared_logs
sudo chown 1000:1000 shared_logs
```

Se o repositório já existir nessa pasta:

```bash
cd ~/dragonwilds-server/dragonwilds-join-code
git pull
cd ..
```

Suba os dois serviços usando os dois arquivos Compose:

```bash
docker compose \
  -f docker-compose.yml \
  -f dragonwilds-join-code/docker-compose.join-code.yml \
  up -d --build
```

Confira:

```bash
docker compose \
  -f docker-compose.yml \
  -f dragonwilds-join-code/docker-compose.join-code.yml \
  ps

curl http://127.0.0.1:8787
```

## Acesso externo

A porta é publicada somente em `127.0.0.1:8787`. Aponte Caddy, Nginx ou um
Cloudflare Tunnel para esse endereço. Dessa forma, a aplicação não expõe uma
porta adicional diretamente na internet.

Exemplo Caddy:

```caddyfile
join.seudominio.com {
    reverse_proxy 127.0.0.1:8787
}
```

## Atualizações e operação

Para aplicar atualizações do projeto:

```bash
cd ~/dragonwilds-server/dragonwilds-join-code
git pull
cd ..
docker compose \
  -f docker-compose.yml \
  -f dragonwilds-join-code/docker-compose.join-code.yml \
  up -d --build
```

Logs:

```bash
docker logs -f dragonwilds-join-code
docker logs -f dragonwilds-local
```

O Join Code é lido quando alguém acessa a página. Não há consulta periódica.
