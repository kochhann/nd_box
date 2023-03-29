from django.views.generic import (
    TemplateView,
    View
)
from decimal import Decimal
from django.db import connection
from django.http import HttpResponse
from datetime import datetime
from io import BytesIO
from reportlab.lib.colors import black
from reportlab.lib.styles import ParagraphStyle as PS
from reportlab.platypus import (
    Table,
    TableStyle
)
from .printing import *
from functions import (
    namedtuplefetchall,
    get_quotes,
    nl2br
)


def get_nd_school_id(id_house):
    cursor = connection.cursor()
    cursor.execute("SELECT IDESCOLA FROM ND_PROVINCIA.DBO.TCASAS WHERE CODIGO='%s'" % id_house)
    gen_data = namedtuplefetchall(cursor)
    id_school = gen_data[0].IDESCOLA
    return id_school


def update_stay(id_movimento, periodo):
    cursor = connection.cursor()
    cursor.execute("UPDATE ND_SAUDE.DBO.MOVIMENTO SET PERIODO = '%s' WHERE ID = '%s'" % (periodo, id_movimento))
    return True


def manage_stay(item):
    periodo = ''
    if item.PERIODO is not None and item.PERIODO != '':
        periodo = item.PERIODO
    else:
        data_entrada = item.DATA.split('/')
        data_alta = item.DATAALTA.split('/')
        dia_entrada = data_entrada[0]
        mes_entrada = data_entrada[1]
        ano_entrada = data_entrada[2]
        dia_alta = data_alta[0]
        mes_alta = data_alta[1]
        ano_alta = data_alta[2]
        periodo = dia_entrada
        if ano_entrada == ano_alta:
            if mes_entrada == mes_alta:
                periodo += f' a {dia_alta}/{mes_alta}'
            else:
                periodo += f'/{mes_alta} a {dia_alta}/{mes_alta}'
        else:
            periodo = f'{item.DATA} a {item.DATAALTA}'
        update_stay(item.ID, periodo)
    return periodo



def get_gv_school_id(id_house):
    old_id = get_nd_school_id(id_house)
    cursor = connection.cursor()
    cursor.execute("SELECT GVCODIGO FROM NDSISTEMAS.dbo.ESTABELECIMENTOS "
                   "WHERE CODIGO = '%s'" % old_id)
    sql_data = namedtuplefetchall(cursor)
    school_id = sql_data[0].GVCODIGO
    return school_id


def get_employees_data(id_school, slctd_year):
    cursor = connection.cursor()
    if id_school != 15:
        cursor.execute("SELECT RHCONTRATOS.CONTRATO,"
                       "       NOME,"
                       "       RHFUNCOES.DESCRICAO40,"
                       "       RHCONTRATOS.HORASCONTRATUAIS,"
                       "       RHCONTRATOS.TIPOCONTRATO,"
                       "       FORMAT(RHCONTRATOS.DATAADMISSAO,'dd/MM/yyyy') DATAADMISSAO,"
                       "       YEAR(RHCONTRATOS.DATAADMISSAO) YEAR_AD,"
                       "       FORMAT(RHCONTRATOS.DATARESCISAO,'dd/MM/yyyy') DATARESCISAO,"
                       "       YEAR(RHCONTRATOS.DATARESCISAO) YEAR_RE,"
                       "       RHCONTRATOS.SINDICATO,"
                       "       RHCONTRATOS.DATAULTIMOAFASTAMENTO,"
                       "       CAUSAAFASTFOLHA,"
                       "       RHCONTRATOS.DATARETORNOREINTEGRA,"
                       "       RHPESSOAS.SEXO, "
                       "       RHCONTRATOS.CLASSIFICACAOCONTABIL "
                       "FROM Nd_Folha_SIRH.DBO.RHPESSOAS"
                       "    INNER JOIN Nd_Folha_SIRH.DBO.RHCONTRATOS"
                       "        ON RHPESSOAS.PESSOA = RHCONTRATOS.PESSOA"
                       "           AND RHCONTRATOS.UNIDADE = %s"
                       "    INNER JOIN Nd_Folha_SIRH.DBO.RHFUNCOES"
                       "        ON RHFUNCOES.FUNCAO = RHCONTRATOS.FUNCAO "
                       "WHERE RHCONTRATOS.CONTRATO IN ("
                       "                                  SELECT CONTRATO"
                       "                                  FROM Nd_Folha_SIRH.DBO.RHVDBFOLHA"
                       "                                      INNER JOIN Nd_Folha_SIRH.DBO.RHVDB"
                       "                                          ON RHVDB.VDB = RHVDBFOLHA.VDB"
                       "                                  WHERE UNIDADE = %s"
                       "                                        AND YEAR(DATAFOLHA) = '%s'"
                       "                              )"
                       " AND LEFT(CONTRATO, 1) <> 9"
                       " AND RHCONTRATOS.DATATERMINOSUBCONTRATO IS NULL "
                       "ORDER BY RHPESSOAS.NOME" % (id_school, id_school, slctd_year))
    else:
        cursor.execute("SELECT RHCONTRATOS.CONTRATO,"
                       "       RHCONTRATOS.UNIDADE,"
                       "       NOME,"
                       "       RHFUNCOES.DESCRICAO40,"
                       "       RHCONTRATOS.HORASCONTRATUAIS,"
                       "       RHCONTRATOS.TIPOCONTRATO,"
                       "       FORMAT(RHCONTRATOS.DATAADMISSAO,'dd/MM/yyyy') DATAADMISSAO,"
                       "       YEAR(RHCONTRATOS.DATAADMISSAO) YEAR_AD,"
                       "       FORMAT(RHCONTRATOS.DATARESCISAO,'dd/MM/yyyy') DATARESCISAO,"
                       "       YEAR(RHCONTRATOS.DATARESCISAO) YEAR_RE,"
                       "       RHCONTRATOS.SINDICATO,"
                       "       RHCONTRATOS.DATAULTIMOAFASTAMENTO,"
                       "       CAUSAAFASTFOLHA,"
                       "       RHCONTRATOS.DATARETORNOREINTEGRA,"
                       "       RHPESSOAS.SEXO, "
                       "       RHCONTRATOS.CLASSIFICACAOCONTABIL "
                       "FROM Nd_Folha_SIRH.DBO.RHPESSOAS"
                       "    INNER JOIN Nd_Folha_SIRH.DBO.RHCONTRATOS"
                       "        ON RHPESSOAS.PESSOA = RHCONTRATOS.PESSOA"
                       "           AND RHCONTRATOS.UNIDADE IN (15, 1)"
                       "    INNER JOIN Nd_Folha_SIRH.DBO.RHFUNCOES"
                       "        ON RHFUNCOES.FUNCAO = RHCONTRATOS.FUNCAO "
                       "WHERE RHCONTRATOS.CONTRATO IN ("
                       "                                  SELECT CONTRATO"
                       "                                  FROM Nd_Folha_SIRH.DBO.RHVDBFOLHA"
                       "                                      INNER JOIN Nd_Folha_SIRH.DBO.RHVDB"
                       "                                          ON RHVDB.VDB = RHVDBFOLHA.VDB"
                       "                                  WHERE UNIDADE IN (15, 1)"
                       "                                        AND YEAR(DATAFOLHA) = '%s'"
                       "                              )"
                       " AND LEFT(CONTRATO, 1) <> 9"
                       " AND RHCONTRATOS.DATATERMINOSUBCONTRATO IS NULL "
                       "ORDER BY RHPESSOAS.NOME" % slctd_year)
    employees_list = namedtuplefetchall(cursor)

    return employees_list


def get_house_data(id_house, slctd_year):
    cursor = connection.cursor()
    cursor.execute("SELECT A.ID, A.IDCASA, A.ANO, A.SUMARIO1, A.SUMARIO2,"
                   " NOMEINSTITUICAO, CIDADEINSTITUICAO,NOMECASA, CIDADECASA"
                   " FROM Z_LENIMAR.DBO.ANAIS A INNER JOIN Z_LENIMAR.DBO.ANAISCAPA AC ON A.IDCASA = AC.IDCASA"
                   " WHERE A.IDCASA='%s' AND ANO='%s'" % (id_house, slctd_year)
                   )
    sql_data = namedtuplefetchall(cursor)
    return sql_data


def get_cover_data(id_house, slctd_year):
    cursor = connection.cursor()
    cursor.execute("SELECT A.ID, A.IDCASA, A.ANO, A.SUMARIO1, A.SUMARIO2,"
                   " NOMEINSTITUICAO, CIDADEINSTITUICAO,NOMECASA, CIDADECASA"
                   " FROM Z_LENIMAR.DBO.ANAIS A INNER JOIN Z_LENIMAR.DBO.ANAISCAPA AC ON A.IDCASA = AC.IDCASA"
                   " WHERE A.IDCASA='%s' AND ANO='%s'" % (id_house, slctd_year)
                   )
    sql_data = namedtuplefetchall(cursor)
    return sql_data


def get_status_data(id_annals, slctd_year):
    cursor = connection.cursor()
    cursor.execute("SELECT CODIGOND,NOMERELIGIOSO,NOMEBATISMO,OFICIO.OFICIODESCRICAO,OFICIO.OFICIOTIPO,OFICIO.ORDEM"
                   " FROM ND_PROVINCIA.DBO.IRMAS IRMAS"
                   " INNER JOIN Z_LENIMAR.DBO.ANAISIRMAOFICIO OFICIO ON OFICIO.IDIRMA=IRMAS.CODIGOND"
                   " INNER JOIN Z_LENIMAR.DBO.ANAIS ANAIS ON ANAIS.ID=OFICIO.IDANAIS"
                   " WHERE OFICIO.IDANAIS='%s' AND OFICIOTIPO IN (0,1) AND ANAIS.ANO='%s' ORDER BY ORDEM" % (id_annals,
                                                                                                             slctd_year))
    status_data = namedtuplefetchall(cursor)
    return status_data


def get_transference_data(id_annals):
    cursor = connection.cursor()
    cursor.execute("SELECT IDANAIS,NOME,SITUACAO,LOCAL "
                   "FROM Z_LENIMAR.DBO.ANAISTRANSFERENCIA "
                   "WHERE IDANAIS='%s'" % id_annals)
    status_data = namedtuplefetchall(cursor)
    return status_data


