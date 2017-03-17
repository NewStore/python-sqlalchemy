import os
from sqlalchemy import MetaData, Table, Integer, String, Column, create_engine
from sqlalchemy import select
from sqlalchemy.schema import CreateTable

import lightstep
import sqlalchemy_opentracing

DB_LOCATION = '/tmp/simple.db'

tracer = lightstep.Tracer(
    component_name='sqlalchemy-simple',
    access_token='{your_lightstep_token}'
)


if __name__ == '__main__':
    os.remove(DB_LOCATION) # cleanup

    engine = create_engine('sqlite:///%s' % DB_LOCATION)
    conn = engine.connect()

    sqlalchemy_opentracing.init_tracing(tracer)
    sqlalchemy_opentracing.register_connectable(engine)

    span = tracer.start_span('create sample')

    # 1. Create a table
    metadata = MetaData()
    users = Table('users', metadata,
        Column('id', Integer, primary_key=True),
        Column('name', String),
    )
    span = tracer.start_span('create sample')
    creat = CreateTable(users)
    sqlalchemy_opentracing.set_parent_span(creat, span)
    conn.execute(creat)

    # 2. Insert a single value.
    ins = users.insert().values(name='John Doe', id=1)
    sqlalchemy_opentracing.set_parent_span(ins, span)
    conn.execute(ins)

    # 3. Select the new value.
    sel = select([users])
    sqlalchemy_opentracing.set_parent_span(sel, span)
    print conn.execute(sel).fetchone()

    span.finish()
    tracer.flush()

