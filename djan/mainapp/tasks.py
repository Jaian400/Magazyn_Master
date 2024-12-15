# from celery import shared_task
# from django.utils.timezone import now
# from .models import WarehouseBalance

# @shared_task
# def calculate_daily_balance():
#     """
#     Zadanie przeliczające dzienny balans dla bieżącego dnia.
#     """
#     balance, created = WarehouseBalance.objects.get_or_create(date=now().date())
#     balance.calculate_balance()