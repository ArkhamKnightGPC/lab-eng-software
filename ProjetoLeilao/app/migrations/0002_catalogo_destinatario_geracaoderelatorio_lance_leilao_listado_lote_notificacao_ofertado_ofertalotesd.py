# Generated by Django 3.2.8 on 2021-10-08 22:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Catalogo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='GeracaoDeRelatorio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Lance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valor', models.DecimalField(decimal_places=2, max_digits=11)),
            ],
        ),
        migrations.CreateModel(
            name='Leilao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=200)),
                ('valorMinimoLance', models.DecimalField(decimal_places=2, max_digits=11)),
                ('incrementoPorLance', models.DecimalField(decimal_places=2, max_digits=11)),
                ('dataInicio', models.TimeField()),
                ('dataFinal', models.TimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Lote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.TextField()),
                ('descricao', models.TextField()),
                ('estadoConservacao', models.TextField(choices=[('VELHO', 'VELHO'), ('SEMINOVO', 'SEMINOVO'), ('NOVO', 'NOVO')], default='VELHO')),
                ('estadoVenda', models.TextField(choices=[('VENDIDO', 'VENDIDO'), ('NAO VENDIDO', 'NÃO VENDIDO')], default='NAO VENDIDO')),
                ('valorReserva', models.DecimalField(decimal_places=2, max_digits=11)),
            ],
        ),
        migrations.CreateModel(
            name='Notificacao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('texto', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='OfertaLotesDeProduto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Pagamento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valor', models.DecimalField(decimal_places=2, max_digits=11)),
                ('data', models.TimeField()),
            ],
        ),
        migrations.CreateModel(
            name='RealizaLeilao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='realizado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comprador', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='app.comprador')),
                ('lance', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='app.lance')),
            ],
        ),
        migrations.CreateModel(
            name='ofertado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lote', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='app.lote')),
                ('vendedor', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='app.vendedor')),
            ],
        ),
        migrations.CreateModel(
            name='listado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('catalogo', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='app.catalogo')),
                ('leilao', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='app.leilao')),
            ],
        ),
        migrations.CreateModel(
            name='destinatario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notificacao', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='app.notificacao')),
                ('vendedor', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='app.vendedor')),
            ],
        ),
    ]