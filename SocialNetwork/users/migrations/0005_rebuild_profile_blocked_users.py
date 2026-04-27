from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_profile_name'),
    ]

    operations = [
        migrations.RunSQL(
            sql=[
                """
                CREATE TABLE "users_profile_blocked_users_new" (
                    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                    "profile_id" bigint NOT NULL REFERENCES "users_profile" ("id") DEFERRABLE INITIALLY DEFERRED,
                    "user_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED
                )
                """,
                """
                INSERT INTO "users_profile_blocked_users_new" ("profile_id", "user_id")
                SELECT p."id", old."user_id"
                FROM "users_profile_blocked_users" old
                JOIN "users_profile" p ON p."slug" = old."profile_id"
                """,
                'DROP TABLE "users_profile_blocked_users"',
                'ALTER TABLE "users_profile_blocked_users_new" RENAME TO "users_profile_blocked_users"',
                """
                CREATE UNIQUE INDEX "users_profile_blocked_users_profile_id_user_id_9d6f2271_uniq"
                ON "users_profile_blocked_users" ("profile_id", "user_id")
                """,
                """
                CREATE INDEX "users_profile_blocked_users_profile_id_ec59e5f4"
                ON "users_profile_blocked_users" ("profile_id")
                """,
                """
                CREATE INDEX "users_profile_blocked_users_user_id_32b74840"
                ON "users_profile_blocked_users" ("user_id")
                """,
            ],
            reverse_sql=[
                'DROP INDEX IF EXISTS "users_profile_blocked_users_user_id_32b74840"',
                'DROP INDEX IF EXISTS "users_profile_blocked_users_profile_id_ec59e5f4"',
                'DROP INDEX IF EXISTS "users_profile_blocked_users_profile_id_user_id_9d6f2271_uniq"',
                """
                CREATE TABLE "users_profile_blocked_users_old" (
                    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                    "profile_id" varchar(30) NOT NULL REFERENCES "users_profile" ("slug") DEFERRABLE INITIALLY DEFERRED,
                    "user_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED
                )
                """,
                """
                INSERT INTO "users_profile_blocked_users_old" ("profile_id", "user_id")
                SELECT p."slug", new."user_id"
                FROM "users_profile_blocked_users" new
                JOIN "users_profile" p ON p."id" = new."profile_id"
                """,
                'DROP TABLE "users_profile_blocked_users"',
                'ALTER TABLE "users_profile_blocked_users_old" RENAME TO "users_profile_blocked_users"',
                """
                CREATE UNIQUE INDEX "users_profile_blocked_users_profile_id_user_id_9d6f2271_uniq"
                ON "users_profile_blocked_users" ("profile_id", "user_id")
                """,
                """
                CREATE INDEX "users_profile_blocked_users_profile_id_ec59e5f4"
                ON "users_profile_blocked_users" ("profile_id")
                """,
                """
                CREATE INDEX "users_profile_blocked_users_user_id_32b74840"
                ON "users_profile_blocked_users" ("user_id")
                """,
            ],
        ),
    ]
