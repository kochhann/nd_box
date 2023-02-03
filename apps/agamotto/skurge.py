from apscheduler.schedulers.background import BackgroundScheduler
from .scheduled_task import (
    read_scheduled_tasks,
    update_unidade_gv,
    update_curso_gv,
    update_ciclo_gv,
    update_turma_gv,
    check_enturmacao,
    check_scheduled_messages,
    send_scheduled_messages,
    check_scheduled_sms_boletos
)
from hermes import send_test_mail


##
# Exemplos de configurações de período
# Intervalos de tempo
# scheduler.add_job(read_scheduled_tasks, 'interval', [seconds/minutes/hours/days/weeks]=30)
# Data específica
# scheduler.add_job(read_scheduled_tasks, 'date', run_date=datetime(2022, 3, 15, 11, 00, 00))
# Agenda para execução agendada, similar a tabela cron do sistema UNIX/LINUX
# Documentação:
# https://apscheduler.readthedocs.io/en/3.x/modules/triggers/
# cron.html?highlight=triggers.cron#module-apscheduler.triggers.cron
#
# scheduler.add_job(read_scheduled_tasks, 'cron', hour='0', minute='2')
# ###


def start():
    scheduler = BackgroundScheduler(timezone='America/Sao_Paulo')
    # scheduler.add_job(check_scheduled_sms_boletos, 'interval', minutes=60)
    # scheduler.add_job(check_scheduled_sms_boletos, 'cron', hour='16', minute='37')
    # scheduler.add_job(test_sms, 'cron', hour='12', minute='30')
    scheduler.add_job(read_scheduled_tasks, 'cron', hour= '*', minute= '*/10')
    # scheduler.add_job(check_scheduled_sms_boletos, 'cron', hour='11', minute='*/8')
    # scheduler.add_job(check_enturmacao, 'interval', seconds=35)
    # scheduler.add_job(update_unidade_gv, 'interval', seconds=40)
    # scheduler.add_job(update_curso_gv, 'interval', seconds=45)
    # scheduler.add_job(update_ciclo_gv, 'interval', seconds=50)
    # scheduler.add_job(update_turma_gv, 'interval', seconds=55)
    # scheduler.add_job(read_scheduled_tasks, 'interval', minutes=300)
    # scheduler.add_job(check_scheduled_messages, 'cron', hour='*', minute='*/2')
    # scheduler.add_job(send_scheduled_messages, 'cron', hour='*', minute='*/4')
    # scheduler.add_job(send_test_mail, 'interval', minutes=1)
    # scheduler.add_job(check_scheduled_sms_boletos, 'cron', hour='11', minute='40')
    # scheduler.add_job(check_scheduled_sms_boletos, 'cron', hour='18', minute='00')
    scheduler.add_job(update_unidade_gv, 'cron', hour='0', minute='10')
    scheduler.add_job(update_curso_gv, 'cron', hour='0', minute='15')
    scheduler.add_job(update_ciclo_gv, 'cron', hour='0', minute='20')
    scheduler.add_job(update_turma_gv, 'cron', hour='0', minute='25')
    scheduler.add_job(check_enturmacao, 'cron', hour='0', minute='30')

    # scheduler.start()
