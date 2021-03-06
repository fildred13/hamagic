# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-10 00:09
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Deck',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40, unique=True)),
                ('slug', models.SlugField(unique=True)),
                ('format', models.CharField(choices=[('MODERN', 'Modern'), ('STANDARD', 'Standard'), ('LEGACY', 'Legacy'), ('VINTAGE', 'Vintage'), ('BLOCK', 'Block')], default='MODERN', max_length=12)),
                ('type', models.CharField(choices=[('CONSTRUCTED', 'Constructed'), ('DRAFT', 'Draft'), ('SEALED', 'Sealed'), ('COMMANDER', 'Commander')], default='CONSTRUCTED', max_length=12)),
                ('packs', models.CharField(default='Unlimited', help_text='If Block, Sealed, or Draft, note the associated packs/block', max_length=20)),
                ('deck_list', models.TextField(blank=True, null=True)),
                ('match_wins', models.PositiveSmallIntegerField(default=0)),
                ('match_losses', models.PositiveSmallIntegerField(default=0)),
                ('game_wins', models.PositiveSmallIntegerField(default=0)),
                ('game_losses', models.PositiveSmallIntegerField(default=0)),
                ('tourney_semis', models.PositiveSmallIntegerField(default=0, verbose_name='tourney semis appearances')),
                ('tourney_finals', models.PositiveSmallIntegerField(default=0, verbose_name='tourney finals appearances')),
                ('tourney_wins', models.PositiveSmallIntegerField(default=0)),
                ('tourney_losses', models.PositiveSmallIntegerField(default=0)),
                ('tourney_bow_outs', models.PositiveSmallIntegerField(default=0)),
                ('is_active', models.BooleanField(default=True, help_text='Uncheck to hide deck from your All Active Decks view and Registration Selector.  Useful for "hiding" old or one-time limited decks.')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('last_update', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
