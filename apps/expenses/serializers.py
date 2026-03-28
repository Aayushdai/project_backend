from rest_framework import serializers
from .models import Expense


class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
fields = ['id', 'trip', 'description', 'amount', 'paid_by', 'split_among', 'date']