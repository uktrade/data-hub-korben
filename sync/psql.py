def main(metadata, resp_dir, entity_name):
    table = metadata.tables[entity_name + 'Set']
    col_names = [col.name for col in table.columns]
    # assume one column
    out_temp = tempfile.NamedTemporaryFile(delete=False)

    out_temp_fh = open(out_temp.name, 'w')
    writer = csv.DictWriter(out_temp_fh, col_names, dialect='excel')
    print("Parsing responses from {0}".format(entity_name))

    pages = sorted(os.listdir(os.path.join(resp_dir, entity_name)), key=int)
    '''
    try:
        sample_entry = unpickle_resp(resp_dir, entity_name, pages[0]).find(ENTRY_TAG)
    except AttributeError:
        print('Could not get sample entry')
        exit(1)
    link_fkey_map = utils.link_fkey_map(table, sample_entry)
    '''
    for page in pages:
        root = unpickle_resp(resp_dir, entity_name, page)
        rows = []
        if not root.findall(ENTRY_TAG):
            print('Breaking')
            break
        entries = root.findall(ENTRY_TAG)
        for entry in entries:
            rows.append(utils.entry_row(col_names, None, entry))
        for row in rows:
            writer.writerow(row)
    out_temp_fh.close()
    # print("CSV: {0}".format(out_temp.name))
    # print("SQL: {0}".format(psql_temp.name))
    psql_temp = tempfile.NamedTemporaryFile(delete=False)
    with open(psql_temp.name, 'w') as psql_temp_fh:
        psql_temp_fh.write(
            PSQL_STRAIGHT.format(table.name, out_temp.name)
        )
    psql_proc = subprocess.Popen([
        '/usr/local/pgsql/bin/psql',
        '-d', 'cdms_psql', '-f', psql_temp.name
    ])
    returncode = psql_proc.wait()
    if returncode > 0:
        with open(psql_temp.name, 'w') as psql_temp_fh:
            psql_temp_fh.write(
                PSQL_DEDUPE.format(table.name, out_temp.name, primary_key)
            )
            psql_proc = subprocess.Popen([
                '/usr/local/pgsql/bin/psql',
                '-d', 'cdms_psql', '-f', psql_temp.name
            ])
            returncode = psql_proc.wait()
    return (out_temp, psql_temp), returncode
