import socket
import secrets
import math
import json
import sys


# ============================================================
# CONFIGURAÇÃO
# ============================================================

SERVER_PORT = 1300


# ============================================================
# CORES
# ============================================================

RESET = "\033[0m"
BOLD = "\033[1m"

CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"


def enable_windows_colors():

    if sys.platform == "win32":

        try:
            import os
            os.system("")

        except Exception:
            pass


# ============================================================
# INTERFACE
# ============================================================

def header():

    print("\n")
    print("=" * 72)

    print(
        f"{BOLD}{CYAN}"
        "               RSA + TCP — BOB"
        f"{RESET}"
    )

    print("=" * 72)


def step(number, title):

    print("\n")
    print("-" * 72)

    print(
        f"{BOLD}{CYAN}"
        f"[BOB] PASSO {number} — {title}"
        f"{RESET}"
    )

    print("-" * 72)


def action(message):

    print(
        f"\n{MAGENTA}{BOLD}"
        f"▶ {message}"
        f"{RESET}"
    )


def waiting(message):

    print(
        f"\n{YELLOW}{BOLD}"
        f"⏳ {message}"
        f"{RESET}"
    )


def received(message):

    print(
        f"\n{GREEN}{BOLD}"
        f"✓ {message}"
        f"{RESET}"
    )


def sent(message):

    print(
        f"\n{BLUE}{BOLD}"
        f"➜ {message}"
        f"{RESET}"
    )


# ============================================================
# RSA
# ============================================================

def is_probable_prime(n, rounds=40):

    if n < 2:
        return False

    small_primes = [
        2, 3, 5, 7, 11, 13,
        17, 19, 23, 29, 31, 37
    ]

    for p in small_primes:

        if n == p:
            return True

        if n % p == 0:
            return False

    d = n - 1
    s = 0

    while d % 2 == 0:

        s += 1
        d //= 2

    for _ in range(rounds):

        a = secrets.randbelow(
            n - 3
        ) + 2

        x = pow(
            a,
            d,
            n
        )

        if x == 1 or x == n - 1:
            continue

        for _ in range(s - 1):

            x = pow(
                x,
                2,
                n
            )

            if x == n - 1:
                break

        else:
            return False

    return True


def generate_prime(bits=2048):

    while True:

        candidate = secrets.randbits(
            bits
        )

        candidate |= (
            1 << (bits - 1)
        )

        candidate |= 1

        if is_probable_prime(candidate):

            return candidate


def generate_rsa_keys():

    while True:

        # 1. p e q
        p = generate_prime(2048)
        q = generate_prime(2048)

        if p == q:
            continue

        # 2. N
        n = p * q

        if n.bit_length() != 4096:
            continue

        # 3. φ(N)
        phi = (
            (p - 1) *
            (q - 1)
        )

        # 4. e
        e = 65537

        if math.gcd(
            e,
            phi
        ) != 1:
            continue

        # 5. d
        d = pow(
            e,
            -1,
            phi
        )

        public_key = (
            e,
            n
        )

        private_key = (
            d,
            n
        )

        return (
            public_key,
            private_key
        )


def encrypt(message, public_key):

    e, n = public_key

    data_bytes = message.encode(
        "utf-8"
    )

    message_number = int.from_bytes(
        data_bytes,
        byteorder="big"
    )

    cipher_number = pow(
        message_number,
        e,
        n
    )

    return str(cipher_number)


def decrypt(ciphertext, private_key):

    d, n = private_key

    cipher_number = int(
        ciphertext
    )

    message_number = pow(
        cipher_number,
        d,
        n
    )

    length = max(
        1,
        (
            message_number.bit_length()
            + 7
        ) // 8
    )

    data_bytes = message_number.to_bytes(
        length,
        byteorder="big"
    )

    return data_bytes.decode(
        "utf-8"
    )


# ============================================================
# TCP
# ============================================================

def send_json(sock, data):

    payload = (
        json.dumps(data)
        + "\n"
    ).encode("utf-8")

    sock.sendall(
        payload
    )


def recv_json(sock):

    buffer = b""

    while b"\n" not in buffer:

        chunk = sock.recv(
            4096
        )

        if not chunk:

            raise ConnectionError(
                "A conexão foi encerrada."
            )

        buffer += chunk

    line, _ = buffer.split(
        b"\n",
        1
    )

    return json.loads(
        line.decode("utf-8")
    )


# ============================================================
# PROGRAMA PRINCIPAL
# ============================================================

