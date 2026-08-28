# 🎼 Nexus Vanguard: Original Score & Re-Recording Mix Provenance

- **Track:** Track 2 — ClickHouse Track (CineVector Vault)
- **Scored Final Master:** `evidence_media/Track2_CineVector/final/nexus_vanguard_scored_final.mp4`
- **Foley-Only Reference Master:** `evidence_media/Track2_CineVector/final/nexus_vanguard_foley_only_master.mp4`
- **Model:** `lyria-3-pro-preview` (Google Cloud Vertex AI Interactions API, project `atlas-495807`)
- **Selected Composition:** **Candidate B — “Dimensional Assault”** (Human Selection Confirmed)
- **Date:** 2026-08-28
- **Audio Delivery Standard:** 48 kHz / 24-bit PCM / AAC 320 kbps (EBU R128 Compliant)

---

## 🎨 1. Provenance & Originality Statement

1. **Artifact Nature:**
   - This scored reel is a **fixed, pre-generated cinematic proof artifact** created using Google Vertex AI's `veo-3.1-fast-generate-001` (video) and `lyria-3-pro-preview` (music score). It is not an on-demand generation endpoint inside the CineVector Vault web UI.
2. **Human Selection Rationale:**
   - Three complete candidates were generated under a strict pre-flight cost gate (US$0.24 total spend). Candidate B was selected by Atchayam for its hybrid symphonic/modular electronic textures, immense spatial scale, agile reconnaissance passage, and team-oriented dimensional climax.
   - Candidate B is used as **one continuous, unified composition** without splicing or crossfading from alternative candidates.
3. **SynthID & C2PA Provenance:**
   - The untouched original Lyria 3 Pro MP3 file (`candidate_b_dimensional_assault_original.mp3`) is preserved with its exact cryptographic hash (`3b3a12ba1d51950e11a9e5f863d728ab9127c1a66b84298ad64ba8c64a25c8a7`).
   - The final FFmpeg multi-track re-recording mix incorporates native Foley; it is documented and hashed separately.

---

## 🎚️ 2. Re-Recording Mix & Loudness Compliance

- **Native Foley Stem:** Extracted from the candidate reel (`nexus_vanguard_native_foley.wav`) and mixed with dynamic side-chain ducking so laser impacts, shield deflections, and footsteps remain audible.
- **Measured Integrated Loudness:** **$-16.0\text{ LUFS}$** (Target $-16\text{ to }-14\text{ LUFS}$).
- **Maximum True Peak:** **$-1.1\text{ dBFS}$** ($\le -1.0\text{ dBTP}$, zero clipping).
- **Loudness Range (LRA):** $8.1\text{ LU}$.
- **Video Synchronization:** Sample-accurate 1,341 frames @ 24 fps (56.166 seconds) with natural acoustic decay to the final frame.

---

## 📦 3. Master Deliverables & SHA-256 Manifest

| Deliverable | File Path | Format / Channels | Size (Bytes) | SHA-256 Checksum |
| :--- | :--- | :--- | :--- | :--- |
| **Scored Presentation Master** | `evidence_media/Track2_CineVector/final/nexus_vanguard_scored_final.mp4` | MP4 (1080p24 / AAC 320k 48kHz Stereo) | 252,399,359 | `e201250e37f8b7c0b3555db9a1001b420f81ac4c28fff011cc590e04398d2013` |
| **Foley-Only Reference Master** | `evidence_media/Track2_CineVector/final/nexus_vanguard_foley_only_master.mp4` | MP4 (1080p24 / AAC 48kHz Stereo) | 251,890,496 | `b29a9b1e9b3092dd8aceb0fa1598e725027d73af37bf13cca8d575a2491c1438` |
| **Isolated Original Score Stem** | `evidence_media/Track2_CineVector/final/nexus_vanguard_original_score.wav` | WAV (48kHz 24-bit Stereo) | 16,175,852 | `f62629b3504fc8198f3b145d554a7114674744d0392e624c9657b5fb95fb886f` |
| **Isolated Native Foley Stem** | `evidence_media/Track2_CineVector/final/nexus_vanguard_native_foley.wav` | WAV (48kHz 24-bit Stereo) | 16,146,534 | `7a94dd89966b44747ebc798031d2798e4e9cf768b556f8f5339f400767cb4432` |
| **Untouched Candidate B MP3** | `evidence_media/Track2_CineVector/audio/lyria3_pro_candidates/candidate_b_dimensional_assault_original.mp3` | MP3 (Lyria 3 Pro Original) | 1,308,565 | `3b3a12ba1d51950e11a9e5f863d728ab9127c1a66b84298ad64ba8c64a25c8a7` |
