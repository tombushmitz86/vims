import logging

from django.db import connection
from django.core.management.base import BaseCommand, CommandError


logger = logging.getLogger('eliyahu.geography.load_streets_from_gov')


def fetch_csv():
    from urllib.request import urlopen
    import io

    # https://data.gov.il/dataset/321
    URL = 'https://data.gov.il/dataset/321/resource/a7296d1a-f8c9-4b70-96c2-6ebb4352f8e3/download'
    response_bytes = urlopen(URL, timeout=30)

    response_text = io.TextIOWrapper(response_bytes, encoding='windows-1255')

    return response_text


def load_csv_to_temp_table(cursor, csv):
    TABLE_NAME = 'temp_streets_csv_table'

    # טבלה
    # סמל_ישוב
    # שם_ישוב
    # סמל_רחוב
    # שם_רחוב
    cursor.execute('''
        CREATE TEMPORARY TABLE {} (
            table_name varchar(100),
            settlement_gov_id integer,
            settlement_name varchar(100),
            street_gov_id integer,
            street_name varchar(100)
        );
    '''.format(TABLE_NAME), ())

    # Skip date comment.
    next(csv)
    # Skip header.
    next(csv)

    cursor.copy_from(csv, table=TABLE_NAME, sep=',')

    return TABLE_NAME


def sync_from_temp_table(cursor, table_name):
    cursor.execute('''
        INSERT INTO geography_street AS street (
            created_at,
            modified_at,
            settlement_id,
            gov_id,
            name
        )
        SELECT
            NOW() AS created_at,
            NOW() AS modified_at,
            settlement.id AS settlement_id,
            csv.street_gov_id AS gov_id,
            TRANSLATE(TRIM(BOTH FROM csv.street_name), '()', ')(') AS name
        FROM
            {} csv,
            geography_settlement settlement
        WHERE
            settlement.gov_id = csv.settlement_gov_id
        ON CONFLICT (settlement_id, gov_id) DO UPDATE SET
            modified_at = EXCLUDED.modified_at,
            name = EXCLUDED.name
        WHERE
            street.name != EXCLUDED.name;
    '''.format(table_name))


class Command(BaseCommand):
    help = 'Synchronize streets table from data.gov.il'

    def handle(self, *args, **options):
        try:
            csv = fetch_csv()
        except Exception as e:
            logger.exception('failed to fetch csv')
            raise CommandError('Failed to load streets') from e

        with connection.cursor() as cursor:
            try:
                with csv:
                    table_name = load_csv_to_temp_table(cursor, csv)
            except Exception as e:
                logger.exception('failed to load temp table')
                raise CommandError('Failed to load streets') from e

            try:
                sync_from_temp_table(cursor, table_name)
            except Exception as e:
                logger.exception('failed to sync from temp table')
                raise CommandError('Failed to load streets') from e

        self.stdout.write(self.style.SUCCESS('Loaded streets'))
