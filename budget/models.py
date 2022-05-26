from django.db import models
from django.contrib.auth.models import User

from uuid import uuid4


# Create your models here.

def get_system_category(type_pay):
    return Category.objects.get_or_create(type_pay=type_pay, name='Прочее', user_id=None)[0].id


class Category(models.Model):
    name = models.CharField(max_length=32, verbose_name="Категория")
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    type_pay = models.PositiveSmallIntegerField(choices=((0, 'Расход'), (1, 'Доход')), default=0)

    def __str__(self):
        return self.name  # + " | " + self.get_type_pay_display()

    def delete(self, using=None, keep_parents=False):
        Operation.objects.filter(category_id=self.id).update(category_id=get_system_category(self.type_pay))
        return super().delete(using=None, keep_parents=False)


class Operation(models.Model):
    value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма")
    date = models.DateField(auto_now_add=True)
    description = models.CharField(max_length=128, verbose_name="Описание", blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Категория",
                                 related_name='operations', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='operations')

    def __str__(self):
        return f'{self.value} | {self.category} | {self.date} | {self.user}'

    # class Meta:
    # ordering = ['-date', '-id']


class Family(models.Model):
    name = models.CharField(max_length=32, verbose_name="Семья")
    author = models.ForeignKey(User, verbose_name='Создатель', blank=True, null=True, on_delete=models.CASCADE,
                               related_name='author_families')
    uuid = models.UUIDField(default=uuid4, editable=True)
    users = models.ManyToManyField(User, blank=True, related_name='family')
    # users = models.ManyToManyField(User, through='FamilyUsers', through_fields=('family', 'user'),
    #                                related_name='family')

    def __str__(self):
        return self.name

    # class Meta:
    #     unique_together = ['users__family', 'users__user']


# class FamilyUsers(models.Model):
#     family = models.ForeignKey(Family, on_delete=models.CASCADE)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#
#     class Meta:
#         db_table = 'budget_family_users'
#         unique_together = ['family', 'user']
