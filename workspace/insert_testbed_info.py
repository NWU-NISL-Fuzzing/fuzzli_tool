import sqlite3

db = sqlite3.connect('top2000corpus-20250619.db')
cursor = db.cursor()
sql = """INSERT INTO "main"."Engines" ("id", "testbed", "engine_name", "version", "mode") VALUES (1, '/home/fuzzli_tool/engines/hermes/hermes-0.12.0/build_release/bin/hermes -w', 'hermes', '0.12.0', NULL);
INSERT INTO "main"."Engines" ("id", "testbed", "engine_name", "version", "mode") VALUES (2, '/home/fuzzli_tool/engines/quickjs/quickjs-2021-03-27/qjs', 'quickjs', '2021-03-27', NULL);
INSERT INTO "main"."Engines" ("id", "testbed", "engine_name", "version", "mode") VALUES (3, '/home/fuzzli_tool/engines/jerryscript/jerryscript-2.4.0/jerryscript-2.4.0/build/bin/jerry', 'jerryscript', '2.4.0', NULL);
INSERT INTO "main"."Engines" ("id", "testbed", "engine_name", "version", "mode") VALUES (4, '/home/fuzzli_tool/engines/XS/moddable-3.7.0/build/bin/lin/release/xst', 'xs', '3.7.0', NULL);
INSERT INTO "main"."Engines" ("id", "testbed", "engine_name", "version", "mode") VALUES (5, '/home/fuzzli_tool/engines/duktape/duktape-2.7.0/duk', 'duktape', '2.7.0', NULL);
INSERT INTO "main"."Engines" ("id", "testbed", "engine_name", "version", "mode") VALUES (6, '/home/fuzzli_tool/engines/mujs/mujs-1.3.2/build/release/mujs', 'mujs', '1.3.2', NULL);
"""
for line in sql.split('\n'):
    if line.strip() != '':
        cursor.execute(line)
db.commit()
db.close()