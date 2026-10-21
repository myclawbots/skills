---
name: appointment_taker
description: Automated 24/7 appointment booking via web chat and WhatsApp. Syncs with Google Calendar, handles rescheduling and reminders.
author:
  name: MyClawBots
  url: https://myclawbots.ai
license: MIT
category: productivity
tags: [booking, calendar, whatsapp, scheduling]
suggested_template: customer_support
---

# Appointment Taker

This skill enables you to set up automated 24/7 appointment booking through web chat and WhatsApp, manage availability, handle rescheduling, send reminders, and sync all bookings to Google Calendar. All requests are handled through a proxy-wrapped appointment scheduling API.

> **Dashboard Connection:** Connect your Google Calendar and WhatsApp account to the MyClawBots dashboard before using this skill. The proxy will handle all authentication via `$PROXY_API_KEY` and `${PROXY_URL}`.

## Prerequisites

- Google Calendar account connected in dashboard
- WhatsApp Business Account configured (for WhatsApp booking channel)
- Valid `$PROXY_API_KEY` for the proxy
- Access to `${PROXY_URL}` endpoint
- Defined business hours and appointment types

## Dependencies

| Dependency | Required? | Why |
|---|---|---|
| Booking system connected via dashboard | Yes | The proxy needs a connected booking system to manage appointment requests |
| `${PROXY_URL}` and `$PROXY_API_KEY` configured | Yes | Required for all API calls to the appointment proxy endpoints |
| `google-workspace` | Recommended | Use to sync appointments to Google Calendar automatically |
| `whatsapp` skill | No | Optional; use to enable WhatsApp as a booking channel for customers |

**Pre-flight checks:**
- Verify the booking system is connected in the MyClaw Bots dashboard
- Confirm `${PROXY_URL}` and `$PROXY_API_KEY` environment variables are set
- Test getting booking configuration to verify connectivity before enabling channels

## How It Works

This skill wraps an appointment scheduling API. You can:
- Configure business hours, appointment types, and availability windows
- Accept bookings via web chat and WhatsApp 24/7
- Automatically sync all appointments to Google Calendar
- Send confirmation emails and SMS/WhatsApp messages
- Handle rescheduling and cancellations
- Send automated reminders before appointments
- Track no-show rates and booking analytics
- Support multiple time zones for customers

All requests use the proxy endpoint format: `${PROXY_URL}/appointments/...`

## Available Tools

**1. Get Current Booking Configuration**

```bash
curl -X GET "${PROXY_URL}/appointments/config" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

**Response:** Returns business hours, appointment types, availability settings, and timezone.

---

**2. Set Up or Update Configuration**

```bash
curl -X POST "${PROXY_URL}/appointments/config" \
  -H "Authorization: Bearer $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "business_name": "Acme Consulting",
    "business_hours": {
      "monday": {"start": "09:00", "end": "17:00"},
      "tuesday": {"start": "09:00", "end": "17:00"}
    },
    "appointment_types": [
      {"name": "Consultation", "duration_minutes": 30, "buffer_minutes": 15},
      {"name": "Strategy Session", "duration_minutes": 60, "buffer_minutes": 30}
    ],
    "max_advance_days": 60,
    "timezone": "America/New_York"
  }'
```

**Response:** Returns `{ "configured": true, "status": "active" }`

---

**3. List Upcoming Appointments**

```bash
curl -X GET "${PROXY_URL}/appointments/upcoming?limit=20" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

**Response:** Returns array of upcoming appointments with customer details, times, type, and status.

---

**4. Get Single Appointment Details**

```bash
curl -X GET "${PROXY_URL}/appointments/{id}" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

**Response:** Returns appointment details including customer name, email, phone, notes, and calendar status.

---

**5. Manually Book an Appointment**

```bash
curl -X POST "${PROXY_URL}/appointments/book" \
  -H "Authorization: Bearer $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "Jane Doe",
    "customer_email": "jane@example.com",
    "customer_phone": "+1-555-0123",
    "appointment_type": "Consultation",
    "datetime": "2026-04-05T14:30:00",
    "notes": "First time customer, interested in strategy"
  }'
```

**Response:** Returns `{ "appointment_id": "...", "confirmed": true, "calendar_synced": true }`

---

**6. Reschedule an Appointment**

```bash
curl -X PUT "${PROXY_URL}/appointments/{id}/reschedule" \
  -H "Authorization: Bearer $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "new_datetime": "2026-04-06T10:00:00"
  }'
```

**Response:** Returns `{ "rescheduled": true, "new_datetime": "...", "confirmation_sent": true }`

---

**7. Cancel an Appointment**

```bash
curl -X PUT "${PROXY_URL}/appointments/{id}/cancel" \
  -H "Authorization: Bearer $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "reason": "Customer requested cancellation"
  }'
```

**Response:** Returns `{ "cancelled": true, "cancellation_sent": true }`

---

**8. Check Availability**

```bash
curl -X GET "${PROXY_URL}/appointments/availability?date=2026-04-05&type=consultation" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

**Response:** Returns array of available time slots for the specified date and appointment type.

---

**9. Configure Reminders**

```bash
curl -X POST "${PROXY_URL}/appointments/reminders" \
  -H "Authorization: Bearer $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "appointment_id": "12345",
    "send_before_hours": [24, 1],
    "via": ["email", "whatsapp"]
  }'
```

**Response:** Returns `{ "reminders_configured": true, "schedule": [...] }`

---

**10. Get Booking Analytics**

```bash
curl -X GET "${PROXY_URL}/appointments/analytics?period=30d" \
  -H "Authorization: Bearer $PROXY_API_KEY"
```

**Response:** Returns `{ "total_bookings": 45, "completed": 42, "no_shows": 2, "cancellations": 1, "conversion_rate": 0.94 }`

---

**11. Enable a Booking Channel**

```bash
curl -X POST "${PROXY_URL}/appointments/channels/enable" \
  -H "Authorization: Bearer $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "whatsapp",
    "config": {
      "business_phone": "+1-555-0199",
      "greeting_message": "Hi! Book an appointment with us..."
    }
  }'
```

**Response:** Returns `{ "channel_enabled": true, "webhook_url": "..." }`

---

## Important Rules

1. **Always confirm time zone** — Clarify customer's time zone before confirming appointments to avoid confusion.
2. **Send immediate confirmation** — Confirm booking via email and WhatsApp within seconds of booking.
3. **Send reminders** — Automated reminders at 24 hours and 1 hour before appointment (adjustable).
4. **Respect business hours** — Never book outside configured business hours or on days off.
5. **Handle conflicts gracefully** — Don't allow double bookings; offer alternative slots.
6. **Sync to Google Calendar** — All bookings must sync to your connected Google Calendar.
7. **Track no-shows** — Monitor no-show rate; if >10%, follow up to understand issues.
8. **Update buffers as needed** — Adjust time buffers between appointments based on actual turnaround needs.

## Smart Strategy

- **Configure first:** Set up business hours, appointment types, and buffer times before enabling booking channels.
- **Enable channels gradually:** Start with web chat, add WhatsApp after testing.
- **Test booking flow:** Book a test appointment through both channels to verify configuration.
- **Monitor no-shows:** Check analytics weekly; if no-show rate climbs, tighten reminder schedule or require deposit.
- **Gather feedback:** Include follow-up survey in reminder messages to improve service.
- **Adjust buffer times:** Review calendar to identify if buffer times are adequate for your operations.
- **Use analytics:** Track which appointment types are most popular and which time slots fill fastest.
- **Optimize availability:** Increase capacity for high-demand slots and adjust pricing/availability accordingly.
