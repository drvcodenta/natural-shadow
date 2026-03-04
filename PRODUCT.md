# Natural Shadow — Product Document

## What is Natural Shadow?

Natural Shadow is a **pre-production sandbox** that lets teams observe, audit, and control how their AI agents make financial decisions — *before* a single real dollar moves.

Think of it as a **flight simulator for AI spending**. You wouldn't put a pilot in a cockpit without simulation hours. Natural Shadow gives AI agents the same treatment.

---

## The Problem It Solves

Companies are deploying AI agents that can autonomously:
- Pay invoices
- Transfer funds
- Approve vendor contracts
- Reorder inventory

But **nobody knows what these agents would actually do** until they're live — with a real bank account attached. That's terrifying.

### What goes wrong today:
| Scenario | Risk |
|----------|------|
| Agent pays a $12,500 GPU invoice without approval | Uncontrolled capital expenditure |
| Agent sends money to a flagged vendor | Compliance violation |
| Agent makes 47 micro-transactions in an hour | Treasury drain via death-by-a-thousand-cuts |
| Agent provides no reasoning for a transfer | Zero audit trail |

**Natural Shadow catches all of these before they happen.**

---

## How It Works

```
┌─────────────────────┐       ┌──────────────────────┐       ┌─────────────────────┐
│   AI Agent          │       │   Natural Shadow SDK │       │   Shadow Dashboard  │
│                     │──────▶│                       │──────▶│                     │
│ "Pay $4,500 to      │       │ ✓ Policy check        │       │ ✓ Live feed         │
│  Enterprise AI Ltd" │       │ ✓ Risk scoring        │       │ ✓ Decision log      │
│                     │       │ ✓ Block / Approve     │       │ ✓ Analytics         │
└─────────────────────┘       └──────────────────────┘       └─────────────────────┘
```

### 1. SDK Wrapper (Python)
A lightweight wrapper that sits between the AI agent and any financial tool call. It:
- **Intercepts** every spending intent
- **Evaluates** against configurable policy rules (per-tx limits, daily caps, blocked recipients)
- **Scores** risk (0–100) using transaction heuristics
- **Logs** every decision to the dashboard

### 2. Shadow Dashboard (Web)
A real-time monitoring interface showing:
- **Agent Reasoning** — why the agent wanted to spend
- **Natural's Decision** — would it have been approved or blocked?
- **Risk Score** — simulated fraud/risk analysis

---

## Why Natural's Production Team Should Care

### 1. Sales Enablement
> *"Look how many times your agent tried to overspend today. Our ledger caught all of them."*

This is a **live demo you can show prospects**. Instead of slides, show them their own agent trying to spend $12,500 and Natural blocking it in real-time. That's a deal closer.

### 2. Pre-Production Risk Assessment
Before any company connects a real bank account to Natural, Shadow answers:
- How aggressive is this agent's spending behavior?
- Does it provide reasoning for its decisions?
- How often does it hit policy limits?
- What's the average risk profile?

This data shapes the **actual policy configuration** for production.

### 3. Policy Tuning Engine
Shadow lets teams **experiment with different policy limits** without consequences:
- "What if we set max_per_tx to $500 instead of $1,000?"
- "What if we require reasoning for every transaction?"
- "What if we block this vendor category?"

Run the agent through Shadow with different configs. See the results. Then go live confident.

### 4. Compliance & Audit Trail
Every agent attempt is logged with:
- Timestamp
- Tool called
- Amount & recipient
- Agent's reasoning
- Decision & reason
- Risk score

This is the **audit log regulators will ask for**. Shadow builds it before you even go live.

### 5. Agent Benchmarking
Comparing two agent models? Run both through Shadow:
- Which one overspends more?
- Which one provides better reasoning?
- Which one triggers fewer flags?

Shadow becomes a **testing framework for financial AI agents**.

---

## How This Fits Into Natural's Product

```
┌─────────────────────────────────────────────────────┐
│                 CUSTOMER JOURNEY                     │
│                                                      │
│  ┌──────────┐    ┌──────────────┐    ┌────────────┐ │
│  │ Sign Up  │───▶│ SHADOW MODE  │───▶│ Production │ │
│  │          │    │              │    │ (Real Bank)│ │
│  │          │    │ • Test agent │    │            │ │
│  │          │    │ • Set limits │    │ • Live $   │ │
│  │          │    │ • Tune policy│    │ • Real API │ │
│  │          │    │ • See risks  │    │ • Audit    │ │
│  └──────────┘    └──────────────┘    └────────────┘ │
│                                                      │
│  Shadow is the BRIDGE between signup and production  │
└─────────────────────────────────────────────────────┘
```

Shadow isn't a separate product — it's the **onboarding ramp**. Every customer passes through it. It:
- Reduces onboarding risk to zero
- Builds customer confidence before they connect real money
- Generates data that auto-configures their production policy
- Creates an "aha moment" when they see their agent's behavior for the first time

---

## Metrics That Matter (from demo data)

| Metric | Value | Insight |
|--------|-------|---------|
| **Blocked Rate** | 50% | Half of all agent attempts were policy violations |
| **Amount Saved** | $20,000 | Money that would have moved without Natural |
| **Avg Risk Score** | 39/100 | Overall moderate risk — needs policy tuning |
| **No-Reasoning Rate** | 10% | Some agents skip justification entirely |

These numbers tell a story: **AI agents need guardrails, and Natural provides them.**

---

## Next Steps for Production

1. **Persistent Storage** — Swap in-memory store for Vercel KV or Supabase for persistent logs
2. **Real-time WebSocket Feed** — Live updates without page refresh
3. **Multi-Agent Support** — Track multiple agents across different teams
4. **Policy Builder UI** — Visual config editor for spending rules
5. **Export & Reports** — PDF/CSV compliance reports for auditors
6. **Webhook Alerts** — Slack/email notifications on high-risk attempts
