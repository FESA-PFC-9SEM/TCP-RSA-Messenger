import socket
import secrets
import math
import json
import time
import sys


# ============================================================
# CONFIGURAÇÃO
# ============================================================

SERVER_NAME = "10.1.70.16"  # IP da máquina de Bob
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
    """
    Tenta habilitar cores ANSI no Windows.
    """

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
        "              RSA + TCP — ALICE"
        f"{RESET}"
    )
    print("=" * 72)


def step(number, title):
    print("\n")
    print("-" * 72)
    print(
        f"{BOLD}{CYAN}"
        f"[ALICE] PASSO {number} — {title}"
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


def data(title, value):
    print(
        f"\n{GREEN}"
        f"{title}:"
        f"{RESET}"
    )
    print(value)


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

        # 1. Escolher p e q
        p = generate_prime(2048)
        q = generate_prime(2048)

        if p == q:
            continue

        # 2. N = p * q
        n = p * q

        if n.bit_length() != 4096:
            continue

        # 3. φ(N)
        phi = (
            (p - 1) *
            (q - 1)
        )

        # 4. Escolher e
        e = 65537

        if math.gcd(
            e,
            phi
        ) != 1:
            continue

        # 5. Encontrar d
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

    if message_number >= n:

        raise ValueError(
            "Mensagem grande demais "
            "para esta demonstração RSA."
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

    # O RTT começa aqui, conforme a atividade.
    start_time = time.perf_counter()

    # ========================================================
    # PASSO 1
    # ========================================================

    step(
        1,
        "Inicialização"
    )

    print(
        "Alice será responsável por iniciar "
        "a comunicação e enviar a primeira mensagem."
    )

    input(
        f"\n{MAGENTA}"
        "Pressione ENTER para continuar..."
        f"{RESET}"
    )

    # ========================================================
    # PASSO 2
    # ========================================================

    step(
        2,
        "Geração da chave de Alice"
    )

    action(
        "Pressione ENTER para gerar a chave de Alice."
    )

    input()

    print(
        f"{YELLOW}"
        "Gerando p e q e calculando as chaves RSA "
        "de 4096 bits..."
        f"{RESET}"
    )

    alice_public, alice_private = generate_rsa_keys()

    received(
        "Chaves de Alice geradas."
    )

    print(
        "\nChave pública:"
    )

    print(
        f"e = {alice_public[0]}"
    )

    print(
        f"N = {alice_public[1]}"
    )

    # ========================================================
    # PASSO 3
    # ========================================================

    step(
        3,
        "Conexão com Bob"
    )

    action(
        "Pressione ENTER para conectar ao Bob."
    )

    input()

    client_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    waiting(
        f"Conectando a {SERVER_NAME}:{SERVER_PORT}..."
    )

    client_socket.connect(
        (
            SERVER_NAME,
            SERVER_PORT
        )
    )

    received(
        "Conexão TCP estabelecida com Bob."
    )

    # ========================================================
    # PASSO 4
    # ========================================================

    step(
        4,
        "Envio da chave pública de Alice"
    )

    action(
        "Pressione ENTER para enviar "
        "a chave pública de Alice ao Bob."
    )

    input()

    send_json(
        client_socket,
        {
            "type": "public_key",
            "e": alice_public[0],
            "n": alice_public[1]
        }
    )

    sent(
        "Chave pública de Alice enviada ao Bob."
    )

    print(
        "\n"
        "A chave privada NÃO foi enviada."
    )

    # ========================================================
    # PASSO 5
    # ========================================================

    step(
        5,
        "Recebimento da chave pública de Bob"
    )

    waiting(
        "Agora é a vez de Bob."
    )

    waiting(
        "Aguardando Bob enviar sua chave pública..."
    )

    bob_public_data = recv_json(
        client_socket
    )

    bob_public = (
        int(bob_public_data["e"]),
        int(bob_public_data["n"])
    )

    received(
        "Chave pública de Bob recebida."
    )

    print(
        f"\ne = {bob_public[0]}"
    )

    print(
        f"N = {bob_public[1]}"
    )

    input(
        f"\n{MAGENTA}"
        "Pressione ENTER para continuar..."
        f"{RESET}"
    )

    # ========================================================
    # PASSO 6
    # ========================================================

    step(
        6,
        "Preparação da mensagem"
    )

    print(
        "Alice possui agora a chave pública de Bob."
    )

    print(
        "Ela poderá utilizá-la para criptografar "
        "uma mensagem que somente Bob poderá descriptografar."
    )

    action(
        "Digite a mensagem e pressione ENTER para enviar."
    )

    message = input(
        f"{CYAN}Alice: {RESET}"
    )

    # ========================================================
    # PASSO 7
    # ========================================================

    step(
        7,
        "Criptografia da mensagem"
    )

    action(
        "Pressione ENTER para criptografar "
        "a mensagem com a chave pública de Bob."
    )

    input()

    encrypted_message = encrypt(
        message,
        bob_public
    )

    print(
        f"\n{GREEN}"
        "Ciphertext gerado:"
        f"{RESET}"
    )

    print(
        encrypted_message
    )

    # ========================================================
    # PASSO 8
    # ========================================================

    step(
        8,
        "Envio da mensagem criptografada"
    )

    action(
        "Pressione ENTER para enviar "
        "a mensagem criptografada ao Bob."
    )

    input()

    send_json(
        client_socket,
        {
            "type": "encrypted_message",
            "ciphertext": encrypted_message
        }
    )

    sent(
        "Mensagem criptografada enviada ao Bob."
    )

    # ========================================================
    # PASSO 9
    # ========================================================

    step(
        9,
        "Aguardando resposta de Bob"
    )

    waiting(
        "Agora é a vez de Bob."
    )

    waiting(
        "Aguardando Bob descriptografar, "
        "processar e responder..."
    )

    encrypted_response = recv_json(
        client_socket
    )["ciphertext"]

    received(
        "Resposta criptografada recebida de Bob."
    )

    print(
        f"\n{GREEN}"
        "Ciphertext recebido:"
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
        "Descriptografia da resposta"
    )

    action(
        "Pressione ENTER para descriptografar "
        "a resposta usando a chave privada de Alice."
    )

    input()

    final_message = decrypt(
        encrypted_response,
        alice_private
    )

    print(
        f"\n{GREEN}{BOLD}"
        "Alice recebeu:"
        f"{RESET}"
    )

    print(
        f"{CYAN}"
        f"Bob: {final_message}"
        f"{RESET}"
    )

    # ========================================================
    # FINALIZAÇÃO
    # ========================================================

    end_time = time.perf_counter()

    elapsed = (
        end_time -
        start_time
    )

    print("\n")
    print("=" * 72)

    print(
        f"{GREEN}{BOLD}"
        "COMUNICAÇÃO FINALIZADA"
        f"{RESET}"
    )

    print(
        f"RTT conforme a atividade: "
        f"{elapsed:.6f} segundos"
    )

    print(
        f"RTT: "
        f"{elapsed * 1000:.3f} ms"
    )

    print("=" * 72)

    client_socket.close()


if __name__ == "__main__":
    main()