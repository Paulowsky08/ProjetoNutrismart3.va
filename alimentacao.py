# Importações necessárias para o código
import random
from datetime import datetime, date
from database import cursor, conn  

class Comida:
    """Classe principal para gerenciar operações relacionadas a alimentos"""
    
    def __init__(self, email_usuario):
        """
        Inicializa a instância da classe Comida
        
        Args:
            email_usuario (str): Email do usuário que será associado às operações
        """
        self.email_usuario = email_usuario
    
    def registrar_refeicao(self, alimento, quantidade):
        """
        Registra uma refeição no banco de dados
        
        Args:
            alimento (str): Nome do alimento a ser registrado
            quantidade (float): Quantidade consumida em gramas
            
        Returns:
            tuple: (bool, str) Indicando sucesso/falha e mensagem correspondente
        """
        try:
            # Verifica se o alimento existe no banco de dados
            cursor.execute("SELECT calorias FROM alimentos WHERE nome = ?", (alimento,))
            resultado = cursor.fetchone()
            if not resultado:
                return False, "Alimento não cadastrado"
            
            # Calcula as calorias consumidas com base na quantidade (em gramas)
            calorias = (quantidade / 100) * resultado[0]
            
            # Insere a refeição no banco de dados com data/hora atual
            data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute('''
                INSERT INTO refeicoes (email_usuario, alimento, quantidade_gramas, calorias, data)
                VALUES (?, ?, ?, ?, ?)
            ''', (self.email_usuario, alimento, quantidade, calorias, data))
            conn.commit()
            return True, "Refeição registrada com sucesso"
            
        except Exception as e:
            # Trata erros durante o registro
            print(f"Erro ao registrar refeição: {e}")
            return False, f"Erro ao registrar: {str(e)}"
        
    # Ver refeições registradas

    def verificar_registro_diario(self):
        hoje = datetime.now().strftime("%Y-%m-%d")
        
        # Verifica refeições registradas no dia
        cursor.execute('''
            SELECT COUNT(*) FROM refeicoes 
            WHERE email_usuario = ? AND data LIKE ?
        ''', (self.email_usuario, f"{hoje}%"))
        refeicoes_count = cursor.fetchone()[0]
        
        # Verifica registro de consumo de água no dia
        cursor.execute('''
            SELECT COUNT(*) FROM consumos_agua 
            WHERE email_usuario = ? AND data LIKE ?
        ''', (self.email_usuario, f"{hoje}%"))
        agua_count = cursor.fetchone()[0]
        
        # Mensagens de aviso
        if refeicoes_count == 0:
            print("⚠️ Atenção: Você não registrou nenhuma refeição hoje. Sem esses dados, o app não consegue monitorar sua alimentação, calcular nutrientes ou dar dicas personalizadas.")
            
        if agua_count == 0:
            print("⚠️ Lembrete: Você não registrou o consumo de água hoje. A hidratação é fundamental para evitar dores de cabeça, fadiga e outros problemas de saúde.")

        if refeicoes_count > 0 and agua_count > 0:
            print("✅ Ótimo! Você registrou suas refeições e consumo de água hoje.")

        # Ver refeições

    def ver_refeicoes(self):
        cursor.execute('''
            SELECT alimento, quantidade_gramas, data
            FROM refeicoes
            WHERE email_usuario = ?
            ORDER BY data DESC
        ''', (self.email_usuario,))
        
        refeicoes = cursor.fetchall()

        print("\n=== Suas Refeições Registradas ===")
        if not refeicoes:
            print("Nenhuma refeição registrada ainda.\n")
            print("💡 Lembre-se: não registrar suas refeições pode prejudicar o acompanhamento da sua alimentação.")
            print("💧 Além disso, manter-se hidratado é essencial para o bom funcionamento do organismo.\n")
        else:
            for alimento, quantidade, data in refeicoes:
                print(f"{data} - {alimento} ({quantidade}g)")
            print("\n✅ Ótimo! Registrar suas refeições ajuda a manter uma alimentação equilibrada.")
            print("💧 Dica: beba água regularmente para manter-se hidratado e saudável.\n")


    def ver_alimentos_recomendados(self):
        """
        Exibe 4 alimentos aleatórios recomendados com base na dieta do usuário
        
        Obtém a dieta do usuário do banco de dados e recomenda alimentos adequados
        """
        # Obtém a dieta do usuário do banco de dados
        cursor.execute("SELECT dieta FROM usuarios WHERE email = ?", (self.email_usuario,))
        resultado = cursor.fetchone()
        if not resultado:
            print("❌ Usuário não encontrado.")
            return

        dieta_usuario = resultado[0]

        # Dicionário com alimentos recomendados para cada tipo de dieta
        recomendacoes = {
            "Low carb": [
                "Ovos", "Abacate", "Peixes", "Nozes", "Couve-flor", "Espinafre", "Brócolis", "Azeite de oliva",
                "Amêndoas", "Queijo", "Cogumelos", "Carne bovina", "Salmão", "Aspargos", "Alface", "Cenoura",
                "Tomate", "Pepino", "Pimentão", "Berinjela", "Abobrinha", "Castanha-do-pará", "Aipo", "Azeitona",
                "Sementes de chia", "Sementes de linhaça", "Coco", "Framboesa", "Morango", "Repolho", "Alcachofra",
                "Cebola", "Algo", "Rúcula", "Manjericão", "Salsinha", "Endívia", "Alcaparras", "Pimenta", "Ervilha-torta",
                "Limão", "Laranja", "Carne de porco", "Frango", "Iogurte natural", "Ricota", "Chá verde", "Água com gás",
                "Vinagre de maçã", "Café"
            ],
            "Cetogênica": [
                "Bacon", "Queijo cheddar", "Carne de cordeiro", "Manteiga", "Nata", "Óleo de coco", "Salmão selvagem",
                "Ovos caipiras", "Espinafre", "Couve", "Brócolis", "Couve-flor", "Abacate", "Nozes", "Castanhas",
                "Sementes de abóbora", "Azeitonas", "Chá de hortelã", "Café sem açúcar", "Queijo parmesão",
                "Frango caipira", "Carne moída", "Camarão", "Atum", "Aspargos", "Abobrinha", "Cogumelos", "Algo",
                "Cebola", "Pimenta", "Ervas frescas", "Alface", "Rúcula", "Salsa", "Manjericão", "Nata fresca",
                "Creme de leite", "Óleo MCT", "Chá de camomila", "Queijo mozzarella", "Carne bovina", "Carne de porco",
                "Peixes gordurosos", "Sementes de chia", "Sementes de linhaça", "Abacate", "Limão", "Vinagre de maçã",
                "Água mineral"
            ],
            "Hiperproteica": [
                "Peito de frango", "Clara de ovo", "Carne magra", "Peixes", "Queijo cottage", "Iogurte grego",
                "Atum", "Carne bovina magra", "Salmão", "Ovos inteiros", "Tofu", "Tempeh", "Lentilhas", "Feijão",
                "Quinoa", "Amêndoas", "Nozes", "Sementes de abóbora", "Camarão", "Proteína isolada", "Leite desnatado",
                "Ricota", "Brócolis", "Couve-flor", "Espinafre", "Cenoura", "Abobrinha", "Alface", "Tomate",
                "Pepino", "Pimentão", "Azeite de oliva", "Chá verde", "Água"
            ],
            "Bulking": [
                "Arroz integral", "Batata doce", "Aveia", "Massas integrais", "Carne vermelha", "Peito de frango",
                "Ovos", "Salmão", "Atum", "Quinoa", "Feijão", "Grão-de-bico", "Lentilha", "Leite integral",
                "Iogurte natural", "Queijo", "Nozes", "Amêndoas", "Castanha-do-pará", "Abacate", "Banana",
                "Morangos", "Espinafre", "Brócolis", "Cenoura", "Abobrinha", "Tomate", "Pepino", "Pimentão",
                "Azeite de oliva", "Manteiga de amendoim", "Chá verde", "Água", "Mel", "Chocolate amargo",
                "Batata inglesa", "Milho", "Pão integral", "Sementes de chia", "Sementes de linhaça", "Ervilha"
            ]
        }

        # Obtém a lista de alimentos recomendados para a dieta do usuário
        alimentos_recomendados = recomendacoes.get(dieta_usuario, [])

        if not alimentos_recomendados:
            print("❌ Nenhum alimento recomendado encontrado para esta dieta.")
            return

        # Seleciona 4 alimentos aleatórios da lista
        aleatorios = random.sample(alimentos_recomendados, k=4)

        # Exibe os alimentos recomendados
        print(f"\n🍽️ 4 Alimentos aleatórios recomendados para a dieta {dieta_usuario}:")
        for alimento in aleatorios:
            print(f"- {alimento}")

    def ranking_alimentos_mais_consumidos(self):
        """
        Exibe um ranking dos 10 alimentos mais consumidos pelo usuário (em gramas)
        
        Mostra os alimentos ordenados pela quantidade total consumida
        """
        print("\n🏆 Ranking dos alimentos mais consumidos:")
        cursor.execute('''
            SELECT alimento, SUM(quantidade_gramas) as total_gramas
            FROM refeicoes
            WHERE email_usuario = ?
            GROUP BY alimento
            ORDER BY total_gramas DESC
            LIMIT 10
        ''', (self.email_usuario,))
        ranking = cursor.fetchall()

        if not ranking:
            print("❌ Nenhuma refeição registrada para gerar o ranking.")
            return

        # Exibe o ranking formatado
        for i, (alimento, total) in enumerate(ranking, 1):
            print(f"{i}. {alimento.capitalize()} - {total:.2f} g")


