[README.md](https://github.com/user-attachments/files/25560223/README.md)
# 🎨 Daily Picasso Mastodon Bot

Posts a random Picasso painting (image + title + year) to Mastodon every day, scraped from artchive.com.

## Setup

### 1. Create a GitHub repo
Create a new repo and push these files to it.

### 2. Get your Mastodon credentials
1. Log into your Mastodon account
2. Go to **Preferences → Development → New Application**
3. Give it a name (e.g. "Picasso Bot"), and tick the `write:media` and `write:statuses` scopes
4. Click **Submit**, then copy the **Your access token**

### 3. Add GitHub Secrets
In your repo go to **Settings → Secrets and variables → Actions → New repository secret** and add:

| Secret name             | Value                            |
|-------------------------|----------------------------------|
| `MASTODON_BASE_URL`     | Your instance, e.g. `https://mastodon.social` |
| `MASTODON_ACCESS_TOKEN` | The token you copied above       |

### 4. Enable Actions
Go to the **Actions** tab in your repo and enable workflows if prompted.

### 5. Test it
Click **Actions → Daily Picasso Bot → Run workflow** to trigger it manually and confirm it posts correctly.

## Posting schedule
The bot runs daily at **12:00 UTC** by default. To change the time, edit the `cron` line in `.github/workflows/daily.yml`:

```yaml
- cron: "0 12 * * *"   # minute hour day month weekday
```

For example, `"0 9 * * *"` posts at 9:00 UTC.
