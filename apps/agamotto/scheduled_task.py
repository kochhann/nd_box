from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from .models import (
    ScheduledTask,
    MailMessageScheduler,
    SmsCobrancaScheduler
)
from apps.core.models import (
    Unidade,
    Curso,
    Ciclo,
    Turma
)
from apps.autorizacoes.models import Aluno
from functions import (
    get_gv_unidade,
    get_gv_curso,
    get_gv_ciclo,
    get_gv_turma,
    user_creation_autorizador,
    generate_authorization,
    get_turma_aluno,
    get_email_nd,
    set_message_as_sent,
    get_gv_unidade_from_nd_code,
    get_sms_boletos_nd,
    set_sms_as_sent
)
from hermes import send_test_mail


def read_scheduled_tasks():
    st = ScheduledTask.objects.filter(status='scheduled', ativo=True)
    if len(st) > 0:
        for item in st:
            if item.task == 'createUser':
                # a = open('log_scheduled.txt', 'a')
                # now = datetime.now()
                # date_time = now.strftime("%m/%d/%Y, %H:%M:%S\n")
                # a.write(date_time)
                # a.close()
                user_creation_autorizador(item.id)
            if item.task == 'generateAuth':
                print('criar autorizações')
                generate_authorization(item.gv_code, item.extra_field)
                item.status = 'completed'
                item.soft_delete()
    else:
        print('nothing do run')


def update_unidade_gv():
    unidades = Unidade.objects.all()
    gv_unidades = get_gv_unidade(0)
    list_codes_gv = []
    list_codes_local = []
    for item in gv_unidades:
        list_codes_gv.append(item.GV_CODE)
        for l_item in unidades:
            if item.GV_CODE == l_item.gv_code:
                nu = Unidade(nome=item.NOME,
                             cidade=item.CIDADE,
                             estado=item.ESTADO,
                             cnpj=item.CNPJ,
                             cnae=item.CNAE)
                if nu.cnae[0:2] == '85':
                    nu.is_school = True
                l_item.update_from_origin(nu)
    for item in unidades:
        list_codes_local.append(item.gv_code)
    new_codes = set(list_codes_gv) ^ set(list_codes_local)
    if len(new_codes) > 0:
        for code in new_codes:
            for item in gv_unidades:
                if code == item.GV_CODE:
                    nu = Unidade(nome=item.NOME.title(),
                                 cidade=item.CIDADE.title(),
                                 estado=item.ESTADO,
                                 gv_code=item.GV_CODE,
                                 cnpj=item.CNPJ,
                                 cnae=item.CNAE)
                    if item.CNAE[0:2] == '85':
                        nu.is_school = True
                    nu.save()


def update_curso_gv():
    cursos = Curso.objects.all()
    gv_cursos = get_gv_curso(0, datetime.now().year)
    list_codes_gv = []
    list_codes_local = []
    for item in gv_cursos:
        list_codes_gv.append(item.GV_CODE)
        for l_item in cursos:
            if item.GV_CODE == l_item.gv_code and item.CODIGOUNIDADE == l_item.unidade.gv_code:
                unidade = Unidade.objects.get(gv_code=item.CODIGOUNIDADE)
                nc = Curso(nome=item.CURSO,
                           gv_code=item.GV_CODE,
                           unidade=unidade)
                l_item.update_from_origin(nc)
    for item in cursos:
        list_codes_local.append(item.gv_code)
    new_codes = set(list_codes_gv) ^ set(list_codes_local)
    if len(new_codes) > 0:
        for code in new_codes:
            for item in gv_cursos:
                if code == item.GV_CODE:
                    unidade = Unidade.objects.get(gv_code=item.CODIGOUNIDADE)
                    nc = Curso(nome=item.CURSO,
                               gv_code=item.GV_CODE,
                               unidade=unidade)
                    nc.save()


def update_ciclo_gv():
    ciclos = Ciclo.objects.all()
    gv_ciclos = get_gv_ciclo(0, datetime.now().year)
    list_codes_gv = []
    list_codes_local = []
    for item in gv_ciclos:
        list_codes_gv.append(item.GV_CODE)
        for l_item in ciclos:
            if item.GV_CODE == l_item.gv_code and item.CURSO == l_item.curso.gv_code:
                curso = Curso.objects.get(gv_code=item.CURSO)
                nc = Ciclo(nome=item.CICLO,
                           gv_code=item.GV_CODE,
                           curso=curso)
                l_item.update_from_origin(nc)
    for item in ciclos:
        list_codes_local.append(item.gv_code)
    new_codes = set(list_codes_gv) ^ set(list_codes_local)
    if len(new_codes) > 0:
        for code in new_codes:
            for item in gv_ciclos:
                if code == item.GV_CODE:
                    curso = Curso.objects.get(gv_code=item.CURSO)
                    nc = Ciclo(nome=item.CICLO,
                               gv_code=item.GV_CODE,
                               curso=curso)
                    nc.save()