class Adm_alimentar(Comida):
    """Classe para administração de alimentos (herda de Comida)"""
    
    @staticmethod
    def cadastrar_alimento():
        """
        Cadastra um novo alimento no banco de dados
        
        Solicita nome e calorias do alimento e insere no sistema
        """
        print("\n=== Inserir novo alimento ===")
        nome = input("Nome do alimento: ").strip().lower()
        try:
            calorias = float(input("Calorias por 100g: "))
            if calorias <= 0:
                print("❌ Calorias devem ser maior que zero.")
                return
        except ValueError:
            print("❌ Digite um número válido para calorias.")
            return

        # Verifica se o alimento já existe
        cursor.execute("SELECT * FROM alimentos WHERE nome = ?", (nome,))
        if cursor.fetchone():
            print("❌ Alimento já cadastrado!")
            return

        # Insere o novo alimento
        cursor.execute("INSERT INTO alimentos (nome, calorias) VALUES (?, ?)", (nome, calorias))
        conn.commit()
        print(f"✅ Alimento '{nome}' cadastrado com sucesso.")

    @staticmethod
    def ver_alimentos():
        """
        Lista todos os alimentos cadastrados no sistema
        
        Exibe nome e calorias por 100g de cada alimento
        """
        print("\n=== Lista de alimentos cadastrados ===")
        cursor.execute("SELECT nome, calorias FROM alimentos")
        alimentos = cursor.fetchall()
        if alimentos:
            for a in alimentos:
                print(f"- {a[0]} | {a[1]} cal por 100g")
        else:
            print("❌ Nenhum alimento cadastrado.")

    @staticmethod
    def excluir_alimento():
        """
        Remove um alimento do banco de dados
        
        Solicita o nome do alimento a ser removido e confirma a operação
        """
        print("\n=== Excluir alimento ===")
        nome = input("Nome do alimento para excluir: ").strip().lower()
        cursor.execute("SELECT * FROM alimentos WHERE nome = ?", (nome,))
        if not cursor.fetchone():
            print("❌ Alimento não encontrado.")
            return
        cursor.execute("DELETE FROM alimentos WHERE nome = ?", (nome,))
        conn.commit()
        print(f"✅ Alimento '{nome}' excluído com sucesso.")


