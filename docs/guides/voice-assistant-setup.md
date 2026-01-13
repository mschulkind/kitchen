# Google Home / Assistant Setup Guide 🎙️

> 🤖 **Goal**: "Hey Google, add milk to the list" -> Adds item to Kitchen App.

This guide explains how to connect your Google Home/Assistant ecosystem to the Kitchen API. Since Google deprecated "Conversational Actions" in 2023, the most reliable method for personal projects is using **Webhooks** via **IFTTT** or **Home Assistant**.

## Prerequisites

- **Kitchen API** running and accessible from the internet (e.g., via Cloudflare Tunnel, ngrok, or VPS IP).
- **Google Home** device or Google Assistant on phone.
- **IFTTT Account** (Free tier works for 2 applets) OR **Home Assistant** instance.

## Method 1: IFTTT (Simplest) 🔌

This method connects Google Assistant directly to your Kitchen API webhook.

### 1. Create the Applet

1.  Log in to [IFTTT](https://ifttt.com/).
2.  Click **Create**.
3.  **If This**: Select **Google Assistant v2**.
    *   Choose trigger: **"Say a phrase with a text ingredient"**.
    *   *What do you want to say?*: `Add $ to my kitchen list` (or just `Kitchen add $`).
    *   *What's another way?*: `Buy $`.
    *   *Your Assistant's response*: `Okay, adding $ to the kitchen list.`
4.  **Then That**: Select **Webhooks**.
    *   Choose action: **"Make a web request"**.
    *   **URL**: `https://<YOUR-API-DOMAIN>/api/v1/hooks/add-item`
    *   **Method**: `POST`
    *   **Content Type**: `application/json`
    *   **Additional Headers**: `X-Webhook-Key: <YOUR_WEBHOOK_SECRET>`
    *   **Body**: `{"text": "{{TextField}}"}`

### 2. Configure Your API

Ensure your `.env` file has a secure secret:

```bash
WEBHOOK_SECRET=my-super-secret-voice-key-123
```

### 3. Test It

*   "Hey Google, Kitchen add Milk and Eggs."
*   Google: "Okay, adding Milk and Eggs to the kitchen list."
*   Check Kitchen App: "Milk" and "Eggs" should appear in your shopping list.

---

## Method 2: Home Assistant (Advanced) 🏠

If you run Home Assistant (HA), this gives you more control and doesn't rely on IFTTT limits.

### 1. Define REST Command

Add to your `configuration.yaml`:

```yaml
rest_command:
  kitchen_add_item:
    url: "http://<KITCHEN-API-IP>:5300/api/v1/hooks/add-item"
    method: POST
    headers:
      X-Webhook-Key: "my-super-secret-voice-key-123"
      Content-Type: "application/json"
    payload: '{"text": "{{ text }}"}'
```

### 2. Expose to Google Assistant

Ensure your HA is connected to Google Assistant (via Nabu Casa or manual setup).

### 3. Create a Script/Automation

Create a script in HA that takes a variable and calls the REST command.

```yaml
alias: "Add to Kitchen List"
sequence:
  - service: rest_command.kitchen_add_item
    data:
      text: "{{ text }}"
```

You can then expose this script to Google Home as a Scene or use an automation to trigger it.

---

## Troubleshooting 🔧

### "I don't have a public IP"

If your API is running on `localhost` or a local server:

1.  **Cloudflare Tunnel (Recommended)**:
    *   Install `cloudflared`.
    *   Run `cloudflared tunnel --url http://localhost:5300`.
    *   Use the generated `https://....trycloudflare.com` URL in IFTTT.

2.  **Tailscale Funnel**:
    *   If you use Tailscale, `tailscale funnel 5300`.

### "It says 401 Unauthorized"

*   Check that `X-Webhook-Key` in IFTTT matches `WEBHOOK_SECRET` in your `.env`.
*   Ensure the header is formatted exactly as `X-Webhook-Key: value`.

### "It adds 'milk and eggs' as one item"

*   The backend parser (`VoiceParser`) is responsible for splitting "and".
*   Check logs: `src/api/app/domain/voice/parser.py` logic might need tuning.
