import sys

import sql_migrate as sql


def run():
    sql.migrate('/usr/db/Deployment')

if __name__ == '__main__':
    run()

    sys.exit(0)
