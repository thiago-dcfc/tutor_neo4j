from flask import session, redirect, url_for, render_template, Blueprint

bp = Blueprint('', __name__)

# TODO CKEditor ou semelhante
# TODO esqueceu a senha?
# TODO terminar parte do aluno
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
    # session['username'] = 'sirlon'
    # session['person_name'] = 'Sirlon'
    # session['email'] = 'sirlon@sirlon.com'
    # session['type'] = 'teacher'
    return render_template('index.html')