def get_io_data(slctd_year, id_house):
    cursor = connection.cursor()
    print(str(id_house))
    cursor.execute("SELECT NOMERELIGIOSO,CONVERT(CHAR,SAIDACONGREGACAO,103) AS SAIDACONGREGACAO,"
                   "CONVERT(CHAR,DATAEXCLAUSTRACAO,103) AS DATAEXCLAUSTRACAO,"
                   "CONVERT(CHAR,RETORNOEXCLAUSTRACAO,103) AS RETORNOEXCLAUSTRACAO,"
                   "OBSSAIDA,"
                   "YEAR(SAIDACONGREGACAO) AS ANOSAIDA,"
                   "YEAR(DATAEXCLAUSTRACAO) AS ANOEXCLAUSTRACAO"
                   " FROM ND_PROVINCIA.DBO.IRMAS"
                   " WHERE (YEAR(SAIDACONGREGACAO)='%s' OR (YEAR(DATAEXCLAUSTRACAO)='%s'))"
                   " AND CASAATUAL='%s'" % (slctd_year, slctd_year, id_house))
    io_data = namedtuplefetchall(cursor)
    return io_data


def get_deaths_data(id_house, slctd_year):
    cursor = connection.cursor()
    cursor.execute("SELECT CODIGOND,NOMERELIGIOSO,"
                   "       FORMAT(DATAMORTE,'dd/MM/yyyy') DATAMORTE"
                   " FROM ND_PROVINCIA.DBO.IRMAS"
                   " WHERE YEAR(DATAMORTE)='%s' AND CASAATUAL IN ("
                   " SELECT CODIGO FROM ND_PROVINCIA.DBO.TCASAS WHERE CODIGO='%s')"
                   " ORDER BY DATAMORTE" % (slctd_year, id_house))
    deaths_data = namedtuplefetchall(cursor)
    return deaths_data


def get_healthcare_data(slctd_year):
    cursor = connection.cursor()
    cursor.execute("SELECT P.CODIGOND,"
                   "       M.ID,"
                   "       P.NOME,"
                   "       P.LOCALTRABALHO,"
                   "       M.PERIODO AS PERIODO,"
                   "       FORMAT(M.DATA,'dd/MM/yyyy') DATA,"
                   "       FORMAT(M.DATAALTA,'dd/MM/yyyy') DATAALTA,"
                   "       M.DESCRICAO"
                   " FROM ND_SAUDE.DBO.PACIENTES AS P,"
                   "     ND_SAUDE.DBO.MOVIMENTO AS M"
                   " WHERE M.TIPO = 2"
                   "      AND M.IDPACIENTE = P.CODIGOND"
                   "      AND YEAR(M.DATA) = '%s'"
                   " ORDER BY DATA" % slctd_year)
    healthcare_data = namedtuplefetchall(cursor)
    print('healtcare ins: ' + str(len(healthcare_data)))
    return healthcare_data


def get_outpatient_data(slctd_year):
    cursor = connection.cursor()
    cursor.execute("SELECT P.CODIGOND AS CODIGOND,"
                   "       P.NOME AS NOME,"
                   "       M.DESCRICAO AS DESCRICAO,"
                   "       MED.NOME AS MEDICO,"
                   "       H.NOME AS HOSPITAL,"
                   "       C.NOME AS CIDADE,"
                   "       C.ESTADO AS UF,"
                   "	   COUNT(1) AS QUANT"
                   " FROM ND_SAUDE.DBO.HOSPITAIS AS H,"
                   "     ND_SAUDE.DBO.MEDICOS AS MED,"
                   "     ND_SAUDE.DBO.PACIENTES AS P,"
                   "     ND_SAUDE.DBO.MOVIMENTO AS M,"
                   "     ND_SAUDE.DBO.CIDADES AS C"
                   " WHERE M.TIPO = 3"
                   "      AND M.IDMEDICO = MED.ID"
                   "      AND YEAR(M.DATA) = '%s'"
                   "      AND M.LOCAL = H.ID"
                   "      AND M.IDPACIENTE = P.CODIGOND"
                   "      AND C.ID = H.CIDADE"
                   " GROUP BY P.CODIGOND,"
                   "      P.NOME,"
                   "      M.DESCRICAO,"
                   "      MED.NOME,"
                   "      H.NOME,"
                   "      C.NOME,"
                   "      C.ESTADO" % slctd_year)
    outpatient_data = namedtuplefetchall(cursor)
    return outpatient_data


def get_healthcare_summary_data(id_annals):
    cursor = connection.cursor()
    cursor.execute("SELECT IDANAIS,"
                   "       ITEM,"
                   "       DESCRICAO,"
                   "       QTDE"
                   " FROM ND_SAUDE.DBO.ANAISPROCEDIMENTOS"
                   " WHERE IDANAIS = '%s'"
                   " ORDER BY ID" % id_annals)
    outpatient_data = namedtuplefetchall(cursor)
    return outpatient_data


def get_medical_care_data(id_annals, id_house):
    cursor = connection.cursor()
    cursor.execute("SELECT NOME,"
                   "       ATIVIDADE,"
                   "       QTDE"
                   " FROM Z_LENIMAR.DBO.ANAISOUTROSCOLABORADORES"
                   " WHERE IDANAIS = '%s'"
                   "      AND IDCASA = '%s'"
                   "      AND NOME LIKE '%s'"
                   " ORDER BY ID" % (id_annals, id_house, '%Dr%'))
    medical_care_data = namedtuplefetchall(cursor)
    return medical_care_data


def get_other_helpers_data(id_annals, id_house):
    cursor = connection.cursor()
    cursor.execute("SELECT IDCASA,"
                   "       IDANAIS,"
                   "       NOME,"
                   "       ATIVIDADE"
                   " FROM Z_LENIMAR.DBO.ANAISOUTROSCOLABORADORES"
                   " WHERE IDANAIS = '%s'"
                   "      AND IDCASA = '%s'"
                   "      AND NOME LIKE '%s'"
                   " ORDER BY ID" % (id_annals, id_house, '%irmã%'))
    other_helpers_data = namedtuplefetchall(cursor)
    return other_helpers_data


def get_surgical_data(slctd_year):
    cursor = connection.cursor()
    cursor.execute("SELECT P.CODIGOND AS CODIGOND,"
                   "       P.NOME AS NOME,"
                   "       M.DESCRICAO AS DESCRICAO,"
                   "       MED.NOME AS MEDICO,"
                   "       H.NOME AS HOSPITAL,"
                   "       C.NOME AS CIDADE,"
                   "       C.ESTADO AS UF"
                   " FROM ND_SAUDE.DBO.HOSPITAIS AS H,"
                   "     ND_SAUDE.DBO.MEDICOS AS MED,"
                   "     ND_SAUDE.DBO.PACIENTES AS P,"
                   "     ND_SAUDE.DBO.MOVIMENTO AS M,"
                   "     ND_SAUDE.DBO.CIDADES AS C"
                   " WHERE M.TIPO = 1"
                   "      AND M.IDMEDICO = MED.ID"
                   "      AND YEAR(M.DATA) = '%s'"
                   "      AND M.LOCAL = H.ID"
                   "      AND M.IDPACIENTE = P.CODIGOND"
                   "      AND C.ID = H.CIDADE"
                   " ORDER BY M.DATA" % slctd_year)
    surgical_data = namedtuplefetchall(cursor)
    return surgical_data


def get_resident_data(id_house):
    cursor = connection.cursor()
    cursor.execute("SELECT IDCASA,"
                   "       FORMAT(DATAENTRADA,'dd/MM/yyyy') DATAENTRADA,"
                   "       NOME,"
                   "       OBSERVACAO"
                   " FROM Z_LENIMAR.DBO.ANAISRESIDENTESRECANTO"
                   " WHERE DATASAIDA IS NULL"
                   " AND IDCASA = '%s' " % id_house)
    residents_data = namedtuplefetchall(cursor)
    return residents_data


def get_activities(id_annals, id_house):
    print('id_annals' + str(id_annals))
    print('id_house' + str(id_house))
    cursor = connection.cursor()
    cursor.execute("SELECT IDANAIS, IDCASA"
                   ", ANO, ATIVIDADEPRINCIPAL"
                   ", ATIVIDADESTERCEIRIZADAS"
                   ", OUTRASATIVIDADES"
                   " FROM Z_LENIMAR.DBO.ANAISATIVIDADESCASAS"
                   " WHERE IDANAIS='%s'"
                   " AND IDCASA='%s'" % (id_annals, id_house))
    activities_data = namedtuplefetchall(cursor)
    return activities_data


def get_events(id_annals):
    cursor = connection.cursor()
    cursor.execute("SELECT FORMAT(DATA, 'dd/MM/yyyy') AS DATA,"
                   "       PERIODO,"
                   "       LOCAL,"
                   "       ATIVIDADE.NOME AS ATIVIDADE,"
                   "       RESPONSAVEL,"
                   "       NUMPARTICIPANTES,"
                   "       ANAIS.IDATIVIDADEOBS,"
                   "       OBS.ID,"
                   "       OBS.DESCRICAO,"
                   "       OBS.APARECE"
                   " FROM Z_LENIMAR.DBO.ANAISATIVIDADES ANAIS"
                   "    INNER JOIN Z_LENIMAR.DBO.ATIVIDADE"
                   "        ON ATIVIDADE.ID = ANAIS.IDATIVIDADE"
                   "    LEFT JOIN Z_LENIMAR.DBO.ANAISOBSERVACAOATIVIDADE OBS"
                   "        ON OBS.ID = ANAIS.IDATIVIDADEOBS"
                   " WHERE IDANAIS = '%s'"
                   " ORDER BY IDATIVIDADEOBS,"
                   "         DATA" % id_annals)
    activities_data = namedtuplefetchall(cursor)
    return activities_data


def get_pastoral_activities(id_annals, id_house):
    cursor = connection.cursor()
    cursor.execute("SELECT ATIVIDADES.ID,"
                   "       IDANAIS,"
                   "       IDCASA,"
                   "       CASAS.NOME AS NOMECASA,"
                   "       ANO,"
                   "       ATIVIDADES.NOME AS NOME,"
                   "       PUBLICOALVO,"
                   "       NUMATINGIDO"
                   " FROM Z_LENIMAR.DBO.ANAISATIVIDADESPASTORAIS ATIVIDADES"
                   "    INNER JOIN Z_LENIMAR.DBO.ANAIS ANAIS"
                   "        ON ANAIS.ID = ATIVIDADES.IDANAIS"
                   "    INNER JOIN ND_PROVINCIA.DBO.TCASAS CASAS"
                   "        ON CASAS.CODIGO = ANAIS.IDCASA"
                   " WHERE IDANAIS = %s"
                   "      AND IDCASA = %s" % (id_annals, id_house))
    pastoral_activities = namedtuplefetchall(cursor)
    return pastoral_activities


