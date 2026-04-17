# Platform Statistics Dashboard

## Overview
A real-time statistics dashboard displaying platform metrics including user counts, trip data, and KYC verification status.

## Features

✅ **Real-time Data** - Fetches actual data from your database  
✅ **Interactive Charts** - Chart.js visualizations with 6-month history  
✅ **Responsive Design** - Works on desktop and tablets  
✅ **Auto-refresh** - Updates every 30 seconds automatically  
✅ **Beautiful UI** - Matches your platform's design language

## What's Displayed

### Stat Cards
- **Total Users** - All registered users
- **Active Users** - Users who logged in last 30 days or have active trips
- **Deleted Accounts** - Deactivated accounts
- **Total Trips** - All created trips
- **Completed Trips** - Finished trips
- **Verified Accounts** - Users with approved KYC
- **Non-Verified** - Users without approved KYC

### Charts (6-month history)
1. **User Growth** - Total vs Active users over time
2. **Trip Activity** - Total vs Completed trips over time
3. **Account Verification** - Verified vs Unverified users trend
4. **Account Status** - Active vs Deleted accounts trend

## How to Access

### Development
```
http://localhost:8000/stats/
```

### Production
```
https://your-domain.com/stats/
```

### API Endpoint
Get raw JSON data:
```
GET /api/stats/
```

Response format:
```json
{
  "success": true,
  "stats": {
    "total_users": 12400,
    "active_users": 7800,
    "deleted_accounts": 50,
    "total_trips": 5300,
    "completed_trips": 3900,
    "verified_users": 9100,
    "non_verified_users": 3300
  },
  "chart_data": {
    "months": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
    "total_users": [...],
    "active_users": [...],
    ...
  }
}
```

## Files Created/Modified

### New Files
- `core/templates/stats_dashboard.html` - Dashboard UI and charts
- `core/urls.py` - URL routing for stats

### Modified Files
- `core/views.py` - Added statistics views
- `travel_companion/urls.py` - Included core URLs

## Requirements
- Chart.js (loaded from CDN)
- Django Templates
- All standard Django components

## Data Definitions

**Active Users**: Users who have:
- Logged in within the last 30 days, OR
- Have active trips (end date >= today)

**Completed Trips**: Trips where `is_completed = True` AND end_date < today

**Verified Accounts**: Users with `KYCProfile.status = 'approved'`

**Non-Verified**: All other users (pending, under_review, rejected, or no KYC)

## Customization

To modify the dashboard:

1. **Colors**: Edit CSS variables in `stats_dashboard.html` (`:root` section)
2. **Refresh Rate**: Change interval in JavaScript (currently 30 seconds)
3. **Time Period**: Modify the date range logic in `api_stats()` view
4. **Chart Types**: Edit chart configurations in the JavaScript

## Performance Notes

- Data is calculated on-demand (not cached)
- For very large databases, consider adding caching
- Each request calculates 6 months of historical data
- Typical response time: < 500ms

## Security

The dashboard currently has no authentication required. To add admin/staff-only access, modify the views:

```python
from django.contrib.auth.decorators import permission_required

@permission_required('auth.change_user', redirect_field_name=None)
def stats_dashboard(request):
    ...
```

## Troubleshooting

**Dashboard showing "Loading..." forever?**
- Check browser console for errors
- Verify `/api/stats/` endpoint is accessible
- Check Django logs for backend errors

**Charts not displaying?**
- Clear browser cache
- Check that Chart.js CDN is accessible
- Verify no JavaScript errors in console

**Data looks incorrect?**
- Run database migrations
- Check that all models are created properly
- Verify KYCProfile data exists

## Future Enhancements

Potential improvements:
- [ ] Date range selection
- [ ] Export to CSV/PDF
- [ ] Admin authentication requirement
- [ ] Email report scheduling
- [ ] More granular time periods
- [ ] Filtering by date ranges
- [ ] User demographic breakdowns
