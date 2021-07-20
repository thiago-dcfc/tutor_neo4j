from flask import render_template, Blueprint

bp = Blueprint('', __name__)

# TODO esqueceu a senha?
# TODO terminar parte do aluno (react?)
# TODO campos extras dos relacionamentos (questão criada em/alterada em, questão respondida em/alterada em etc.)
# TODO aceitar múltiplos assuntos anteriores/posteriores
# TODO o que vai ter no Ver Perfil?
# TODO colocar algo na tela principal do professor. últimas respostas? algum gráfico?
# TODO colocar algo na tela principal do estudante. últimas respostas? perguntas/assuntos que outras pessoas da mesma turma estão respondendo?
# TODO papel e funções de administrador. mudar papeis dos usuários
# TODO dockerizar
# TODO testes


@bp.route('/')
def index():
    return render_template('index.html')
