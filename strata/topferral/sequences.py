from .. import toolkit


class SequenceGenerator(object):
    def cleanup(self):
        ctx = toolkit.context()
        id = ctx.query(
            "SELECT id FROM sequences WHERE TIMESTAMPDIFF(MINUTE, created, CURRENT_TIMESTAMP) > 10 ORDER BY id DESC LIMIT 1;"
        ).scalar()
        if id is not None:
            sql = "DELETE FROM sequences WHERE id < %s;" % str(id)
            ctx.query(sql).update()

    def next(self):
        return self.generate()

    def generate(self, *count):
        token = toolkit.guid()
        ctx = toolkit.context()
        count = 1 if len(count) == 0 else count[0]
        if count < 2:
            id = ctx.query("INSERT INTO sequences (token) VALUES ('%s');" % token).insert()
            return id

        queries = ctx.query_buffer()
        for x in xrange(count):
            queries.append("INSERT INTO sequences (token) VALUES ('%s');" % token)

        queries.execute()
        keys = ctx.query("SELECT id FROM sequences WHERE token='%s';" % token).scalars()
        return keys