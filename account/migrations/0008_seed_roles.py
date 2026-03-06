from django.db import migrations


def seed_roles(apps, schema_editor):
    Role = apps.get_model("account", "Role")
    for name in ("teacher", "student"):
        Role.objects.get_or_create(name=name)


def unseed_roles(apps, schema_editor):
    Role = apps.get_model("account", "Role")
    Role.objects.filter(name__in=["teacher", "student"]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("account", "0007_auto_20260226_1047"),
    ]

    operations = [
        migrations.RunPython(seed_roles, unseed_roles),
    ]
