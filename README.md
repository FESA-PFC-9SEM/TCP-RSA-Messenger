# 🔐 Atividade RSA sobre TCP

## 🎯 Objetivo

Implementar o algoritmo **RSA (Rivest–Shamir–Adleman)** utilizando chaves assimétricas de **4096 bits**, integrado aos códigos TCP Client/Server fornecidos na atividade.

A aplicação simula uma comunicação entre duas entidades:

* **Alice:** `client.py`
* **Bob:** `server.py`
* **Transporte:** TCP
* **Porta:** `1300`
* **Chaves públicas:** trocadas em texto puro
* **Mensagem:** definida pelo usuário durante a execução
* **RTT:** medido com `time.perf_counter()`, desde o início do cliente até a apresentação da resposta final.

O objetivo é demonstrar, de forma prática, como a criptografia assimétrica pode ser utilizada sobre uma comunicação TCP.

---

## 🔑 Funcionamento do RSA

O RSA utiliza um **par de chaves matematicamente relacionadas**:

* **Chave pública:** pode ser compartilhada com outras pessoas.
* **Chave privada:** deve permanecer protegida e somente com seu proprietário.

Nesta aplicação, **Alice e Bob possuem seu próprio par de chaves**.

### Geração das chaves

A geração segue os quatro passos apresentados no material da atividade:

### 1. Escolha de `p` e `q`

São escolhidos dois números primos grandes:

```text
p
q
```

Nesta implementação, são utilizados primos de **2048 bits**, resultando em um módulo RSA de 4096 bits.

### 2. Cálculo de `N` e `φ(N)`

O módulo RSA é calculado por:

```text
N = p × q
```

E a função totiente:

```text
φ(N) = (p - 1) × (q - 1)
```

### 3. Escolha de `e`

É escolhido um valor `e` tal que:

```text
1 < e < φ(N)
```

e que seja coprimo com `φ(N)`.

A implementação utiliza:

```text
e = 65537
```

### 4. Cálculo de `d`

É calculado o inverso multiplicativo de `e` módulo `φ(N)`:

```text
e × d ≡ 1 (mod φ(N))
```

Assim são formadas as chaves:

```text
Chave pública  = (e, N)
Chave privada  = (d, N)
```

Esses são os quatro passos apresentados no material da atividade.

---

## 🔒 Criptografia e descriptografia

Quando uma mensagem precisa ser enviada para Bob, Alice utiliza a **chave pública de Bob**.

A operação de criptografia é:

```text
C = P^e mod N
```

Onde:

* `P` = mensagem original representada numericamente;
* `e` = expoente da chave pública;
* `N` = módulo RSA;
* `C` = mensagem cifrada.

Bob utiliza sua **chave privada** para recuperar a mensagem:

```text
P = C^d mod N
```

Esse é o princípio fundamental demonstrado na atividade: **uma mensagem criptografada com a chave pública do destinatário pode ser recuperada utilizando a chave privada correspondente**.

---

# 🔄 Fluxo da aplicação

A comunicação acontece entre duas máquinas, representadas por **Alice** e **Bob**.

```text
        ALICE                                  BOB
       Cliente                                Servidor
          │                                      │
          │────── Conexão TCP ─────────────────>│
          │                                      │
          │──── Chave pública de Alice ─────────>│
          │                                      │
          │<──── Chave pública de Bob ──────────│
          │                                      │
          │                                      │
          │  Mensagem original                  │
          │       ↓                              │
          │  Criptografa com                    │
          │  chave pública de Bob               │
          │       ↓                              │
          │────── Ciphertext ──────────────────>│
          │                                      │
          │                              Descriptografa
          │                              com chave privada
          │                                      │
          │                              Converte para
          │                              MAIÚSCULAS
          │                                      │
          │                              Criptografa com
          │                              chave pública
          │                              de Alice
          │                                      │
          │<────── Ciphertext da resposta ──────│
          │                                      │
          │  Descriptografa com                 │
          │  chave privada de Alice             │
          │       ↓                              │
          │  Resposta final                     │
          │                                      │
```

