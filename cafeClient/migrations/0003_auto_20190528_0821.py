# Generated by Django 2.2 on 2019-05-28 08:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cafeClient', '0002_modclear'),
    ]

    operations = [
        migrations.AlterField(
            model_name='modclear',
            name='time',
            field=models.DateTimeField(max_length=200, verbose_name='清理日期'),
        ),
        migrations.AlterField(
            model_name='modorder',
            name='Etime',
            field=models.DateTimeField(max_length=200, verbose_name='订单完成时间'),
        ),
        migrations.AlterField(
            model_name='modorder',
            name='Stime',
            field=models.DateTimeField(verbose_name='接单时间'),
        ),
    ]