class Registros(Comida):
    """Classe para gerenciar registros diários e lembretes (herda de Comida)"""
    
    def pegar_registros_do_dia(self):
        """
        Obtém todos os registros alimentares do dia atual
        
        Returns:
            list: Lista de registros do dia atual
        """
        hoje = date.today()
        cursor.execute("SELECT * FROM registro_refeicoes WHERE email = ? AND data = ?", (self.email_usuario, str(hoje)))
        registros = cursor.fetchall()
        return registros

    def submenu_lembretes(self):
        """
        Exibe lembretes personalizados com base nos registros do dia
        
        Mostra alertas sobre consumo alimentar e hidratação
        """
        registros_diarios = self.pegar_registros_do_dia()

        print("\n--- Lembretes e Alertas ---")

        if not registros_diarios:
            print("Atenção! Você ainda não registrou nenhuma refeição hoje. Não esqueça de se alimentar!")
        else:
            print(f"Você já registrou {len(registros_diarios)} refeição(ões) hoje. Continue assim!")

        print("Lembrete: Beba pelo menos 2 litros de água ao longo do dia.")
        input("\nPressione Enter para voltar ao menu principal...")

    def encerrar_dia(self):
        """
        Calcula e exibe um resumo nutricional do dia
        
        Compara as calorias consumidas com a meta calórica baseada na dieta
        """
        print("\n📅 Encerramento do Dia")
        hoje = date.today().strftime("%Y-%m-%d")

        # Obtém dados do usuário (dieta, peso, altura)
        cursor.execute("SELECT dieta, peso, altura FROM usuarios WHERE email = ?", (self.email_usuario,))
        resultado = cursor.fetchone()
        if not resultado:
            print("❌ Usuário não encontrado.")
            return
        dieta_usuario, peso, altura = resultado

        # Obtém todas as refeições registradas hoje
        cursor.execute('''
            SELECT r.alimento, r.quantidade_gramas, a.calorias
            FROM refeicoes r
            JOIN alimentos a ON r.alimento = a.nome
            WHERE r.email_usuario = ? AND date(r.data) = ?
        ''', (self.email_usuario, hoje))
        refeicoes_hoje = cursor.fetchall()

        if not refeicoes_hoje:
            print("❌ Nenhuma refeição registrada para hoje.")
            return

        # Calcula o total de calorias consumidas
        calorias_totais = 0
        for alimento, quantidade, cal_100g in refeicoes_hoje:
            calorias_totais += (cal_100g * quantidade) / 100

        calorias_totais = round(calorias_totais, 2)

        # Define metas calóricas baseadas no tipo de dieta
        metas = {
            "Low carb": 25 * peso,
            "Cetogênica": 27 * peso,
            "Hiperproteica": 30 * peso,
            "Bulking": 35 * peso
        }

        meta_calorias = metas.get(dieta_usuario, 30 * peso)

        # Exibe o resumo e feedback
        print(f"\nDieta: {dieta_usuario}")
        print(f"Calorias consumidas hoje: {calorias_totais} kcal")
        print(f"Meta calórica diária aproximada: {meta_calorias} kcal")

        if calorias_totais < meta_calorias * 0.9:
            print("⚠️ Você consumiu menos calorias que o recomendado para sua dieta hoje.")
        elif calorias_totais > meta_calorias * 1.1:
            print("⚠️ Você consumiu mais calorias que o recomendado para sua dieta hoje.")
        else:
            print("✅ Consumo calórico dentro da meta para hoje. Bom trabalho!")

