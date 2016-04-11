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
        ('deck', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('round', models.PositiveSmallIntegerField(default=0)),
                ('size', models.PositiveSmallIntegerField()),
                ('is_active', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='GroupStats',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('points', models.PositiveSmallIntegerField(default=0)),
                ('margin', models.PositiveSmallIntegerField(default=0)),
                ('deck', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='deck.Deck')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tourney.Group')),
            ],
        ),
        migrations.CreateModel(
            name='Match',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('round', models.PositiveSmallIntegerField(default=0)),
                ('position', models.PositiveSmallIntegerField(default=0)),
                ('elimination', models.CharField(choices=[('SINGLE', 'Single'), ('BEST_THREE', 'Best of Three'), ('BEST_FIVE', 'Best of Five'), ('BEST_SEVEN', 'Best of Seven')], default='BEST_THREE', max_length=12)),
                ('is_qualifier', models.BooleanField(default=False)),
                ('is_semi', models.BooleanField(default=False)),
                ('is_final', models.BooleanField(default=False)),
                ('is_loser', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False)),
                ('is_bye', models.BooleanField(default=False)),
                ('first_deck_wins', models.PositiveSmallIntegerField(default=0)),
                ('second_deck_wins', models.PositiveSmallIntegerField(default=0)),
                ('is_complete', models.BooleanField(default=False)),
                ('date_completed', models.DateTimeField(blank=True, null=True)),
                ('first_deck', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tourney_match_first', to='deck.Deck')),
                ('group', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='tourney.Group')),
                ('second_deck', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tourney_match_second', to='deck.Deck')),
            ],
        ),
        migrations.CreateModel(
            name='Tourney',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('slug', models.SlugField(help_text='Unique value for tournament page URL, created from name.', unique=True)),
                ('format', models.CharField(choices=[('MODERN', 'Modern'), ('STANDARD', 'Standard'), ('LEGACY', 'Legacy'), ('VINTAGE', 'Vintage'), ('BLOCK', 'Block')], default='MODERN', max_length=12)),
                ('type', models.CharField(choices=[('CONSTRUCTED', 'Constructed'), ('DRAFT', 'Draft'), ('SEALED', 'Sealed'), ('COMMANDER', 'Commander')], default='CONSTRUCTED', max_length=12)),
                ('packs', models.CharField(default='Unlimited', help_text='If Block, Sealed, or Draft, note the associated packs/block', max_length=20)),
                ('qr_bracket', models.CharField(choices=[('SINGLE', 'Single'), ('DOUBLE', 'Double'), ('ROUND_ROBIN', 'Round Robin')], default='SINGLE', max_length=12)),
                ('bracket', models.CharField(choices=[('SINGLE', 'Single'), ('DOUBLE', 'Double'), ('ROUND_ROBIN', 'Round Robin')], default='SINGLE', help_text='If qualifying round is DOUBLE, this must also be DOUBLE.', max_length=12)),
                ('qr_rr_group_size', models.PositiveSmallIntegerField(default=4, help_text='Only used if Qualifying Round Bracket is Round Robin', verbose_name='QR Round Robin Group Size')),
                ('qr_rr_num_advance', models.PositiveSmallIntegerField(default=2, help_text='Must be less than qr_rr_group_size', verbose_name='QR Round Robin Number of Advancers')),
                ('rr_group_size', models.PositiveSmallIntegerField(default=4, help_text='Only used if Bracket is Round Robin', verbose_name='Round Robin Group Size')),
                ('rr_num_advance', models.PositiveSmallIntegerField(default=2, help_text='Must be less than rr_group_size', verbose_name='Round Robin Number of Advancers')),
                ('qr_elimination', models.CharField(choices=[('SINGLE', 'Single'), ('BEST_THREE', 'Best of Three'), ('BEST_FIVE', 'Best of Five'), ('BEST_SEVEN', 'Best of Seven')], default='BEST_THREE', max_length=12)),
                ('elimination', models.CharField(choices=[('SINGLE', 'Single'), ('BEST_THREE', 'Best of Three'), ('BEST_FIVE', 'Best of Five'), ('BEST_SEVEN', 'Best of Seven')], default='BEST_THREE', max_length=12)),
                ('semi_elimination', models.CharField(choices=[('SINGLE', 'Single'), ('BEST_THREE', 'Best of Three'), ('BEST_FIVE', 'Best of Five'), ('BEST_SEVEN', 'Best of Seven')], default='BEST_THREE', max_length=12)),
                ('final_elimination', models.CharField(choices=[('SINGLE', 'Single'), ('BEST_THREE', 'Best of Three'), ('BEST_FIVE', 'Best of Five'), ('BEST_SEVEN', 'Best of Seven')], default='BEST_THREE', max_length=12)),
                ('max_decks_per_player', models.PositiveSmallIntegerField(default=1)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('registration_deadline', models.DateTimeField(help_text='This datetime MUST be BEFORE the start datetime')),
                ('start_date', models.DateTimeField(help_text='All dates Eastern Standard Time!')),
                ('finished_date', models.DateTimeField(blank=True, null=True)),
                ('has_started', models.BooleanField(default=False)),
                ('is_finished', models.BooleanField(default=False)),
                ('decks', models.ManyToManyField(blank=True, to='deck.Deck')),
                ('winner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tourney_tourney_winner', to=settings.AUTH_USER_MODEL)),
                ('winning_deck', models.ManyToManyField(blank=True, related_name='tourney_tourney_windeck', to='deck.Deck')),
            ],
        ),
        migrations.AddField(
            model_name='match',
            name='tourney',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tourney.Tourney'),
        ),
        migrations.AddField(
            model_name='group',
            name='decks',
            field=models.ManyToManyField(blank=True, through='tourney.GroupStats', to='deck.Deck'),
        ),
        migrations.AddField(
            model_name='group',
            name='tourney',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='tourney.Tourney'),
        ),
    ]
