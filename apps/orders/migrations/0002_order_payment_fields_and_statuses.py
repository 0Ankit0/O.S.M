from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("finances", "0002_webhookevent_paymenttransaction"),
        ("orders", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="payment_gateway",
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name="order",
            name="payment_status",
            field=models.CharField(
                choices=[
                    ("unpaid", "Unpaid"),
                    ("pending", "Pending"),
                    ("completed", "Completed"),
                    ("failed", "Failed"),
                    ("refunded", "Refunded"),
                ],
                default="unpaid",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="order",
            name="payment_transaction",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="orders",
                to="finances.paymenttransaction",
            ),
        ),
        migrations.AlterField(
            model_name="order",
            name="status",
            field=models.CharField(
                choices=[
                    ("draft", "Draft"),
                    ("pending_payment", "Pending Payment"),
                    ("confirmed", "Confirmed"),
                    ("fulfilled", "Fulfilled"),
                    ("cancelled", "Cancelled"),
                    ("failed", "Failed"),
                ],
                default="draft",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="orderstatusevent",
            name="from_status",
            field=models.CharField(
                blank=True,
                choices=[
                    ("draft", "Draft"),
                    ("pending_payment", "Pending Payment"),
                    ("confirmed", "Confirmed"),
                    ("fulfilled", "Fulfilled"),
                    ("cancelled", "Cancelled"),
                    ("failed", "Failed"),
                ],
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="orderstatusevent",
            name="to_status",
            field=models.CharField(
                choices=[
                    ("draft", "Draft"),
                    ("pending_payment", "Pending Payment"),
                    ("confirmed", "Confirmed"),
                    ("fulfilled", "Fulfilled"),
                    ("cancelled", "Cancelled"),
                    ("failed", "Failed"),
                ],
                max_length=20,
            ),
        ),
    ]
