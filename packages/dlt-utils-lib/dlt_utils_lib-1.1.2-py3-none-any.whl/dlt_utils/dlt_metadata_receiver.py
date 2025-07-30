def get_table_description(spark,
                          catalog_name: str,
                          table_schema: str) -> dict:
    bonze_table_comment = spark.sql(f'''
                        SELECT table_name, description
                                    FROM (
                                        SELECT *,
                                            ROW_NUMBER() OVER (PARTITION BY  table_catalog, table_schema,table_name ORDER BY last_updated_time DESC) as rn
                                        FROM apollo.core_map.ai_table_doc_metadata
                                        WHERE table_catalog = '{catalog_name}'
                                        AND table_schema = '{table_schema}'
                                    ) tmp
                                    WHERE rn = 1
                                    ''')

    return {el.table_name: el.description for el in
            bonze_table_comment.collect()} if bonze_table_comment.count() > 0 else {}


def get_column_comments(spark,
                        catalog_name: str,
                        table_schema: str) -> dict:
    bonze_column_comment = spark.sql(f'''
        SELECT table_name, column_name, comment
        FROM (
            SELECT *,
                   ROW_NUMBER() OVER (
                       PARTITION BY table_catalog, table_schema, table_name, column_name
                       ORDER BY last_updated_time DESC
                   ) as rn
            FROM apollo.core_map.ai_column_doc_metadata
            WHERE table_catalog = "{catalog_name}"
              AND table_schema = "{table_schema}"
        ) tmp
        WHERE rn = 1
    ''')

    rows = bonze_column_comment.collect()

    result = {}

    if not rows:
        return result

    for row in rows:
        table = row.table_name
        column = row.column_name
        comment = row.comment

        if table not in result:
            result[table] = {}

        result[table][column] = comment

    return result
