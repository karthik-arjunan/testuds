# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('uds', '0006_add_user_parent_uuid'),
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uuid', models.CharField(default=None, max_length=50, unique=True, null=True)),
                ('name', models.CharField(unique=True, max_length=128, db_index=True)),
                ('stamp', models.DateTimeField()),
                ('data', models.BinaryField()),
                ('thumb', models.BinaryField()),
                ('width', models.IntegerField(default=0)),
                ('height', models.IntegerField(default=0)),
            ],
            options={
                'db_table': 'uds_images',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='deployedservice',
            name='image',
            field=models.ForeignKey(related_name='deployedServices', blank=True, to='uds.Image', null=True),
            preserve_default=True,
        ),
    ]
