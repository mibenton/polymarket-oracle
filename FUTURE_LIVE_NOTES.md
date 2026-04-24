# Future Live Deployment Notes (暫不執行)

**Current status**: Paper-only. 3-month validation in progress until 2026-07-24.
Revisit this file when paper trade results justify live deployment.

## Pre-deployment Checklist

When paper trade passes thresholds, walk through in order:

### 1. VPN Setup
- Subscribe to **NordVPN / ExpressVPN / Mullvad** (paid, NOT free)
- Primary node: Japan or Singapore (stable + fast to TW)
- Backup node: UK or Canada
- **Always connect to same city** (avoid IP jumping = red flag)
- Confirm IP with https://whatismyipaddress.com before each Polymarket session

### 2. New Wallet (Separation)
- Install MetaMask
- Create **new account** (not daily-use account)
- Name: `polymarket-trading` or similar
- Store seed phrase offline (paper, safe)
- Add **Polygon network**:
  - RPC URL: https://polygon-rpc.com
  - Chain ID: 137
  - Symbol: MATIC

### 3. USDC Funding Path
- Register at **Gate.io** or **Bybit** (Taiwan-friendly)
- Buy USDC with NT$ (C2C or bank transfer)
- Withdraw to new MetaMask wallet on **Polygon network** (much lower fee than Ethereum)
- NEVER withdraw from main exchange account directly to same addresses that handle personal spending

### 4. First Polymarket Session
- Start VPN, verify IP location
- Go to polymarket.com, register with the new wallet
- **Do NOT enter any real name, address, or KYC data**
- Keep first deposit small: **$100 max**
- Verify deposit lands in Polymarket balance
- Place **1 small bet** ($20) on a Tier S++ or A candidate
- Wait for settlement
- If winning: **immediately withdraw** to confirm withdrawal loop works
- Only scale up after this full round-trip succeeds

### 5. Scaling Rules
- Stage 1 (validation): $100 total, single bet
- Stage 2 (flow test): $500, 3-5 bets over 1 week
- Stage 3 (steady): $1,000-2,000, per-week stake cap
- **Never exceed 5% of stage 3 bankroll in a single bet**

### 6. Withdrawal Discipline
- **NEVER** accumulate > $2,000 in Polymarket balance
- Weekly withdraw: $200-500 (keeps you under radar)
- USDC back to your MetaMask, then exchange → NT$ via Gate/Bybit
- **Keep transaction records** for tax (store dates, amounts, Polygon tx hashes)

### 7. Legal & Tax (Taiwan 2026)
- Current status: Polymarket banned in TW (close-only)
- Using VPN + wallet: **違反 Polymarket TOS, but no Taiwan law specifically criminalizes crypto prediction market usage** (as of knowledge cutoff)
- However, **if gains > NT$800k annually**, considered taxable income
- If you achieve meaningful profit, **consult an accountant** before year-end
- Keep a **transaction log** in spreadsheet with:
  - Date
  - Market slug
  - Bet size (USD)
  - Result (USD)
  - Polygon tx hash
  - Running balance

### 8. Risk Mitigation
- **Assume 20-30% of paper edge evaporates** in live conditions
- **Assume UMA disputes** happen occasionally — budget -$1000 as "insurance"
- **Have a kill switch**: if real PnL < -25% after 1 month, STOP
- **Don't go all-in**: never put > 5% of your net worth into Polymarket

### 9. What NOT to do
- ❌ KYC with real ID (unless you're OK losing access)
- ❌ Use same address as a regulated exchange account for deposits
- ❌ Tell anyone about it (legal gray area)
- ❌ Grow balance > $10k (KYC trigger)
- ❌ Switch VPN nodes randomly
- ❌ Connect from your home network without VPN

### 10. Kill switches
- Polymarket freezes your account → take the loss, move on
- Taiwan law changes → stop immediately
- Edge decay confirmed (< +5% monthly for 2+ months) → stop
- Personal life stress from it → stop

---

## Critical mindset

**This is gambling with moderate edge**, not investing.
- Expect 15-25% drawdowns
- Expect occasional UMA disputes
- Expect your account to be eventually restricted
- **Have an exit plan** from day 1

## Decision point

After 3 months paper trade:
- **If cumulative > +30%**: consider Stage 1 with $100 test
- **If 0-30%**: continue paper 3 more months
- **If negative**: abandon Polymarket, move on

---

*This document is a memo for future self. Do not execute until paper trade validates.*
