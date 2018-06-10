# Generated by Django 2.0.2 on 2018-02-10 17:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('adoptions', '0002_auto_20171224_0829'),
    ]

    operations = [
        # Add triggers to update status_set_at fields when status changes.
        migrations.RunSQL("""
            CREATE FUNCTION adoptions__update_status_set_at() RETURNS trigger AS $$
            BEGIN
                NEW.status_set_at = NOW();
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

            CREATE TRIGGER
                adoptions_adoption__status_set_at__update
            BEFORE UPDATE OF
                status
            ON
                adoptions_adoption
            FOR EACH ROW
            WHEN (
                OLD.status IS DISTINCT FROM NEW.status
            )
            EXECUTE PROCEDURE adoptions__update_status_set_at();


            CREATE TRIGGER
                adoptions_delivery__status_set_at__update
            BEFORE UPDATE OF
                status
            ON
                adoptions_delivery
            FOR EACH ROW
            WHEN (
                OLD.status IS DISTINCT FROM NEW.status
            )
            EXECUTE PROCEDURE adoptions__update_status_set_at();
        """),
    ]
