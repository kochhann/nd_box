import re
import uuid
from collections import namedtuple
from datetime import datetime, date
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import (
    User,
    Group
)
from django.db import connection
from django.conf import settings
from apps.agamotto.models import (
    ScheduledTask
)
from apps.autorizacoes.models import (
    Autorizador,
    Aluno,
    Enturmacao,
    Evento,
    AnexoAutorizacao
)
from apps.core.models import (
    Unidade,
    Turma
)
from apps.healt.models import (
    Paciente,
    Profissional,
    Evolucao,
    Afericoes,
    Medidas,
    Cuidados,
    Prescricao,
    Vacinacao
)
from hermes import send_welcome_mail


def validate(cpf: str) -> bool:
    # Verifica a formatação do CPF
    if not re.match(r'\d{3}\.\d{3}\.\d{3}-\d{2}', cpf):
        return False

    # Obtém apenas os números do CPF, ignorando pontuações
    numbers = [int(digit) for digit in cpf if digit.isdigit()]

    # Validação do primeiro dígito verificador:
    sum_of_products = sum(a * b for a, b in zip(numbers[0:9], range(10, 1, -1)))
    expected_digit = (sum_of_products * 10 % 11) % 10
    if numbers[9] != expected_digit:
        return False

    # Validação do segundo dígito verificador:
    sum_of_products = sum(a * b for a, b in zip(numbers[0:10], range(11, 1, -1)))
    expected_digit = (sum_of_products * 10 % 11) % 10
    if numbers[10] != expected_digit:
        return False

    return True


def calculate_age(birth_date):
    today = date.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

    return age


def cleanhtml(raw_html):
    CLEANR = re.compile('<.*?>')
    cleantext = re.sub(CLEANR, '', raw_html)
    return cleantext


def get_quotes(day, month):
    cursor = connection.cursor()
    cursor.execute("SELECT PENSAMENTO, AUTORIA FROM NDSISTEMAS.DBO.PENSAMENTOS"
                   " WHERE DAY(data) = '%s' AND MONTH(data) = '%s'" % (day, month))
    quotes = namedtuplefetchall(cursor)
    return quotes


def get_jund_member(member_id, tp):
    cursor = connection.cursor()
    if tp == 1:
        cursor.execute("SELECT COALESCE(P.NOME,'') NOME,"
                       "	   CASE WHEN C.NOME IS NOT NULL THEN"
                       "			C.NOME + ', ' + C.ESTADO"
                       "	   ELSE 'Não cadastrada' END AS CIDADE,"
                       "       P.ID,"
                       "	   COALESCE(NASCIMENTO,'') NASCIMENTO,"
                       "	   COALESCE(EMAIL,'') EMAIL,"
                       "	   COALESCE(CELULAR,'') CELULAR,"
                       "       P.IDGRUPO"
                       " FROM Z_LENIMAR.DBO.PARTICIPANTESGRUPO P"
                       " LEFT JOIN Z_LENIMAR.DBO.TCIDADES C"
                       " ON P.CIDADE = C.CODIGO"
                       " WHERE P.ID = '%s'" % member_id)
    else:
        cursor.execute("SELECT COALESCE(P.NOME,'') NOME,"
                       "	   COALESCE(C.CIDADE,'Não cadastrada') CIDADE,"
                       "       U.ID,"
                       "	   COALESCE(P.NASCIMENTO,'') NASCIMENTO,"
                       "	   COALESCE(P.EMAIL,'') EMAIL,"
                       "	   COALESCE(P.CELULAR,'') CELULAR,"
                       "       P.IDGRUPO"
                       " FROM Z_LENIMAR.DBO.JUNDUSUARIOS U"
                       " INNER JOIN Z_LENIMAR.DBO.ACOMPANHANTESGRUPO P"
                       "	ON U.IDACOMPANHANTESGRUPO = P.ID"
                       " LEFT JOIN Z_LENIMAR.DBO.GRUPOJOVEM C"
                       "	ON P.IDGRUPO = C.ID"
                       " WHERE U.ID = '%s'"
                       "       AND P.SITUACAO = 1" % member_id)
    member = namedtuplefetchall(cursor)
    return member


def namedtuplefetchall(cursor):
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]


