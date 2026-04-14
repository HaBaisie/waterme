from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='VendorProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('business_name', models.CharField(max_length=150)),
                ('avatar_url', models.URLField(blank=True)),
                ('service_area_latitude', models.FloatField()),
                ('service_area_longitude', models.FloatField()),
                ('service_radius_km', models.DecimalField(decimal_places=2, default=10, max_digits=6)),
                ('price_per_litre', models.DecimalField(decimal_places=2, max_digits=10)),
                ('min_order_litres', models.PositiveIntegerField(default=500)),
                ('max_order_litres', models.PositiveIntegerField(default=10000)),
                ('tanker_capacity_litres', models.PositiveIntegerField(default=10000)),
                ('available_litres', models.PositiveIntegerField(default=0)),
                ('available', models.BooleanField(default=False)),
                ('eta_minutes', models.PositiveIntegerField(default=30)),
                ('verification_status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', max_length=20)),
                ('bank_code', models.CharField(blank=True, max_length=20)),
                ('account_number', models.CharField(blank=True, max_length=20)),
                ('account_name', models.CharField(blank=True, max_length=100)),
                ('schedule', models.JSONField(blank=True, default=dict)),
                ('rating_average', models.DecimalField(decimal_places=2, default=0, max_digits=3)),
                ('review_count', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='vendor_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['business_name'],
            },
        ),
    ]