## 🧩 Etapas da comunicação

### 1. Alice gera suas chaves

Alice gera:

```text
Chave pública de Alice
Chave privada de Alice
```

A chave privada permanece somente com Alice.

---

### 2. Bob gera suas chaves

Bob também gera:

```text
Chave pública de Bob
Chave privada de Bob
```

Sua chave privada permanece somente com Bob.

---

### 3. Estabelecimento da conexão TCP

Alice conecta-se ao servidor de Bob utilizando:

```text
TCP
Porta: 1300
```

---

### 4. Troca das chaves públicas

Alice envia sua chave pública para Bob.

```text
Alice ──────── Chave pública ────────> Bob
```

Bob então envia sua chave pública para Alice.

```text
Alice <─────── Chave pública ──────── Bob
```

As chaves públicas são enviadas **em texto puro**, pois não existe necessidade de mantê-las secretas.

As chaves privadas nunca são transmitidas pela rede.

---

### 5. Alice envia uma mensagem

Alice digita a mensagem diretamente no terminal:

```text
Alice: Hello Bob!
```

A aplicação transforma a mensagem em um número e realiza a criptografia utilizando a chave pública de Bob.

```text
Mensagem
   ↓
Chave pública de Bob
   ↓
RSA
   ↓
Ciphertext
```

---

### 6. Alice envia o ciphertext

O resultado da criptografia é enviado através da conexão TCP:

```text
Alice ─────── Ciphertext ───────> Bob
```

Quem observar a comunicação de rede não verá diretamente a mensagem original nesse campo, mas sim o valor cifrado.

---

### 7. Bob descriptografa

Bob recebe o ciphertext e utiliza sua **chave privada**:

```text
Ciphertext
    ↓
Chave privada de Bob
    ↓
RSA
    ↓
Mensagem original
```

Bob então consegue recuperar a mensagem enviada por Alice.

---

### 8. Bob processa a mensagem

Assim como no código TCP original da atividade, Bob transforma a mensagem para letras maiúsculas:

```text
Hello Bob!
```

torna-se:

```text
HELLO BOB!
```

---

### 9. Bob responde

Bob utiliza a **chave pública de Alice** para criptografar a resposta:

```text
Resposta
   ↓
Chave pública de Alice
   ↓
RSA
   ↓
Ciphertext
```

E envia o resultado para Alice:

```text
Alice <────── Ciphertext ────── Bob
```

---

### 10. Alice descriptografa

Alice utiliza sua chave privada para recuperar a resposta:

```text
Ciphertext
    ↓
Chave privada de Alice
    ↓
RSA
    ↓
Resposta original
```

O resultado é apresentado no terminal:

```text
Bob: HELLO BOB!
```

---

# 🖥️ Interface da demonstração

A aplicação foi organizada como uma sequência interativa de passos.

Cada máquina controla suas próprias ações utilizando **Enter**, permitindo que o procedimento seja apresentado com calma durante a gravação.

Exemplo:

```text
[ALICE] PASSO 4 — Envio da chave pública

▶ Pressione ENTER para enviar
  a chave pública de Alice ao Bob.
```

Enquanto Alice aguarda uma ação de Bob, o terminal indica:

```text
⏳ Aguardando Bob enviar sua chave pública...
```

Quando Bob realiza a ação correspondente, Alice recebe os dados e continua a execução.

Esse comportamento permite acompanhar visualmente o fluxo da comunicação sem que todas as operações aconteçam imediatamente.

---

# 📁 Arquivos

```text
├── client.py
├── server.py
├── roteiro_demonstracao.md
└── README.md
```

### `client.py`

Implementação do **cliente TCP**, representando Alice.

Responsável por:

* gerar as chaves de Alice;
* conectar-se ao servidor;
* enviar a chave pública;
* receber a chave pública de Bob;
* solicitar a mensagem;
* criptografar a mensagem;
* enviar o ciphertext;
* receber a resposta cifrada;
* descriptografar a resposta;
* apresentar o resultado;
* calcular o RTT.

