# Gestão de Alunos

Sistema de gestão de alunos, docentes, turmas e disciplinas desenvolvido pelo **Grupo 2 MADS 2ano**.
Utilização do modulo:
📚 Aluno
➕ Adicionar um aluno
Aluno.adicionar_aluno(nome, numero, nif, email, data_nascimento)
📋 Listar todos os alunos
Aluno.listar_alunos()
👨‍🏫 Docente
➕ Adicionar um docente
Docente.adicionar_docente(nome, numero, data_nascimento)
📋 Listar todos os docentes
Docente.listar_docentes()
🏫 Turma
➕ Criar uma turma
Turma.adicionar_turma(nome_turma)
➕ Adicionar um aluno a uma turma
Turma.adicionar_aluno_turma(nome_turma, numero_aluno)
📋 Listar todas as turmas e respetivos alunos
Turma.listar_turmas()
📖 Disciplina
➕ Criar uma disciplina
Disciplina.adicionar_disciplina(nome_disciplina)
👨‍🏫 Atribuir docente a uma disciplina
Disciplina.atribuir_docente(nome_disciplina, numero_docente)
👥 Atribuir turma a uma disciplina
Disciplina.atribuir_turma(nome_disciplina, nome_turma)
➕ Inscrever aluno numa disciplina
Disciplina.inscrever_aluno(nome_disciplina, numero_aluno)
📝 Adicionar classificação (nota ou falta) a aluno
Disciplina.adicionar_classificacao(nome_disciplina, numero_aluno, tipo, nota)
# tipo deve ser "M1", "M2" ou "M3"
# nota pode ser número (0–20) ou "F"
📋 Listar todas as disciplinas e informações associadas
Disciplina.listar_disciplinas()
📊 Gerar estatísticas por disciplina
Disciplina.relatorio_estatisticas()
✅ Verificar integridade dos dados
Disciplina.validar_integridade_total()
📈 Relatório de alunos por turma (fora da classe)
relatorio_alunos_por_turma()
💾 Guardar dados em ficheiro JSON
guardar_dados("dados.json")
📂 Carregar dados de ficheiro JSON
carregar_dados("dados.json")
📦 Available on PyPI