def update_turma_gv():
    turmas = Turma.objects.all()
    gv_turmas = get_gv_turma(0, datetime.now().year)
    list_codes_gv = []
    list_codes_local = []
    for item in gv_turmas:
        list_codes_gv.append(item.GV_CODE)
        for l_item in turmas:
            if item.GV_CODE == l_item.gv_code and item.CICLO == l_item.ciclo.gv_code:
                ciclo = Ciclo.objects.get(gv_code=item.CICLO)
                nt = Turma(nome=item.TURMA,
                           ano=item.ANO,
                           gv_code=item.GV_CODE,
                           ciclo=ciclo)
                l_item.update_from_origin(nt)
    for item in turmas:
        list_codes_local.append(item.gv_code)
    new_codes = set(list_codes_gv) ^ set(list_codes_local)
    if len(new_codes) > 0:
        for code in new_codes:
            for item in gv_turmas:
                if code == item.GV_CODE:
                    ciclo = Ciclo.objects.get(gv_code=item.CICLO)
                    nt = Turma(nome=item.TURMA,
                               ano=item.ANO,
                               gv_code=item.GV_CODE,
                               ciclo=ciclo)
                    nt.save()


def check_enturmacao():
    alunos = Aluno.objects.filter(ativo=True)
    for a in alunos:
        print(a.nome)
        gv_turma = get_turma_aluno(a.matricula, timezone.now().year)
        if gv_turma > 0:  # se estiver enturmado
            if gv_turma == a.turma_atual.gv_code:  # se a turma não foi alterada
                print(a.nome + ' permanece na mesma turma')
                continue
            else:
                print(a.nome + ' teve a turma modificada')
                continue
                # a.update_enturmacao(gv_turma)
        else:
            print('Não está enturmado no GV')
            # a.remove_enturmacao()


def check_scheduled_messages():
    qs = get_email_nd(0)
    messages = MailMessageScheduler.objects.all()
    o_id = []
    for item in qs:
        o_id.append(item.ID)
    r_id = []
    for item in messages:
        r_id.append(item.nd_code)
    new_codes = set(o_id) ^ set(r_id)
    filtered = [x for x in set(qs) if x.ID in new_codes]
    cnt = 0
    if len(filtered) > 0:
        enviado = False
        data_envio = None
        for msg in filtered:
            try:
                unidade = Unidade.objects.get(gv_code=get_gv_unidade_from_nd_code(msg.escola))
            except ObjectDoesNotExist:
                unidade = Unidade.objects.get(gv_code=2)
            if msg.dataEnvio:
                data_envio = msg.dataEnvio
                enviado = True
            ms = MailMessageScheduler(
                unidade=unidade,
                codigo_aluno=msg.codigoAluno,
                data_geracao=msg.data,
                email_remetente=msg.emailRemetente,
                nome_remetente=msg.nomeRemetente,
                email_destino=msg.emailEnvio,
                assunto=msg.titulo,
                mensagem=msg.mensagem,
                usuario=msg.usuario,
                data_envio=data_envio,
                enviado=enviado,
                nd_code=msg.ID
            )
            ms.save()
            cnt += 1


def send_scheduled_messages():
    msg = MailMessageScheduler.objects.filter(enviado=False)
    if msg:
        for item in msg:
            item.send()
            set_message_as_sent(item.nd_code)


def check_scheduled_sms_boletos():
    sms = get_sms_boletos_nd()
    if sms:
        send_test_mail()
        # while sms:
        #     s = sms.pop()
        #     item = SmsCobrancaScheduler(
        #         nd_code=s.ID,
        #         unidade=Unidade.objects.get(gv_code=get_gv_unidade_from_nd_code(s.escola)),
        #         codigo_aluno=s.codigoAluno,
        #         data_geracao=s.dataEnvio,
        #         data_vencimento=s.vencimento,
        #         fone_destino=s.telefone,
        #         mensagem=s.mensagem,
        #         enviado=False
        #     )
        #     item.save()
        #     set_sms_as_sent(item.nd_code)
        #     print(f'Salvo como enviado em ND')
        #     print(f'SMS Salvo - {s}')
    else:
        send_test_mail()
    n_sms = SmsCobrancaScheduler.objects.filter(enviado=False)
    if n_sms:
        send_test_mail()
        # for item in n_sms:
        #     item.send()
        #     print(f'Item enviado')
    else:
        send_test_mail()

