# Importações necessárias para o código
import re  
from database import cursor, conn  

class Usuario:
    """Classe que representa um usuário do sistema de saúde e nutrição."""
    
    def __init__(self, email):
        """Inicializa um usuário com seu e-mail.
        
        Args:
            email (str): Endereço de e-mail do usuário.
        """
        self.email = email

    @staticmethod
    def validar_email(email):
        """Valida se um e-mail tem formato válido usando regex.
        
        Args:
            email (str): Endereço de e-mail a ser validado.
            
        Returns:
            bool: True se o e-mail for válido, False caso contrário.
        """
        padrao = r'^[\w\.-]+@[\w\.-]+\.\w+$'  # Padrão básico para e-mails
        return re.match(padrao, email) is not None

    @staticmethod
    def calcular_imc(peso, altura):
        """Calcula o IMC (Índice de Massa Corporal) com base no peso e altura.
        
        Args:
            peso (float): Peso do usuário em quilogramas.
            altura (float): Altura do usuário em metros.
            
        Returns:
            float: Valor do IMC.
        """
        return round(peso / (altura ** 2), 2)  # Arredonda para 2 casas decimais

    @staticmethod
    def escolher_dieta():
        """Permite ao usuário escolher uma dieta entre as opções disponíveis e mostra uma descrição breve."""
        opcoes = {
            "Low carb": "Dieta com baixo consumo de carboidratos para ajudar na perda de peso e controle glicêmico.",
            "Cetogênica": "Dieta rica em gorduras e pobre em carboidratos, que induz o corpo a queimar gordura como energia.",
            "Hiperproteica": "Dieta focada no alto consumo de proteínas para ganho muscular e recuperação.",
            "Bulking": "Dieta para ganho de massa muscular, com aumento calórico e balanço de macronutrientes."
        }

        nomes = list(opcoes.keys())

        while True:
            print("\nEscolha sua dieta:")
            for i, dieta in enumerate(nomes, 1):
                print(f"{i}. {dieta}")
            escolha = input("Digite o número da dieta: ")
            if escolha.isdigit() and 1 <= int(escolha) <= len(nomes):
                dieta_escolhida = nomes[int(escolha) - 1]
                print(f"\nVocê escolheu '{dieta_escolhida}':")
                print(opcoes[dieta_escolhida])
                confirmar = input("Deseja confirmar essa escolha? (s/n): ").strip().lower()
                if confirmar == 's':
                    return dieta_escolhida
                else:
                    print("Ok, escolha novamente.")
            else:
                print("❌ Opção inválida! Tente novamente.")
                continue

    @staticmethod
    def registrar():
        """Registra um novo usuário no sistema, coletando e validando todos os dados necessários."""
        print("\n=== Cadastro de Usuário ===")
        # Validação do e-mail
        while True:
            email = input("E-mail: ").strip()
            if not Usuario.validar_email(email):
                print("❌ E-mail inválido!")
                continue
            # Verifica se e-mail já existe
            cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
            if cursor.fetchone():
                print("❌ E-mail já está cadastrado!")
                continue
            break

        # Validação da senha (não pode ser vazia)
        while True:
            senha = input("Senha: ").strip()
            if senha == "":
                print("❌ A senha não pode ser vazia!")
            else:
                break

        # Validação de peso e altura (devem ser números positivos)
        try:
            peso = float(input("Peso (kg): "))
            altura = float(input("Altura (m): "))
            if peso <= 0 or altura <= 0:
                print("❌ Peso e altura devem ser maiores que zero.")
                return
        except ValueError:
            print("❌ Digite apenas números válidos para peso e altura.")
            return

        # Validação do sexo (apenas M ou F)
        sexo = input("Sexo (M/F): ").strip().upper()
        if sexo not in ['M', 'F']:
            print("❌ Sexo inválido! Use apenas 'M' ou 'F'.")
            return

        # Seleção de dieta e cálculo do IMC
        dieta = Usuario.escolher_dieta()
        imc = Usuario.calcular_imc(peso, altura)

        # Configuração de pergunta de segurança para recuperação
        pergunta, resposta = escolher_pergunta_seguranca()

        # Insere todos os dados no banco de dados
        cursor.execute('''
            INSERT INTO usuarios (email, senha, peso, altura, sexo, dieta, imc, pergunta_seguranca, resposta_seguranca)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (email, senha, peso, altura, sexo, dieta, imc, pergunta, resposta))
        conn.commit()
        print(f"✅ Usuário cadastrado com sucesso!")
        explicar_imc(imc)

        # Pergunta sobre conhecimento prévio em nutrição
        resposta_conhecimento = input("Você possui conhecimento prévio em nutrição? (s/n): ").strip().lower()

        if resposta_conhecimento == "s":
            conhecimento = "Sim"
        elif resposta_conhecimento == "n":
            conhecimento = "Não"
        else:
            print("❌ Responda apenas com 's' ou 'n'.")
            return
        print("\n" + "="*50)
        adicionar_descricao_corporal(email)
        
    @staticmethod
    def recuperar_senha():
        """Permite ao usuário recuperar sua senha respondendo à pergunta de segurança."""
        print("\n🔐 Recuperação de Senha")
        email = input("Digite seu e-mail cadastrado: ").strip()
        cursor.execute("SELECT pergunta_seguranca, resposta_seguranca, senha FROM usuarios WHERE email = ?", (email,))
        resultado = cursor.fetchone()
        if not resultado:
            print("❌ E-mail não encontrado!")
            return

        pergunta, resposta_correta, senha = resultado
        print(f"Pergunta de segurança: {pergunta}")
        resposta_usuario = input("Sua resposta: ").strip().lower()
        if resposta_usuario == resposta_correta:
            print(f"✅ Sua senha é: {senha}")
        else:
            print("❌ Resposta incorreta!")

    @staticmethod
    def login():
        """Realiza o login do usuário no sistema.
        
        Returns:
            Usuario: Instância do usuário se o login for bem-sucedido, None caso contrário.
        """
        print("\n=== Login ===")
        while True:
            email = input("E-mail: ").strip()
            cursor.execute("SELECT senha FROM usuarios WHERE email = ?", (email,))
            resultado = cursor.fetchone()
            if not resultado:
                print("❌ E-mail não encontrado. Tente novamente.")
                return None

            senha_digitada = input("Senha: ").strip()
            if senha_digitada != resultado[0]:
                print("❌ Senha incorreta.")
                escolha = input("Deseja recuperar sua senha? (s/n): ").strip().lower()
                if escolha == 's':
                    Usuario.recuperar_senha()
                else:
                    print("Tente novamente.")
                continue

            print("✅ Login realizado com sucesso!")
            return Usuario(email)  # Retorna uma instância do usuário

    def editar_meus_dados(self):
        """Permite ao usuário editar seus dados pessoais (peso, altura, dieta) e recalcula o IMC."""
        print("\n=== Editar Meus Dados ===")
        try:
            novo_peso = float(input("Novo peso (kg): "))
            nova_altura = float(input("Nova altura (m): "))
            if novo_peso <= 0 or nova_altura <= 0:
                print("❌ Peso e altura devem ser maiores que zero.")
                return
        except ValueError:
            print("❌ Digite valores numéricos válidos para peso e altura.")
            return

        nova_dieta = Usuario.escolher_dieta()
        novo_imc = Usuario.calcular_imc(novo_peso, nova_altura)

        # Atualiza os dados no banco de dados
        cursor.execute('''
            UPDATE usuarios
            SET peso = ?, altura = ?, dieta = ?, imc = ?
            WHERE email = ?
        ''', (novo_peso, nova_altura, nova_dieta, novo_imc, self.email))
        conn.commit()

        print("✅ Dados atualizados com sucesso!")
        print(f"📊 Novo IMC: {novo_imc}")

class Adm(Usuario):
    """Classe que representa um administrador do sistema, com funcionalidades adicionais."""
    
    @staticmethod
    def ver_usuarios():
        """Exibe todos os usuários cadastrados no sistema com seus dados principais."""
        print("\n=== Usuários Cadastrados ===")
        cursor.execute("SELECT email, peso, altura, sexo, conhecimento, dieta, imc FROM usuarios")
        usuarios = cursor.fetchall()
        if usuarios:
            for u in usuarios:
                print(f"- Email: {u[0]} | Peso: {u[1]} kg | Altura: {u[2]} m | Sexo: {u[3]} | Conhecimento: {u[4]} | Dieta: {u[5]} | IMC: {u[6]}")
        else:
            print("❌ Nenhum usuário cadastrado.")

            # Descrição do Usuário
# Dicionário para guardar as descrições dos usuários
descricoes_usuarios = {}

def adicionar_descricao_corporal(email_usuario):
    """Permite ao usuário adicionar/atualizar como se sente com o corpo"""
    print("\n=== COMO VOCÊ SE SENTE COM SEU CORPO? ===")
    print("💭 Descreva como você está se sentindo atualmente com seu corpo")
    print("💡 Exemplos: 'Me sinto bem, mas quero melhorar', 'Não estou satisfeito', etc.")
    
    # Coleta nova descrição
    nova_descricao = input("\nSua descrição: ").strip()
    
    if nova_descricao:
        descricoes_usuarios[email_usuario] = nova_descricao
        print("\n✅ Descrição salva com sucesso!")
        print("💪 Continue trabalhando em seus objetivos!")
    else:
        print("❌ Descrição não pode estar vazia.")

# Pergunta de segurança melhorada
def escolher_pergunta_seguranca():
    """Função melhorada com mais perguntas de segurança"""
    print("\nEscolha uma pergunta de segurança:")
    
    perguntas = [
        "Qual é o nome da sua mãe?",
        "Em que cidade você nasceu?",
        "Qual é o nome do seu pai?",
        "Em que dia você nasceu? (só o dia, ex: 15)",
        "Qual foi o nome da sua primeira escola?",
        "Em que mês você nasceu?",
        "Qual é o nome da rua onde você cresceu?",
        "Qual é o seu sobrenome de família da sua mãe?"
    ]
    
    # Mostra todas as perguntas
    for i, pergunta in enumerate(perguntas, 1):
        print(f"{i:2}. {pergunta}")
    
    # Valida a escolha
    while True:
        try:
            escolha = int(input(f"\nDigite o número da pergunta (1-{len(perguntas)}): "))
            if 1 <= escolha <= len(perguntas):
                pergunta_escolhida = perguntas[escolha - 1]
                break
            else:
                print(f"❌ Escolha um número entre 1 e {len(perguntas)}!")
        except ValueError:
            print("❌ Digite apenas números!")
    
    # Coleta a resposta
    print(f"\nPergunta escolhida: {pergunta_escolhida}")
    while True:
        resposta = input("Digite a resposta para a pergunta de segurança: ").strip().lower()
        if resposta:
            break
        print("❌ A resposta não pode estar vazia!")
    
    return pergunta_escolhida, resposta

# Novo IMC explicado
def explicar_imc(imc):
    """Explica o que significa o valor do IMC calculado"""
    
    if imc < 18.5:
        categoria = "Abaixo do peso"
        emoji = "⚠️"
        dica = "Considere consultar um nutricionista para ganhar peso de forma saudável."
    elif 18.5 <= imc < 25:
        categoria = "Peso normal"
        emoji = "✅"
        dica = "Parabéns! Continue mantendo seus hábitos saudáveis."
    elif 25 <= imc < 30:
        categoria = "Sobrepeso"
        emoji = "⚠️"
        dica = "Uma alimentação balanceada e exercícios podem ajudar."
    elif 30 <= imc < 35:
        categoria = "Obesidade grau I"
        emoji = "🔴"
        dica = "Recomendamos acompanhamento médico e nutricional."
    elif 35 <= imc < 40:
        categoria = "Obesidade grau II"
        emoji = "🔴"
        dica = "É importante buscar orientação médica especializada."
    else:
        categoria = "Obesidade grau III"
        emoji = "🔴"
        dica = "Procure acompanhamento médico urgente."
    
    print(f"\n📊 RESULTADO DO SEU IMC:")
    print(f"{emoji} IMC: {imc:.1f}")
    print(f"{emoji} Classificação: {categoria}")
    print(f"💡 {dica}")
    
    return categoria

# Função melhorada para calcular e explicar o IMC
def calcular_e_explicar_imc(peso, altura):
    """Calcula o IMC e já explica o resultado"""
    imc = peso / (altura ** 2)
    categoria = explicar_imc(imc)
    return imc, categoria

# Exemplo de uso:
if __name__ == "__main__":
    # Teste
    peso = 70
    altura = 1.75
    imc, categoria = calcular_e_explicar_imc(peso, altura)