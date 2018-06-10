import logging

from django.core.management.base import BaseCommand, CommandError
from django.db import connection


logger = logging.getLogger('eliyahu.geography.load_settlements_from_gov')


def fetch_csv():
    from urllib.request import urlopen
    import io

    # https://data.gov.il/dataset/citiesandsettelments CSV
    URL = 'https://data.gov.il/dataset/citiesandsettelments/resource/d4901968-dad3-4845-a9b0-a57d027f11ab/download'
    response_bytes = urlopen(URL, timeout=30)

    response_text = io.TextIOWrapper(response_bytes, encoding='windows-1255')

    return response_text


def load_csv_to_temp_table(cursor, csv):
    TABLE_NAME = 'temp_settlements_csv_table'

    # טבלה
    # סמל_ישוב
    # שם_ישוב
    # שם_ישוב_לועזי
    # סמל_נפה
    # שם_נפה
    # סמל_לשכת_מנא
    # לשכה
    # סמל_מועצה_איזורית
    # שם_מועצה
    cursor.execute('''
        CREATE TEMPORARY TABLE {} (
            table_name varchar(100),
            settlement_gov_id integer,
            settlement_name varchar(100),
            settlement_name_english varchar(100),
            county_gov_id integer,
            county_name varchar(100),
            lishka_gov_id integer,
            lishka_name varchar(100),
            municipality_gov_id integer,
            municipality_name varchar(100)
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
        INSERT INTO geography_settlement AS settlement (
            created_at,
            modified_at,
            gov_id,
            name,
            county_gov_id,
            county_name,
            municipality_gov_id,
            municipality_name
        )
        SELECT
            NOW() AS created_at,
            NOW() AS modified_at,
            csv.settlement_gov_id AS gov_id,
            TRANSLATE(TRIM(BOTH FROM csv.settlement_name), '()', ')(') AS name,
            csv.county_gov_id AS county_gov_id,
            TRANSLATE(TRIM(BOTH FROM csv.county_name), '()', ')(') AS county_name,
            csv.municipality_gov_id AS municipality_gov_id,
            TRANSLATE(TRIM(BOTH FROM csv.municipality_name), '()', ')(') AS municipality_name
        FROM
            {} csv
        ON CONFLICT (gov_id) DO UPDATE SET
            modified_at = EXCLUDED.modified_at,
            name = EXCLUDED.name,
            county_gov_id = EXCLUDED.county_gov_id,
            county_name = EXCLUDED.county_name,
            municipality_gov_id = EXCLUDED.municipality_gov_id,
            municipality_name = EXCLUDED.municipality_name
        WHERE
            settlement.name != EXCLUDED.name;
    '''.format(table_name))


class Command(BaseCommand):
    help = 'Synchronize settlements table from data.gov.il'

    def handle(self, *args, **options):
        try:
            csv = fetch_csv()
        except Exception as e:
            logger.exception('failed to fetch csv')
            raise CommandError('Failed to load settlements') from e

        with connection.cursor() as cursor:
            try:
                with csv:
                    table_name = load_csv_to_temp_table(cursor, csv)
            except Exception as e:
                logger.exception('failed to load temp table')
                raise CommandError('Failed to load settlements') from e

            try:
                sync_from_temp_table(cursor, table_name)
            except Exception as e:
                logger.exception('failed to sync from temp table')
                raise CommandError('Failed to load settlements') from e

        self.stdout.write(self.style.SUCCESS('Loaded settlements'))
