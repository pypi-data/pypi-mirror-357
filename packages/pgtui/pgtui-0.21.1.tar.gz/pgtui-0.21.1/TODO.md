TODO
====

* see about selecting rows/columns/blocks in the datatable
    * https://github.com/Textualize/textual/discussions/3606
* use datatable loading indicator
    * https://textual.textualize.io/guide/widgets/#loading-indicator
* figure out how to render the autocomplete menu in the \_tooltips layer,
  using \_absolute_offset instead of calculating it each time
* see about using COPY for exporting data
  https://www.psycopg.org/psycopg3/docs/basic/copy.html
* add way to reconnect after being disconnected from postgresql
* if connection is in transaction, add a popup asking the user to commit or
  rollback before doing an action which will close the connection such as
  closing pgtui or switching databases
* use command palette?