# Agenda Alimentar

def agenda_alimentar():
    """Nova funcionalidade: Agenda alimentar com horários"""
    global agenda_usuario
    
    print("\n=== AGENDA ALIMENTAR ===")
    print("Vamos definir seus horários de refeição!")
    
    # Coletando horários
    cafe = input("Que horas você planeja tomar café da manhã? (ex: 07:30): ")
    almoco = input("Que horas você planeja almoçar? (ex: 12:00): ")
    jantar = input("Que horas você planeja jantar? (ex: 19:00): ")
    
    # Salvando os horários na variável global
    agenda_usuario = {
        "cafe_da_manha": cafe,
        "almoco": almoco,
        "jantar": jantar
    }
    
    print("\n✅ Agenda criada com sucesso!")
    print(f"☕ Café da manhã: {cafe}")
    print(f"🍽️  Almoço: {almoco}")
    print(f"🌙 Jantar: {jantar}")

# Variável global para guardar a agenda
agenda_usuario = {}

def ver_agenda():
    """Função para mostrar a agenda do usuário"""
    if agenda_usuario:
        print("\n=== SUA AGENDA ALIMENTAR ===")
        print(f"☕ Café da manhã: {agenda_usuario['cafe_da_manha']}")
        print(f"🍽️  Almoço: {agenda_usuario['almoco']}")
        print(f"🌙 Jantar: {agenda_usuario['jantar']}")
    else:
        print("❌ Você ainda não criou uma agenda alimentar.")
        print("💡 Use a opção 8 para criar sua agenda!")

