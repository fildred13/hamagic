# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'GroupStats'
        db.create_table(u'tourney_groupstats', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('deck', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['deck.Deck'])),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tourney.Group'])),
            ('points', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0)),
            ('margin', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0)),
        ))
        db.send_create_signal(u'tourney', ['GroupStats'])

        # Deleting field 'Group.deck_8_points'
        db.delete_column(u'tourney_group', 'deck_8_points')

        # Deleting field 'Group.deck_6_points'
        db.delete_column(u'tourney_group', 'deck_6_points')

        # Deleting field 'Group.deck_1_margin'
        db.delete_column(u'tourney_group', 'deck_1_margin')

        # Deleting field 'Group.deck_5_margin'
        db.delete_column(u'tourney_group', 'deck_5_margin')

        # Deleting field 'Group.deck_2_points'
        db.delete_column(u'tourney_group', 'deck_2_points')

        # Deleting field 'Group.deck_1_points'
        db.delete_column(u'tourney_group', 'deck_1_points')

        # Deleting field 'Group.deck_3_margin'
        db.delete_column(u'tourney_group', 'deck_3_margin')

        # Deleting field 'Group.deck_7_margin'
        db.delete_column(u'tourney_group', 'deck_7_margin')

        # Deleting field 'Group.deck_7_points'
        db.delete_column(u'tourney_group', 'deck_7_points')

        # Deleting field 'Group.deck_6_margin'
        db.delete_column(u'tourney_group', 'deck_6_margin')

        # Deleting field 'Group.deck_5_points'
        db.delete_column(u'tourney_group', 'deck_5_points')

        # Deleting field 'Group.deck_4_margin'
        db.delete_column(u'tourney_group', 'deck_4_margin')

        # Deleting field 'Group.deck_2_margin'
        db.delete_column(u'tourney_group', 'deck_2_margin')

        # Deleting field 'Group.deck_4_points'
        db.delete_column(u'tourney_group', 'deck_4_points')

        # Deleting field 'Group.deck_3_points'
        db.delete_column(u'tourney_group', 'deck_3_points')

        # Deleting field 'Group.deck_8_margin'
        db.delete_column(u'tourney_group', 'deck_8_margin')

        # Removing M2M table for field decks on 'Group'
        db.delete_table('tourney_group_decks')


    def backwards(self, orm):
        # Deleting model 'GroupStats'
        db.delete_table(u'tourney_groupstats')

        # Adding field 'Group.deck_8_points'
        db.add_column(u'tourney_group', 'deck_8_points',
                      self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Group.deck_6_points'
        db.add_column(u'tourney_group', 'deck_6_points',
                      self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Group.deck_1_margin'
        db.add_column(u'tourney_group', 'deck_1_margin',
                      self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Group.deck_5_margin'
        db.add_column(u'tourney_group', 'deck_5_margin',
                      self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Group.deck_2_points'
        db.add_column(u'tourney_group', 'deck_2_points',
                      self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Group.deck_1_points'
        db.add_column(u'tourney_group', 'deck_1_points',
                      self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Group.deck_3_margin'
        db.add_column(u'tourney_group', 'deck_3_margin',
                      self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Group.deck_7_margin'
        db.add_column(u'tourney_group', 'deck_7_margin',
                      self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Group.deck_7_points'
        db.add_column(u'tourney_group', 'deck_7_points',
                      self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Group.deck_6_margin'
        db.add_column(u'tourney_group', 'deck_6_margin',
                      self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Group.deck_5_points'
        db.add_column(u'tourney_group', 'deck_5_points',
                      self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Group.deck_4_margin'
        db.add_column(u'tourney_group', 'deck_4_margin',
                      self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Group.deck_2_margin'
        db.add_column(u'tourney_group', 'deck_2_margin',
                      self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Group.deck_4_points'
        db.add_column(u'tourney_group', 'deck_4_points',
                      self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Group.deck_3_points'
        db.add_column(u'tourney_group', 'deck_3_points',
                      self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Group.deck_8_margin'
        db.add_column(u'tourney_group', 'deck_8_margin',
                      self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0),
                      keep_default=False)

        # Adding M2M table for field decks on 'Group'
        db.create_table(u'tourney_group_decks', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('group', models.ForeignKey(orm[u'tourney.group'], null=False)),
            ('deck', models.ForeignKey(orm[u'deck.deck'], null=False))
        ))
        db.create_unique(u'tourney_group_decks', ['group_id', 'deck_id'])


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'deck.deck': {
            'Meta': {'object_name': 'Deck'},
            'created_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'format': ('django.db.models.fields.CharField', [], {'default': "'MODERN'", 'max_length': '12'}),
            'game_losses': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'game_wins': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'main_deck': ('django.db.models.fields.TextField', [], {}),
            'match_losses': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'match_wins': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'}),
            'sideboard': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'tourney_finals': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'tourney_losses': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'tourney_semis': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'tourney_wins': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'CONSTRUCTED'", 'max_length': '12'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'tourney.group': {
            'Meta': {'object_name': 'Group'},
            'decks': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['deck.Deck']", 'null': 'True', 'through': u"orm['tourney.GroupStats']", 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'round': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'size': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'tourney': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tourney.Tourney']", 'null': 'True', 'blank': 'True'})
        },
        u'tourney.groupstats': {
            'Meta': {'object_name': 'GroupStats'},
            'deck': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['deck.Deck']"}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tourney.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'margin': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'points': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'})
        },
        u'tourney.match': {
            'Meta': {'object_name': 'Match'},
            'date_completed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'elimination': ('django.db.models.fields.CharField', [], {'default': "'BEST_THREE'", 'max_length': '12'}),
            'first_deck': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'tourney_match_first'", 'null': 'True', 'to': u"orm['deck.Deck']"}),
            'first_deck_wins': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tourney.Group']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_bye': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_complete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_final': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_loser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_qualifier': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_semi': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'position': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'round': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'second_deck': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'tourney_match_second'", 'null': 'True', 'to': u"orm['deck.Deck']"}),
            'second_deck_wins': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'tourney': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tourney.Tourney']"})
        },
        u'tourney.tourney': {
            'Meta': {'object_name': 'Tourney'},
            'bracket': ('django.db.models.fields.CharField', [], {'default': "'SINGLE'", 'max_length': '12'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'decks': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['deck.Deck']", 'null': 'True', 'blank': 'True'}),
            'elimination': ('django.db.models.fields.CharField', [], {'default': "'BEST_THREE'", 'max_length': '12'}),
            'final_elimination': ('django.db.models.fields.CharField', [], {'default': "'BEST_THREE'", 'max_length': '12'}),
            'finished_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'format': ('django.db.models.fields.CharField', [], {'default': "'MODERN'", 'max_length': '12'}),
            'has_started': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_finished': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'max_decks_per_player': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'qr_bracket': ('django.db.models.fields.CharField', [], {'default': "'SINGLE'", 'max_length': '12'}),
            'qr_elimination': ('django.db.models.fields.CharField', [], {'default': "'BEST_THREE'", 'max_length': '12'}),
            'qr_rr_group_size': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '4'}),
            'qr_rr_num_advance': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '2'}),
            'registration_deadline': ('django.db.models.fields.DateTimeField', [], {}),
            'rr_group_size': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '4'}),
            'rr_num_advance': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '2'}),
            'semi_elimination': ('django.db.models.fields.CharField', [], {'default': "'BEST_THREE'", 'max_length': '12'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'CONSTRUCTED'", 'max_length': '12'}),
            'winner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'tourney_tourney_winner'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'winning_deck': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'tourney_tourney_windeck'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['deck.Deck']"})
        }
    }

    complete_apps = ['tourney']