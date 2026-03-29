# Kengo Website Setup

## Environment Variables

The following environment variables must be set in Vercel for full functionality:

### Required for /demo page (Live Interactive Demo)

| Variable | Description | Where to get it |
|---|---|---|
| `ANTHROPIC_API_KEY` | Claude API key for personalized demo | [console.anthropic.com](https://console.anthropic.com) |

### How to add in Vercel:

1. Go to [vercel.com](https://vercel.com) → Your Project → Settings → Environment Variables
2. Add `ANTHROPIC_API_KEY` with your API key value
3. Set it for Production, Preview, and Development environments
4. Redeploy the project (Settings → Deployments → Redeploy)

### Without the API key:

The /demo page will still work — it uses a fallback response that generates 3 generic (but still compelling) tasks for any company name entered. With the API key, Claude Sonnet generates truly personalized, industry-specific tasks for each company.
