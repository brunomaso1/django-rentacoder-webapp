# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-04 19:33
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import rentacoder_app.fields


class Migration(migrations.Migration):

    dependencies = [
        ('rentacoder_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectScore',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('owner_score', rentacoder_app.fields.IntegerRangeField(default=0)),
                ('coder_score', rentacoder_app.fields.IntegerRangeField(default=0)),
                ('coder', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rentacoder_app.Project')),
            ],
            options={
                'db_table': 'project_score',
            },
        ),
        migrations.AddField(
            model_name='joboffer',
            name='accepted',
            field=models.BooleanField(default=False),
        ),
    ]