def main():

    enable_windows_colors()

    header()

    # ========================================================
    # PASSO 1
    # ========================================================

    step(
        1,
        "Inicialização"
    )

    print(
        "Bob será responsável por receber "
        "a comunicação de Alice."
    )

    input(
        f"\n{MAGENTA}"
        "Pressione ENTER para iniciar o servidor..."
        f"{RESET}"
    )

    # ========================================================
    # PASSO 2
    # ========================================================

    step(
        2,
        "Geração da chave de Bob"
    )

    action(
        "Pressione ENTER para gerar a chave de Bob."
    )

    input()

    print(
        f"{YELLOW}"
        "Gerando p e q e calculando as chaves RSA "
        "de 4096 bits..."
        f"{RESET}"
    )

    bob_public, bob_private = generate_rsa_keys()

    received(
        "Chaves de Bob geradas."
    )

    print(
        "\nChave pública:"
    )

    print(
        f"e = {bob_public[0]}"
    )

    print(
        f"N = {bob_public[1]}"
    )

    # ========================================================
    # PASSO 3
    # ========================================================

    step(
        3,
        "Aguardando Alice"
    )

    server_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    server_socket.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )

    server_socket.bind(
        (
            "",
            SERVER_PORT
        )
    )

    server_socket.listen(1)

    waiting(
        f"Aguardando Alice conectar "
        f"na porta {SERVER_PORT}..."
    )

    connection, address = (
        server_socket.accept()
    )

    received(
        f"Alice conectada: "
        f"{address[0]}:{address[1]}"
    )

    # ========================================================
    # PASSO 4
    # ========================================================

    step(
        4,
        "Recebimento da chave pública de Alice"
    )

    waiting(
        "Aguardando Alice enviar sua chave pública..."
    )

    alice_public_data = recv_json(
        connection
    )

    alice_public = (
        int(alice_public_data["e"]),
        int(alice_public_data["n"])
    )

    received(
        "Chave pública de Alice recebida."
    )

    print(
        f"\ne = {alice_public[0]}"
    )

    print(
        f"N = {alice_public[1]}"
    )

    # ========================================================
    # PASSO 5
    # ========================================================

    step(
        5,
        "Envio da chave pública de Bob"
    )

    action(
        "Pressione ENTER para enviar "
        "a chave pública de Bob para Alice."
    )

    input()

    send_json(
        connection,
        {
            "type": "public_key",
            "e": bob_public[0],
            "n": bob_public[1]
        }
    )

    sent(
        "Chave pública de Bob enviada para Alice."
    )

    print(
        "\nA chave privada continua somente com Bob."
    )

    # ========================================================
    # PASSO 6
    # ========================================================

    step(
        6,
        "Aguardando mensagem criptografada"
    )

    waiting(
        "Agora é a vez de Alice."
    )

    waiting(
        "Aguardando Alice enviar "
        "a mensagem criptografada..."
    )

    encrypted_message = recv_json(
        connection
    )["ciphertext"]

    received(
        "Mensagem criptografada recebida."
    )

    print(
        f"\n{GREEN}"
        "Ciphertext recebido:"
        f"{RESET}"
    )

    print(
        encrypted_message
    )

    # ========================================================
    # PASSO 7
    # ========================================================

    step(
        7,
        "Descriptografia da mensagem"
    )

    action(
        "Pressione ENTER para descriptografar "
        "a mensagem usando a chave privada de Bob."
    )

    input()

    message = decrypt(
        encrypted_message,
        bob_private
    )

    print(
        f"\n{GREEN}{BOLD}"
        "Bob recebeu:"
        f"{RESET}"
    )

    print(
        f"{CYAN}"
        f"Alice: {message}"
        f"{RESET}"
    )

    # ========================================================
    # PASSO 8
    # ========================================================

    step(
        8,
        "Processamento da mensagem"
    )

    action(
        "Pressione ENTER para converter "
        "a mensagem para letras maiúsculas."
    )

    input()

    response = message.upper()

    print(
        f"\n{GREEN}"
        "Mensagem processada:"
        f"{RESET}"
    )

    print(
        response
    )

    # ========================================================
    # PASSO 9
    # ========================================================

    step(
        9,
        "Criptografia da resposta"
    )

    action(
        "Pressione ENTER para criptografar "
        "a resposta usando a chave pública de Alice."
    )

    input()

    encrypted_response = encrypt(
        response,
        alice_public
    )

    print(
        f"\n{GREEN}"
        "Ciphertext da resposta:"
        f"{RESET}"
    )

    print(
        encrypted_response
    )

    # ========================================================
    # PASSO 10
    # ========================================================

    step(
        10,
        "Envio da resposta"
    )

    action(
        "Pressione ENTER para enviar "
        "a resposta criptografada para Alice."
    )

    input()

    send_json(
        connection,
        {
            "type": "encrypted_response",
            "ciphertext": encrypted_response
        }
    )

    sent(
        "Resposta criptografada enviada para Alice."
    )

    waiting(
        "Aguardando Alice receber e descriptografar a resposta..."
    )

    # ========================================================
    # FINALIZAÇÃO
    # ========================================================

    input(
        f"\n{MAGENTA}"
        "Pressione ENTER para encerrar a conexão..."
        f"{RESET}"
    )

    connection.close()
    server_socket.close()

    print(
        f"\n{GREEN}{BOLD}"
        "Bob encerrou a comunicação."
        f"{RESET}"
    )


if __name__ == "__main__":
    main()