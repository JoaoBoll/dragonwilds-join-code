# Dragonwilds Join Code

Uma página pública que exibe somente o `JoinCode` mais recente do contêiner
`dragonwilds-local`.

Cada acesso à página consulta o código naquele momento. Não há atualização em
segundo plano, JavaScript, formulário, login, parâmetros ou comandos enviados
pelo visitante.

## O que fica exposto

Somente uma página HTML, uma folha de estilos e o Join Code. A aplicação:

- não monta nem publica o socket do Docker;
- não pertence ao grupo `docker`;
- não aceita nomes de contêiner, comandos ou qualquer entrada do visitante;
- permite executar somente um helper root de caminho fixo e sem argumentos;
- valida a saída e só mostra algo que tenha o formato `XXXX-XXXX`;
- devolve `404` para qualquer outra rota;
- limita a leitura dos logs a uma vez a cada três segundos em caso de muitos
  acessos simultâneos.

O Join Code será público para qualquer pessoa que conheça a URL. Isso é parte
da finalidade da página; nenhum outro dado do servidor é retornado.

## Instalação no servidor

Copie a pasta para o servidor e execute:

```bash
cd ~/dragonwilds-server/join-code-web
chmod +x install.sh bin/dragonwilds-join-code
sudo ./install.sh
```

Teste no próprio servidor:

```bash
curl http://127.0.0.1:8787
```

O serviço escuta somente em `127.0.0.1:8787`. Para disponibilizar a página,
aponte seu proxy HTTPS (Caddy, Nginx ou Cloudflare Tunnel) para esse endereço.
Assim, a aplicação continua sem uma porta própria aberta na internet.

Exemplo mínimo para Caddy, substituindo o domínio:

```caddyfile
join.seudominio.com {
    reverse_proxy 127.0.0.1:8787
}
```

## Operação

```bash
journalctl -u dragonwilds-join-code -f
sudo systemctl restart dragonwilds-join-code
```
