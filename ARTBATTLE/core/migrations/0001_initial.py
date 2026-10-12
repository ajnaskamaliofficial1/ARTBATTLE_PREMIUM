import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.CreateModel(
            name='ArtistProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('display_name', models.CharField(max_length=80)),
                ('bio', models.TextField(blank=True)),
                ('avatar', models.ImageField(blank=True, null=True, upload_to='avatars/')),
                ('country', models.CharField(blank=True, max_length=60)),
                ('website', models.URLField(blank=True)),
                ('rating', models.PositiveIntegerField(default=0)),
                ('wins', models.PositiveIntegerField(default=0)),
                ('top_three', models.PositiveIntegerField(default=0)),
                ('battles_joined', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='artist', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Battle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=120)),
                ('theme', models.CharField(max_length=120)),
                ('description', models.TextField(blank=True)),
                ('start_at', models.DateTimeField()),
                ('submission_deadline', models.DateTimeField()),
                ('voting_deadline', models.DateTimeField()),
                ('prize_text', models.CharField(default='Sponsor-funded prize', max_length=160)),
                ('prize_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('status', models.CharField(choices=[('draft','Draft'),('open','Open'),('voting','Voting'),('closed','Closed')], default='draft', max_length=10)),
                ('is_monthly', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'ordering': ['-start_at']},
        ),
        migrations.CreateModel(
            name='Artwork',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=140)),
                ('description', models.TextField(blank=True)),
                ('image', models.ImageField(upload_to='artworks/')),
                ('medium', models.CharField(blank=True, max_length=80)),
                ('ai_declared', models.BooleanField(default=False)),
                ('image_hash', models.CharField(editable=False, max_length=64)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('votes', models.PositiveIntegerField(default=0)),
                ('integrity_status', models.CharField(default='Pending review', max_length=40)),
                ('artist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='artworks', to='core.artistprofile')),
                ('battle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='artworks', to='core.battle')),
            ],
            options={'ordering': ['-votes','-created_at'], 'constraints': [models.UniqueConstraint(fields=('battle','artist'), name='one_entry_per_artist_per_battle')]},
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('artwork', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vote_records', to='core.artwork')),
                ('voter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='votes', to=settings.AUTH_USER_MODEL)),
            ],
            options={'constraints': [models.UniqueConstraint(fields=('artwork','voter'), name='one_vote_per_user')]},
        ),
        migrations.CreateModel(
            name='Winner',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rank', models.PositiveIntegerField(default=1)),
                ('awarded_at', models.DateTimeField(auto_now_add=True)),
                ('prize_note', models.CharField(blank=True, max_length=200)),
                ('artwork', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.artwork')),
                ('battle', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='winner', to='core.battle')),
            ],
        ),
    ]