def get_file_path(_instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return filename


def nl2br(s):
    return '<br />\n'.join(s.split('\n'))


def get_start_load_healt_module():
    cursor = connection.cursor()
    cnt_sucesso = 0
    cnt_falha = 0
    ## Paciente
    cursor.execute("SELECT NOME"
                   "	,NOMEPAI"
                   "	,NOMEMAE"
                   "	,DATANASCIMENTO"
                   "	,FONECONTATO"
                   "	,CODIGOND"
                   "    ,DATAMORTE"
                   "  FROM ND_SAUDE.DBO.PACIENTES")
    qs = namedtuplefetchall(cursor)
    if qs:
        for item in qs:
            cont = 'Não informado'
            if item.FONECONTATO is not None:
                cont = item.FONECONTATO
            dcs = False
            if item.DATAMORTE is not None:
                dcs = True
            paciente = Paciente(id=item.CODIGOND,
                                nome=item.NOME,
                                data_nascimento=item.DATANASCIMENTO,
                                data_falecimento=item.DATAMORTE,
                                nome_pai=item.NOMEPAI,
                                nome_mae=item.NOMEMAE,
                                contato=cont,
                                falecido=dcs,
                                nd_code=item.CODIGOND)
            paciente.save()
            cnt_sucesso += 1
    print(f'Pacientes cadastrados: {cnt_sucesso}')
    print('-------------')

    ## Profissional
    cursor.execute("SELECT M.ID"
                   "	,CRM"
                   "	,M.NOME"
                   "	,CASE WHEN CELULAR IS NULL"
                   "		THEN TELEFONECONSULTORIO"
                   "		ELSE CELULAR"
                   "	END CONTATO"
                   "	,CASE WHEN M.IDESPECIALIDADE IS NULL"
                   "        THEN 'Não consta'"
                   "        ELSE E.NOME"
                   "    END ESPECIALIDADE"
                   " FROM ND_SAUDE.DBO.MEDICOS M"
                   "	LEFT JOIN ND_SAUDE.DBO.MEDICOSESPECIALIDADES E"
                   "	ON M.IDESPECIALIDADE = E.ID")
    qs = namedtuplefetchall(cursor)
    cnt_sucesso = 0
    if qs:
        for item in qs:
            profissional = Profissional(nd_code=item.ID,
                                        nome=item.NOME,
                                        id_funcional=item.CRM,
                                        especialidade=item.ESPECIALIDADE,
                                        contato=item.CONTATO)
            profissional.save()
            cnt_sucesso += 1
    print(f'Profissionais cadastrados: {cnt_sucesso}')
    print('-------------')

    ## Movimentos

    ## Selecionar todos os pacientes e profissionais cadastrados
    pacientes = Paciente.objects.filter(ativo=True)
    profissionais = Profissional.objects.filter(ativo=True)

    ## Evoluções
    cursor.execute("SELECT"
                   "	data"
                   "	,subjetivo"
                   "	,objetivo"
                   "	,avaliacao"
                   "	,plano"
                   "	,IDPaciente"
                   "	,IDMedicosProfissional"
                   " FROM ND_SAUDE.DBO.EVOLUCAOSOAP")
    qs = namedtuplefetchall(cursor)
    cnt_sucesso = 0
    cnt_falha = 0
    if qs:
        for item in qs:
            try:
                pro = profissionais.get(nd_code=item.IDMedicosProfissional)
                pac = pacientes.get(nd_code=item.IDPaciente)
            except ObjectDoesNotExist:
                cnt_falha += 1
                continue
            evolucao = Evolucao(profissional=pro,
                                paciente=pac,
                                subjetivo=item.subjetivo,
                                objetivo=item.objetivo,
                                avaliacao=item.avaliacao,
                                plano=item.plano)
            evolucao.save()
            cnt_sucesso += 1
    print(f'Evoluções cadastradas: {cnt_sucesso}')
    print(f'Cadastros falharam: {cnt_falha}')
    print('-------------')

    ## Sinais vitais
    cursor.execute("SELECT I.data"
                   "   ,I.temperatura"
                   "   ,I.paSistolica"
                   "   ,I.paDiastolica"
                   "   ,I.pressaoArterialMedia"
                   "   ,I.frequenciaRespiratoria"
                   "   ,I.frequenciaCardiaca"
                   "   ,I.pulsacao"
                   "   ,I.glicemia"
                   "   ,I.coleta"
                   "   ,I.saturacaoO2"
                   "   ,I.saturacaoCO2"
                   "   ,I.IDPaciente"
                   "   ,I.IDMedicosProfissional"
                   " FROM ND_SAUDE.DBO.AFERICOESVITAISPACIENTE I")
    qs = namedtuplefetchall(cursor)
    cnt_sucesso = 0
    cnt_falha = 0
    if qs:
        for item in qs:
            try:
                pro = profissionais.get(nd_code=item.IDMedicosProfissional)
                pac = pacientes.get(nd_code=item.IDPaciente)
            except ObjectDoesNotExist:
                cnt_falha += 1
                continue
            afericao = Afericoes(profissional=pro,
                                 paciente=pac,
                                 temperatura=item.temperatura,
                                 sistolica=item.paSistolica,
                                 diastolica=item.paDiastolica,
                                 media=item.pressaoArterialMedia,
                                 freq_respiratoria=item.frequenciaRespiratoria,
                                 freq_cardiaca=item.frequenciaCardiaca,
                                 pulso=item.pulsacao,
                                 glicemia=item.glicemia,
                                 coleta=item.coleta,
                                 saturacao_o2=item.saturacaoO2,
                                 saturacao_co2=item.saturacaoCO2)
            afericao.save()
            cnt_sucesso += 1
    print(f'Aferições cadastradas: {cnt_sucesso}')
    print(f'Cadastros falharam: {cnt_falha}')
    print('-------------')

    ## Cuidados
    cursor.execute("SELECT I.data"
                   "    ,C.nome"
                   "	,I.obsEnfermagem"
                   "	,IDPaciente"
                   "	,IDMedico"
                   " FROM ND_SAUDE.DBO.pacienteCuidados I INNER JOIN"
                   "	ND_SAUDE.DBO.cuidados C ON I.IDCuidados = C.ID")
    qs = namedtuplefetchall(cursor)
    cnt_sucesso = 0
    cnt_falha = 0
    if qs:
        for item in qs:
            try:
                pro = profissionais.get(nd_code=item.IDMedico)
                pac = pacientes.get(nd_code=item.IDPaciente)
            except ObjectDoesNotExist:
                cnt_falha += 1
                continue
            cuidado = Cuidados(profissional=pro,
                               paciente=pac,
                               cuidado=item.nome,
                               observacao=item.obsEnfermagem)
            cuidado.save()
            cnt_sucesso += 1
    print(f'Cuidados cadastrados: {cnt_sucesso}')
    print(f'Cadastros falharam: {cnt_falha}')
    print('-------------')

    ## Medidas
    cursor.execute("SELECT INS.dataAlteracao"
                   "    ,INS.areadeSuperficieCorporal"
                   "	,INS.quadril"
                   "	,INS.cintura"
                   "	,INS.circulacaoBraquial"
                   "	,INS.pgCutanea"
                   "	,EN.descricao"
                   "	,INS.circunPanturrilha"
                   "	,INS.altura"
                   "	,INS.pesoAtual"
                   "	,INS.IMC"
                   "	,INS.obsNutricao"
                   "	,INS.dieta"
                   "	,INS.IDPaciente"
                   "	,INS.IDMedicosProfissional"
                   " FROM ND_SAUDE.DBO.medicaoAntropometrica INS"
                   "     INNER JOIN ND_SAUDE.DBO.estadoNutricional EN"
                   "		ON INS.IDEstadoNutricional = EN.ID")
    qs = namedtuplefetchall(cursor)
    cnt_sucesso = 0
    cnt_falha = 0
    if qs:
        for item in qs:
            try:
                pro = profissionais.get(nd_code=item.IDMedicosProfissional)
                pac = pacientes.get(nd_code=item.IDPaciente)
            except ObjectDoesNotExist:
                cnt_falha += 1
                continue
            medida = Medidas(profissional=pro,
                             paciente=pac,
                             superficie_corporal=item.areadeSuperficieCorporal,
                             quadril=item.quadril,
                             cintura=item.cintura,
                             circulacao_braquial=item.circulacaoBraquial,
                             pg_cutaneas=item.pgCutanea,
                             estado_nutricional=item.descricao,
                             panturrilha=item.circunPanturrilha,
                             altura=item.altura,
                             peso=item.pesoAtual,
                             imc=item.IMC,
                             observacao=item.obsNutricao,
                             dieta=item.dieta)
            medida.save()
            cnt_sucesso += 1
    print(f'Medidas cadastradas: {cnt_sucesso}')
    print(f'Cadastros falharam: {cnt_falha}')
    print('-------------')

    ## Prescrições
    cursor.execute("SELECT M.nomeComercial"
                   "	   ,INS.dtInicio"
                   "	   ,INS.dtFim"
                   "	   ,INS.motivo"
                   "	   ,TA.nome"
                   "	   ,INS.intervalomedicacao"
                   "	   ,INS.horario"
                   "	   ,INS.IDPaciente"
                   "	   ,INS.IDMedico"
                   " FROM ND_SAUDE.DBO.prescricoesMedicamentos INS"
                   "	INNER JOIN ND_SAUDE.DBO.medicamentos M on INS.IDfarmaco = M.ID"
                   "	INNER JOIN ND_SAUDE.DBO.tiposAplicacao TA on INS.IDtipoAplicacao = TA.ID")
    qs = namedtuplefetchall(cursor)
    cnt_sucesso = 0
    cnt_falha = 0
    if qs:
        for item in qs:
            try:
                pro = profissionais.get(nd_code=item.IDMedico)
                pac = pacientes.get(nd_code=item.IDPaciente)
            except ObjectDoesNotExist:
                cnt_falha += 1
                continue
            prescricao = Prescricao(profissional=pro,
                                    paciente=pac,
                                    farmaco=item.nomeComercial,
                                    aplicacao=item.nome,
                                    data_inicio=item.dtInicio,
                                    data_fim=item.dtFim,
                                    motivo=item.motivo,
                                    intervalo=item.intervalomedicacao,
                                    horario=item.horario)
            prescricao.save()
            cnt_sucesso += 1
    print(f'Prescrições cadastradas: {cnt_sucesso}')
    print(f'Cadastros falharam: {cnt_falha}')
    print('-------------')

    ## Vacinas
    cursor.execute("SELECT INS.data"
                   "    ,V.nome"
                   "	,INS.lote"
                   "	,INS.nroCarteira"
                   "	,INS.localidade"
                   "	,INS.IDPaciente"
                   "	,INS.nomeProfissional"
                   " FROM ND_SAUDE.DBO.vacinacaoPacientes INS"
                   "	INNER JOIN ND_SAUDE.DBO.vacinas V on INS.IDVacina = V.ID")
    qs = namedtuplefetchall(cursor)
    cnt_sucesso = 0
    cnt_falha = 0
    if qs:
        for item in qs:
            try:
                pac = pacientes.get(nd_code=item.IDPaciente)
            except ObjectDoesNotExist:
                cnt_falha += 1
                continue
            vacina = Vacinacao(paciente=pac,
                               profissional=item.nomeProfissional,
                               vacina=item.nome,
                               lote=item.lote,
                               id_carteira=item.nroCarteira,
                               localidade=item.localidade,
                               data=item.data)
            vacina.save()
            cnt_sucesso += 1
    print(f'Vacinações cadastradas: {cnt_sucesso}')
    print(f'Cadastros falharam: {cnt_falha}')
    print('-------------')


def get_gv_unidade(gv_code):
    cursor = connection.cursor()
    if gv_code == 0:
        cursor.execute("SELECT P.NOMEREDUZIDO AS NOME,"
                       "       C.NOME AS CIDADE,"
                       "       UF.SIGLA AS ESTADO,"
                       "       P.CODIGOPESSOA AS GV_CODE,"
                       "       COALESCE(U.CNAE, '00000000') AS CNAE,"
                       "       PJ.CNPJ AS CNPJ,"
                       "       U.CODIGOEMPRESA"
                       " FROM GVContabilidade.dbo.PAD_UNIDADE U"
                       "    INNER JOIN GVContabilidade.dbo.PAD_PESSOA P"
                       "        ON U.CODIGOPESSOA = P.CODIGOPESSOA"
                       "    INNER JOIN GVContabilidade.dbo.PAD_PESSOAENDERECO E"
                       "        ON P.CODIGOPESSOA = E.CODIGOPESSOA"
                       "    INNER JOIN GVContabilidade.dbo.PAD_CIDADE C"
                       "        ON E.CODIGOCIDADE = C.CODIGOCIDADE"
                       "    INNER JOIN GVContabilidade.dbo.PAD_UNIDADEFEDERACAO UF"
                       "        ON C.CODIGOUF = UF.CODIGOUF"
                       "    INNER JOIN GVContabilidade.dbo.PAD_PESSOAJURIDICA PJ"
                       "        ON P.CODIGOPESSOA = PJ.CODIGOPESSOA")
    else:
        cursor.execute("SELECT P.NOMEREDUZIDO AS NOME,"
                       "       C.NOME AS CIDADE,"
                       "       UF.SIGLA AS ESTADO,"
                       "       P.CODIGOPESSOA AS GV_CODE,"
                       "       COALESCE(U.CNAE, '00000000') AS CNAE,"
                       "       PJ.CNPJ AS CNPJ,"
                       "       U.CODIGOEMPRESA"
                       " FROM GVContabilidade.dbo.PAD_UNIDADE U"
                       "    INNER JOIN GVContabilidade.dbo.PAD_PESSOA P"
                       "        ON U.CODIGOPESSOA = P.CODIGOPESSOA"
                       "    INNER JOIN GVContabilidade.dbo.PAD_PESSOAENDERECO E"
                       "        ON P.CODIGOPESSOA = E.CODIGOPESSOA"
                       "    INNER JOIN GVContabilidade.dbo.PAD_CIDADE C"
                       "        ON E.CODIGOCIDADE = C.CODIGOCIDADE"
                       "    INNER JOIN GVContabilidade.dbo.PAD_UNIDADEFEDERACAO UF"
                       "        ON C.CODIGOUF = UF.CODIGOUF"
                       "    INNER JOIN GVContabilidade.dbo.PAD_PESSOAJURIDICA PJ"
                       "        ON P.CODIGOPESSOA = PJ.CODIGOPESSOA"
                       " WHERE P.CODIGOPESSOA = '%s'" % gv_code)

    qs = namedtuplefetchall(cursor)
    return qs


def get_gv_user_data(user_id, option):
    cursor = connection.cursor()
    if option == 1:
        cursor.execute("SELECT P.CODIGOPESSOA"
                       " ,P.NOME"
                       " FROM GVContabilidade.dbo.PAD_PESSOA P"
                       "    INNER JOIN GVContabilidade.dbo.PAD_PESSOAFISICA PF"
                       "        ON PF.CODIGOPESSOA = P.CODIGOPESSOA"
                       " WHERE CPF = '%s'" % user_id)
    if option == 2:
        cursor.execute("SELECT P.CODIGOPESSOA"
                       " ,P.NOME"
                       " FROM GVContabilidade.dbo.PAD_PESSOA P"
                       "    INNER JOIN GVContabilidade.dbo.PAD_PESSOAFISICA PF"
                       "        ON PF.CODIGOPESSOA = P.CODIGOPESSOA"
                       " WHERE P.CODIGOPESSOA = '%s'" % user_id)
    qs = namedtuplefetchall(cursor)
    return qs


def get_gv_user_relatives(gv_code, year):
    cursor = connection.cursor()
    cursor.execute("SELECT P.NOME,"
                   "       PA.DESCRICAO,"
                   "       PA.CODIGOPAPEL,"
                   "       P_ALUNO.CODIGOPESSOA,"
                   "       P_ALUNO.NOME ALUNO"
                   " FROM GVContabilidade.dbo.PAD_PESSOA P"
                   "    INNER JOIN GVContabilidade.dbo.PAD_PESSOAPAPEL PP"
                   "        ON P.CODIGOPESSOA = PP.CODIGOPESSOA"
                   "    INNER JOIN GVContabilidade.dbo.PAD_PAPEL PA"
                   "        ON PP.CODIGOPAPEL = PA.CODIGOPAPEL"
                   "    INNER JOIN GVContabilidade.dbo.PAD_PESSOA P_ALUNO"
                   "        ON PP.CODIGOPESSOAVINCULO = P_ALUNO.CODIGOPESSOA"
                   "    INNER JOIN GVContabilidade.dbo.ACD_ALUNO ALU"
                   "        ON P_ALUNO.CODIGOPESSOA = ALU.CODIGOPESSOA"
                   "    INNER JOIN GVContabilidade.dbo.ACD_ENTURMACAO ENT"
                   "        ON ALU.CODIGOALUNO = ENT.CODIGOALUNO"
                   "    INNER JOIN GVContabilidade.dbo.ACD_TURMA TUR"
                   "        ON ENT.CODIGOTURMA = TUR.CODIGOTURMA"
                   " WHERE P.CODIGOPESSOA = '%s'"
                   "      AND PA.CODIGOPAPEL = 30"
                   "      AND TUR.ANOINICIO = '%s'" % (gv_code, year))
    qs = namedtuplefetchall(cursor)
    return qs


def get_enturmacao(gv_code, year):
    cursor = connection.cursor()
    if gv_code > 0:
        cursor.execute("SELECT ALUP.NOME ALUNO,"
                       "       ALU.MATRICULA"
                       " FROM GVContabilidade.dbo.ACD_TURMA TUR"
                       "    INNER JOIN GVContabilidade.dbo.ACD_ENTURMACAO ENT"
                       "        ON TUR.CODIGOTURMA = ENT.CODIGOTURMA"
                       "    INNER JOIN GVContabilidade.dbo.ACD_ALUNO ALU"
                       "        ON ENT.CODIGOALUNO = ALU.CODIGOALUNO"
                       "    INNER JOIN GVContabilidade.dbo.PAD_PESSOA ALUP"
                       "        ON ALU.CODIGOPESSOA = ALUP.CODIGOPESSOA"
                       " WHERE ALUP.CODIGOPESSOA = '%s'"
                       "      AND TUR.ANOINICIO = '%s'"
                       " GROUP BY ALUP.NOME,"
                       "         ALU.MATRICULA" % (gv_code, year))
    qs = namedtuplefetchall(cursor)
    return qs


def get_gv_curso(gv_code, year):
    cursor = connection.cursor()
    if gv_code == 0:
        cursor.execute("SELECT PESUNI.CODIGOPESSOA CODIGOUNIDADE,"
                       "       PESUNI.NOMEREDUZIDO UNIDADE,"
                       "       CUR.DESCRICAO CURSO,"
                       "	   CUR.CODIGOCURSO GV_CODE"
                       " FROM GVContabilidade.dbo.ACD_TURMA TUR"
                       "    INNER JOIN GVContabilidade.dbo.PAD_UNIDADE UNI"
                       "        ON TUR.CODIGOEMPRESA = UNI.CODIGOEMPRESA"
                       "           AND TUR.CODIGOUNIDADE = UNI.CODIGOUNIDADE"
                       "    INNER JOIN GVContabilidade.dbo.PAD_PESSOA PESUNI"
                       "        ON UNI.CODIGOPESSOA = PESUNI.CODIGOPESSOA"
                       "    INNER JOIN GVContabilidade.dbo.ACD_CICLO CIC"
                       "        ON TUR.CODIGOCICLO = CIC.CODIGOCICLO"
                       "    INNER JOIN GVContabilidade.dbo.ACD_CURSO CUR"
                       "        ON CIC.CODIGOCURSO = CUR.CODIGOCURSO"
                       "    INNER JOIN GVContabilidade.dbo.ACD_ENTURMACAO ENT"
                       "        ON TUR.CODIGOTURMA = ENT.CODIGOTURMA"
                       " WHERE TUR.ANOINICIO = '%s'"
                       " GROUP BY PESUNI.CODIGOPESSOA,"
                       "         PESUNI.NOMEREDUZIDO,"
                       "         CUR.DESCRICAO,"
                       "	     CUR.CODIGOCURSO" % year)
    else:
        cursor.execute("SELECT PESUNI.CODIGOPESSOA CODIGOUNIDADE,"
                       "       PESUNI.NOMEREDUZIDO UNIDADE,"
                       "       CUR.DESCRICAO CURSO,"
                       "	   CUR.CODIGOCURSO GV_CODE"
                       " FROM GVContabilidade.dbo.ACD_TURMA TUR"
                       "    INNER JOIN GVContabilidade.dbo.PAD_UNIDADE UNI"
                       "        ON TUR.CODIGOEMPRESA = UNI.CODIGOEMPRESA"
                       "           AND TUR.CODIGOUNIDADE = UNI.CODIGOUNIDADE"
                       "    INNER JOIN GVContabilidade.dbo.PAD_PESSOA PESUNI"
                       "        ON UNI.CODIGOPESSOA = PESUNI.CODIGOPESSOA"
                       "    INNER JOIN GVContabilidade.dbo.ACD_CICLO CIC"
                       "        ON TUR.CODIGOCICLO = CIC.CODIGOCICLO"
                       "    INNER JOIN GVContabilidade.dbo.ACD_CURSO CUR"
                       "        ON CIC.CODIGOCURSO = CUR.CODIGOCURSO"
                       "    INNER JOIN GVContabilidade.dbo.ACD_ENTURMACAO ENT"
                       "        ON TUR.CODIGOTURMA = ENT.CODIGOTURMA"
                       " WHERE CUR.CODIGOCURSO = '%s'"
                       " GROUP BY PESUNI.CODIGOPESSOA,"
                       "         PESUNI.NOMEREDUZIDO,"
                       "         CUR.DESCRICAO,"
                       "	     CUR.CODIGOCURSO" % gv_code)
    qs = namedtuplefetchall(cursor)
    return qs


def get_gv_ciclo(gv_code, year):
    cursor = connection.cursor()
    if gv_code == 0:
        cursor.execute("SELECT CUR.CODIGOCURSO CURSO,"
                       "       CIC.DESCRICAO CICLO,"
                       "       CIC.CODIGOCICLO GV_CODE"
                       " FROM GVContabilidade.dbo.ACD_TURMA TUR"
                       "    INNER JOIN GVContabilidade.dbo.PAD_UNIDADE UNI"
                       "        ON TUR.CODIGOEMPRESA = UNI.CODIGOEMPRESA"
                       "           AND TUR.CODIGOUNIDADE = UNI.CODIGOUNIDADE"
                       "    INNER JOIN GVContabilidade.dbo.PAD_PESSOA PESUNI"
                       "        ON UNI.CODIGOPESSOA = PESUNI.CODIGOPESSOA"
                       "    INNER JOIN GVContabilidade.dbo.ACD_CICLO CIC"
                       "        ON TUR.CODIGOCICLO = CIC.CODIGOCICLO"
                       "    INNER JOIN GVContabilidade.dbo.ACD_CURSO CUR"
                       "        ON CIC.CODIGOCURSO = CUR.CODIGOCURSO"
                       "    INNER JOIN GVContabilidade.dbo.ACD_ENTURMACAO ENT"
                       "        ON TUR.CODIGOTURMA = ENT.CODIGOTURMA"
                       " WHERE TUR.ANOINICIO = '%s'"
                       " GROUP BY CUR.CODIGOCURSO,"
                       "       CIC.DESCRICAO,"
                       "       CIC.CODIGOCICLO" % year)
    else:
        cursor.execute("SELECT CUR.CODIGOCURSO CURSO,"
                       "       CIC.DESCRICAO CICLO,"
                       "       CIC.CODIGOCICLO GV_CODE"
                       " FROM GVContabilidade.dbo.ACD_TURMA TUR"
                       "    INNER JOIN GVContabilidade.dbo.PAD_UNIDADE UNI"
                       "        ON TUR.CODIGOEMPRESA = UNI.CODIGOEMPRESA"
                       "           AND TUR.CODIGOUNIDADE = UNI.CODIGOUNIDADE"
                       "    INNER JOIN GVContabilidade.dbo.PAD_PESSOA PESUNI"
                       "        ON UNI.CODIGOPESSOA = PESUNI.CODIGOPESSOA"
                       "    INNER JOIN GVContabilidade.dbo.ACD_CICLO CIC"
                       "        ON TUR.CODIGOCICLO = CIC.CODIGOCICLO"
                       "    INNER JOIN GVContabilidade.dbo.ACD_CURSO CUR"
                       "        ON CIC.CODIGOCURSO = CUR.CODIGOCURSO"
                       "    INNER JOIN GVContabilidade.dbo.ACD_ENTURMACAO ENT"
                       "        ON TUR.CODIGOTURMA = ENT.CODIGOTURMA"
                       " WHERE CIC.CODIGOCICLO = '%s'"
                       " GROUP BY CUR.CODIGOCURSO,"
                       "       CIC.DESCRICAO,"
                       "       CIC.CODIGOCICLO" % gv_code)
    qs = namedtuplefetchall(cursor)
    return qs


def get_gv_turma(gv_code, year):
    cursor = connection.cursor()
    if gv_code == 0:
        cursor.execute("SELECT CIC.CODIGOCICLO CICLO,"
                       "       TUR.CODIGOTURMA,"
                       "       TUR.DESCRICAO TURMA,"
                       "	   TUR.CODIGOTURMA GV_CODE,"
                       "       TUR.ANOINICIO ANO"
                       " FROM GVContabilidade.dbo.ACD_TURMA TUR"
                       "    INNER JOIN GVContabilidade.dbo.PAD_UNIDADE UNI"
                       "        ON TUR.CODIGOEMPRESA = UNI.CODIGOEMPRESA"
                       "           AND TUR.CODIGOUNIDADE = UNI.CODIGOUNIDADE"
                       "    INNER JOIN GVContabilidade.dbo.PAD_PESSOA PESUNI"
                       "        ON UNI.CODIGOPESSOA = PESUNI.CODIGOPESSOA"
                       "    INNER JOIN GVContabilidade.dbo.ACD_CICLO CIC"
                       "        ON TUR.CODIGOCICLO = CIC.CODIGOCICLO"
                       "    INNER JOIN GVContabilidade.dbo.ACD_CURSO CUR"
                       "        ON CIC.CODIGOCURSO = CUR.CODIGOCURSO"
                       "    INNER JOIN GVContabilidade.dbo.ACD_ENTURMACAO ENT"
                       "        ON TUR.CODIGOTURMA = ENT.CODIGOTURMA"
                       " WHERE TUR.ANOINICIO = '%s'"
                       " GROUP BY CIC.CODIGOCICLO,"
                       "       TUR.CODIGOTURMA,"
                       "       TUR.DESCRICAO,"
                       "	   TUR.CODIGOTURMA,"
                       "       TUR.ANOINICIO" % year)
    else:
        cursor.execute("SELECT CIC.CODIGOCICLO CICLO,"
                       "       TUR.CODIGOTURMA,"
                       "       TUR.DESCRICAO TURMA,"
                       "	   TUR.CODIGOTURMA GV_CODE"
                       " FROM GVContabilidade.dbo.ACD_TURMA TUR"
                       "    INNER JOIN GVContabilidade.dbo.PAD_UNIDADE UNI"
                       "        ON TUR.CODIGOEMPRESA = UNI.CODIGOEMPRESA"
                       "           AND TUR.CODIGOUNIDADE = UNI.CODIGOUNIDADE"
                       "    INNER JOIN GVContabilidade.dbo.PAD_PESSOA PESUNI"
                       "        ON UNI.CODIGOPESSOA = PESUNI.CODIGOPESSOA"
                       "    INNER JOIN GVContabilidade.dbo.ACD_CICLO CIC"
                       "        ON TUR.CODIGOCICLO = CIC.CODIGOCICLO"
                       "    INNER JOIN GVContabilidade.dbo.ACD_CURSO CUR"
                       "        ON CIC.CODIGOCURSO = CUR.CODIGOCURSO"
                       "    INNER JOIN GVContabilidade.dbo.ACD_ENTURMACAO ENT"
                       "        ON TUR.CODIGOTURMA = ENT.CODIGOTURMA"
                       " WHERE TUR.CODIGOTURMA = '%s'"
                       " GROUP BY CIC.CODIGOCICLO,"
                       "       TUR.CODIGOTURMA,"
                       "       TUR.DESCRICAO,"
                       "	   TUR.CODIGOTURMA" % gv_code)
    qs = namedtuplefetchall(cursor)
    return qs


def get_gv_unidade_from_nd_code(nd_code):
    cursor = connection.cursor()
    cursor.execute("SELECT U.CODIGOPESSOA"
                   " FROM NDSISTEMAS.DBO.ESTABELECIMENTOS E"
                   " INNER JOIN GVCONTABILIDADE.DBO.PAD_UNIDADE U"
                   "	ON E.GVCODIGO = U.CODIGOUNIDADE"
                   " WHERE CODIGO = '%s'" % nd_code)
    qs = namedtuplefetchall(cursor)
    gv_code = 2
    if qs:
        gv_code = qs[0].CODIGOPESSOA
    return gv_code


def get_nd_code_from_gv_unidade(unidade):
    cursor = connection.cursor()
    cursor.execute("SELECT"
                   " 	E.CODIGO"
                   " FROM NDSISTEMAS.DBO.ESTABELECIMENTOS E"
                   "	INNER JOIN GVCONTABILIDADE.DBO.PAD_UNIDADE U"
                   "	ON E.GVCODIGO = U.CODIGOUNIDADE"
                   " WHERE U.CODIGOPESSOA = '%s' AND"
                   "	U.CODIGOEMPRESA = '%s' AND"
                   "	E.CODIGO < 50" % (unidade.gv_code, unidade.empresa))
    qs = namedtuplefetchall(cursor)
    gv_code = 2
    if qs:
        nd_code = qs[0].CODIGO
    return nd_code


def get_relatives(gv_code, year):
    cursor = connection.cursor()
    cursor.execute("SELECT P_ALUNO.NOME ALUNO,"
                   "       P_ALUNO.CODIGOPESSOA GV_CODE,"
                   "	   P_UNI.CODIGOPESSOA UNIDADE,"
                   "	   ALU.MATRICULA,"
                   "	   P.CODIGOPESSOA RESPONSAVEL,"
                   "       PA.DESCRICAO,"
                   "       PA.CODIGOPAPEL"
                   " FROM GVContabilidade.dbo.PAD_PESSOA P"
                   "    INNER JOIN GVContabilidade.dbo.PAD_PESSOAPAPEL PP"
                   "        ON P.CODIGOPESSOA = PP.CODIGOPESSOA"
                   "    INNER JOIN GVContabilidade.dbo.PAD_PAPEL PA"
                   "        ON PP.CODIGOPAPEL = PA.CODIGOPAPEL"
                   "    INNER JOIN GVContabilidade.dbo.PAD_PESSOA P_ALUNO"
                   "        ON PP.CODIGOPESSOAVINCULO = P_ALUNO.CODIGOPESSOA"
                   "    INNER JOIN GVContabilidade.dbo.ACD_ALUNO ALU"
                   "        ON P_ALUNO.CODIGOPESSOA = ALU.CODIGOPESSOA"
                   "    INNER JOIN GVContabilidade.dbo.ACD_ENTURMACAO ENT"
                   "        ON ALU.CODIGOALUNO = ENT.CODIGOALUNO"
                   "    INNER JOIN GVContabilidade.dbo.ACD_TURMA TUR"
                   "        ON ENT.CODIGOTURMA = TUR.CODIGOTURMA"
                   "	INNER JOIN GVContabilidade.dbo.PAD_UNIDADE UNI"
                   "		ON TUR.CODIGOUNIDADE = UNI.CODIGOUNIDADE"
                   "	INNER JOIN GVContabilidade.dbo.PAD_PESSOA P_UNI"
                   "		ON UNI.CODIGOPESSOA = P_UNI.CODIGOPESSOA"
                   " WHERE P.CODIGOPESSOA = '%s'"
                   "      AND PA.CODIGOPAPEL = 30"
                   "      AND TUR.ANOINICIO = '%s'" % (gv_code, year))
    qs = namedtuplefetchall(cursor)
    qs = list(dict.fromkeys(qs))
    return qs


def set_message_as_sent(m_id):
    cursor = connection.cursor()
    cursor.execute("UPDATE NDSISTEMAS.DBO.EMAILENVIADOS "
                   "SET DATAENVIO = GETDATE() WHERE ID = '%s'" % m_id)


def set_sms_as_sent(m_id):
    cursor = connection.cursor()
    query = f'UPDATE NDSISTEMAS.DBO.SMSENVIADOS SET ENVIADO = 1 WHERE ID = {m_id}'
    cursor.execute(query)


def get_email_nd(o_id):
    limit_date = '2021-01-01'
    cursor = connection.cursor()
    if o_id == 0:
        cursor.execute(f'SELECT * FROM NDSISTEMAS.DBO.EMAILENVIADOS WHERE DATA > {limit_date} AND DATAENVIO IS NULL')
    else:
        cursor.execute(f"SELECT * FROM NDSISTEMAS.DBO.EMAILENVIADOS WHERE ID IN {tuple(o_id)}")
    qs = namedtuplefetchall(cursor)
    return qs


def get_sms_boletos_nd():
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM NDSISTEMAS.DBO.SMSENVIADOS WHERE ENVIADO = 0")
    qs = namedtuplefetchall(cursor)
    return qs


def create_aluno(rel):
    responsavel = Autorizador.objects.get(gv_code=rel.RESPONSAVEL)
    unidade = Unidade.objects.get(gv_code=rel.UNIDADE)
    aluno = Aluno(nome=rel.ALUNO.title(),
                  matricula=int(rel.MATRICULA),
                  gv_code=rel.GV_CODE,
                  unidade=unidade,
                  responsavel=responsavel)
    aluno.save()
    return aluno


def get_turma_aluno(matricula, year):
    cursor = connection.cursor()
    cursor.execute("SELECT TUR.CODIGOTURMA"
                   " FROM GVContabilidade.dbo.ACD_ALUNO ALU"
                   "    INNER JOIN GVContabilidade.dbo.ACD_ENTURMACAO ENT"
                   "        ON ALU.CODIGOALUNO = ENT.CODIGOALUNO"
                   "    INNER JOIN GVContabilidade.dbo.ACD_TURMA TUR"
                   "        ON ENT.CODIGOTURMA = TUR.CODIGOTURMA"
                   " WHERE ALU.MATRICULA = '%s'"
                   "      AND TUR.ANOINICIO = '%s'" % (matricula, year))
    qs = namedtuplefetchall(cursor)
    codigo = 0
    if len(qs) > 0:
        codigo = qs[0].CODIGOTURMA
    return codigo


def create_enturmacao(aluno, turma):
    enturmacao = Enturmacao(unidade=aluno.unidade,
                            aluno=aluno,
                            turma=turma)
    enturmacao.save()
    return enturmacao.id


def user_creation_autorizador(id_number):
    task = ScheduledTask.objects.get(id=id_number)
    gv_user = get_gv_user_data(task.gv_code, 2)
    full = gv_user[0].NOME.title()
    nome, *sobrenome = full.split()
    sobrenome = " ".join(sobrenome)
    email = task.extra_field
    gv_code = gv_user[0].CODIGOPESSOA

    # create user in auth system
    user = User.objects.create_user(email, email, sobrenome)
    user.first_name = nome
    user.last_name = sobrenome
    user.save()

    # add in Autorizadores group
    g = Group.objects.get(name='Autorizadores')
    g.user_set.add(user)

    # create Autorizador and references user
    autorizador = Autorizador(user=user,
                              gv_code=gv_code)
    autorizador.save()

    # get relatives
    rel = get_relatives(gv_code, datetime.now().year)
    alunos = []
    for aluno in rel:
        new_aluno = create_aluno(aluno)
        alunos.append(new_aluno)

    # make grouping
    for item in alunos:
        turma = Turma.objects.get(gv_code=get_turma_aluno(item.matricula, datetime.now().year))
        item.create_enturmacao(turma)

    task.status = 'completed'
    task.soft_delete()
    send_welcome_mail(autorizador)


def generate_authorization(id_evento, tipo):
    evento = Evento.objects.get(pk=id_evento)
    evento.gera_autorizacoes(tipo)
    print('autorizações geradas')


def mail_is_valid(email):
    regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
    return re.fullmatch(regex, email)


def log_writer(function_name, log_message):
    path = settings.LOG_FILES
    now = datetime.now()
    date_only = now.strftime("%m_%d_%Y")
    date_time = now.strftime("%m/%d/%Y, %H:%M:%S\n")
    a = open(f'{path}\\{function_name}_{date_only}.txt', 'a')
    a.write(date_time)
    a.writelines(log_message)
    a.write('---------------------\n')
    a.close()


def error_log_writer(function_name, log_message):
    path = settings.LOG_FILES
    now = datetime.now()
    date_only = now.strftime("%m_%d_%Y")
    date_time = now.strftime("%m/%d/%Y, %H:%M:%S\n")
    a = open(f'{path}\\error_log_{function_name}_{date_only}.txt', 'a')
    a.write(date_time)
    a.writelines(log_message)
    a.write('---------------------\n')
    a.close()


def nd_document_registration(autorizacao):
    # year = str(autorizacao.evento.data_evento.year)
    year = '2021'
    gv_unidade = autorizacao.evento.eventounidade_set.first().unidade
    nd_code = str(get_nd_code_from_gv_unidade(gv_unidade))
    if len(nd_code) < 2:
        nd_code = '0' + nd_code
    table = f'nd_{nd_code}_escola.dbo.afastamento_{year}'
    cursor = connection.cursor()
    q = f'INSERT INTO {table} (' \
        f'  ALUNO' \
        f'  ,DATAINICIO' \
        f'  ,DATAFIM' \
        f'  ,MOTIVO_AFAST' \
        f'  ,MOTIVO) ' \
        f'VALUES (' \
        f'  {autorizacao.aluno.matricula}' \
        f'  ,\'{autorizacao.evento.data_evento}\'' \
        f'  ,\'{autorizacao.evento.data_termino}\'' \
        f'  ,\'{autorizacao.evento.descricao}\'' \
        f'  ,null)'
    cursor.execute(q)
