> **運用方針更新（2026-10-13 JST）:** Instagramの投稿・状態確認・分析の実行基盤はこのGitHubリポジトリとGitHub Actionsに統一する。Metricoolは今後使用せず、フォールバックや再接続先にも指定しない。投稿先はInstagram公式API。既存の承認済みCanva Connect素材制作と出自検証は維持する。
>
> **確認済みの状態:** 日次5枠のworkflowは有効、公開スイッチもtrue。公式Canva素材の公開記録がある。定期実行による継続公開の成否は各Actions runとstate/postsのmedia_id・permalinkで確認する。設定だけで稼働成功と報告しない。以前の「PAUSED／OAuth未設定」という記載は古いため廃止する。

# Panipani Instagram — Autonomous Operation Policy

Effective: 2026-10-13 (JST)
Instagram account: @reiv2220
GitHub repository: https://github.com/o9o84441100-droid/panipani-instagram-auto

## Delegation
The account owner has authorized the project to:
- Publish original, accurate Japanese educational AI productivity Reels on the five configured daily slots.
- Choose topics, visual hooks, cover wording, caption prompts and posting experiments without seeking per-post approval.
- Monitor actual Instagram outcomes and refine the strategy and content mix automatically.
- Add operational safeguards, monitoring, validation, and failure alerts.

The owner will intervene when results such as follower growth or reach are not satisfactory. This is a standing policy for **the configured automation**, not authorization to make unrelated account changes, spend money, impersonate others, use copyrighted audio, or follow/message strangers.

## Desired outcomes and review
Primary measures: verified net follower growth, meaningful reach and qualified engaged viewers.
Secondary measures: Reel views (with age window noted), saves, shares, comments, and profile visits where the API provides them.
Keep zero, unavailable, and unpublished distinct. Record post age before comparing outcomes. Do not claim causation from a few posts.
Start with a 14-day observation window at five posts per day, then reassess empirically. Do not equate output volume with audience growth.
No bought followers, engagement exchanges, fake reviews, fabricated claims or unsolicited automated engagement.

## Active background automation
- Five scheduled daily Reel publications: .github/workflows/panipani-daily-reels.yml
- Official read-only metrics and snapshot: .github/workflows/performance-review.yml (nightly)
- Weekly data-driven category weighting: .github/workflows/weekly-optimizer.yml
- Next-morning audit of missing publication records: .github/workflows/post-audit.yml
- Separate safe no-publish validation workflow: .github/workflows/validate-daily.yml

These are GitHub Actions jobs; they do not require the user's phone or PC to remain open. Runs can be delayed, fail, or be skipped; never assume publication without Meta media ID/permalink confirmation.
The assistant does NOT independently monitor the account outside scheduled workflows or active tool sessions.

## Guardrails
- Secrets are stored in GitHub Actions repository Secrets and must never appear in source, logs, Issues, captions or public Pages files.
- A Reel is published only after its MP4 is verifiably retrievable via public HTTPS.
- Never blindly retry a failed job if the Instagram publish step may already have succeeded.
- Issue an operational alert for missing ledger slots; use posted media IDs to reconcile before any rerun.
- Use original, self-generated visuals and sound. Do not automatically publish private Drive photos or personal user data.
- Escalate owner-only permission/authorization and token renewal steps rather than requesting credentials in chat.
- Analytics not exposed by the API must be shown as unavailable rather than guessed.
- Algorithmic weighting is disabled until at least 30 comparable approximately 48h media samples over at least three topic categories exist; weights are capped and other topics remain in rotation.

## Current limitations
- Posts use an original template-driven 86-topic bank, not dynamic LLM generation from current trends.
- Google Drive material folder is currently separate from the GitHub-generated Reel archive.
- GitHub Actions artifacts have finite retention, and GitHub Pages delivery depends on provider availability.
- A Google Calendar reminder exists for checking/renewing the Instagram token; automatic token secret rotation is not implemented.
- An autonomous analytics loop is installed, but actual performance improvement can only be assessed over time.