# Exemplo de uso:
if __name__ == "__main__":
    # Criar agenda
    minha_agenda = agenda_alimentar()
    
    # Ver agenda
    ver_agenda(minha_agenda)

    # Pesquisa de Satisfação / Lista de feedbacks

feedbacks_usuarios = []

def feedback_usuario():
    """Nova funcionalidade: Coleta feedback do usuário sobre o projeto"""
    print("\n=== 🐤 FEEDBACK NUTRISMART 🐤 ===")
    print("Sua opinião é muito importante para nós!")
    
    # Pergunta 1 - Satisfação geral
    print("\n1. Você está gostando da ferramenta NutriSmart?")
    print("1 - Não gosto")
    print("2 - Gosto pouco") 
    print("3 - Gosto")
    print("4 - Gosto muito")
    print("5 - Amo!")
    
    while True:
        satisfacao = input("Sua resposta (1-5): ")
        if satisfacao in ['1', '2', '3', '4', '5']:
            break
        print("❌ Digite apenas números de 1 a 5")
    
    # Pergunta 2 - Facilidade de uso
    print("\n2. O sistema é fácil de usar?")
    print("1 - Muito difícil")
    print("2 - Difícil")
    print("3 - Normal")
    print("4 - Fácil") 
    print("5 - Muito fácil")
    
    while True:
        facilidade = input("Sua resposta (1-5): ")
        if facilidade in ['1', '2', '3', '4', '5']:
            break
        print("❌ Digite apenas números de 1 a 5")
    
    # Pergunta 3 - Recomendação
    print("\n3. Você recomendaria o NutriSmart para um amigo?")
    recomendaria = input("(s/n): ").lower().strip()
    while recomendaria not in ['s', 'n', 'sim', 'não', 'nao']:
        recomendaria = input("Por favor, responda 's' para sim ou 'n' para não: ").lower().strip()
    
    # Pergunta 4 - Comentário livre
    print("\n4. Deixe um comentário sobre o que achou do sistema:")
    comentario = input("Seu comentário: ").strip()
    
    # Salva o feedback
    feedback = {
        "satisfacao": satisfacao,
        "facilidade": facilidade, 
        "recomendaria": recomendaria in ['s', 'sim'],
        "comentario": comentario
    }
    
    feedbacks_usuarios.append(feedback)
    
    print("\n✅ Obrigado pelo seu feedback!")
    print("🫂 Sua opinião nos ajuda a melhorar o NutriSmart!")