### `server.py`

Implementação do **servidor TCP**, representando Bob.

Responsável por:

* gerar as chaves de Bob;
* aguardar a conexão;
* receber a chave pública de Alice;
* enviar a chave pública de Bob;
* receber o ciphertext;
* descriptografar a mensagem;
* converter a mensagem para maiúsculas;
* criptografar a resposta;
* enviar a resposta cifrada.

### `roteiro_demonstracao.md`

Contém o roteiro utilizado para executar e apresentar a atividade, incluindo a sequência recomendada de execução e observação no Wireshark.

### `README.md`

Documento atual com a explicação do RSA, funcionamento da aplicação e instruções de execução.

---

# ▶️ Execução

## Máquina do Bob

### 1. Descubra o endereço IP

No Windows:

```bash
ipconfig
```

No Linux:

```bash
ip addr
```

Identifique o endereço IPv4 da interface de rede utilizada.

### 2. Execute o servidor

```bash
python server.py
```

O servidor ficará aguardando a conexão de Alice.

### 3. Firewall

Se necessário, permita conexões TCP na porta:

```text
1300
```

---

## Máquina da Alice

### 1. Configure o endereço de Bob

Abra `client.py` e altere:

```python
SERVER_NAME = "192.168.78.169"
```

para o IPv4 da máquina de Bob.

### 2. Execute o cliente

```bash
python client.py
```

As duas máquinas precisam estar na mesma rede ou possuir roteamento entre elas.

---

# 🔎 Análise com Wireshark

A comunicação pode ser observada utilizando o **Wireshark**.

### 1. Inicie o Wireshark

Selecione a interface de rede utilizada pela comunicação.

### 2. Utilize o filtro

```text
tcp.port == 1300
```

### 3. Execute a aplicação

Inicie primeiro:

```bash
python server.py
```

Depois:

```bash
python client.py
```

### 4. Observe a comunicação

É possível identificar:

* handshake TCP;
* chave pública de Alice;
* chave pública de Bob;
* mensagem criptografada;
* resposta criptografada;
* encerramento da conexão.

As chaves públicas podem ser observadas em texto puro porque são informações que podem ser compartilhadas.

Já as mensagens transmitidas após a criptografia aparecem como **ciphertexts**.

Para acompanhar a comunicação completa, selecione um pacote TCP e utilize:

**Follow → TCP Stream**

---

# 📊 RTT

O cliente mede o tempo total da atividade utilizando:

```python
time.perf_counter()
```

O cronômetro começa no início da execução do cliente e termina quando a resposta final é apresentada.

O resultado é exibido em segundos e milissegundos:

```text
RTT conforme a atividade: 0.123456 segundos
RTT: 123.456 ms
```

O valor pode variar de acordo com:

* desempenho das máquinas;
* tempo necessário para gerar as chaves RSA;
* processamento da criptografia;
* velocidade da rede;
* latência da conexão.

---

# ⚠️ Observação importante

Esta implementação é **didática**, desenvolvida para demonstrar o fluxo solicitado na atividade.

A criptografia utiliza RSA diretamente sobre os blocos, sem mecanismos de padding como **OAEP** ou **PKCS#1**.

Portanto, esta implementação **não deve ser utilizada como uma implementação de segurança real**.

Em aplicações reais, devem ser utilizados esquemas de criptografia padronizados e bibliotecas criptográficas apropriadas.

---

# 📚 Relação com o material

O material da atividade apresenta a geração das chaves RSA através da escolha de `p` e `q`, cálculo de `N` e `φ(N)`, escolha de `e` coprimo com `φ(N)` e cálculo de `d` como inverso multiplicativo de `e`. Também apresenta a utilização da chave pública para criptografia e da chave privada para descriptografia.

A implementação segue esse fluxo e o integra à comunicação TCP, permitindo observar tanto o funcionamento matemático do RSA quanto sua utilização prática na troca de mensagens entre Alice e Bob.
