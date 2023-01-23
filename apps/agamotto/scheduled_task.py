from datetime import datetime
from django.core.exceptions import *
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
    set_sms_as_sent,
    log_writer,
    error_log_writer
)
from hermes import send_test_mail


def read_scheduled_tasks():
    st = ScheduledTask.objects.filter(status='scheduled', ativo=True)
    log_message = []
    log_message.append('Execução de fila de agendamento\n')
    if len(st) > 0:
        log_message.append(f'Existem {len(st)} tarefas na fila \n')
        for item in st:
            if item.task == 'createUser':
                user_creation_autorizador(item.id)
            if item.task == 'generateAuth':
                print('criar autorizações')
                generate_authorization(item.gv_code, item.extra_field)
                item.status = 'completed'
                item.soft_delete()
        log_message.append(f'Tarefas executadas.\n')
    else:
        log_message = ['Não há agendamentos a executar\n']
    log_writer(read_scheduled_tasks.__name__, log_message)


def update_unidade_gv():
    log_message = []
    log_message.append('Atualização de Unidades\n')
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
        log_message.append(f'Novas unidades: {len(new_codes)}\n')
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
                    log_message.append(f'Unidade adicionada: {nu.nome}\n')
    else:
        log_message.append('Não há novas unidades.\n')
    log_message.append('Atualização de unidades concluída.\n')
    log_writer(update_unidade_gv.__name__, log_message)


def update_curso_gv():
    log_message = []
    log_message.append('Atualização de Cursos\n')
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
        log_message.append(f'Novos cursos: {len(new_codes)}\n')
        for code in new_codes:
            for item in gv_cursos:
                if code == item.GV_CODE:
                    unidade = Unidade.objects.get(gv_code=item.CODIGOUNIDADE)
                    nc = Curso(nome=item.CURSO,
                               gv_code=item.GV_CODE,
                               unidade=unidade)
                    nc.save()
                    log_message.append(f'Curso adicionado: {nc.nome}\n')
    else:
        log_message.append('Não há novos cursos.\n')
    log_message.append('Atualização de cursos concluída.\n')
    log_writer(update_curso_gv.__name__, log_message)


def update_ciclo_gv():
    log_message = []
    log_message.append('Atualização de Cursos\n')
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
        log_message.append(f'Novos ciclos: {len(new_codes)}\n')
        for code in new_codes:
            for item in gv_ciclos:
                if code == item.GV_CODE:
                    curso = Curso.objects.get(gv_code=item.CURSO)
                    nc = Ciclo(nome=item.CICLO,
                               gv_code=item.GV_CODE,
                               curso=curso)
                    nc.save()
                    log_message.append(f'Ciclo adicionado: {nc.nome}\n')
    else:
        log_message.append('Não há novos ciclos.\n')
    log_message.append('Atualização de ciclos concluída.\n')
    log_writer(update_ciclo_gv.__name__, log_message)


def update_turma_gv():
    log_message = []
    log_message.append('Atualização de Turmas\n')
    turmas = Turma.objects.filter(ativo=True)
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
        log_message.append(f'Novas turmas: {len(new_codes)}\n')
        for code in new_codes:
            for item in gv_turmas:
                if code == item.GV_CODE:
                    ciclo = Ciclo.objects.get(gv_code=item.CICLO)
                    nt = Turma(nome=item.TURMA,
                               ano=item.ANO,
                               gv_code=item.GV_CODE,
                               ciclo=ciclo)
                    nt.save()
                    log_message.append(f'Turma adicionada: {nt.nome}\n')
    else:
        log_message.append('Não há novas turmas.\n')
    old = Turma.objects.filter(ativo=True).exclude(ano=timezone.now().year)
    if old:
        for item in old:
            item.soft_delete()
        log_message.append(f'Desativação de turmas antigas\n'
                           f'Foram desativadas {str(len(old))} turmas.\n')
    log_message.append('Atualização de turmas concluída.\n')
    log_writer(update_turma_gv.__name__, log_message)


def check_enturmacao():
    log_message = []
    log_message.append('Atualização de Enturmação\n')
    alunos = Aluno.objects.filter(ativo=True)
    try:
        for a in alunos:
            print(a.nome)
            gv_turma = get_turma_aluno(a.matricula, timezone.now().year)
            if gv_turma > 0:  # se estiver enturmado
                if gv_turma == a.turma_atual.gv_code:  # se a turma não foi alterada
                    continue
                else:
                    turma = Turma.objects.get(gv_code=gv_turma)
                    a.remove_enturmacao()
                    a.create_enturmacao(turma)
                    a.save()
                    log_message.append(f'Nova enturmação: {a.nome} na turma {turma.nome}\n')
            else:
                a.remove_enturmacao()
                a.save()
                log_message.append(f'{a.nome} não está enturmado para o ano atual.\n')
        log_message.append('Atualização de enturmação concluída.\n')
        log_writer(check_enturmacao.__name__, log_message)
    except e:
        error_log_message = [f'Erro ao atualizar enturmação: {str(e)}\n']
        error_log_writer(check_enturmacao.__name__, log_message)


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
            try:
                item.send()
                set_message_as_sent(item.nd_code)
            except e:
                log_message = [f'ID: {tem.id}\n',
                               f'Destino: {item.email_destino}\n']
                error_log_writer(send_scheduled_messages.__name__, log_message)


def check_scheduled_sms_boletos():
    sms = get_sms_boletos_nd()
    if sms:
        log_message = [f'Quantidade de mensagens a importar: {len(sms)}\n',
                       'Fim do log.\n']
        log_writer(check_scheduled_sms_boletos.__name__, log_message)
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
        log_message = ['Não há mensagens a importar\n',
                       'Fim do log.\n']
        log_writer(check_scheduled_sms_boletos.__name__, log_message)
    n_sms = SmsCobrancaScheduler.objects.filter(enviado=False)
    if n_sms:
        log_message = [f'Quantidade de mensagens a enviar: {len(n_sms)}\n',
                       'Fim do log.\n']
        log_writer(check_scheduled_sms_boletos.__name__, log_message)
        # for item in n_sms:
        #     item.send()
        #     print(f'Item enviado')
    else:
        log_message = ['Não há mensagens a enviar\n',
                       'Fim do log.\n']
        log_writer(check_scheduled_sms_boletos.__name__, log_message)

