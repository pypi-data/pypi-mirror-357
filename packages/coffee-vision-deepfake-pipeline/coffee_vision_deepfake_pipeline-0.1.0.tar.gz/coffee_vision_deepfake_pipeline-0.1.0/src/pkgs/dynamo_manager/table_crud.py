
# add records in bulk
def put_items_bulk(table_client, items):
    with table_client.batch_writer() as batch:
        for item in items:
            batch.put_item(Item=item)

# Add record
def put_item(table, item):
    return table.put_item(Item=item)

# Get record by primary key
def get_item(table_client, pk_key, pk_value):
    return table_client.get_item(Key={pk_key: pk_value}).get('Item')