def get_students_data(id_house, slctd_year):
    id_partner = get_gv_school_id(id_house)
    cursor = connection.cursor()
    cursor.execute("SELECT CODIGOUNIDADE, NOME_REDUZIDO, CURSO, SERIE"
                   ", COUNT(CASE WHEN SEXO = 'M' AND"
                   "				  SITUACAOALUNO = 'ATIVO' THEN 1 END) MASC"
                   ", COUNT(CASE WHEN SEXO = 'F' AND"
                   "				  SITUACAOALUNO = 'ATIVO' THEN 1 END) FEM"
                   ", COUNT(CASE WHEN SITUACAOALUNO = 'CANCELADO' OR"
                   "				  SITUACAOALUNO = 'TRANSFERIDO' THEN 1 END) CANC"
                   ", COUNT(CASE WHEN SITUACAOALUNO = 'ATIVO' THEN 1 END) ATIVO"
                   ", COUNT(MATRICULA) TOTAL"
                   " FROM BI_Suporte_Decisao.dbo.ANALISE_DADOS_CADASTRAIS A"
                   " WHERE ANO = '%s' AND CODIGOUNIDADE = '%s'"
                   "AND CURSO IN ('Ensino Fundamental II','Ensino Médio','Ensino Fundamental I'"
                   ",'Educação Infantil','Educacao Infantil', 'Novo Ensino Médio')"
                   "GROUP BY CODIGOUNIDADE"
                   ",NOME_REDUZIDO, CURSO, SERIE"
                   " ORDER BY"
                   " NOME_REDUZIDO"
                   ",CURSO"
                   ",SERIE;" % (slctd_year, id_partner))
    sql_data = namedtuplefetchall(cursor)
    return sql_data


def get_story_data(id_house, id_annals, slctd_year):
    cursor = connection.cursor()
    str_query = 'SELECT DESCRICAO1 AS DESCRICAO1,' \
                ' DESCRICAO2 AS DESCRICAO2,' \
                ' DESCRICAO3 AS DESCRICAO3,' \
                ' TITULO, PERIODO' \
                ' FROM Z_LENIMAR.DBO.ANAISNARRATIVA' \
                ' WHERE IDANAIS=' + str(id_annals) + ' AND' \
                                                     ' IDCASA=' + str(
        id_house) + ' AND ANO=' + slctd_year + ' ORDER BY DATAINICIO'
    print(str_query)
    cursor.execute(str_query)
    story_data = namedtuplefetchall(cursor)
    return story_data


# @method_decorator(login_required, name='dispatch')
class ReportsView(TemplateView):
    template_name = 'reports.html'

    def get_context_data(self, **kwargs):
        context = super(ReportsView, self).get_context_data(**kwargs)
        day = datetime.now().day
        month = datetime.now().month
        quotes = get_quotes(day, month)
        id_house = self.kwargs['id_house']
        slctd_year = self.kwargs['slctd_year']
        house_data = get_house_data(id_house, slctd_year)
        quote = quotes[0].PENSAMENTO
        author = quotes[0].AUTORIA
        context['doc_title'] = 'Reports'
        context['top_app_name'] = 'Reports'
        context['pt_h1'] = 'Sumário Estatístico'
        context['pt_span'] = ''
        context['pt_breadcrumb2'] = 'Reports'
        context['quote'] = quote
        context['author'] = author
        context['sql_data'] = house_data
        context['id_annals'] = self.kwargs['id_annals']
        return context


class PrintCoverView(View):
    def get(self, request, *args, **kwargs):
        id_house = self.kwargs['id_house']
        slctd_year = self.kwargs['slctd_year']
        sql_data = get_cover_data(id_house, slctd_year)
        inst_name = sql_data[0].NOMEINSTITUICAO.strip()
        inst_city = sql_data[0].CIDADEINSTITUICAO.strip()
        inst_city = ''.join(inst_city.split())
        inst_uf = inst_city[-2:]
        inst_city = inst_city[:-3]
        house_name = sql_data[0].NOMECASA.strip()
        house_city = sql_data[0].CIDADECASA.strip()
        i = Image('https://otordame.sirv.com/Images/notre_dame/v02.png')
        i.drawHeight = 2 * cm
        i.drawWidth = 3 * cm

        response = HttpResponse(content_type='application/pdf')
        doc = SimpleDocTemplate(response, topMargin=2.5 * cm, rightMargin=3 * cm, leftMargin=3 * cm,
                                bottomMargin=2.5 * cm)

        # Style
        h1 = PS(
            name='Heading1',
            fontName='Times-Bold',
            alignment=TA_CENTER,
            fontSize=14,
            leading=18)

        # Body
        elements = [Paragraph(inst_name.title(), h1),
                    Paragraph(inst_city.title() + ' - ' + inst_uf.upper(), h1),
                    Spacer(1, 1.5 * cm),
                    i,
                    Spacer(1, 5 * cm),
                    Paragraph("ANAIS", h1),
                    Paragraph("Comunidade " + house_name.title(), h1),
                    Spacer(1, 11.5 * cm), Paragraph(house_city, h1),
                    Paragraph(slctd_year, h1)]
        buffer = BytesIO()
        doc.title = house_name + ' | ' + slctd_year + ' - Capa'

        report = MyPrint(buffer, 'A4')

        response.write(doc.build(elements))

        return response