## 制作と補助素材の優先順位（2026-10-13訂正）
- 基本経路は承認済みCanvaリールテンプレートへの内容反映、Canva公式MP4書き出し、GitHub Pagesでの配信、Instagram公式APIでの公開。
- Google Driveは補助。素材なし・アクセス不可でもCanva標準制作を止めない。指定した素材を使う場合だけ権利、第三者、個人情報、可読性を確認してCanvaに取り込む。
- 既存Drive「投稿用」を補助素材置き場として利用する。Driveの認証情報や内部フォルダIDを公開ソースに追加しない。GitHubからDriveを自動走査する連携は未実装であり、自動取込済みと報告しない。
- CanvaのAI画像・AI動画生成を毎回自動実行する処理は現状未実装。現行は承認済みの実Canvaテンプレートの自動内容反映と公式MP4出力。AI生成機能の可用性・契約・公開権利を確認できる範囲で素材制作に利用し、未実行の生成を完了と称さない。
- 既存JST実行時刻08:05／10:05／12:05／18:05／21:05と公開スイッチを維持する。Driveへの素材追加やユーザーの端末起動を実行条件にしない。
- Canva書き出し前にInstagramの接続を確認。秘密鍵未設定の接続チェックは失敗扱いとする。

## Canva完成素材のDrive保存
- Canva編集元はCanvaに保持し、GitHub Actionsの制作artifactにMP4・caption.txt・canva_provenance.jsonを含める。
- 接続済みGitHub/Google Driveコネクタを使用する「Canva制作物をDriveへ保存」タスクを毎時15分に実行し、動画・本文・元デザイン参照を既存「投稿用」へ保存する。投稿スケジュールは変更しない。
- 保存タスクはartifact IDとファイル名で重複を防ぎ、アップロード後にmetadataを読み戻す。GitHub上のアーカイブ削除・Instagramへの再投稿をしない。
- Driveへの追加認証情報をGitHubへ移さない。Drive保存に失敗してもCanvaからInstagramへの投稿は独立に継続。
- 初回確認済み: run38348128190のCanva動画はDriveへ保存済み、サイズ1288452bytes、SHA256 a861de0c4f13b85d30fe498e158f67369417dc4392bd5894ea8d1b59287114e7。定期保存と日次5投稿の継続完遂は各実行で検証する。

## 実写背景の優先（2026-10-13・ユーザー指定）
可能な限りリール背景は実写写真・実写動画を優先する。Canvaの既存リールテンプレートと利用できる実写素材を制作の中心にする。カフェ、手元、PC作業、街並み、部屋、自然など投稿内容に合う素材を選び、同じ背景を連発しない。Driveは補助であり必須にしない。人物・場所をユーザー本人の実体験として偽らない。背景に暗幕・余白を使って日本語字幕を読みやすくし、テンプレートの文字重なり・切れ・画面端を確認する。実写素材の権利・可用性を確認できないときは無理に使わず、図解など必要な代替を選ぶ。新たなテンプレートの自動運用への追加は、内容差替えと公式動画書き出しを確認してから行う。この方針保存だけで既存の非実写テンプレートの自動差替え完了と報告しない。

## スケジュール関連の確認状態（2026-10-13 22時台）
既存の朝分析07:30、投稿08:05/10:05/12:05/18:05/21:05、Drive保存毎時15分、成果報告23:50を維持。関連タスクを実写背景優先・実写/AI素材の区別・公開事実の確認に統一。
実写候補DAHX5Y7yKgQはdatasetが空。現在のHOOK/SITUATION/PROMPT/CAUTION/CTAを前提としたautofillには未登録で、追加にはフィールド設定と動画出力の確認が必要。Canva Connectの更新はHTTP400で失敗中であり、新規制作の連続運用は未復旧。チャットCanva連携成功をGitHub OAuth復旧の証拠にしない。実写の制作方針を保存したことと、実写リールの自動制作実装を区別する。

## 2026-10-14再実行と確認済み阻害要因
日次cronの遅延実行で元の枠が古くなり、2時間の許容範囲外として投稿が全件スキップされていた。cronを起動信号として現在時刻の直近当日枠を選択し、POST_SLOT_OVERRIDEで制作・公開・記録を固定。5つの投稿目標時刻は維持し、毎時17分の補助確認を追加。早出し・翌日への繰越・二重公開を防ぐ。
2026-10-14再実行run38552071722ではguard成功、公開工程への進行を確認したがInstagram事前確認で失敗。/meでHTTP400/code200/OAuthException/transient=false/message=API access blocked。投稿を実行せず停止。Meta側の具体的な制限理由はレスポンスから未確定で、アプリ状態と権限確認が必要。
独立診断run38552068982でCanva更新はHTTP400/code=invalid_grantを確認。トークン失効・無効・取消などの内訳は未確定。新規制作のOAuthは未復旧。再認証してCANVA_REFRESH_TOKEN secretを更新後、canva-reauthorize.ymlを一度実行し、新規認証を保存済み旧トークンに優先して交換・暗号保存できる手順を用意した。成功後は通常の暗号保存された更新トークンを使用する。秘密の値をチャットへ出さない。