def ver_todos_feedbacks():
    """Função para ver todos os feedbacks (para admin)"""
    if not feedbacks_usuarios:
        print("❌ Nenhum feedback foi enviado ainda.")
        return
    
    print(f"\n=== TODOS OS FEEDBACKS ({len(feedbacks_usuarios)}) ===")
    
    for i, feedback in enumerate(feedbacks_usuarios, 1):
        print(f"\n--- Feedback {i} ---")
        print(f"Satisfação: {feedback['satisfacao']}/5")
        print(f"Facilidade: {feedback['facilidade']}/5")
        print(f"Recomendaria: {'Sim' if feedback['recomendaria'] else 'Não'}")
        print(f"Comentário: {feedback['comentario']}")

# Exemplo de uso:
if __name__ == "__main__":
    feedback_usuario()
   
    # Área de dicas nutricionais

def dicas_nutricionais():
    """Nova funcionalidade: Área com dicas para vida nutricional saudável"""
    print("\n=== DICAS NUTRICIONAIS ===")
    print("💡 Dicas para uma vida nutricional mais saudável!\n")
    
    dicas = [
        "💧 Beba pelo menos 2 litros de água por dia",
        "🥗 Inclua verduras e legumes em todas as refeições",
        "🍎 Prefira frutas inteiras no lugar de sucos",
        "🥜 Consuma castanhas e nozes com moderação",
        "🐟 Coma peixe pelo menos 2 vezes por semana",
        "🍚 Prefira carboidratos integrais",
        "⏰ Faça refeições em horários regulares",
        "🥛 Consuma laticínios com baixo teor de gordura",
        "🧂 Reduza o consumo de sal e açúcar",
        "🥘 Evite alimentos ultraprocessados",
        "🏃 Pratique exercícios físicos regularmente",
        "😴 Durma bem - o sono afeta o metabolismo",
        "🍽️ Mastigue bem os alimentos",
        "🥕 Varie as cores dos alimentos no prato",
        "☕ Modere o consumo de cafeína",
        "🥤 Evite refrigerantes e bebidas açucaradas",
        "🧘 Controle o estresse - ele afeta a alimentação",
        "📱 Evite distrações durante as refeições",
        "🍳 Prefira alimentos cozidos, assados ou grelhados",
        "🥬 Lave bem frutas e verduras antes de consumir"
    ]
    
    print("📋 SUAS DICAS NUTRICIONAIS:")
    print("=" * 50)
    
    for i, dica in enumerate(dicas, 1):
        print(f"{i:2}. {dica}")
    
    print("\n" + "=" * 50)
    print("✨ Lembre-se: pequenas mudanças fazem grande diferença!")
    print("🎯 Escolha algumas dicas e comece hoje mesmo!")
    
    input("\nPressione Enter para voltar ao menu...")

# Exemplo de uso:
if __name__ == "__main__":
    dicas_nutricionais()

    # Desafios Semanais

def desafio_semanal_aleatorio():
    desafios = [
        "Beba 2 litros de água todos os dias da semana.",
        "Inclua uma porção extra de vegetais nas refeições diárias.",
        "Evite alimentos processados durante toda a semana.",
        "Pratique 30 minutos de atividade física pelo menos 4 dias.",
        "Reduza o consumo de açúcar refinado durante a semana.",
        "Experimente uma receita nova e saudável.",
        "Faça um diário alimentar por 7 dias.",
        "Evite bebidas açucaradas.",
        "Inclua uma porção de frutas no café da manhã.",
        "Caminhe pelo menos 30 minutos diariamente.",
        "Durma pelo menos 7 horas por noite.",
        "Evite fast food durante a semana.",
        "Reduza o consumo de sal nos alimentos.",
        "Prefira alimentos integrais em suas refeições.",
        "Faça alongamentos diários por 10 minutos."
    ]

    desafio = random.choice(desafios)
    print("\n🎯 Desafio da Semana:")
    print(f"➡ {desafio}")
    input("\nPressione Enter para voltar ao menu.")