class PrintStatisticsView(View):
    def get(self, request, *args, **kwargs):
        id_house = self.kwargs['id_house']
        slctd_year = self.kwargs['slctd_year']
        id_annals = self.kwargs['id_annals']
        status_data = get_status_data(id_annals, slctd_year)
        start_data = []
        end_data = []
        for a in status_data:
            if a.OFICIOTIPO == 0:
                start_data.append(a)
            else:
                end_data.append(a)

        id_school = get_nd_school_id(id_house)
        recanto = False
        school = True
        employer = True
        if id_school is None:
            school = employer = False
        if id_school in (7, 15, 1):
            school = False
            employer = True
            if id_school == 15:
                recanto = True

        general_data = get_cover_data(id_house, slctd_year)

        transference_data = get_transference_data(id_annals)

        ins_outs_data = get_io_data(slctd_year, id_house)

        deaths_data = get_deaths_data(id_house, slctd_year)

        pastoral_activities = get_pastoral_activities(id_annals, id_house)

        if employer:
            employees_data = get_employees_data(id_school, slctd_year)
            teatcher = []
            regular = []
            for a in employees_data:
                # TODO: Remover as linhas abaixo até a marcação, após atualização da
                #  consulta nos contratos de trabalho
                if a.NOME.title() == 'Tais Streb Artmann':
                    if slctd_year in ('2020', '2021', '2023'):
                        regular.append(a)
                    else:
                        teatcher.append(a)
                else:
                    if a.SINDICATO == '0001':
                        teatcher.append(a)
                    else:
                        regular.append(a)
                # ------ #
                # TODO: Retornar trecho abaixo após correção
                # if a.SINDICATO == '0001':
                #     teatcher.append(a)
                # else:
                #     regular.append(a)
        activities_data = get_activities(id_annals, id_house)

        if school:
            students = get_students_data(id_house, slctd_year)
            male = 0
            female = 0
            canceled = 0
            active = 0
            general = 0
            for item in students:
                male += item.MASC
                female += item.FEM
                canceled += item.CANC
                active += item.ATIVO
                general += item.TOTAL

        story_data = get_story_data(id_house, id_annals, slctd_year)

        inst_name = general_data[0].NOMEINSTITUICAO.strip()
        inst_city = general_data[0].CIDADEINSTITUICAO.strip()
        inst_city = ''.join(inst_city.split())
        inst_uf = inst_city[-2:]
        inst_city = inst_city[:-3]
        house_name = general_data[0].NOMECASA.strip()
        house_city = general_data[0].CIDADECASA.strip()
        house_city = ''.join(house_city.split())
        house_uf = house_city[-2:]
        house_city = house_city[:-3]
        summary_1 = general_data[0].SUMARIO1.strip()
        summary_2 = general_data[0].SUMARIO2.strip()

        response = HttpResponse(content_type='application/pdf')
        doc = SimpleDocTemplate(response, topMargin=1.8 * cm, rightMargin=2.5 * cm, leftMargin=2.5 * cm,
                                bottomMargin=2 * cm)

        # Style
        h1 = PS(
            name='Heading1',
            fontName='Times-Bold',
            alignment=TA_LEFT,
            fontSize=12,
            leading=14)

        h2 = PS(
            name='Heading2',
            fontName='Times-Bold',
            alignment=TA_CENTER,
            fontSize=12,
            leading=14)

        c1 = PS(
            name='Cell1',
            fontName='Times-Roman',
            alignment=TA_JUSTIFY,
            fontSize=12,
            leading=14)

        c2 = PS(
            name='Cell2',
            fontName='Times-Roman',
            alignment=TA_LEFT,
            fontSize=12,
            leading=14)

        n_session = 1

        # Body
        elements = [Paragraph('I - SUMÁRIO ESTATÍSTICO', h1),
                    Spacer(1, 0.25 * cm),
                    Paragraph(str(n_session) + '. Número de Irmãs no início do ano letivo', h1),
                    Spacer(1, 0.25 * cm),
                    Paragraph(summary_1, c1),
                    Spacer(1, 0.25 * cm)]
        ###
        n_session += 1
        elements.append(Paragraph(str(n_session) + '. Relação das Irmãs', h1))
        elements.append(Spacer(1, 0.25 * cm))
        count = 0
        for a in start_data:
            count += 1
            data = [[Paragraph(str(count), c2),
                     Paragraph(a.NOMERELIGIOSO.title() + '<br />(' + a.NOMEBATISMO.title() + ')', c2),
                     '-',
                     Paragraph(a.OFICIODESCRICAO, c1)]]
            t = Table(data, colWidths=[25.0, 170.0, 15.0, 245.0])
            t.setStyle(TableStyle([('ALIGN', (0, 0), (1, 0), 'LEFT'),
                                   ('ALIGN', (1, 0), (3, 0), 'CENTRE'),
                                   ('VALIGN', (0, 0), (3, 0), 'TOP'),
                                   ]))
            elements.append(t)
            elements.append(Spacer(1, 0.25 * cm))
        ##
        n_session += 1
        elements.append(Spacer(1, 0.25 * cm))
        elements.append(Paragraph(str(n_session) + '. Transferências durante o ano', h1))
        elements.append(Spacer(1, 0.25 * cm))

        if len(transference_data) == 0 and len(ins_outs_data) == 0:
            elements.append(Paragraph('Não houve transferência ao longo do ano', c1))
            elements.append(Spacer(1, 0.25 * cm))
        else:
            transf = []
            arrival = []
            outs = []
            comes = []
            if len(transference_data) > 0:
                for a in transference_data:
                    if a.SITUACAO == '1':
                        transf.append(a)
                    if a.SITUACAO == '0':
                        arrival.append(a)
            if len(ins_outs_data) > 0:
                for a in ins_outs_data:
                    if str(a.ANOSAIDA) == str(slctd_year):
                        outs.append(a)
                    if str(a.ANOEXCLAUSTRACAO) == str(slctd_year):
                        comes.append(a)

            if len(transf) == 1:
                elements.append(Paragraph('a) Durante o ano a seguinte irmã foi transferida:', h1))
            else:
                elements.append(Paragraph('a) Durante o ano as seguintes irmãs foram transferidas:', h1))
            elements.append(Spacer(1, 0.25 * cm))
            count = 0
            for a in transf:
                count += 1
                data = [[Paragraph(str(count), c2),
                         Paragraph(a.NOME.title(), c2),
                         Paragraph(a.LOCAL, c1)]]
                t = Table(data, colWidths=[25.0, 185.0, 245.0])
                t.setStyle(TableStyle([('ALIGN', (0, 0), (1, 0), 'LEFT'),
                                       ('ALIGN', (1, 0), (2, 0), 'CENTRE'),
                                       ('VALIGN', (0, 0), (2, 0), 'TOP'),
                                       ]))
                elements.append(t)
                elements.append(Spacer(1, 0.25 * cm))
            elements.append(Spacer(1, 0.25 * cm))
            if len(outs) > 0:
                if len(outs) == 1:
                    elements.append(Paragraph('Durante o ano a seguinte irmã deixou a Congregação:', h1))
                else:
                    elements.append(Paragraph('Durante o ano as seguintes irmãs deixaram a Congregação:', h1))
                for a in outs:
                    elements.append(Spacer(1, 0.25 * cm))
                    elements.append(Paragraph(a.NOMERELIGIOSO.title() + ', na data de ' + a.SAIDACONGREGACAO, c1))
                    elements.append(Paragraph(a.OBSSAIDA, c1))
                    elements.append(Spacer(1, 0.25 * cm))

            if len(deaths_data) > 0:
                str_deaths = 'Durante o ano faleceu:'
                if len(deaths_data) > 1:
                    str_deaths = 'Durante o ano faleceram:'
                elements.append(Paragraph(str_deaths, h1))
                elements.append(Spacer(1, 0.25 * cm))
                count = 0
                data = [[Paragraph('', h1),
                         Paragraph('Nome', h1),
                         Paragraph('Data Falecimento', h1)]]
                t = Table(data, colWidths=[25.0, 245.0, 185.0])
                t.setStyle(TableStyle([('ALIGN', (0, 0), (1, 0), 'LEFT'),
                                       ('ALIGN', (1, 0), (2, 0), 'CENTRE'),
                                       ('VALIGN', (0, 0), (2, 0), 'TOP'),
                                       ]))
                elements.append(t)
                for a in deaths_data:
                    count += 1
                    data = [[Paragraph(str(count), c2),
                             Paragraph(a.NOMERELIGIOSO.title(), c2),
                             Paragraph(a.DATAMORTE, c2)]]
                    t = Table(data, colWidths=[25.0, 245.0, 185.0])
                    t.setStyle(TableStyle([('ALIGN', (0, 0), (1, 0), 'LEFT'),
                                           ('ALIGN', (1, 0), (2, 0), 'CENTRE'),
                                           ('VALIGN', (0, 0), (2, 0), 'TOP'),
                                           ]))
                    elements.append(t)
                    elements.append(Spacer(1, 0.25 * cm))
                elements.append(Spacer(1, 0.25 * cm))

            if len(arrival) == 1:
                elements.append(Paragraph('b) Durante o ano a seguinte irmã integrou a comunidade:', h1))
            else:
                elements.append(Paragraph('b) Durante o ano as seguintes irmãs integraram a comunidade:', h1))
            elements.append(Spacer(1, 0.25 * cm))
            count = 0
            data = [[Paragraph('', h1),
                     Paragraph('Nome', h1),
                     Paragraph('Local', h1)]]
            t = Table(data, colWidths=[25.0, 185.0, 245.0])
            t.setStyle(TableStyle([('ALIGN', (0, 0), (1, 0), 'LEFT'),
                                   ('ALIGN', (1, 0), (2, 0), 'CENTRE'),
                                   ('VALIGN', (0, 0), (2, 0), 'TOP'),
                                   ]))
            elements.append(t)
            elements.append(Spacer(1, 0.25 * cm))
            for a in arrival:
                count += 1
                data = [[Paragraph(str(count), c2),
                         Paragraph(a.NOME.title(), c2),
                         Paragraph(a.LOCAL, c1)]]
                t = Table(data, colWidths=[25.0, 185.0, 245.0])
                t.setStyle(TableStyle([('ALIGN', (0, 0), (1, 0), 'LEFT'),
                                       ('ALIGN', (1, 0), (2, 0), 'CENTRE'),
                                       ('VALIGN', (0, 0), (2, 0), 'TOP'),
                                       ]))
                elements.append(t)
                elements.append(Spacer(1, 0.25 * cm))
            elements.append(Spacer(1, 0.25 * cm))

            if len(comes) > 0:
                if len(comes) == 1:
                    elements.append(Paragraph('Durante o ano a seguinte Irmã estava exclaustrada:', h1))
                else:
                    elements.append(Paragraph('Durante o ano as seguintes Irmãs estavam exclaustradas:', h1))
                for a in comes:
                    elements.append(Spacer(1, 0.25 * cm))
                    print(a.DATAEXCLAUSTRACAO + '|')
                    elements.append(Paragraph(a.NOMERELIGIOSO.title() + ', exclaustrada desde '
                                              + a.DATAEXCLAUSTRACAO.replace(' ', '') + ', retornou em '
                                              + a.RETORNOEXCLAUSTRACAO + '.', c1))
                    elements.append(Spacer(1, 0.25 * cm))
        ##
        n_session += 1
        elements.append(Spacer(1, 0.25 * cm))
        elements.append(Paragraph(str(n_session) + '. Situação no final do ano letivo:', h1))
        elements.append(Spacer(1, 0.25 * cm))
        elements.append(Paragraph(summary_2, c1))
        elements.append(Spacer(1, 0.25 * cm))
        count = 0
        for a in end_data:
            count += 1
            data = [[Paragraph(str(count), c2),
                     Paragraph(a.NOMERELIGIOSO.title() + '<br />(' + a.NOMEBATISMO.title() + ')', c2),
                     '-',
                     Paragraph(a.OFICIODESCRICAO, c1)]]
            t = Table(data, colWidths=[25.0, 170.0, 15.0, 245.0])
            t.setStyle(TableStyle([('ALIGN', (0, 0), (1, 0), 'LEFT'),
                                   ('ALIGN', (1, 0), (3, 0), 'CENTRE'),
                                   ('VALIGN', (0, 0), (3, 0), 'TOP'),
                                   ]))
            elements.append(t)
            elements.append(Spacer(1, 0.25 * cm))

        ## RECANTO APARECIDA
        if recanto:
            ## Residentes
            resident = get_resident_data(id_house)
            res_number = str(len(resident))
            res_design = 'senhora leiga que está'
            if len(resident) > 1:
                res_design = 'senhoras leigas que estão'
            cont = 1
            elements.append(Spacer(1, 0.25 * cm))
            elements.append(Paragraph('Além das Irmãs residiram no Recanto Aparecida ' + res_number + ' ' + res_design +
                                      ' sob o cuidado das Irmãs:', h1))
            elements.append(Spacer(1, 0.25 * cm))

            for item in resident:
                data = [[Paragraph(str(cont), c2),
                         Paragraph(item.NOME, c2),
                         Paragraph(item.OBSERVACAO, c2)]]
                t = Table(data, colWidths=[25.0, 185.0, 245.0])
                t.setStyle(TableStyle([('ALIGN', (0, 0), (1, 0), 'LEFT'),
                                       ('ALIGN', (1, 0), (2, 0), 'CENTRE'),
                                       ('VALIGN', (0, 0), (2, 0), 'TOP'),
                                       ]))
                elements.append(t)
                elements.append(Spacer(1, 0.25 * cm))
                cont += 1

            ## Atendimentos de saúde
            healthcare_data = get_healthcare_data(slctd_year)
            elements.append(
                Paragraph('Irmãs da Casa Provincial e das Casas Filiais atendidas no Recanto Aparecida durante '
                          'o ano ' + slctd_year + ':', h1))
            elements.append(Spacer(1, 0.25 * cm))
            data = [[Paragraph('', h1),
                     Paragraph('Data', h1),
                     Paragraph('Nome', h1),
                     Paragraph('Tratamento', h1),
                     Paragraph('Origem', h1)]]
            t = Table(data, colWidths=[25, 60, 125, 115, 130])
            t.setStyle(TableStyle([('ALIGN', (0, 0), (1, 0), 'LEFT'),
                                   ('ALIGN', (1, 0), (4, 0), 'CENTRE'),
                                   ('VALIGN', (0, 0), (4, 0), 'TOP'),
                                   ]))
            elements.append(t)
            elements.append(Spacer(1, 0.25 * cm))
            cont = 1
            for item in healthcare_data:
                # Manage Período
                periodo = manage_stay(item)
                data = [[Paragraph(str(cont), c2),
                         Paragraph(periodo, c2),
                         Paragraph(item.NOME.title(), c2),
                         Paragraph(item.DESCRICAO, c2),
                         Paragraph(item.LOCALTRABALHO, c2)]]
                t = Table(data, colWidths=[25, 60, 125, 115, 130])
                t.setStyle(TableStyle([('ALIGN', (0, 0), (1, 0), 'LEFT'),
                                       ('ALIGN', (1, 0), (4, 0), 'CENTRE'),
                                       ('VALIGN', (0, 0), (4, 0), 'TOP'),
                                       ]))
                elements.append(t)
                elements.append(Spacer(1, 0.25 * cm))
                cont += 1

            ## Atendimento ambulatorial
            outpatient_data = get_outpatient_data(slctd_year)
            elements.append(
                Paragraph('Cirurgias e procedimentos ambulatoriais realizados ao longo do ano de ' + slctd_year
                          + ':', h1))
            elements.append(Spacer(1, 0.25 * cm))
            data = [[Paragraph('Cirurgia', h1),
                     Paragraph('Nome', h1),
                     Paragraph('Qtd', h1)]]
            t = Table(data, colWidths=[200.0, 185.0, 70.0])
            t.setStyle(TableStyle([('ALIGN', (0, 0), (1, 0), 'LEFT'),
                                   ('ALIGN', (1, 0), (2, 0), 'CENTRE'),
                                   ('VALIGN', (0, 0), (2, 0), 'TOP'),
                                   ]))
            elements.append(t)
            elements.append(Spacer(1, 0.25 * cm))
            cont = 1
            for item in outpatient_data:
                data = [[Paragraph(item.DESCRICAO, c2),
                         Paragraph(item.NOME.title(), c2),
                         Paragraph(str(item.QUANT), c2)]]
                t = Table(data, colWidths=[200.0, 185.0, 70.0])
                t.setStyle(TableStyle([('ALIGN', (0, 0), (1, 0), 'LEFT'),
                                       ('ALIGN', (1, 0), (2, 0), 'CENTRE'),
                                       ('VALIGN', (0, 0), (2, 0), 'TOP'),
                                       ]))
                elements.append(t)
                elements.append(Spacer(1, 0.25 * cm))
                cont += 1

            ## Atendimento cirúrgico
            surgical_data = get_surgical_data(slctd_year)
            elements.append(
                Paragraph('Internações cirúrgicas e clínicas realizadas ao longo do ano de ' + slctd_year + ':', h1))
            elements.append(Spacer(1, 0.25 * cm))
            data = [[Paragraph('', h1),
                     Paragraph('Nome', h1),
                     Paragraph('Procedimento', h1),
                     Paragraph('Médico', h1),
                     Paragraph('Local', h1)]]
            t = Table(data, colWidths=[25, 100, 120, 105, 105])
            t.setStyle(TableStyle([('ALIGN', (0, 0), (1, 0), 'LEFT'),
                                   ('ALIGN', (1, 0), (4, 0), 'CENTRE'),
                                   ('VALIGN', (0, 0), (4, 0), 'TOP'),
                                   ]))
            elements.append(t)
            elements.append(Spacer(1, 0.25 * cm))
            cont = 1
            for item in surgical_data:
                data = [[Paragraph(str(cont), c2),
                         Paragraph(item.NOME.title(), c2),
                         Paragraph(item.DESCRICAO, c2),
                         Paragraph(item.MEDICO.title(), c2),
                         Paragraph(item.CIDADE.title() + '-' + item.UF, c2)]]
                t = Table(data, colWidths=[25, 100, 120, 105, 105])
                t.setStyle(TableStyle([('ALIGN', (0, 0), (1, 0), 'LEFT'),
                                       ('ALIGN', (1, 0), (4, 0), 'CENTRE'),
                                       ('VALIGN', (0, 0), (4, 0), 'TOP'),
                                       ]))
                elements.append(t)
                elements.append(Spacer(1, 0.25 * cm))
                cont += 1

            ## Emergência ambulatorial
            healthcare_summary_data = get_healthcare_summary_data(id_annals)
            previous_item = None
            active_item = None
            for item in healthcare_summary_data:
                active_item = item.ITEM
                QTD = item.QTDE
                if item.QTDE == 0:
                    QTD = 1
                if active_item != previous_item:
                    data = [[Paragraph(item.ITEM.upper(), h1),
                             Paragraph('', h1),
                             Paragraph('', h1)]]
                    t = Table(data, colWidths=[290.0, 70.0, 95.0])
                    t.setStyle(TableStyle([('ALIGN', (0, 0), (1, 0), 'LEFT'),
                                           ('ALIGN', (1, 0), (2, 0), 'CENTRE'),
                                           ('VALIGN', (0, 0), (2, 0), 'TOP'),
                                           ]))
                    elements.append(t)
                    elements.append(Spacer(1, 0.25 * cm))
                    previous_item = item.ITEM
                else:
                    data = [[Paragraph(item.DESCRICAO, c1),
                             Paragraph('-', c1),
                             Paragraph(str(QTD), c1)]]
                    t = Table(data, colWidths=[290.0, 70.0, 95.0])
                    t.setStyle(TableStyle([('ALIGN', (0, 0), (1, 0), 'LEFT'),
                                           ('ALIGN', (1, 0), (2, 0), 'CENTRE'),
                                           ('VALIGN', (0, 0), (2, 0), 'TOP'),
                                           ]))
                    elements.append(t)
                    elements.append(Spacer(1, 0.25 * cm))
                    previous_item = item.ITEM

            ## Atendimentos x médico
            medical_care_data = get_medical_care_data(id_annals, id_house)
            previous_item = None
            active_item = None
            for item in medical_care_data:
                active_item = item.NOME
                if active_item != previous_item:
                    data = [[Paragraph(item.NOME, h1),
                             Paragraph('', h1),
                             Paragraph('', h1)]]
                    t = Table(data, colWidths=[290.0, 70.0, 95.0])
                    t.setStyle(TableStyle([('ALIGN', (0, 0), (1, 0), 'LEFT'),
                                           ('ALIGN', (1, 0), (2, 0), 'CENTRE'),
                                           ('VALIGN', (0, 0), (2, 0), 'TOP'),
                                           ]))
                    elements.append(t)
                    elements.append(Spacer(1, 0.25 * cm))
                    data = [[Paragraph(item.ATIVIDADE, c1),
                             Paragraph('-', c1),
                             Paragraph(str(item.QTDE), c1)]]
                    t = Table(data, colWidths=[290.0, 70.0, 95.0])
                    t.setStyle(TableStyle([('ALIGN', (0, 0), (1, 0), 'LEFT'),
                                           ('ALIGN', (1, 0), (2, 0), 'CENTRE'),
                                           ('VALIGN', (0, 0), (2, 0), 'TOP'),
                                           ]))
                    elements.append(t)
                    elements.append(Spacer(1, 0.25 * cm))
                    previous_item = item.NOME
                else:
                    data = [[Paragraph(item.ATIVIDADE, c1),
                             Paragraph('-', c1),
                             Paragraph(str(item.QTDE), c1)]]
                    t = Table(data, colWidths=[290.0, 70.0, 95.0])
                    t.setStyle(TableStyle([('ALIGN', (0, 0), (1, 0), 'LEFT'),
                                           ('ALIGN', (1, 0), (2, 0), 'CENTRE'),
                                           ('VALIGN', (0, 0), (2, 0), 'TOP'),
                                           ]))
                    elements.append(t)
                    elements.append(Spacer(1, 0.25 * cm))
                    previous_item = item.NOME

            ## Outros colaboradores
            other_helpers_data = get_other_helpers_data(id_annals, id_house)
            elements.append(Paragraph('Irmãs de outras comunidades que colaboraram na comunidade Recanto Aparecida em'
                                      ' ' + slctd_year + ':', h1))
            elements.append(Spacer(1, 0.25 * cm))
            data = [[Paragraph('', h1),
                     Paragraph('Nome', h1),
                     Paragraph('Atividade', h1)]]
            t = Table(data, colWidths=[25, 145, 285])
            t.setStyle(TableStyle([('ALIGN', (0, 0), (1, 0), 'LEFT'),
                                   ('ALIGN', (1, 0), (2, 0), 'CENTRE'),
                                   ('VALIGN', (0, 0), (2, 0), 'TOP'),
                                   ]))
            elements.append(t)
            elements.append(Spacer(1, 0.25 * cm))
            cont = 1
            for item in other_helpers_data:
                data = [[Paragraph(str(cont), c2),
                         Paragraph(item.NOME, c2),
                         Paragraph(item.ATIVIDADE, c2)]]
                t = Table(data, colWidths=[25, 145, 285])
                t.setStyle(TableStyle([('ALIGN', (0, 0), (1, 0), 'LEFT'),
                                       ('ALIGN', (1, 0), (2, 0), 'CENTRE'),
                                       ('VALIGN', (0, 0), (2, 0), 'TOP'),
                                       ]))
                elements.append(t)
                elements.append(Spacer(1, 0.25 * cm))
                cont += 1

        if employer:
            if recanto:
                n_session += 1
                emp_sede = []
                emp_org = []
                for item in regular:
                    if item.UNIDADE == '0001':
                        if item.CLASSIFICACAOCONTABIL == '007':
                            emp_sede.append(item)
                    if item.UNIDADE == '0015':
                        emp_org.append(item)
                elements.append(Paragraph(str(n_session) + '. Relação do pessoal leigo:', h1))
                elements.append(Spacer(1, 0.25 * cm))

                man = 0
                woman = 0
                emp_total = 0
                for a in emp_sede:
                    if a.SEXO == 'M':
                        man += 1
                    else:
                        woman += 1
                for b in emp_org:
                    if a.SEXO == 'M':
                        man += 1
                    else:
                        woman += 1
                emp_total = man + woman

                elements.append(Spacer(1, 0.25 * cm))
                elements.append(
                    Paragraph('b) Além das Irmãs, trabalharam em nossa Casa %s funcionários leigos: %s masculinos'
                              ' e %s femininas.' % (emp_total, man, woman), c1))
                elements.append(Spacer(1, 0.25 * cm))
                elements.append(
                    Paragraph('Funcionários contratados pela Organização Religiosa Santa Júlia', c1))
                elements.append(Spacer(1, 0.25 * cm))
                count = 0
                data = [[Paragraph('Nº', h1),
                         Paragraph('Funcionário', h1),
                         Paragraph('Função', h1),
                         Paragraph('C/H', h1)]]
                t = Table(data, colWidths=[35.0, 190.0, 180.0, 50.0])
                t.setStyle(TableStyle([('ALIGN', (0, 0), (1, 0), 'LEFT'),
                                       ('ALIGN', (1, 0), (3, 0), 'CENTRE'),
                                       ('VALIGN', (0, 0), (3, 0), 'TOP'),
                                       ('INNERGRID', (0, 0), (3, 0), 0.15, black),
                                       ('BOX', (0, 0), (3, 0), 0.15, black),
                                       ]))
                elements.append(t)
                count = 0
                for a in emp_org:
                    count += 1
                    data = [[Paragraph(str(count), c2),
                             Paragraph(a.NOME.title(), c2),
                             Paragraph(a.DESCRICAO40, c2),
                             Paragraph(str(round(a.HORASCONTRATUAIS/Decimal(5.0))), c1)]]
                    t = Table(data, colWidths=[35.0, 190.0, 180.0, 50.0])
                    t.setStyle(TableStyle([('ALIGN', (0, 0), (1, 0), 'LEFT'),
                                           ('ALIGN', (1, 0), (3, 0), 'CENTRE'),
                                           ('VALIGN', (0, 0), (3, 0), 'TOP'),
                                           ('INNERGRID', (0, 0), (3, 0), 0.15, black),
                                           ('BOX', (0, 0), (3, 0), 0.15, black),
                                           ]))
                    elements.append(t)
                    # elements.append(Spacer(1, 0.25 * cm))

                elements.append(Spacer(1, 0.25 * cm))
                elements.append(
                    Paragraph('Funcionários contratados pela Associação Notre Dame', c1))
                elements.append(Spacer(1, 0.25 * cm))
                count = 0
                data = [[Paragraph('Nº', h1),
                         Paragraph('Funcionário', h1),
                         Paragraph('Função', h1),
                         Paragraph('C/H', h1)]]
                t = Table(data, colWidths=[35.0, 190.0, 180.0, 50.0])
                t.setStyle(TableStyle([('ALIGN', (0, 0), (1, 0), 'LEFT'),
                                       ('ALIGN', (1, 0), (3, 0), 'CENTRE'),
                                       ('VALIGN', (0, 0), (3, 0), 'TOP'),
                                       ('INNERGRID', (0, 0), (3, 0), 0.15, black),
                                       ('BOX', (0, 0), (3, 0), 0.15, black),
                                       ]))
                elements.append(t)
                count = 0
                for a in emp_sede:
                    count += 1
                    data = [[Paragraph(str(count), c2),
                             Paragraph(a.NOME.title(), c2),
                             Paragraph(a.DESCRICAO40, c2),
                             Paragraph(str(round(a.HORASCONTRATUAIS/Decimal(5.0))), c1)]]
                    t = Table(data, colWidths=[35.0, 190.0, 180.0, 50.0])
                    t.setStyle(TableStyle([('ALIGN', (0, 0), (1, 0), 'LEFT'),
                                           ('ALIGN', (1, 0), (3, 0), 'CENTRE'),
                                           ('VALIGN', (0, 0), (3, 0), 'TOP'),
                                           ('INNERGRID', (0, 0), (3, 0), 0.15, black),
                                           ('BOX', (0, 0), (3, 0), 0.15, black),
                                           ]))
                    elements.append(t)

                elements.append(Spacer(1, 0.25 * cm))
                elements.append(Paragraph('Funcionários admitidos pela ORSJ - Organização Religiosa Santa Júlia:', c1))
                elements.append(Spacer(1, 0.25 * cm))
                data = [[Paragraph('Funcionário', h1),
                         Paragraph('Função', h1),
                         Paragraph('Admissão', h1)]]
                t = Table(data, colWidths=[190.0, 195.0, 70.0])
                t.setStyle(TableStyle([('ALIGN', (0, 0), (1, 0), 'LEFT'),
                                       ('ALIGN', (1, 0), (2, 0), 'CENTRE'),
                                       ('VALIGN', (0, 0), (2, 0), 'TOP'),
                                       ('INNERGRID', (0, 0), (2, 0), 0.15, black),
                                       ('BOX', (0, 0), (2, 0), 0.15, black),
                                       ]))
                elements.append(t)
                for a in emp_org:
                    if str(a.YEAR_AD) == slctd_year:
                        data = [[Paragraph(a.NOME.title(), c2),
                                 Paragraph(str(a.DESCRICAO40), c2),
                                 Paragraph(a.DATAADMISSAO, c2)]]
                        t = Table(data, colWidths=[190.0, 195.0, 70.0])
                        t.setStyle(TableStyle([('ALIGN', (0, 0), (1, 0), 'LEFT'),
                                               ('ALIGN', (1, 0), (2, 0), 'CENTRE'),
                                               ('VALIGN', (0, 0), (2, 0), 'TOP'),
                                               ('INNERGRID', (0, 0), (2, 0), 0.15, black),
                                               ('BOX', (0, 0), (2, 0), 0.15, black),
                                               ]))
                        elements.append(t)

                elements.append(Spacer(1, 0.25 * cm))
                elements.append(Paragraph('Funcionários admitidos pela AND - Associação Notre Dame:', c1))
                elements.append(Spacer(1, 0.25 * cm))
                data = [[Paragraph('Funcionário', h1),
                         Paragraph('Função', h1),
                         Paragraph('Admissão', h1)]]
                t = Table(data, colWidths=[190.0, 195.0, 70.0])
                t.setStyle(TableStyle([('ALIGN', (0, 0), (1, 0), 'LEFT'),
                                       ('ALIGN', (1, 0), (2, 0), 'CENTRE'),
                                       ('VALIGN', (0, 0), (2, 0), 'TOP'),
                                       ('INNERGRID', (0, 0), (2, 0), 0.15, black),
                                       ('BOX', (0, 0), (2, 0), 0.15, black),
                                       ]))
                elements.append(t)
                for a in emp_sede:
                    if str(a.YEAR_AD) == slctd_year:
                        data = [[Paragraph(a.NOME.title(), c2),
                                 Paragraph(str(a.DESCRICAO40), c2),
                                 Paragraph(a.DATAADMISSAO, c2)]]
                        t = Table(data, colWidths=[190.0, 195.0, 70.0])
                        t.setStyle(TableStyle([('ALIGN', (0, 0), (1, 0), 'LEFT'),
                                               ('ALIGN', (1, 0), (2, 0), 'CENTRE'),
                                               ('VALIGN', (0, 0), (2, 0), 'TOP'),
                                               ('INNERGRID', (0, 0), (2, 0), 0.15, black),
                                               ('BOX', (0, 0), (2, 0), 0.15, black),
                                               ]))
                        elements.append(t)

                elements.append(Spacer(1, 0.25 * cm))
                elements.append(Paragraph('Funcionários desligados pela Organização Religiosa Santa Júlia:', c1))
                elements.append(Spacer(1, 0.25 * cm))
                data = [[Paragraph('Funcionário', h1),
                         Paragraph('Função', h1),
                         Paragraph('Desligamento', h1)]]
                t = Table(data, colWidths=[190.0, 195.0, 70.0])
                t.setStyle(TableStyle([('ALIGN', (0, 0), (1, 0), 'LEFT'),
                                       ('ALIGN', (1, 0), (2, 0), 'CENTRE'),
                                       ('VALIGN', (0, 0), (2, 0), 'TOP'),
                                       ('INNERGRID', (0, 0), (2, 0), 0.15, black),
                                       ('BOX', (0, 0), (2, 0), 0.15, black),
                                       ]))
                elements.append(t)
                for a in emp_org:
                    if str(a.YEAR_RE) == slctd_year:
                        data = [[Paragraph(a.NOME.title(), c2),
                                 Paragraph(a.DESCRICAO40, c2),
                                 Paragraph(str(a.DATARESCISAO), c2)]]
                        t = Table(data, colWidths=[190.0, 195.0, 70.0])
                        t.setStyle(TableStyle([('ALIGN', (0, 0), (1, 0), 'LEFT'),
                                               ('ALIGN', (1, 0), (2, 0), 'CENTRE'),
                                               ('VALIGN', (0, 0), (2, 0), 'TOP'),
                                               ('INNERGRID', (0, 0), (2, 0), 0.15, black),
                                               ('BOX', (0, 0), (2, 0), 0.15, black),
                                               ]))
                        elements.append(t)

                elements.append(Spacer(1, 0.25 * cm))
                elements.append(Paragraph('Funcionários desligados pela Associação Notre Dame:', c1))
                elements.append(Spacer(1, 0.25 * cm))
                data = [[Paragraph('Funcionário', h1),
                         Paragraph('Função', h1),
                         Paragraph('Desligamento', h1)]]
                t = Table(data, colWidths=[190.0, 195.0, 70.0])
                t.setStyle(TableStyle([('ALIGN', (0, 0), (1, 0), 'LEFT'),
                                       ('ALIGN', (1, 0), (2, 0), 'CENTRE'),
                                       ('VALIGN', (0, 0), (2, 0), 'TOP'),
                                       ('INNERGRID', (0, 0), (2, 0), 0.15, black),
                                       ('BOX', (0, 0), (2, 0), 0.15, black),
                                       ]))
                elements.append(t)
                for a in emp_sede:
                    if str(a.YEAR_RE) == slctd_year:
                        data = [[Paragraph(a.NOME.title(), c2),
                                 Paragraph(a.DESCRICAO40, c2),
                                 Paragraph(str(a.DATARESCISAO), c2)]]
                        t = Table(data, colWidths=[190.0, 195.0, 70.0])
                        t.setStyle(TableStyle([('ALIGN', (0, 0), (1, 0), 'LEFT'),
                                               ('ALIGN', (1, 0), (2, 0), 'CENTRE'),
                                               ('VALIGN', (0, 0), (2, 0), 'TOP'),
                                               ('INNERGRID', (0, 0), (2, 0), 0.15, black),
                                               ('BOX', (0, 0), (2, 0), 0.15, black),
                                               ]))
                        elements.append(t)

            else:
                n_session += 1
                elements.append(Paragraph(str(n_session) + '. Relação do pessoal leigo:', h1))
                elements.append(Spacer(1, 0.25 * cm))

                if len(teatcher) > 0:
                    t_man = 0
                    t_woman = 0
                    count = 0
                    str_name = ''
                    for a in teatcher:
                        if count == 0:
                            if a.SEXO == 'M':
                                t_man += 1
                            else:
                                t_woman += 1
                            str_name = a.NOME
                            count += 1
                        else:
                            if str_name == a.NOME:
                                continue
                            else:
                                if a.SEXO == 'M':
                                    t_man += 1
                                else:
                                    t_woman += 1
                                str_name = a.NOME
                                count += 1

                    elements.append(
                        Paragraph('a) Além das Irmãs, trabalharam em nossa escola %s professores leigos: %s masculinos'
                                  ' e %s femininas.' % (count, t_man, t_woman), c1))
                    elements.append(Spacer(1, 0.25 * cm))
                    count = 0
                    str_name = ''
                    str_bname = ''
                    str_count = ''
                    data = [[Paragraph('Nº', h1),
                             Paragraph('Professor', h1),
                             Paragraph('Disciplina', h1),
                             Paragraph('H/A', h1)]]
                    t = Table(data, colWidths=[35.0, 190.0, 180.0, 50.0])
                    t.setStyle(TableStyle([('ALIGN', (0, 0), (1, 0), 'LEFT'),
                                           ('ALIGN', (1, 0), (3, 0), 'CENTRE'),
                                           ('VALIGN', (0, 0), (3, 0), 'TOP'),
                                           ('INNERGRID', (0, 0), (3, 0), 0.15, black),
                                           ('BOX', (0, 0), (3, 0), 0.15, black),
                                           ]))
                    elements.append(t)
                    count = 0
                    for a in teatcher:
                        if count == 0:
                            str_name = a.NOME
                            count += 1
                            str_count = str(count)
                        else:
                            if str_bname == a.NOME:
                                str_name = str_count = ''
                            else:
                                str_name = a.NOME
                                count += 1
                                str_count = str(count)
                        desc = a.DESCRICAO40
                        hr_cont = str(round(a.HORASCONTRATUAIS/Decimal(4.5)))
                        # TODO: Remover as linhas abaixo até a marcação, após atualização da
                        #  consulta nos contratos de trabalho
                        if a.NOME.title() == 'Tais Streb Artmann':
                            if slctd_year in ('2020', '2021'):
                                desc = 'Assistente de Ensino'
                                hr_cont = str(round(150.00/Decimal(4.5)))
                            if slctd_year == '2022':
                                desc = 'Prof. Ens. Fundamental'
                                hr_cont = str(round(94.5 / Decimal(4.5)))
                            else:
                                desc = 'Coord. Pedagógica'
                                hr_cont = str(round(200.00 / Decimal(4.5)))
                        # ------ #
                        data = [[Paragraph(str_count, c2),
                                 Paragraph(str_name.title(), c2),
                                 Paragraph(desc, c2),
                                 Paragraph(hr_cont, c1)]]
                        t = Table(data, colWidths=[35.0, 190.0, 180.0, 50.0])
                        t.setStyle(TableStyle([('ALIGN', (0, 0), (1, 0), 'LEFT'),
                                               ('ALIGN', (1, 0), (3, 0), 'CENTRE'),
                                               ('VALIGN', (0, 0), (3, 0), 'TOP'),
                                               ('INNERGRID', (0, 0), (3, 0), 0.15, black),
                                               ('BOX', (0, 0), (3, 0), 0.15, black),
                                               ]))
                        elements.append(t)
                        str_bname = a.NOME
                        # elements.append(Spacer(1, 0.25 * cm))

                    elements.append(Spacer(1, 0.25 * cm))
                    elements.append(Paragraph('Durante o ano foram admitidos os seguintes professores:', c1))
                    elements.append(Spacer(1, 0.25 * cm))
                    data = [[Paragraph('Professor', h1),
                             Paragraph('Admissão', h1),
                             Paragraph('Disciplina', h1),
                             Paragraph('H/A', h1)]]
                    t = Table(data, colWidths=[165.0, 70.0, 170.0, 50.0])
                    t.setStyle(TableStyle([('ALIGN', (0, 0), (1, 0), 'LEFT'),
                                           ('ALIGN', (1, 0), (3, 0), 'CENTRE'),
                                           ('VALIGN', (0, 0), (3, 0), 'TOP'),
                                           ('INNERGRID', (0, 0), (3, 0), 0.15, black),
                                           ('BOX', (0, 0), (3, 0), 0.15, black),
                                           ]))
                    elements.append(t)
                    count = 0
                    for a in teatcher:
                        if str(a.YEAR_AD) == slctd_year:
                            if count == 0:
                                str_name = a.NOME
                                count += 1
                                str_count = str(count)
                            else:
                                if str_bname == a.NOME:
                                    str_name = str_count = ''
                                else:
                                    str_name = a.NOME
                                    count += 1
                                    str_count = str(count)
                            data = [[Paragraph(str_name.title(), c2),
                                     Paragraph(str(a.DATAADMISSAO), c2),
                                     Paragraph(a.DESCRICAO40, c2),
                                     Paragraph(str(round(a.HORASCONTRATUAIS/Decimal(4.5))), c1)]]
                            t = Table(data, colWidths=[165.0, 70.0, 170.0, 50.0])
                            t.setStyle(TableStyle([('ALIGN', (0, 0), (1, 0), 'LEFT'),
                                                   ('ALIGN', (1, 0), (3, 0), 'CENTRE'),
                                                   ('VALIGN', (0, 0), (3, 0), 'TOP'),
                                                   ('INNERGRID', (0, 0), (3, 0), 0.15, black),
                                                   ('BOX', (0, 0), (3, 0), 0.15, black),
                                                   ]))
                            elements.append(t)
                            str_bname = a.NOME

                    elements.append(Spacer(1, 0.25 * cm))
                    elements.append(
                        Paragraph('Durante o ano foram rescindidos os contratos dos seguintes professores:', c1))
                    elements.append(Spacer(1, 0.25 * cm))
                    data = [[Paragraph('Professor', h1),
                             Paragraph('Data de demissão', h1)]]
                    t = Table(data, colWidths=[230.0, 225.0])
                    t.setStyle(TableStyle([('ALIGN', (0, 0), (1, 0), 'LEFT'),
                                           ('VALIGN', (0, 0), (1, 0), 'TOP'),
                                           ('INNERGRID', (0, 0), (1, 0), 0.15, black),
                                           ('BOX', (0, 0), (1, 0), 0.15, black),
                                           ]))
                    elements.append(t)
                    count = 0
                    str_name = str_bname = ''
                    for a in teatcher:
                        if str(a.YEAR_RE) == slctd_year:
                            data = [[Paragraph(a.NOME.title(), c2),
                                     Paragraph(str(a.DATARESCISAO), c2)]]
                            t = Table(data, colWidths=[230.0, 225.0])
                            t.setStyle(TableStyle([('ALIGN', (0, 0), (1, 0), 'LEFT'),
                                                   ('VALIGN', (0, 0), (1, 0), 'TOP'),
                                                   ('INNERGRID', (0, 0), (1, 0), 0.15, black),
                                                   ('BOX', (0, 0), (1, 0), 0.15, black),
                                                   ]))
                            if count == 0:
                                elements.append(t)
                                str_name = a.NOME
                                count += 1
                            else:
                                count += 1
                                if a.NOME == str_name:
                                    continue
                                else:
                                    elements.append(t)
                                    str_name = a.NOME

                if len(regular) > 0:
                    man = 0
                    woman = 0
                    for a in regular:
                        if a.SEXO == 'M':
                            man += 1
                        else:
                            woman += 1
                    str_comp = ''
                    if len(teatcher) > 1:
                        str_comp = ' e dos professores'
                    elements.append(Spacer(1, 0.25 * cm))
                    elements.append(
                        Paragraph('b) Além das Irmãs%s, trabalharam em nossa Casa %s funcionários leigos: %s masculinos'
                                  ' e %s femininas.' % (str_comp, len(regular), man, woman), c1))
                    elements.append(Spacer(1, 0.25 * cm))
                    count = 0
                    data = [[Paragraph('Nº', h1),
                             Paragraph('Funcionário', h1),
                             Paragraph('Função', h1),
                             Paragraph('C/H', h1)]]
                    t = Table(data, colWidths=[35.0, 190.0, 180.0, 50.0])
                    t.setStyle(TableStyle([('ALIGN', (0, 0), (1, 0), 'LEFT'),
                                           ('ALIGN', (1, 0), (3, 0), 'CENTRE'),
                                           ('VALIGN', (0, 0), (3, 0), 'TOP'),
                                           ('INNERGRID', (0, 0), (3, 0), 0.15, black),
                                           ('BOX', (0, 0), (3, 0), 0.15, black),
                                           ]))
                    elements.append(t)
                    count = 0
                    for a in regular:
                        count += 1
                        desc = a.DESCRICAO40
                        hr_cont = str(round(a.HORASCONTRATUAIS/Decimal(4.5)))
                        # TODO: Remover as linhas abaixo até a marcação, após atualização da
                        #  consulta nos contratos de trabalho
                        if a.NOME.title() == 'Tais Streb Artmann':
                            if slctd_year in ('2020', '2021'):
                                desc = 'Assistente de Ensino'
                                hr_cont = str(round(150.00/Decimal(4.5)))
                            if slctd_year == '2022':
                                desc = 'Prof. Ens. Fundamental'
                                hr_cont = str(round(94.5 / Decimal(4.5)))
                            else:
                                desc = 'Coord. Pedagógica'
                                hr_cont = str(round(200.00 / Decimal(4.5)))
                        # ------ #
                        data = [[Paragraph(str(count), c2),
                                 Paragraph(a.NOME.title(), c2),
                                 Paragraph(desc, c2),
                                 Paragraph(hr_cont, c1)]]
                        t = Table(data, colWidths=[35.0, 190.0, 180.0, 50.0])
                        t.setStyle(TableStyle([('ALIGN', (0, 0), (1, 0), 'LEFT'),
                                               ('ALIGN', (1, 0), (3, 0), 'CENTRE'),
                                               ('VALIGN', (0, 0), (3, 0), 'TOP'),
                                               ('INNERGRID', (0, 0), (3, 0), 0.15, black),
                                               ('BOX', (0, 0), (3, 0), 0.15, black),
                                               ]))
                        elements.append(t)
                        # elements.append(Spacer(1, 0.25 * cm))

                    elements.append(Spacer(1, 0.25 * cm))
                    elements.append(Paragraph('Durante o ano foram admitidos os seguintes funcionários:', c1))
                    elements.append(Spacer(1, 0.25 * cm))
                    data = [[Paragraph('Funcionário', h1),
                             Paragraph('Função', h1),
                             Paragraph('Admissão', h1)]]
                    t = Table(data, colWidths=[190.0, 195.0, 70.0])
                    t.setStyle(TableStyle([('ALIGN', (0, 0), (1, 0), 'LEFT'),
                                           ('ALIGN', (1, 0), (2, 0), 'CENTRE'),
                                           ('VALIGN', (0, 0), (2, 0), 'TOP'),
                                           ('INNERGRID', (0, 0), (2, 0), 0.15, black),
                                           ('BOX', (0, 0), (2, 0), 0.15, black),
                                           ]))
                    elements.append(t)
                    for a in regular:
                        if str(a.YEAR_AD) == slctd_year:
                            data = [[Paragraph(a.NOME.title(), c2),
                                     Paragraph(str(a.DESCRICAO40), c2),
                                     Paragraph(a.DATAADMISSAO, c2)]]
                            t = Table(data, colWidths=[190.0, 195.0, 70.0])
                            t.setStyle(TableStyle([('ALIGN', (0, 0), (1, 0), 'LEFT'),
                                                   ('ALIGN', (1, 0), (2, 0), 'CENTRE'),
                                                   ('VALIGN', (0, 0), (2, 0), 'TOP'),
                                                   ('INNERGRID', (0, 0), (2, 0), 0.15, black),
                                                   ('BOX', (0, 0), (2, 0), 0.15, black),
                                                   ]))
                            elements.append(t)

                    elements.append(Spacer(1, 0.25 * cm))
                    elements.append(
                        Paragraph('Durante o ano foram rescindidos os contratos dos seguintes funcionários:', c1))
                    elements.append(Spacer(1, 0.25 * cm))
                    data = [[Paragraph('Funcionário', h1),
                             Paragraph('Função', h1),
                             Paragraph('Demissão', h1)]]
                    t = Table(data, colWidths=[190.0, 195.0, 70.0])
                    t.setStyle(TableStyle([('ALIGN', (0, 0), (1, 0), 'LEFT'),
                                           ('ALIGN', (1, 0), (2, 0), 'CENTRE'),
                                           ('VALIGN', (0, 0), (2, 0), 'TOP'),
                                           ('INNERGRID', (0, 0), (2, 0), 0.15, black),
                                           ('BOX', (0, 0), (2, 0), 0.15, black),
                                           ]))
                    elements.append(t)
                    for a in regular:
                        if str(a.YEAR_RE) == slctd_year:
                            data = [[Paragraph(a.NOME.title(), c2),
                                     Paragraph(a.DESCRICAO40, c2),
                                     Paragraph(str(a.DATARESCISAO), c2)]]
                            t = Table(data, colWidths=[190.0, 195.0, 70.0])
                            t.setStyle(TableStyle([('ALIGN', (0, 0), (1, 0), 'LEFT'),
                                                   ('ALIGN', (1, 0), (2, 0), 'CENTRE'),
                                                   ('VALIGN', (0, 0), (2, 0), 'TOP'),
                                                   ('INNERGRID', (0, 0), (2, 0), 0.15, black),
                                                   ('BOX', (0, 0), (2, 0), 0.15, black),
                                                   ]))
                            elements.append(t)

        if len(activities_data) > 0:
            n_session += 1
            elements.append(Spacer(1, 0.25 * cm))
            elements.append(Paragraph(str(n_session) + '. Relatório das atividades', h1))
            elements.append(Spacer(1, 0.25 * cm))
            if activities_data[0].ATIVIDADEPRINCIPAL not in (None, ' ', ''):
                activities = nl2br(activities_data[0].ATIVIDADEPRINCIPAL)
                elements.append(Paragraph('Nossa casa abrange as seguintes atividades:', h1))
                elements.append(Spacer(1, 0.25 * cm))
                elements.append(Paragraph(activities, c1))
                elements.append(Spacer(1, 0.25 * cm))
            if activities_data[0].ATIVIDADESTERCEIRIZADAS not in (None, ' ', ''):
                thrd_activities = nl2br(activities_data[0].ATIVIDADESTERCEIRIZADAS)
                elements.append(Paragraph('Atividades terceirizadas:', c1))
                elements.append(Spacer(1, 0.25 * cm))
                elements.append(Paragraph(thrd_activities, c1))
                elements.append(Spacer(1, 0.25 * cm))
            if activities_data[0].OUTRASATIVIDADES not in (None, ' ', ''):
                other_activities = nl2br(activities_data[0].OUTRASATIVIDADES)
                elements.append(Paragraph('Outras atividades:', c1))
                elements.append(Spacer(1, 0.25 * cm))
                elements.append(Paragraph(other_activities, c1))
                elements.append(Spacer(1, 0.25 * cm))

        if len(pastoral_activities) > 0:
            elements.append(Spacer(1, 0.25 * cm))
            elements.append(Paragraph('Número de pessoas atingidas nos serviços das pastorais e movimentos', h1))
            elements.append(Spacer(1, 0.25 * cm))
            data = [[Paragraph('Atividades', h1),
                     Paragraph('Público Alvo', h1),
                     Paragraph('Nº Atingido', h1)]]
            t = Table(data, colWidths=[205.0, 170.0, 80.0])
            t.setStyle(TableStyle([('ALIGN', (0, 0), (1, 0), 'LEFT'),
                                   ('ALIGN', (1, 0), (2, 0), 'CENTRE'),
                                   ('VALIGN', (0, 0), (2, 0), 'TOP'),
                                   ]))
            elements.append(t)
            elements.append(Spacer(1, 0.25 * cm))
            for a in pastoral_activities:
                data = [[Paragraph(a.NOME, c2),
                         Paragraph(a.PUBLICOALVO, c2),
                         Paragraph(str(a.NUMATINGIDO), c1)]]
                t = Table(data, colWidths=[205.0, 170.0, 80.0])
                t.setStyle(TableStyle([('ALIGN', (0, 0), (1, 0), 'LEFT'),
                                       ('ALIGN', (1, 0), (2, 0), 'CENTRE'),
                                       ('VALIGN', (0, 0), (2, 0), 'TOP'),
                                       ]))
                elements.append(t)
                elements.append(Spacer(1, 0.25 * cm))

        if school:
            elements.append(Spacer(1, 0.25 * cm))
            elements.append(Paragraph('Matrículas', c1))
            elements.append(Spacer(1, 0.25 * cm))
            data = [[Paragraph('Curso', h1),
                     Paragraph('Série', h1),
                     Paragraph('Fem', h1),
                     Paragraph('Masc', h1),
                     Paragraph('Transf Cancel', h1),
                     Paragraph('Ativos', h1),
                     Paragraph('Mat Geral', h1)]]
            t = Table(data, colWidths=[137.0, 69.0, 48.0, 48.0, 50.0, 50.0, 50.0])
            t.setStyle(TableStyle([('ALIGN', (0, 0), (2, 0), 'LEFT'),
                                   ('VALIGN', (0, 0), (6, 0), 'CENTRE'),
                                   ('INNERGRID', (0, 0), (6, 0), 0.15, black),
                                   ('BOX', (0, 0), (6, 0), 0.15, black),
                                   ]))
            elements.append(t)
            count = 0
            for a in students:
                if count == 0:
                    str_name = a.CURSO
                    count += 1
                else:
                    if str_bname == a.CURSO:
                        str_name = ''
                    else:
                        str_name = a.CURSO
                        count += 1
                data = [[Paragraph(str_name, c1),
                         Paragraph(a.SERIE, c1),
                         Paragraph(str(a.FEM), c1),
                         Paragraph(str(a.MASC), c1),
                         Paragraph(str(a.CANC), c1),
                         Paragraph(str(a.ATIVO), c1),
                         Paragraph(str(a.TOTAL), c1)]]
                t = Table(data, colWidths=[137.0, 69.0, 48.0, 48.0, 50.0, 50.0, 50.0])
                t.setStyle(TableStyle([('ALIGN', (0, 0), (2, 0), 'LEFT'),
                                       ('VALIGN', (0, 0), (6, 0), 'CENTRE'),
                                       ('INNERGRID', (0, 0), (6, 0), 0.15, black),
                                       ('BOX', (0, 0), (6, 0), 0.15, black),
                                       ]))
                elements.append(t)
                str_bname = a.CURSO
            data = [[Paragraph('TOTAL', h1),
                     Paragraph('', h1),
                     Paragraph(str(female), h1),
                     Paragraph(str(male), h1),
                     Paragraph(str(canceled), h1),
                     Paragraph(str(active), h1),
                     Paragraph(str(general), h1)]]
            t = Table(data, colWidths=[137.0, 69.0, 48.0, 48.0, 50.0, 50.0, 50.0])
            t.setStyle(TableStyle([('ALIGN', (0, 0), (2, 0), 'LEFT'),
                                   ('VALIGN', (0, 0), (6, 0), 'CENTRE'),
                                   ('INNERGRID', (0, 0), (6, 0), 0.15, black),
                                   ('BOX', (0, 0), (6, 0), 0.15, black),
                                   ]))
            elements.append(t)

        ## Eventos
        events_data = get_events(id_annals)
        if len(events_data) > 0:
            elements.append(Spacer(1, 0.25 * cm))
            elements.append(Paragraph('Atividades desenvolvidas em ' + slctd_year + ':', h1))
            elements.append(Spacer(1, 0.25 * cm))
            previous_item = None
            active_item = None
            data = [[Paragraph('Data', h1),
                     Paragraph('Local', h1),
                     Paragraph('Atividade', h1),
                     Paragraph('Responsável', h1),
                     Paragraph('QTD', h1)]]
            t = Table(data, colWidths=[80, 110, 100.0, 105.0, 60.0])
            t.setStyle(TableStyle([('ALIGN', (0, 0), (1, 0), 'LEFT'),
                                   ('ALIGN', (1, 0), (4, 0), 'CENTRE'),
                                   ('VALIGN', (0, 0), (4, 0), 'TOP'),
                                   ]))
            elements.append(t)
            elements.append(Spacer(1, 0.25 * cm))
            for item in events_data:
                desc = item.DESCRICAO or ''
                date = item.PERIODO or ''
                if date == '':
                    date = item.DATA or ''
                if item.DESCRICAO is not None:
                    active_item = item.DESCRICAO
                    if active_item != previous_item:
                        elements.append(Paragraph(desc, h1))
                        elements.append(Spacer(1, 0.25 * cm))
                        data = [[Paragraph(date, c2),
                                 Paragraph(item.LOCAL, c2),
                                 Paragraph(item.ATIVIDADE, c2),
                                 Paragraph(item.RESPONSAVEL, c2),
                                 Paragraph(str(item.NUMPARTICIPANTES), c2)]]
                        t = Table(data, colWidths=[80, 110, 100.0, 105.0, 60.0])
                        t.setStyle(TableStyle([('ALIGN', (0, 0), (1, 0), 'LEFT'),
                                               ('ALIGN', (1, 0), (4, 0), 'CENTRE'),
                                               ('VALIGN', (0, 0), (4, 0), 'TOP'),
                                               ]))
                        elements.append(t)
                        elements.append(Spacer(1, 0.25 * cm))
                        previous_item = item.DESCRICAO
                    else:
                        data = [[Paragraph(date, c2),
                                 Paragraph(item.LOCAL, c2),
                                 Paragraph(item.ATIVIDADE, c2),
                                 Paragraph(item.RESPONSAVEL, c2),
                                 Paragraph(str(item.NUMPARTICIPANTES), c2)]]
                        t = Table(data, colWidths=[80, 110, 100.0, 105.0, 60.0])
                        t.setStyle(TableStyle([('ALIGN', (0, 0), (1, 0), 'LEFT'),
                                               ('ALIGN', (1, 0), (4, 0), 'CENTRE'),
                                               ('VALIGN', (0, 0), (4, 0), 'TOP'),
                                               ]))
                        elements.append(t)
                        elements.append(Spacer(1, 0.25 * cm))
                        previous_item = item.DESCRICAO
                else:
                    data = [[Paragraph(date, c2),
                             Paragraph(item.LOCAL, c2),
                             Paragraph(item.ATIVIDADE, c2),
                             Paragraph(item.RESPONSAVEL, c2),
                             Paragraph(str(item.NUMPARTICIPANTES), c2)]]
                    t = Table(data, colWidths=[80, 110, 100.0, 105.0, 60.0])
                    t.setStyle(TableStyle([('ALIGN', (0, 0), (1, 0), 'LEFT'),
                                           ('ALIGN', (1, 0), (4, 0), 'CENTRE'),
                                           ('VALIGN', (0, 0), (4, 0), 'TOP'),
                                           ]))
                    elements.append(t)
                    elements.append(Spacer(1, 0.25 * cm))

        elements.append(Spacer(1, 0.25 * cm))
        elements.append(PageBreak())
        elements.append(Paragraph('II - NARRATIVA', h1))
        elements.append(Spacer(1, 0.25 * cm))
        for a in story_data:
            story = a.DESCRICAO1 or ''
            story2 = a.DESCRICAO2 or ''
            story3 = a.DESCRICAO3 or ''
            story += story2
            story += story3
            elements.append(Paragraph(a.PERIODO + ' - ' + a.TITULO, h1))
            elements.append(Spacer(1, 0.25 * cm))
            elements.append(Paragraph(story, c1))
            elements.append(Spacer(1, 0.25 * cm))

        buffer = BytesIO()
        doc.title = house_name + ' | ' + slctd_year + ' - Estatísticas'

        report = MyPrint(buffer, 'A4')

        # response.write(doc.build(elements))
        response.write(doc.build(elements, canvasmaker=NumberedCanvas))

        return response