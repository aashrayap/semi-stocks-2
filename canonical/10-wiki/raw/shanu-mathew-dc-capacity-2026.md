# How Much Data Center Capacity Is Actually Coming Online Per Year — And Who Is Absorbing It?

**Author:** Shanu Mathew (@ShanuMathew93)
**Platform:** X (Post)
**Date:** 2026-04-13
**Views:** 5,503

---

Trying to bridge thoughts from different sources & podcast given the focus around the AI buildout.

## The Installed Base

FERC confirmed in their March 2026 State of the Markets report that US data center capacity exceeded 50 GW at year-end 2025. Industry estimates put total US capacity in the 35-40 GW range at year-end 2024 (Bain was at ~35GW, Morgan Stanley's model pegged it at 37 GW). That implies roughly 10-15 GW of net additions in 2025, a massive step-up from prior years. Total facility power, critical IT load, and hyperscale-only all produce different baselines — I haven't seen two sources use the same definition consistently.

## Frontier Labs

Brad Gerstner (@altcap, investor in both OpenAI and Anthropic) says OAI and Anthropic have 1.5-2 GW each today, going to ~5 GW by year-end.

Dylan Patel at SemiAnalysis (Dwarkesh Podcast, March 2026): Both at roughly 2-2.5 GW today. Both reach 5-6 GW by year-end 2026, OpenAI slightly higher. Both targeting ~10 GW by end of 2027.

Sarah Friar disclosed 1.9 GW for OpenAI at year-end 2025. Anthropic's operational capacity is likely in the 1.5-2 GW range.

On year-end targets, there's a wide gap between what's been contracted (Stargate US + UAE, NVIDIA 10 GW partnership, CoreWeave, Google TPU mega-deal) and what will physically be energized by December. Dylan's 5-6 GW per lab is likely the more physically grounded number, built bottom-up. Per Dylan, Anthropic was conservative on locking up compute early while OpenAI signed aggressively with Microsoft, CoreWeave, Oracle, & even SoftBank Energy — so Anthropic has to now pay premium rental rates or go to lower-quality providers to catch up (but Gerstner's comments made it sound like the take rate wasn't that high).

Neither leading lab owns or builds data centers. Their ~6 GW of combined incremental capacity in 2026 is physically built and operated by AWS, Google, Microsoft, CoreWeave, Oracle, and others but contractually dedicated to serving OpenAI and Anthropic workloads. Assume a meaningful chunk of AWS's disclosed additions goes to Anthropic's Trainium/Rainier clusters, and a meaningful chunk of CoreWeave's build goes to OpenAI. CoreWeave also recently signed a multi-year agreement to support Anthropic's Claude models, with new capacity coming online in 2026. Frontier lab demand and hyperscaler supply overlap — they are not additive.

## Hyperscaler Disclosures on Physical Delivery

These are a mix of US and global figures, and facility power vs. IT load definitions vary across companies.

**Amazon (AWS):** Jassy disclosed AWS added 3.9 GW of new power capacity in 2025 (1.2 GW in Q4 alone). Operating from a base of roughly 8 GW at year-end 2025, with a target to double total capacity by year-end 2027 implying ~16 GW total. Still describes demand as outpacing supply. AWS operates 38 regions across 27 countries = the 3.9 GW is almost certainly global, not US-only, though the US is the clear majority.

**Microsoft:** Nadella's team disclosed over 2 GW added in FY2025, with roughly 1 GW brought on in the December quarter alone. 400+ data centers globally. Also targeting roughly double capacity by 2027. SemiAnalysis reported that Microsoft paused over 3.5 GW of capacity that would have been built by 2028, though Reuters/TD Cowen put the figure lower at ~2 GW of terminated leases in the US and Europe, and Bernstein says actual cancelled contracts total only "a couple hundred megawatts." The precise number is disputed. The directional point is clear that Microsoft was recalibrating its self-build vs. lease mix but now seems to be building again.

**Google (Alphabet):** Pichai and team guided 2026 capex at $175-185B, nearly double 2025. No explicit "we added X GW" disclosure comparable to AWS. Dylan describes them as "still capacity constrained" and acting fast = buying an energy company, putting down turbine deposits for 2028-29, negotiating long-term power agreements. A large chunk of new capacity is going to TPUs for internal products (Gemini across Search, Android, Workspace) and the Anthropic deal (~1 GW in 2026, ~3.5 GW from 2027). Without a disclosed GW figure, estimated 3-5 GW of 2026 additions based on capex trajectory similar to the other giants.

**Meta:** Zuckerberg guided $115-135B in 2026 capex, nearly double 2025. Building for internal AI workloads (Llama training, inference across Instagram-WhatsApp-Threads) + Meta Superintelligence Labs. 1 GW campus in El Paso (investment scaled from $1.5B to $10B), 1 GW campus in Lebanon, Indiana, JV in Louisiana (~$27B estimated), Prometheus bringing 1 GW online in 2026. On top of the self-build, Meta committed $35.2B to CoreWeave across two deals for third-party capacity.

## Independent Builders and Neoclouds

**xAI:** Colossus 2 in Memphis is targeting 1-2 GW of capacity to support 550,000 next-gen Nvidia chips, scaling to 1 million GPUs. Deployed 35 natural gas turbines generating 420 MW behind the meter to work around grid constraints.

**CoreWeave:** Added 490 MW across 11 data centers in 2025 (260 MW in Q4). Total active capacity hit 850 MW at year-end against 3.1 GW contracted. Planning $30-35B of 2026 capex. Also acting as lead builder on the 1.2 GW Stargate Abilene campus for OpenAI.

**Nebius:** Tracking toward 800 MW - 1 GW of available capacity in 2026. 310 MW facility in Finland. Meta agreed to buy $12B of AI computing capacity from Nebius by 2027, with an option for an additional $15B over five years — up to $27B total.

## Sense-Checking the Total

A few different ways to triangulate:

- Morgan Stanley forecasts ~24 GW of global additions in 2026 × 50-60% US = ~13-14 GW.
- BloombergNEF has something like ~8-10 GW of IT Load × 1.4 PUE = ~12-13 GW.
- ClimateTech VC data showing at least 16 GW of US data center capacity slated to come online in 2026 across 140 projects but warns 30-50% may face delays due to power constraints and equipment shortages.
- Crude capex math: $600-700B in 2026 hyperscaler capex at roughly $40-50B per GW of fully-built capacity also implies mid-teens GW.
- Colliers reported that North American data center absorption hit 15.6 GW in 2025, double the 2024 level. The narrower CBRE primary-colocation-market figure of 2.5 GW only captures a subset of traditional leased space and misses hyperscaler self-build, behind-the-meter neocloud facilities, and training clusters entirely.
- Epoch AI's frontier data center tracker confirms the step-function: most of the largest campuses (e.g., Meta Hyperion at 2.2 GW, Microsoft Fairwater above 1 GW) don't fully arrive until 2027-2028.

## Base Case: ~15 GW US Net Energized Capacity Additions in 2026

- Bear case: 12-13 GW (permitting delays push energizations into 2027)
- Bull case: 18-20 GW (everything announced delivers on schedule)

### Bucket Breakdown

| Bucket | GW | Details |
|--------|-----|---------|
| Frontier labs (OpenAI + Anthropic) | ~6 GW | Physically built by AWS/Google/MSFT/CRWV/ORCL, contractually dedicated. ~3 GW incremental per lab. |
| Hyperscaler first-party AI | ~4-5 GW | MSFT Copilot (900M MAUs), Google Gemini, Amazon Alexa+, Meta ad/reco/Llama |
| Third-party AI cloud + independents | ~2-3 GW | xAI, Meta as CRWV/Nebius customer, enterprise, sovereign AI, inference APIs |
| Non-AI cloud + overbuild/commissioning lag | ~2 GW | Traditional enterprise + power energized ahead of full rack load |

### Where the Number Could Be Higher

- ~90% of incremental build is AI-related. Only ~1 GW traditional cloud.
- Enterprise inference and cloud AI demand growing faster than modeled.
- Oracle RPO exploded to $523B. AWS non-Anthropic AI business at $15B+ ARR. Amazon custom chip business at $20B+ run-rate.
- Colliers/Jefferies: North American absorption at 15.6 GW in 2025 = demand tracking much closer to total additions than assumed.
- If enterprise AI API adoption inflecting harder, "third-party AI cloud" and "hyperscaler first-party" buckets each 1-2 GW bigger → 18-20 GW.
