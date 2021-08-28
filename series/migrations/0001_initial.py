# Generated by Django 2.2.23 on 2021-08-15 09:09

from django.db import migrations, models
import django.db.models.deletion
import djrichtextfield.models
import sort_order_field.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Episode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('slug', models.SlugField(max_length=100, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('description', models.TextField(blank=True, max_length=10000, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_freemium', models.BooleanField(default=False)),
                ('duration_seconds', models.IntegerField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('order', sort_order_field.fields.SortOrderField(db_index=True, default=0, verbose_name='Sort')),
            ],
            options={
                'ordering': ('order',),
            },
        ),
        migrations.CreateModel(
            name='Serial',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('slug', models.SlugField(max_length=100, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('description', models.TextField(blank=True, max_length=10000, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_freemium', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('content', djrichtextfield.models.RichTextField()),
                ('categories', models.ManyToManyField(blank=True, null=True, to='base.Category')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='base.Profile')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SerialImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_featured', models.BooleanField(default=False)),
                ('order', sort_order_field.fields.SortOrderField(db_index=True, default=0, verbose_name='Sort')),
                ('image', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.Image')),
                ('serial', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='series.Serial')),
            ],
            options={
                'ordering': ('order',),
            },
        ),
        migrations.AddField(
            model_name='serial',
            name='images',
            field=models.ManyToManyField(through='series.SerialImage', to='base.Image'),
        ),
    ]
