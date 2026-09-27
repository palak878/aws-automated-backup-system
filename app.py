from flask import Flask, render_template
import boto3
from boto3.dynamodb.conditions import Key

app = Flask(__name__)

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table('BackupAuditLog')

@app.route('/')
def dashboard():
    response = table.scan()
    items = response.get('Items', [])
    items.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

    total_backups = len(items)
    successful = len([i for i in items if i.get('status') == 'SUCCESS'])
    failed = len([i for i in items if i.get('status') == 'FAILED'])

    return render_template('dashboard.html',
                            items=items,
                            total_backups=total_backups,
                            successful=successful,
                            failed=failed)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)