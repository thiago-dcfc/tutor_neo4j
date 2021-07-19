from wtforms import Form, validators, StringField, PasswordField, TextAreaField, SelectField, RadioField
from .validations_custom import PasswordEqualToIfProvided, LengthIfProvided

required_message = 'Este campo é obrigatório'


#########################
#   REGISTRATION FORM   #
#########################
class RegistrationForm(Form):
    username = StringField('Nome de usuário',
                           [validators.Length(min=4, max=25,
                                              message='Nome de usuário deve possuir entre 4 e 25 caracteres'),
                            validators.InputRequired(message=required_message)])
    name = StringField('Nome completo',
                       [validators.Length(min=4, max=35,
                                          message='Nome completo deve possuir entre 4 e 35 caracteres'),
                        validators.InputRequired(message=required_message)])
    email = StringField('Email',
                        [validators.Length(min=6, max=35,
                                           message='Email deve possuir entre 6 e 35 caracteres'),
                         validators.Email(message='Email inválido'),
                         validators.InputRequired(message=required_message)])
    password = PasswordField('Senha',
                             [validators.Length(min=5, message='Senha deve possuir, no mínimo, 5 caracteres'),
                              validators.InputRequired(message=required_message),
                              validators.EqualTo('confirm_password',
                                                 message='As senhas não são iguais')])
    confirm_password = PasswordField('Confirmação de senha',
                                     [validators.InputRequired(message=required_message)])


##################
#   LOGIN FORM   #
##################
class LoginForm(Form):
    username = StringField('Nome de usuário',
                           [validators.InputRequired(message=required_message)])
    password = PasswordField('Senha', [validators.InputRequired(message=required_message)])


#########################
#   EDIT PROFILE FORM   #
#########################
class EditProfileForm(Form):
    username = StringField('Nome de usuário')
    name = StringField('Nome completo',
                       [validators.Length(min=4, max=35,
                                          message='Nome completo deve possuir entre 4 e 35 caracteres'),
                        validators.InputRequired(message=required_message)])
    email = StringField('Email',
                        [validators.Length(min=6, max=35,
                                           message='Email deve possuir entre 6 e 35 caracteres'),
                         validators.Email(message='Email inválido'),
                         validators.InputRequired(message=required_message)])
    password = PasswordField('Senha',
                             [LengthIfProvided(min=5, message='Senha deve possuir, no mínimo, 5 caracteres'),
                              PasswordEqualToIfProvided('confirm_password',
                                                        message='As senhas não são iguais')])
    confirm_password = PasswordField('Confirmação de senha')


###########################################
#   COURSE CLASS FORM (create and edit)   #
###########################################
class CourseForm(Form):
    name = StringField('Nome do curso',
                       [validators.Length(min=4, max=120,
                                          message='Nome do curso deve possuir entre 4 e 120 caracteres'),
                        validators.InputRequired(message=required_message)])

    initials = StringField('Sigla',
                           [validators.Length(min=1, max=10,
                                              message='Sigla deve possuir entre 1 e 10 caracteres'),
                            validators.InputRequired(message=required_message)])


###########################################
#   COURSE CLASS FORM (create and edit)   #
###########################################
class CourseClassForm(Form):
    title = StringField('Nome da disciplina',
                        [validators.Length(min=4, max=35,
                                           message='Nome da disciplina deve possuir entre 4 e 35 caracteres'),
                         validators.InputRequired(message=required_message)])
    course = SelectField('Curso')


############################################
#   CLASS SUBJECT FORM (create and edit)   #
############################################
class ClassSubjectForm(Form):
    title = StringField('Assunto da disciplina',
                        [validators.Length(min=4, max=35,
                                           message='Assunto da disciplina deve possuir entre 4 e 35 caracteres'),
                         validators.InputRequired(message=required_message)])
    previous_subject = SelectField('Assunto anterior', validate_choice=False)
    next_subject = SelectField('Assunto posterior', validate_choice=False)
    support_material = TextAreaField('Material de apoio')
    initial = RadioField('Inicial')


############################
#   CREATE QUESTION FORM   #
############################
class QuestionForm(Form):
    title = StringField('Título da questão',
                        [validators.Length(min=4, max=35,
                                           message='Título da questão deve possuir entre 4 e 35 caracteres'),
                         validators.InputRequired(message=required_message)])
    body = TextAreaField('Enunciado',
                         [validators.Length(min=4,
                                            message='Enunciado deve possuir, no mínimo, 4 caracteres'),
                          validators.InputRequired(message=required_message)])
    support_material = TextAreaField('Material de apoio')
    choice_a = TextAreaField('Alternativa A',
                             [validators.InputRequired(message=required_message)])
    choice_b = TextAreaField('Alternativa B',
                             [validators.InputRequired(message=required_message)])
    choice_c = TextAreaField('Alternativa C',
                             [validators.InputRequired(message=required_message)])
    choice_d = TextAreaField('Alternativa D',
                             [validators.InputRequired(message=required_message)])
    right_answer = SelectField('Resposta correta')
    difficulty = SelectField('Dificuldade')
