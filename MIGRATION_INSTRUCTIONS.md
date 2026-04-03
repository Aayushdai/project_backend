# Migration Instructions

## What Changed in the Model

The `Message` model's `receiver` field was changed to be **nullable**:

```python
# Before:
receiver = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='received_messages')

# After:
receiver = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='received_messages', null=True, blank=True)
```

This allows group messages (where `receiver=NULL` and `trip=<TripID>`).

## Running Migrations

### 1. Create Migration File

```bash
cd Travel_Companion_Backend
python manage.py makemigrations apps.chat
```

You should see output like:
```
Migrations for 'chat':
  apps/chat/migrations/XXXX_auto_YYYYMMDD_HHMM.py
    - Alter field receiver on message
```

### 2. Apply Migration

```bash
python manage.py migrate apps.chat
```

You should see output like:
```
Running migrations:
  Applying chat.0004_alter_message_receiver... OK
```

### 3. Verify Success

```bash
python manage.py migrate --plan
```

You should see no pending migrations for chat app.

## If Something Goes Wrong

### Undo Last Migration (if not in production)
```bash
python manage.py migrate chat 0003  # Go back to previous migration
python manage.py migrate chat zero  # Clear all migrations
```

### Check Current Migration Status
```bash
python manage.py showmigrations chat
```

### Full Reset (Development Only!)
```bash
# Delete the database
rm db.sqlite3

# Recreate all tables
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

## After Migration

1. **Start the server**:
   ```bash
   python manage.py runserver
   ```

2. **Test the API**:
   ```bash
   curl -X POST http://localhost:8000/chat/api/messages/ \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"content":"Test message","trip_id":1}'
   ```

3. **Check database**:
   ```bash
   python manage.py dbshell
   sqlite> .schema chat_message
   ```

## Common Issues

### Issue: "No changes detected in app 'chat'"
**Solution**: Ensure you saved all changes to `models.py`

### Issue: "You are trying to change the field while ..."
**Solution**: This is normal - Django is creating a migration. Proceed with apply.

### Issue: Migration fails with "value for receiver cannot be null"
**Solution**: The migration will automatically handle existing records (set to NULL).

### Issue: "Table already exists"
**Solution**: You may need to delete old migration files if using SQLite.

## Troubleshooting Commands

```bash
# List all installed apps and their migrations
python manage.py migrate --plan

# Show detailed migration info
python manage.py showmigrations --list

# Check what migrate would do (dry run)
python manage.py migrate chat --plan

# Detailed error information
python manage.py migrate --verbosity 3

# Squash old migrations (if many exist)
python manage.py squashmigrations chat 0001 0003
```

## For Production

If deploying to production:

```bash
# 1. Backup database
cp db.sqlite3 db.sqlite3.backup

# 2. Run migrations
python manage.py migrate apps.chat

# 3. Restart application
systemctl restart your_app

# 4. Verify
python manage.py shell -c "from apps.chat.models import Message; print(f'Messages: {Message.objects.count()}')"
```

## Migration Files Generated

The migration file created will be something like:
`apps/chat/migrations/0004_alter_message_receiver.py`

Contents will be similar to:
```python
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0003_chatmessage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='receiver',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='received_messages', to='users.userprofile'),
        ),
    ]
```

## Timeline

1. **Run makemigrations**: ~1 second
2. **Run migrate**: ~1-5 seconds (depending on database size)
3. **Verify**: ~1 second

Total: ~10 seconds for the process

---

**Status**: Ready to run
**Estimated Time**: 2 minutes
**Risk Level**: Low (just adding NULL to a column)